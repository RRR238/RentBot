import json
import time
import warnings
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

import re

from .Prompts import (
    agentic_flow_prompt_v2 as agentic_flow_prompt,
    extract_preferences_from_conversation_prompt,
    generate_synthetic_listing_prompt,
    extract_search_keywords_prompt,
    generate_query_title_prompt,
)
from .Schemas import KeyAttributes
from fastembed import SparseTextEmbedding
from qdrant_client.models import SparseVector
from sentence_transformers import CrossEncoder

from .utils import (
    create_chain,
    normalize_key_attributes,
    prepare_enriched_filters_from_key_attributes,
    rerank,
    extract_chat_history_as_dict,
    format_chat_history,
)
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Models / services
# ---------------------------------------------------------------------------

llm_langchain = ChatOpenAI(temperature=0.9,
                           model="gpt-4.1")
llm_langchain_deterministic = ChatOpenAI(temperature=0.0,
                                         model="gpt-4o")
reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",)
sparse_model = SparseTextEmbedding(model_name="Qdrant/bm42-all-minilm-l6-v2-attentions")
llm = LLM()
vdb = Vector_DB_Qdrant('rent-bot-index')
repository = Rent_offers_repository(CONN_STRING)

# ---------------------------------------------------------------------------
# Chains
# ---------------------------------------------------------------------------

agentic_chain = create_chain(
    llm_langchain, agentic_flow_prompt,
    messages_placeholder="chat_history",
    human_template="{input}",
)

_extract_prompt = ChatPromptTemplate.from_messages([
    ("system", extract_preferences_from_conversation_prompt),
    ("human", "{chat_history}\n\nExtrahuj preferencie používateľa z vyššie uvedenej konverzácie."),
])
extract_chain = _extract_prompt | llm_langchain_deterministic.with_structured_output(KeyAttributes)

synthetic_listing_chain = create_chain(
    llm_langchain_deterministic,
    generate_synthetic_listing_prompt,
    human_template="{key_attributes}",
)

_keywords_prompt = ChatPromptTemplate.from_messages([
    ("system", extract_search_keywords_prompt),
    ("human", "{ostatne_preferencie}"),
])
keywords_chain = _keywords_prompt | llm_langchain_deterministic

_query_title_prompt = ChatPromptTemplate.from_messages([
    ("system", generate_query_title_prompt),
    ("human", "Typ nehnuteľnosti: {typ_nehnutelnosti}\nNovostavba: {novostavba}\nPreferencie: {ostatne_preferencie}"),
])
query_title_chain = _query_title_prompt | llm_langchain_deterministic

SOFT_QUALIFIERS_RE = re.compile(
    r'\b(ideálne|skôr|aspoň|najlepšie|určite|nejaký|nejakú|nejaké|nejakého|'
    r'prípadne|možno|keby|pokiaľ možno|nejak[oý]?)\b',
    flags=re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

SEARCH_TRIGGER = "P"
SAVE_TRIGGER = "S"

# --- Search hyperparameters (tune here) ---
HNSW_EF             = 256    # higher = more accurate HNSW (default 128)
EXACT               = False  # True = brute force exact search (slow but 100% accurate)
PREFETCH_MULTIPLIER = 3      # prefetch k*N candidates per source before RRF

chat_history: list = []
eval_records: list = []

opening = agentic_chain.invoke({"chat_history": chat_history, "input": "Začni konverzáciu."})
print(f"🤖: {opening.content}")
chat_history.append(HumanMessage(content="Začni konverzáciu."))
chat_history.append(AIMessage(content=opening.content))

while True:
    query = input("You: ").strip()

    if query == SEARCH_TRIGGER:
        t_start = time.time()

        # --- Step 1: extract structured preferences directly from conversation ---
        formatted_history = format_chat_history(extract_chat_history_as_dict(chat_history))
        key_attributes: KeyAttributes = extract_chain.invoke({"chat_history": formatted_history})
        key_attributes = normalize_key_attributes(key_attributes)
        print(f"\n[key attributes]: {key_attributes}")

        # --- Step 2: build NADPIS/OPIS query matching listing embedding format ---
        raw_opis = key_attributes.ostatne_preferencie or ""
        cleaned_opis = SOFT_QUALIFIERS_RE.sub("", raw_opis).strip(" ,")

        query_title = query_title_chain.invoke({
            "typ_nehnutelnosti": ", ".join(key_attributes.typ_nehnutelnosti) if key_attributes.typ_nehnutelnosti else "byt",
            "novostavba": key_attributes.novostavba,
            "ostatne_preferencie": raw_opis,
        }).content.strip()

        query_text = f"NADPIS:\n{query_title}\n\nOPIS:\n{cleaned_opis}"
        print(f"[query text]:\n{query_text}")

        # --- Step 3: vector search (hybrid: dense + BM42 sparse) ---
        filters = prepare_enriched_filters_from_key_attributes(key_attributes)
        embedding = llm.get_embedding(query_text, model='text-embedding-3-large')
        sparse_result = list(sparse_model.embed([query_text]))[0]
        sparse_vec = SparseVector(
            indices=sparse_result.indices.tolist(),
            values=sparse_result.values.tolist(),
        )
        results = vdb.enriched_filtered_vector_search(
            embedding,
            50,
            filters,
            use_hybrid=True,
            sparse_vector=sparse_vec,
            hnsw_ef=HNSW_EF,
            exact=EXACT,
            prefetch_multiplier=PREFETCH_MULTIPLIER,
        )[0]

        # fetch titles from DB for reranking
        titles = []
        for point in results.points:
            db_id = point.payload.get('id')
            offer = repository.get_offer_by_id_or_url(int(db_id)) if db_id else None
            titles.append(offer.title if offer else "")

        reranked_points = rerank(query_text, results.points, reranker, texts=titles)

        t_total = time.time() - t_start
        print(f"\n[results] ({len(reranked_points)} total, {t_total:.1f}s):")

        result_entries = []
        for i, (rerank_score, point) in enumerate(reranked_points, 1):
            print(f"{i:2}. [{rerank_score:.4f}] {point.payload['source_url']}")
            db_id = point.payload.get('id')
            description = None
            if db_id is not None:
                offer = repository.get_offer_by_id_or_url(int(db_id))
                if offer is not None:
                    description = offer.description

            result_entries.append({
                "description": description,
                "rerank_score": rerank_score,
            })

        eval_records.append({
            "chat_history": formatted_history,
            "key_attributes": key_attributes,
            "query_text": query_text,
            "results": result_entries,
        })

        print(f"\n[eval records collected]: {len(eval_records)}")
        chat_history.clear()

    elif query == SAVE_TRIGGER:
        filename = f"eval_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        serializable = [
            {**r, "key_attributes": r["key_attributes"].model_dump()}
            for r in eval_records
        ]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        print(f"[saved {len(eval_records)} records to {filename}]")

    else:
        response = agentic_chain.invoke({"chat_history": chat_history, "input": query})
        print(f"🤖: {response.content}")
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=response.content))
