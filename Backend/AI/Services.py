from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from Shared.LLM import LLM
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Analytics.AI.Prompts import summarize_chat_history_prompt_v_5, get_key_attributes_prompt
from Analytics.AI.utils import convert_text_to_dict, processing_dict, prepare_filters_qdrant, prepare_filters_elastic


async def generate_ai_answer(
        llm:ChatOpenAI,
        memory:list) -> str:

    prompt = ChatPromptTemplate.from_messages(memory)
    agentic_chain = LLMChain(llm=llm, prompt=prompt)
    response = await agentic_chain.apredict()

    return response


async def search_by_summarized_preferences(llm:LLM,
                        vector_db:Vector_DB_interface,
                        formatted_chat_history:str,
                        gen_model:str = "gpt-4o",
                        embedding_model:str = "text-embedding-3-large",
                        default_summary:str = 'pekne byvanie'
                        ):
    response_summary = llm.generate_answer(
        prompt=summarize_chat_history_prompt_v_5.format(
            conversation_history=formatted_chat_history,
            ), model=gen_model)
    try:
        key_attributes_summary = response_summary[:response_summary.index(', ostatné preferencie')]
    except:
        key_attributes_summary = None
    try:
        summary_to_embedd = response_summary[
                            response_summary.index(', ostatné preferencie') + len(', ostatné preferencie: '):]
    except:
        summary_to_embedd = default_summary

    default_key_attributes = {'price_rent': None,
                            'rooms': None,
                            'rooms_min': None,
                            'rooms_max': None,
                            'size': None,
                            'property_type': None,
                            'property_status': None,
                            'location': None}

    if key_attributes_summary:
        response_key_attr = llm.generate_answer(get_key_attributes_prompt.format(user_prompt=key_attributes_summary),
                                                model=gen_model)
        try:
            key_attributes_dict = convert_text_to_dict(response_key_attr)
            processed_key_attributes_dict = processing_dict(key_attributes_dict)
            if processed_key_attributes_dict['property_type'] in ['loft',
                                                                'penthouse',
                                                                'mezonet',
                                                                'garzónka',
                                                                'garzonka',
                                                                'garsónka',
                                                                'garsonka']:
                processed_key_attributes_dict['rooms'] = None
                processed_key_attributes_dict['rooms_min'] = None
                processed_key_attributes_dict['rooms_max'] = None
        except:
            processed_key_attributes_dict = default_key_attributes
    else:
        processed_key_attributes_dict = default_key_attributes

    filters = prepare_filters_qdrant(processed_key_attributes_dict) if isinstance(vector_db,Vector_DB_Qdrant) \
                else prepare_filters_elastic(processed_key_attributes_dict)
    embedding = llm.get_embedding(summary_to_embedd, model=embedding_model)
    results = vector_db.filtered_vector_search(embedding, 10, filter=filters)[0]
    processed_results = [{'source_url':i.payload['source_url'],'price':i.payload['price_total'],'location':i.payload['location']} for i in results.points]

    return processed_results






