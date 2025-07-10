from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from Shared.LLM import LLM
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Analytics.AI.Prompts import summarize_chat_history_prompt_v_5, get_key_attributes_prompt
from Analytics.AI.utils import convert_text_to_dict, processing_dict, prepare_filters_qdrant, prepare_filters_elastic
from Backend.AI.Utils import prepare_chat_history_for_summarization


async def generate_ai_answer(
        llm:ChatOpenAI,
        memory:list) -> str:

    prompt = ChatPromptTemplate.from_messages(memory)
    agentic_chain = LLMChain(llm=llm, prompt=prompt)
    response = await agentic_chain.apredict()

    return response


async def search_by_summarized_preferences(
    llm: LLM,
    vector_db: Vector_DB_interface,
    memory: list,
    gen_model: str = "gpt-4o",
    embedding_model: str = "text-embedding-3-large",
    default_summary: str = "pekne byvanie"
):

    processed_memory = prepare_chat_history_for_summarization(memory[:-1])
    response_summary = await llm.generate_answer_async(
        prompt=summarize_chat_history_prompt_v_5.format(
            conversation_history=processed_memory,
        ),
        model=gen_model
    )

    try:
        key_attributes_summary = response_summary[:response_summary.index(', ostatné preferencie')]
    except:
        key_attributes_summary = None

    try:
        summary_to_embed = response_summary[
            response_summary.index(', ostatné preferencie') + len(', ostatné preferencie: ')
        ]
    except:
        summary_to_embed = default_summary

    default_key_attributes = {
        'price_rent': None,
        'rooms': None,
        'rooms_min': None,
        'rooms_max': None,
        'size': None,
        'property_type': None,
        'property_status': None,
        'location': None
    }

    if key_attributes_summary:
        response_key_attr = await llm.generate_answer_async(
            get_key_attributes_prompt.format(user_prompt=key_attributes_summary),
            model=gen_model
        )
        try:
            key_attributes_dict = convert_text_to_dict(response_key_attr)
            processed_key_attributes_dict = processing_dict(key_attributes_dict)

            if processed_key_attributes_dict['property_type'] in [
                'loft', 'penthouse', 'mezonet',
                'garzónka', 'garzonka', 'garsónka', 'garsonka'
            ]:
                processed_key_attributes_dict['rooms'] = None
                processed_key_attributes_dict['rooms_min'] = None
                processed_key_attributes_dict['rooms_max'] = None

        except:
            processed_key_attributes_dict = default_key_attributes
    else:
        processed_key_attributes_dict = default_key_attributes

    filters = (
        prepare_filters_qdrant(processed_key_attributes_dict)
        if isinstance(vector_db, Vector_DB_Qdrant)
        else prepare_filters_elastic(processed_key_attributes_dict)
    )

    embedding = await llm.get_embedding_async(summary_to_embed, model=embedding_model)

    results = await vector_db.filtered_vector_search_async(
        embedding, 50, filter=filters
    )
    print(f'results from VDB: {results}')

    processed_results = [
        {   'score':i.score,
            'source_url': i.payload['source_url'],
            'price_total': i.payload['price_total'],
            'location': "Niekde na Slovensku", #i.payload['location']
            'size': i.payload['size'],
            'property_type': i.payload['property_type'],
            'rooms':i.payload['rooms']
        }
        for i in results[0].points
    ]

    return processed_results







