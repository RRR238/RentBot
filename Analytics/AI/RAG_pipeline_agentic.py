import warnings

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

from Prompts import (
    agentic_flow_prompt,
    get_key_attributes_system_prompt,
    summarize_preferences_system_prompt,
)
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from utils import create_chain, parse_json_from_markdown, prepare_multiple_filters_qdrant

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

gen_model = "gpt-4o"

# ---------------------------------------------------------------------------
# Models / services
# ---------------------------------------------------------------------------

llm_langchain = ChatOpenAI(
    temperature=0.2,
    model_name=gen_model,
)
llm = LLM()
vdb = Vector_DB_Qdrant('rent-bot-index')

# ---------------------------------------------------------------------------
# Chains
# ---------------------------------------------------------------------------

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
)

# Agentic chain — conversational, driven by memory; invoke via .predict(input=query)
agentic_chain = create_chain(
    llm_langchain, agentic_flow_prompt,
    messages_placeholder="chat_history",
    human_template="{input}",
    memory=memory,
)

# Summarization chain — invoked with {"messages": [HumanMessage, AIMessage, ...]}
summarization_chain = create_chain(
    llm_langchain, summarize_preferences_system_prompt,
    messages_placeholder="messages",
)

# Key-attributes chain — invoked with {"input": "<summary text>"}
key_attributes_chain = create_chain(
    llm_langchain, get_key_attributes_system_prompt,
    human_template="{input}",
)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

org_summary = (
    "cena: None, počet izieb: None, rozloha: None, typ nehnuteľnosti: None, "
    "novostavba: None, lokalita: None, ostatné preferencie: None"
)

while True:
    query = input()

    # Build message list for summarization: full history + current user message
    messages_for_summary = memory.chat_memory.messages + [HumanMessage(content=query)]

    # --- Step 1: summarize user preferences from the conversation ---
    summary_response = summarization_chain.invoke({"messages": messages_for_summary})
    response_summary = summary_response.content
    print(f"summary: {response_summary}")

    try:
        idx = response_summary.index(', ostatné preferencie')
        processed_summary = response_summary[:idx]
        summary_to_embedd = response_summary[idx + len(', ostatné preferencie: '):]
        org_summary = response_summary
    except ValueError:
        idx = org_summary.index(', ostatné preferencie')
        processed_summary = org_summary[:idx]
        summary_to_embedd = org_summary[idx + len(', ostatné preferencie: '):]

    print(f"processed summary: {processed_summary}")
    print(f"summary to embedd: {summary_to_embedd}")

    # --- Step 2: extract structured key attributes from the summary ---
    key_attr_response = key_attributes_chain.invoke({"input": response_summary})
    response_key_attr = key_attr_response.content
    print(response_key_attr)

    p = parse_json_from_markdown(response_key_attr)
    print(p)

    # --- Step 3: vector search with extracted filters ---
    filters = prepare_multiple_filters_qdrant(p)
    embedding = llm.get_embedding('pekne byvanie', model='text-embedding-3-large')
    results = vdb.enriched_filtered_vector_search(embedding, 10, filters)[0]
    for i in results.points:
        print(i.payload['source_url'])