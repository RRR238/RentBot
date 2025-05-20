from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from Prompts import get_key_attributes_prompt, agentic_flow_prompt,summarize_chat_history_prompt
from utils import chat_history_summary_post_processing, extract_chat_history_as_dict, format_chat_history, convert_text_to_dict, processing_dict,prepare_filters_qdrant, strip_standardized_data
from Shared.LLM import LLM
from Shots import chat_history_summary_few_shots, extract_key_attributes_shots
import warnings
from langchain.schema import SystemMessage
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from langchain.schema import HumanMessage, AIMessage
import json
import sys

warnings.filterwarnings("ignore",
                        category=DeprecationWarning)
warnings.filterwarnings("ignore",
                        category=UserWarning)


llm_langchain = ChatOpenAI(
    temperature=0.2,
    model_name="gpt-3.5-turbo",
    #openai_api_key=
)
llm = LLM()
vdb = Vector_DB_Qdrant('rent-bot-index')

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
system_instruction = SystemMessage(
    content=agentic_flow_prompt
)

memory.chat_memory.messages.append(system_instruction)

agentic_prompt = ChatPromptTemplate.from_messages([
    system_instruction,
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

agentic_chain = LLMChain(
    llm=llm_langchain,
    prompt=agentic_prompt,
    memory=memory
)

org_summary = ""
skip_phrases = [
        "máte nejaké ďalšie požiadavky alebo preferencie",
        "máte ešte nejaké ďalšie požiadavky alebo preferencie",
        "máte ešte nejaké ďalšie požiadavky alebo detaily",
        "máte nejaké ďalšie požiadavky alebo detaily",
        "dokážete uviesť nejaké ďalšie požiadavky",
        "dokážete uviesť ďalšie požiadavky",
        "aké ďalšie kritériá",
        "aké ďalšie požiadavky alebo preferencie máte"
    ]

finish_phrases = ["na základe vašich preferencií hľadám pre vás",
                  "na základe vašich preferencií hľadám",
                  "budem pokračovať v hľadaní"
                  ]

with open('chat_memory.json', 'r', encoding='utf-8') as f:
    convos = json.load(f)

questions = 0
#convos = []
convo = []
while True:
    parts = {}
    query = input()

    if query == 'q':
        convos.append(convo)
        convo = []

    if query == 'wq':
        with open("chat_memory.json", "w", encoding="utf-8") as f:
            convos.append(convo)
            json.dump(convos, f, ensure_ascii=False, indent=2)
            sys.exit()

    parts['query'] = query
    chhd = extract_chat_history_as_dict(memory)
    formatted_chat_history = format_chat_history(chhd)
    #print(formatted_chat_history)
    # response_query_classification = llm.generate_answer(check_conversation_prompt.format(user_prompt=query,
    #                                                                                      chat_history=formatted_chat_history))
    # print(response_query_classification)

    response_summary = llm.generate_answer(summarize_chat_history_prompt.format(conversation_history=formatted_chat_history,
                                                                                original_summary=org_summary,
                                                                                user_prompt=query))
                                                                                #chat_history=chat_history_summary_few_shots)

    processed_summary = chat_history_summary_post_processing(response_summary)
    summary_to_embedd = strip_standardized_data(processed_summary)
    org_summary = response_summary #processed_summary
    # chat_history_summary_few_shots.append({"role": "user", "content": query})
    # chat_history_summary_few_shots.append({"role": "assistant", "content": response_summary})
    #print(f"🤖: {response}")
    print(f"summary: {response_summary}")
    print(f"processed summary: {processed_summary}")
    print(f"sumary to embedd: {summary_to_embedd}")
    response_key_attr = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=response_summary),
                                            chat_history=extract_key_attributes_shots)
    key_attributes_dict = convert_text_to_dict(response_key_attr)
    processed_dict = processing_dict(key_attributes_dict)
    print(processed_dict)
    filters = prepare_filters_qdrant(processed_dict)

    parts['response_summary'] = response_summary
    parts['processed_summary'] = processed_summary
    parts['summary_to_embedd'] = summary_to_embedd
    parts['results'] = []

    embedding = llm.get_embedding(summary_to_embedd, model='text-embedding-3-large') #processed_summary
    results = vdb.filtered_vector_search(embedding, 15, filter=filters)[0]
    for i in results.points:
        parts['results'].append(i.payload['source_url'])
        print(i.payload['source_url'])

    response = agentic_chain.predict(input=query)
    parts['response'] = response

    # if any(phrase in response.lower() for phrase in skip_phrases):
    #     print("skipping to next question")
    #     query = "pýtaj sa ďalej"
    #     response = agentic_chain.predict(input=query)
        # print(f"🤖: {response}")
        # continue
    if any(phrase in response.lower() for phrase in finish_phrases):
        print(f"🤖: Ďakujem za vaše odpovede. Ak budete chcieť doplniť ďalšie kritériá, neváhajte mi napísať.")
        parts['response'] = response
        continue

    print(f"🤖: {response}")
    convo.append(parts)
    #print(f"chat history length: {len(memory.chat_memory.messages)}")