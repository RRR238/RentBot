import warnings

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from .Prompts import (
    agentic_flow_prompt,
    get_key_attributes_structured_prompt,
    summarize_preferences_system_prompt,
)
from .Schemas import KeyAttributes
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from .utils import create_chain, prepare_enriched_filters_from_key_attributes

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

# ---------------------------------------------------------------------------
# Chains
# ---------------------------------------------------------------------------

# Agentic chain — pass chat_history manually on each invoke
agentic_chain = create_chain(
    llm_langchain, agentic_flow_prompt,
    messages_placeholder="chat_history",
    human_template="{input}",
)

# Summarization chain — conversation history + explicit instruction as final human message
summarization_chain = create_chain(
    llm_langchain_deterministic, summarize_preferences_system_prompt,
    messages_placeholder="messages",
    human_template="Zhrň preferencie používateľa z vyššie uvedenej konverzácie podľa inštrukcií v systémovej správe.",
)

# Key-attributes chain — returns a KeyAttributes Pydantic object directly
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

# Conversation history — list of HumanMessage / AIMessage
chat_history = []

# Kick off the conversation
opening = agentic_chain.invoke({"chat_history": chat_history, "input": "Začni konverzáciu."})
print(f"🤖: {opening.content}")
chat_history.append(HumanMessage(content="Začni konverzáciu."))
chat_history.append(AIMessage(content=opening.content))

while True:
    query = input("You: ").strip()

    if query == SEARCH_TRIGGER:
        # --- Step 1: summarize preferences from the full conversation so far ---
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

        # --- Step 2: extract structured key attributes from the summary ---
        key_attributes: KeyAttributes = key_attributes_chain.invoke({"input": processed_summary})
        print(f"[key attributes]: {key_attributes}")

        # --- Step 3: vector search with extracted filters ---
        filters = prepare_enriched_filters_from_key_attributes(key_attributes)
        embedding = llm.get_embedding(summary_to_embedd, model='text-embedding-3-large')
        results = vdb.enriched_filtered_vector_search(embedding, 10, filters)[0]
        print("\n[results]:")
        for i in results.points:
            print(i.payload['source_url'])

    else:
        # Normal conversation turn — agent asks the next question
        response = agentic_chain.invoke({"chat_history": chat_history, "input": query})
        print(f"🤖: {response.content}")
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=response.content))