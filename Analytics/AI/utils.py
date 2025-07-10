import json
from langchain.schema import HumanMessage, AIMessage
import math
import re
from Shared.Geolocation import get_bounding_box_from_location

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


def processing_dict(key_attributes_dict):
    property_type_mappings = {"dom":"house",
                              "loft":"loft",
                              "mezonet":"mezonet",
                              "byt":"flat",
                              "garzónka":"studio",
                              "garzonka": "studio",
                              "garsónka": "studio",
                              "garsonka": "studio",
                              "penthouse":"penthouse"}
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
