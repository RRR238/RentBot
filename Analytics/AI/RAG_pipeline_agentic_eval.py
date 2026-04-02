import json
import warnings
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from .Prompts import (
    agentic_flow_prompt_v2 as agentic_flow_prompt,
    get_key_attributes_structured_prompt,
    summarize_preferences_system_prompt,
)
from .Schemas import KeyAttributes
from .utils import (
    create_chain,
    prepare_enriched_filters_from_key_attributes,
    extract_chat_history_as_dict,
    format_chat_history,
)
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Scrapping.Rent_offers_repository import Rent_offers_repository
from Analytics.config import CONN_STRING

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

gen_model = "gpt-4o"

# ---------------------------------------------------------------------------
# Models / services
# ---------------------------------------------------------------------------

llm_langchain = ChatOpenAI(temperature=0.9, model=gen_model)
llm_langchain_deterministic = ChatOpenAI(temperature=0.0, model=gen_model)
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

summarization_chain = create_chain(
    llm_langchain_deterministic, summarize_preferences_system_prompt,
    messages_placeholder="messages",
    human_template="Zhrň preferencie používateľa z vyššie uvedenej konverzácie podľa inštrukcií v systémovej správe.",
)

_key_attributes_prompt = ChatPromptTemplate.from_messages([
    ("system", get_key_attributes_structured_prompt),
    ("human", "{input}"),
])
key_attributes_chain = _key_attributes_prompt | llm_langchain_deterministic.with_structured_output(KeyAttributes)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

org_summary = (
    "cena: None, počet izieb: None, rozloha: None, typ nehnuteľnosti: None, "
    "novostavba: None, lokalita: None, ostatné preferencie: None"
)

SEARCH_TRIGGER = "P"
SAVE_TRIGGER = "S"

chat_history = []
eval_records = []

opening = agentic_chain.invoke({"chat_history": chat_history, "input": "Začni konverzáciu."})
print(f"🤖: {opening.content}")
chat_history.append(HumanMessage(content="Začni konverzáciu."))
chat_history.append(AIMessage(content=opening.content))

while True:
    query = input("You: ").strip()

    if query == SEARCH_TRIGGER:
        # --- Step 1: summarize preferences ---
        summary_response = summarization_chain.invoke({"messages": chat_history})
        response_summary = summary_response.content
        print(f"\n[summary]: {response_summary}")

        try:
            idx = response_summary.index(', ostatné preferencie')
            processed_summary = response_summary[:idx]
            summary_to_embedd = response_summary[idx + len(', ostatné preferencie: '):]
            org_summary = response_summary
        except ValueError:
            idx = org_summary.index(', ostatné preferencie')
            processed_summary = org_summary[:idx]
            summary_to_embedd = org_summary[idx + len(', ostatné preferencie: '):]

        print(f"[processed summary]: {processed_summary}")
        print(f"[summary to embedd]: {summary_to_embedd}")

        # --- Step 2: extract structured key attributes ---
        key_attributes: KeyAttributes = key_attributes_chain.invoke({"input": processed_summary})
        print(f"[key attributes]: {key_attributes}")

        # --- Step 3: vector search ---
        filters = prepare_enriched_filters_from_key_attributes(key_attributes)
        embedding = llm.get_embedding(summary_to_embedd, model='text-embedding-3-large')
        results = vdb.enriched_filtered_vector_search(embedding, 10, filters)[0]

        print("\n[results]:")
        formatted_history = format_chat_history(extract_chat_history_as_dict(chat_history))

        result_entries = []
        for point in results.points:
            print(point.payload['source_url'])

            db_id = point.payload.get('id')
            description = None
            if db_id is not None:
                offer = repository.get_offer_by_id_or_url(int(db_id))
                if offer is not None:
                    description = offer.description

            result_entries.append({
                "description": description,
                "similarity_score": point.score,
            })

        eval_records.append({
            "chat_history": formatted_history,
            "summary": response_summary,
            "processed_summary": processed_summary,
            "summary_to_embedd": summary_to_embedd,
            "key_attributes": key_attributes,
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
