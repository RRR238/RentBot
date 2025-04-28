from langchain.prompts import PromptTemplate
from Prompts import get_key_attributes_prompt, summarize_chat_history_prompt, follow_up_questions_prompt
from utils import convert_text_to_dict, processing_dict, prepare_filters
from Shared.Elasticsearch import Vector_DB
from Shared.LLM import LLM
from Shots import chat_history_summary_few_shots, extract_key_attributes_shots

llm = LLM()
vdb = Vector_DB('rent-bot-index')

chat_history_summarization_prompt = PromptTemplate(
    input_variables=["original_summary","user_prompt"],
    template=summarize_chat_history_prompt
)


org_summary = ""
while True:
    query = input()
    response = llm.generate_answer(summarize_chat_history_prompt.format(original_summary=org_summary,
                                                                        user_prompt=query),
                                                                        chat_history=chat_history_summary_few_shots)
    print(f"summary: {response}")
    org_summary = response
    response_key_attr = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=response),
                                                                    chat_history=extract_key_attributes_shots)
    key_attributes_dict = convert_text_to_dict(response_key_attr)
    print(key_attributes_dict)
    processed_dict = processing_dict(key_attributes_dict)
    #print(processed_dict)
    filters = prepare_filters(processed_dict)
    #print(filters)
    embedding = llm.get_embedding(query, model='text-embedding-3-large')
    results = vdb.filtered_vector_search(embedding, 15, filter=filters)
    for i in results:
        print(i['_source']['metadata']['source_url'], i['_score'])
    response_follow_up = llm.generate_answer(follow_up_questions_prompt.format(original_summary=org_summary,
                                                                               key_attributes = response_key_attr))
    print(f"🤖 \n{response_follow_up}")