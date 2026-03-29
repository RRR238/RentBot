from Analytics.AI.Prompts import get_key_attributes_system_prompt, summarize_preferences_system_prompt
from Analytics.AI.utils import (
    parse_json_from_markdown,
    prepare_enriched_filters_qdrant,
)
from Shared.LLM import LLM
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
        'cena': [None, None],
        'počet izieb': [None, None],
        'rozloha': [None, None],
        'typ nehnuteľnosti': [],
        'novostavba': False,
        'lokalita': [],
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
            # Ensure list fields are always lists (guard against unexpected LLM output)
            for key in ('cena', 'počet izieb', 'rozloha', 'typ nehnuteľnosti', 'lokalita'):
                if key not in key_attributes_dict or not isinstance(key_attributes_dict[key], list):
                    key_attributes_dict[key] = default_key_attributes[key]
            # Types without numbered rooms — clear the room filter
            roomless_types = {'loft', 'penthouse', 'mezonet', 'garzónka', 'garzonka', 'garsónka', 'garsonka'}
            selected_types = set(key_attributes_dict.get('typ nehnuteľnosti') or [])
            if selected_types and selected_types.issubset(roomless_types):
                key_attributes_dict['počet izieb'] = [None, None]
        except Exception:
            key_attributes_dict = default_key_attributes
    else:
        key_attributes_dict = default_key_attributes

    filters = prepare_enriched_filters_qdrant(key_attributes_dict)

    embedding = await llm.get_embedding_async(summary_to_embed,
                                              model=embedding_model)

    results = await vector_db.enriched_filtered_vector_search_async(embedding,
                                                                    50,
                                                                    filter_input=filters)

    return [
        {'score': i.score, 'id': i.payload['id']}
        for i in results[0].points
    ]
