from Analytics.AI.Prompts import get_key_attributes_system_prompt, summarize_preferences_system_prompt
from Analytics.AI.utils import (
    parse_json_from_markdown,
    prepare_filters_elastic,
    prepare_filters_qdrant,
    processing_dict,
)
from Shared.LLM import LLM
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.Vector_database.Vector_DB_interface import Vector_DB_interface


async def search_by_summarized_preferences(
    llm: LLM,
    vector_db: Vector_DB_interface,
    memory: list[dict],
    model: str = "gpt-4o",
    embedding_model: str = "text-embedding-3-large",
    default_summary: str = "pekne byvanie",
):
    # Step 1: summarize conversation into structured preferences
    response_summary = await llm.generate_answer_async(
        model=model,
        system_prompt=summarize_preferences_system_prompt,
        chat_history=memory,
    )

    try:
        key_attributes_summary = response_summary[:response_summary.index(', ostatné preferencie')]
    except ValueError:
        key_attributes_summary = None

    try:
        summary_to_embed = response_summary[
            response_summary.index(', ostatné preferencie') + len(', ostatné preferencie: '):
        ]
    except ValueError:
        summary_to_embed = default_summary

    default_key_attributes = {
        'price_rent': None,
        'rooms': None,
        'rooms_min': None,
        'rooms_max': None,
        'size': None,
        'property_type': None,
        'property_status': None,
        'location': None,
    }

    if key_attributes_summary:
        # Step 2: extract structured key attributes from the summary
        key_attr_response = await llm.generate_answer_async(
            prompt=key_attributes_summary,
            model=model,
            system_prompt=get_key_attributes_system_prompt,
        )
        try:
            key_attributes_dict = parse_json_from_markdown(key_attr_response)
            processed_key_attributes_dict = processing_dict(key_attributes_dict)

            if processed_key_attributes_dict['property_type'] in [
                'loft', 'penthouse', 'mezonet',
                'garzónka', 'garzonka', 'garsónka', 'garsonka',
            ]:
                processed_key_attributes_dict['rooms'] = None
                processed_key_attributes_dict['rooms_min'] = None
                processed_key_attributes_dict['rooms_max'] = None
        except Exception:
            processed_key_attributes_dict = default_key_attributes
    else:
        processed_key_attributes_dict = default_key_attributes

    filters = (
        prepare_filters_qdrant(processed_key_attributes_dict)
        if isinstance(vector_db, Vector_DB_Qdrant)
        else prepare_filters_elastic(processed_key_attributes_dict)
    )

    embedding = await llm.get_embedding_async(summary_to_embed,
                                              model=embedding_model)

    results = await vector_db.filtered_vector_search_async(embedding,
                                                           50,
                                                           filter=filters)

    return [
        {'score': i.score, 'id': i.payload['id']}
        for i in results[0].points
    ]
