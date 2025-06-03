from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from Prompts import get_key_attributes_prompt, agentic_flow_prompt,summarize_chat_history_prompt_v_3, summarize_chat_history_prompt_v_4
from utils import extract_chat_history_as_dict, format_chat_history, convert_text_to_dict, processing_dict,prepare_filters_qdrant
from Shared.LLM import LLM
from Shots import chat_history_summary_few_shots
import warnings
from langchain.schema import SystemMessage
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from langchain.schema import AIMessage
import json

warnings.filterwarnings("ignore",
                        category=DeprecationWarning)
warnings.filterwarnings("ignore",
                        category=UserWarning)

gen_model = "gpt-4o"


llm_langchain = ChatOpenAI(
    temperature=0.2,
    model_name=gen_model,
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
                  "budem pokračovať v hľadaní",
                  "budem hľadať"
                  ]


with open('chat_memory.json', 'r', encoding='utf-8') as f:
    convos = json.load(f)

questions = 0
#convos = []
convo = []
prev_key_attributes_dict = {'price_rent': None,
                            'rooms': None,
                            'rooms_min': None,
                            'rooms_max': None,
                            'size': None,
                            'property_type': None,
                            'property_status': None,
                            'location': None}
while True:
    parts = {}
    query = input()

    # if query == 'q':
    #     convos.append(convo)
    #     convo = []
    #
    # if query == 'wq':
    #     with open("chat_memory.json", "w", encoding="utf-8") as f:
    #         convos.append(convo)
    #         json.dump(convos, f, ensure_ascii=False, indent=2)
    #         sys.exit()
    #
    # parts['query'] = query
    chhd = extract_chat_history_as_dict(memory)
    formatted_chat_history = format_chat_history(chhd)
    formatted_chat_history += f"Používateľ: {query}\n"
    #print(formatted_chat_history)


    response_summary = llm.generate_answer(prompt=summarize_chat_history_prompt_v_4.format(conversation_history=formatted_chat_history,
                                                                                original_summary=org_summary,
                                                                                #user_prompt=query),
                                                                                ), model=gen_model)

    print(f"summary: {response_summary}")
    try:
        processed_summary = response_summary[:response_summary.index(', ostatné preferencie')]
        summary_to_embedd = llm.generate_answer(prompt=response_summary[response_summary.index(', ostatné preferencie')+len(', ostatné preferencie: '):],
                                                chat_history=chat_history_summary_few_shots, model=gen_model)
        org_summary = response_summary
    except:
        processed_summary = org_summary[:response_summary.index(', ostatné preferencie')]
        summary_to_embedd = llm.generate_answer(prompt=response_summary[response_summary.index(', ostatné preferencie') + len(', ostatné preferencie: '):],
                                                chat_history=chat_history_summary_few_shots, model=gen_model)

    print(f"processed summary: {processed_summary}")
    print(f"sumary to embedd: {summary_to_embedd}")

    try:
        response_key_attr = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=response_summary),
                                                model=gen_model)
                                               # chat_history=extract_key_attributes_shots)
        key_attributes_dict = convert_text_to_dict(response_key_attr)
        processed_dict = processing_dict(key_attributes_dict)
        prev_key_attributes_dict = processed_dict
    except:
        processed_dict = prev_key_attributes_dict

    if processed_dict['property_type'] in ['house','loft','mezonet','garzónka']:
        processed_dict['rooms'] = None
        processed_dict['rooms_min'] = None
        processed_dict['rooms_max'] = None

    print(processed_dict)
    #filters = prepare_filters_qdrant(processed_dict)
    #
    # parts['response_summary'] = response_summary
    # parts['processed_summary'] = processed_summary
    # parts['summary_to_embedd'] = summary_to_embedd
    # parts['results'] = []
    #
    # embedding = llm.get_embedding(summary_to_embedd, model='text-embedding-3-large') #processed_summary
    # results = vdb.filtered_vector_search(embedding, 15, filter=filters)[0]
    # for i in results.points:
    #     #parts['results'].append(i.payload['source_url'])
    #     print(i.payload['source_url'])
    # #
    response = agentic_chain.predict(input=query)
    questions+=1
    #parts['response'] = response

    # if any(phrase in response.lower() for phrase in skip_phrases) and len(memory.chat_memory.messages)<=5:
    #     print("skipping to next question")
    #     query = "pýtaj sa ďalej"
    #     response = agentic_chain.predict(input=query)
    #     print(f"🤖: {response}")
    #     continue

    if questions >= 10:
        print(f"🤖: Ďakujem za vaše odpovede. Ak budete chcieť doplniť ďalšie kritériá, neváhajte mi napísať.")
        memory.chat_memory.messages[-1] = AIMessage(
            content="Ďakujem za vaše odpovede. Ak budete chcieť doplniť ďalšie kritériá, neváhajte mi napísať."
        )
        questions=0
        #parts['response'] = response
        continue

    print(f"🤖: {response}")
    #convo.append(parts)
    #print(f"chat history length: {len(memory.chat_memory.messages)}")