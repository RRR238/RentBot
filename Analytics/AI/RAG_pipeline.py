from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from Prompts import get_key_attributes_prompt, summarize_chat_history_prompt, check_conversation_prompt
from utils import convert_text_to_dict, processing_dict, prepare_filters,few_shots_chat_history
from Shared.Elasticsearch import Vector_DB
from Shared.LLM import LLM
from Shots import chat_history_summary_few_shots, prompt_classification_few_shots
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
# 1. SETUP MODEL
llm_langchain = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",  # or "gpt-4-turbo", "gpt-3.5-turbo", etc.
    #openai_api_key=,  # optional if set as ENV variable
)
llm = LLM()
vdb = Vector_DB('rent-bot-index')

# 2. SHARED MEMORY
# memory = ConversationBufferMemory(
#     memory_key="chat_history",
#     return_messages=True
# )
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=0,
    return_messages=True
)

# few_shots = few_shots_chat_history(chat_history_summary_few_shots,
#                                    summarize_chat_history_prompt)
# # # Manually add to memory before launching the chain
# for shot in few_shots:
#     memory.chat_memory.add_user_message(shot['User'])
#     memory.chat_memory.add_ai_message(shot['AI'])


chat_history_summarization_prompt = PromptTemplate(
    input_variables=["original_summary","user_prompt"],
    template=summarize_chat_history_prompt
)

# 3. KEY ATTRIBUTE EXTRACTION PROMPT
# extract_prompt = PromptTemplate(
#     input_variables=["chat_history","user_prompt"],
#     template=get_key_attributes_prompt
# )

# 4. FOLLOW-UP PROMPT
# follow_up_prompt = PromptTemplate.from_template(
#     follow_up_question_prompt
# )

# 5. CHAINS

chat_history_chain = LLMChain(
    llm=llm_langchain,
    prompt=chat_history_summarization_prompt,
    memory=memory
)

# extract_chain = LLMChain(
#     llm=llm_langchain,
#     prompt=extract_prompt,
#     memory=memory
# )

# follow_up_chain = LLMChain(
#     llm=llm_langchain,
#     prompt=follow_up_prompt,
#     memory=memory
# )

base_dict = {'price_rent': None, 'rooms': None, 'rooms_min': None, 'rooms_max': None, 'size': None, 'property_type': None, 'property_status': None}
org_summary = ""
while True:
    query = input()
    response_check = llm.generate_answer(check_conversation_prompt.format(original_summary=org_summary,
                                                                          user_prompt=query))
    # key_attributes_dict = convert_text_to_dict(response_check)
    # processed_dict = processing_dict(key_attributes_dict)

    print(f"type: {response_check}")
    #if response_check.strip() == 'NOVÝ DOPYT':
        #memory.clear()

    # response = chat_history_chain.predict(original_summary=org_summary,
    #                                       user_prompt=query)
    response = llm.generate_answer(summarize_chat_history_prompt.format(original_summary=org_summary,
                                                                        user_prompt=query))
    print(f"summary: {response}")
    org_summary = response
    # key_attributes_dict = convert_text_to_dict(response)
    # print(key_attributes_dict)
    # processed_dict = processing_dict(key_attributes_dict)
    # print(processed_dict)
    # filters = prepare_filters(processed_dict)
    # print(filters)
    # embedding = llm.get_embedding(query, model='text-embedding-3-large')
    # results = vdb.filtered_vector_search(embedding, 15, filter=filters)
    # for i in results:
    #     print(i['_source']['metadata']['source_url'], i['_score'])
    #follow_up = follow_up_chain.run()
    #print("🤖 Follow-up question:", follow_up)