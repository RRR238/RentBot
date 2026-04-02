import json
import math
import re
from typing import Optional, Union

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from Shared.Geolocation import get_bounding_box_from_location
from qdrant_client.http.models import Filter, FieldCondition, Match, Range, MatchValue


def create_chain(
    llm,
    system_prompt: str,
    *,
    messages_placeholder: Optional[str] = None,
    human_template: Optional[str] = None,
):
    message_templates = [("system", system_prompt)]

    if messages_placeholder is not None:
        message_templates.append(MessagesPlaceholder(variable_name=messages_placeholder))

    if human_template is not None:
        message_templates.append(("human", human_template))

    prompt = ChatPromptTemplate.from_messages(message_templates)

    return prompt | llm

property_type_mappings = {"dom":"house",
                              "loft":"loft",
                              "mezonet":"mezonet",
                              "byt":"flat",
                              "garzónka":"studio",
                              "garzonka": "studio",
                              "garsónka": "studio",
                              "garsonka": "studio",
                              "penthouse":"penthouse"}

def convert_text_to_dict(llm_output):
    final_dict = {}
    no_spaces = llm_output.strip().replace('/n','').replace(' \n','').replace(' ','')
    final_dict['price_rent'] = no_spaces[no_spaces.find('cena')+len('cena'):no_spaces.find('početizieb')].replace(',','').replace('\n','').replace(':','')
    final_dict['rooms'] = no_spaces[no_spaces.find('početizieb') + len('početizieb'):no_spaces.find('početiziebMIN')].replace(',','').replace('\n', '').replace(':', '')
    final_dict['rooms_min'] = no_spaces[no_spaces.find('početiziebMIN') + len('početiziebMIN'):no_spaces.find('početiziebMAX')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['rooms_max'] = no_spaces[no_spaces.find('početiziebMAX') + len('početiziebMAX'):no_spaces.find('rozloha')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['size'] = no_spaces[no_spaces.find('rozloha') + len('rozloha'):no_spaces.find('typnehnuteľnosti')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['property_type'] = no_spaces[no_spaces.find('typnehnuteľnosti') + len('typnehnuteľnosti'):no_spaces.find('novostavba')].replace(',','').replace('\n', '').replace(':', '').replace('.','')
    final_dict['property_status'] = no_spaces[no_spaces.find('novostavba') + len('novostavba'):no_spaces.find('lokalita')].replace(',','').replace('\n', '').replace(':', '').replace('.', '')
    final_dict['location'] = no_spaces[no_spaces.find('lokalita') + len('lokalita'):].replace(',', '').replace('\n', '').replace(':', '').replace('.', '')
    return final_dict


def parse_json_from_markdown(raw: str) -> dict:
    # Remove code block markers if present
    cleaned = raw.strip().strip('` \n')
    if cleaned.lower().startswith('json'):
        cleaned = cleaned[4:].lstrip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")


def processing_dict(key_attributes_dict):
    global property_type_mappings
    for k,v in key_attributes_dict.items():
        if v == 'None':
            key_attributes_dict[k] = None
        elif k == 'property_type':
            key_attributes_dict[k] = property_type_mappings[v]
        elif k == 'property_status':
            key_attributes_dict[k] = 'novostavba'
        elif k == 'location':
            key_attributes_dict[k] = v
        else:
            try:
                key_attributes_dict[k] = int(v)
            except:
                key_attributes_dict[k] = None

    return key_attributes_dict


# def processing_dict_multiple_filters(key_attributes_dict):
#     updated_key_attributes = {}
#     for k, v in key_attributes_dict.items():
#         if k=


def prepare_filters_elastic(processed_dict):
    filter = []
    for k,v in processed_dict.items():
        if k=='price_rent' and v is not None:
            filter.append({"range": {"metadata.price_rent": {"lte": v}}})
        if k=='size' and v is not None:
            filter.append({"range": {"metadata.size": {"gte": v}}})
        if k=='rooms' and v is not None:
            filter.append({"term": {"metadata.rooms": v}})
        if k=='rooms_min' and v is not None:
            filter.append({"range": {"metadata.rooms": {"gte": v}}})
        if k=='rooms_max' and v is not None:
            filter.append({"range": {"metadata.rooms": {"lte": v}}})
        if k=='property_type' and v is not None:
            filter.append({"term": {"metadata.property_type.keyword": v}})
        if k=='property_status' and v is not None:
            filter.append({"term": {"metadata.property_status.keyword": v}})

    return filter

def prepare_filters_qdrant(processed_dict):
    filter = []
    for k,v in processed_dict.items():
        if k=='price_rent' and v is not None:
            filter.append({'type':"lte", 'key':"price_total",'value':v})
        if k=='size' and v is not None:
            filter.append({'type': "gte", 'key': "size", 'value': v})
        if k=='rooms' and v is not None:
            filter.append({'type': "term", 'key': "rooms", 'value': v})
        if k=='rooms_min' and v is not None:
            filter.append({'type': "gte", 'key': "rooms", 'value': v})
        if k=='rooms_max' and v is not None:
            filter.append({'type': "lte", 'key': "rooms", 'value': v})
        if k=='property_type' and v is not None:
            filter.append({'type': "term", 'key': "property_type", 'value': v})
        if k=='property_status' and v is not None:
            filter.append({'type': "term", 'key': "property_status", 'value': v})

    if processed_dict['location'] is None:
        bbox = get_bounding_box_from_location('Slovakia')
    else:
        bbox = get_bounding_box_from_location(processed_dict['location'])

    if bbox is None:
        bbox = get_bounding_box_from_location('Slovakia')

    filter.append({'type': "gte", 'key': "latitude", 'value': bbox['south_lat']})
    filter.append({'type': "lte", 'key': "latitude", 'value': bbox['north_lat']})
    filter.append({'type': "gte", 'key': "longtitude", 'value': bbox['west_lon']})
    filter.append({'type': "lte", 'key': "longtitude", 'value': bbox['east_lon']})

    return filter

#{'cena': [800, 1000], 'počet izieb': [2, 3], 'rozloha': [50, 60], 'typ nehnuteľnosti': None, 'novostavba': False, 'lokalita': ['Bratislava', 'Senec']}
def prepare_enriched_filters_qdrant(processed_dict):
    must_conditions = []
    global property_type_mappings

    for k, v in processed_dict.items():
        if k == 'cena':
            if v[0] is not None:
                must_conditions.append(
                    FieldCondition(key="price_total", range=Range(gte=v[0]))
                )
            if v[1] is not None:
                must_conditions.append(
                    FieldCondition(key="price_total", range=Range(lte=v[1]))
                )

        if k == 'počet izieb':
            if v[0] is not None:
                must_conditions.append(
                    FieldCondition(key="rooms", range=Range(gte=v[0]))
                )
            if v[1] is not None:
                must_conditions.append(
                    FieldCondition(key="rooms", range=Range(lte=v[1]))
                )

        if k == 'rozloha':
            if v[0] is not None:
                must_conditions.append(
                    FieldCondition(key="size", range=Range(gte=v[0]))
                )
            if v[1] is not None:
                must_conditions.append(
                    FieldCondition(key="size", range=Range(lte=v[1]))
                )

        if k == 'typ nehnuteľnosti':
            if v:
                mapped = [
                    property_type_mappings[prop_type]
                    for prop_type in v
                    if prop_type in property_type_mappings
                ]
                if mapped:
                    must_conditions.append(
                        Filter(
                            should=[
                                FieldCondition(
                                    key="property_type",
                                    match=MatchValue(value=mapped_type)
                                )
                                for mapped_type in mapped
                            ]
                        )
                    )

        if k == 'novostavba':
            if v is True:
                must_conditions.append(
                    FieldCondition(
                        key="property_status",
                        match=MatchValue(value="novostavba")
                    )
                )

    # --- LOCATION (multiple bounding boxes) ---
    should_conditions = []

    locations = processed_dict.get('lokalita') or ['Slovakia']
    if len(locations)==0:
        locations.append('Slovakia')

    for loc in locations:
        bbox = get_bounding_box_from_location(loc)
        if bbox is None:
            continue

        should_conditions.append(
            Filter(
                must=[
                    FieldCondition(
                        key="latitude",
                        range=Range(gte=bbox["south_lat"], lte=bbox["north_lat"])
                    ),
                    FieldCondition(
                        key="longtitude",
                        range=Range(gte=bbox["west_lon"], lte=bbox["east_lon"])
                    )
                ]
            )
        )

    # Final filter with must + should
    return Filter(
        must=must_conditions,
        should=should_conditions
    )

def prepare_enriched_filters_from_key_attributes(key_attributes) -> Filter:
    """Build a Qdrant Filter from a KeyAttributes Pydantic object."""
    must_conditions = []
    roomless_mapped = {'loft', 'penthouse', 'mezonet', 'studio'}

    # Price
    if key_attributes.cena.min is not None:
        must_conditions.append(FieldCondition(key="price_total", range=Range(gte=key_attributes.cena.min)))
    if key_attributes.cena.max is not None:
        must_conditions.append(FieldCondition(key="price_total", range=Range(lte=key_attributes.cena.max)))

    # Property type — needed before rooms to check roomless
    mapped_types = [
        property_type_mappings[t]
        for t in key_attributes.typ_nehnutelnosti
        if t in property_type_mappings
    ]
    if mapped_types:
        must_conditions.append(
            Filter(should=[
                FieldCondition(key="property_type", match=MatchValue(value=t))
                for t in mapped_types
            ])
        )

    # Rooms (skip if all selected types are roomless)
    is_all_roomless = bool(mapped_types) and set(mapped_types).issubset(roomless_mapped)
    if not is_all_roomless:
        if key_attributes.pocet_izieb.min is not None:
            must_conditions.append(FieldCondition(key="rooms", range=Range(gte=key_attributes.pocet_izieb.min)))
        if key_attributes.pocet_izieb.max is not None:
            must_conditions.append(FieldCondition(key="rooms", range=Range(lte=key_attributes.pocet_izieb.max)))

    # Size
    if key_attributes.rozloha.min is not None:
        must_conditions.append(FieldCondition(key="size", range=Range(gte=key_attributes.rozloha.min)))
    if key_attributes.rozloha.max is not None:
        must_conditions.append(FieldCondition(key="size", range=Range(lte=key_attributes.rozloha.max)))

    # New build
    if key_attributes.novostavba:
        must_conditions.append(FieldCondition(key="property_status", match=MatchValue(value="novostavba")))

    # Location — multiple bounding boxes in should (OR logic)
    should_conditions = []
    locations = key_attributes.lokalita or ['Slovakia']
    for loc in locations:
        bbox = get_bounding_box_from_location(loc)
        if bbox is None:
            continue
        should_conditions.append(Filter(must=[
            FieldCondition(key="latitude", range=Range(gte=bbox["south_lat"], lte=bbox["north_lat"])),
            FieldCondition(key="longtitude", range=Range(gte=bbox["west_lon"], lte=bbox["east_lon"])),
        ]))

    return Filter(must=must_conditions, should=should_conditions)


def extract_chat_history_as_dict(memory):
    chat_history = []
    if isinstance(memory,list):
        for message in memory:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            chat_history.append({"role": role, "content": message.content})
    else:
        for message in memory.chat_memory.messages:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            chat_history.append({"role": role, "content": message.content})
    return chat_history

def format_chat_history(chat_history):
    formatted_history = ""
    for message in chat_history:
        if message["role"] == "user":
            formatted_history += f"Používateľ: {message['content']}\n"
        elif message["role"] == "assistant":
            formatted_history += f"Asistent: {message['content']}\n"
    return formatted_history
