import json
import warnings
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .Prompts import (
    agentic_flow_prompt_v2 as agentic_flow_prompt,
    extract_preferences_from_conversation_prompt,
    generate_synthetic_listing_prompt,
)
from .Schemas import KeyAttributes
from .utils import (
    create_chain,
    normalize_key_attributes,
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

# ---------------------------------------------------------------------------
# Models / services
# ---------------------------------------------------------------------------

llm_langchain = ChatOpenAI(temperature=0.9, model="gpt-4.1")
llm_langchain_deterministic = ChatOpenAI(model="gpt-4o")
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
    MessagesPlaceholder(variable_name="messages"),
    ("human", "Extrahuj preferencie používateľa z vyššie uvedenej konverzácie."),
])
extract_chain = _extract_prompt | llm_langchain_deterministic.with_structured_output(KeyAttributes)

synthetic_listing_chain = create_chain(
    llm_langchain_deterministic, generate_synthetic_listing_prompt,
    human_template="{key_attributes}",
)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

SEARCH_TRIGGER = "P"
SAVE_TRIGGER = "S"

chat_history: list = []
eval_records: list = []

opening = agentic_chain.invoke({"chat_history": chat_history, "input": "Začni konverzáciu."})
print(f"🤖: {opening.content}")
chat_history.append(HumanMessage(content="Začni konverzáciu."))
chat_history.append(AIMessage(content=opening.content))

while True:
    query = input("You: ").strip()

    if query == SEARCH_TRIGGER:
        # --- Step 1: extract structured preferences directly from conversation ---
        key_attributes: KeyAttributes = extract_chain.invoke({"messages": chat_history})
        key_attributes = normalize_key_attributes(key_attributes)
        print(f"\n[key attributes]: {key_attributes}")

        # --- Step 2: generate synthetic listing for embedding (HyDE) ---
        synthetic_listing = synthetic_listing_chain.invoke(
            {"key_attributes": key_attributes.ostatne_preferencie or ""}
        ).content
        print(f"[synthetic listing]: {synthetic_listing}")

        # --- Step 3: vector search ---
        filters = prepare_enriched_filters_from_key_attributes(key_attributes)
        embedding = llm.get_embedding(synthetic_listing, model='text-embedding-3-large')
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
            "key_attributes": key_attributes,
            "synthetic_listing": synthetic_listing,
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
