import json
from langchain.schema import HumanMessage, AIMessage
import math
import re

def convert_text_to_dict(llm_output):
    final_dict = {}
    no_spaces = llm_output.strip().replace('/n','').replace(' \n','').replace(' ','')
    final_dict['price_rent'] = no_spaces[no_spaces.find('cena')+len('cena'):no_spaces.find('početizieb')].replace(',','').replace('\n','').replace(':','')
    final_dict['rooms'] = no_spaces[no_spaces.find('početizieb') + len('početizieb'):no_spaces.find('početiziebMIN')].replace(',','').replace('\n', '').replace(':', '')
    final_dict['rooms_min'] = no_spaces[no_spaces.find('početiziebMIN') + len('početiziebMIN'):no_spaces.find('početiziebMAX')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['rooms_max'] = no_spaces[no_spaces.find('početiziebMAX') + len('početiziebMAX'):no_spaces.find('rozloha')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['size'] = no_spaces[no_spaces.find('rozloha') + len('rozloha'):no_spaces.find('typnehnuteľnosti')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['property_type'] = no_spaces[no_spaces.find('typnehnuteľnosti') + len('typnehnuteľnosti'):no_spaces.find('novostavba')].replace(',','').replace('\n', '').replace(':', '').replace('.','')
    final_dict['property_status'] = no_spaces[no_spaces.find('novostavba') + len('novostavba'):].replace(',','').replace('\n', '').replace(':', '').replace('.', '')
    return final_dict


def processing_dict(key_attributes_dict):
    property_type_mappings = {"dom":"house",
                              "loft":"loft",
                              "mezonet":"mezonet",
                              "byt":"flat",
                              "garzonka":"studio",
                              "penthouse":"penthouse"}
    for k,v in key_attributes_dict.items():
        if v == 'None':
            key_attributes_dict[k] = None
        elif k == 'property_type':
            key_attributes_dict[k] = property_type_mappings[v]
        elif k == 'property_status':
            key_attributes_dict[k] = 'novostavba'
        else:
            try:
                key_attributes_dict[k] = int(v)
            except:
                key_attributes_dict[k] = None

    return key_attributes_dict


def prepare_filters(processed_dict):
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


import requests

def get_bounding_box(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_name,
        'format': 'json',
        'limit': 1,
        'polygon_geojson': 0,
        'addressdetails': 1
    }

    headers = {
        'User-Agent': 'YourApp/1.0 (richardmacus0@gmail.com)'  # Always use a UA
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data:
        bounding_box = data[0]['boundingbox']  # [south, north, west, east]
        print("Bounding Box:", bounding_box)
        return bounding_box
    else:
        print("No results found.")
        return None

def few_shots_chat_history(shots, prompt_template):
    shots_for_memory = []
    accumulated_history = ""

    for shot in shots:
        # Inject prior history into the prompt
        formatted_prompt = prompt_template.format(
            user_prompt=shot['User'],
            chat_history=accumulated_history.strip()
        )

        # Store in final few-shot memory structure
        shots_for_memory.append({
            "User": formatted_prompt,
            "AI": shot["AI"]
        })

        # Append to accumulated history for next turn
        accumulated_history += f"Používateľ: {shot['User']}\nAI: {shot['AI']}\n\n"

    return shots_for_memory

def extract_chat_history_as_dict(memory):
    chat_history = []
    for message in memory.chat_memory.messages:
        role = "user" if isinstance(message, HumanMessage) else "assistant" if isinstance(message, AIMessage) else "system"
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

def cosine_similarity(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be the same length.")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    if norm_a == 0 or norm_b == 0:
        return 0.0  # Avoid division by zero

    return dot_product / (norm_a * norm_b)

def chat_history_summary_post_processing(summary):
    summary = summary.lower()

    # Phrases to remove up to next comma or period
    removable_phrases = ["bez", "netreba", "nemá", "nevyžaduje", "neviem", "nemusí"]
    for phrase in removable_phrases:
        if phrase in summary:
            summary = re.sub(rf'{phrase}[^,.]*[,.]\s*',
                             '',
                             summary,
                             flags=re.IGNORECASE)

    # Restore specific known useful phrase if removed
    if "bez problémov s parkovaním" in summary:
        summary += " bez problémov s parkovaním"

    return summary.strip()

