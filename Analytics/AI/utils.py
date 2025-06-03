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

def cosine_similarity(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be the same length.")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    if norm_a == 0 or norm_b == 0:
        return 0.0  # Avoid division by zero

    return dot_product / (norm_a * norm_b)


import re


def chat_history_summary_post_processing(summary):
    summary = summary.lower()

    # Odstránenie vzoru typu: ", niečo nie je dôležitý/á/é"
    summary = re.sub(r', [^,]*? nie je dôležit[ýáé]', '', summary)

    # Phrases to remove up to next comma or period
    removable_phrases = [
        "bez ",
        "netreba ",
        "nemá ",
        "nevyžaduje ",
        "neviem ",
        "nemusí ",
        "nie nutne ",
        "nevadí ",
        "nevadi ",
        "nepotrebujem ",
        "nepotrebuje ",
        "novostavba nie ",
        " novostavba nie ",
        "nie ",
        "aj starší byt"
    ]

    for phrase in removable_phrases:
        if phrase in summary:
            summary = re.sub(rf'{phrase}[^,.]*[,.]\s*', '', summary, flags=re.IGNORECASE)

    # Restore specific known useful phrase if removed
    if "bez problémov s parkovaním" in summary or "s bezproblémovým parkovaním" in summary:
        summary += " bez problémov s parkovaním"

    return summary.strip()


def remove_keys_from_response(response: str,
                              keys_to_remove: list) -> str:
    # Normalize whitespace
    response = response.strip()

    # Create regex patterns for each key (matches even if in different order, casing, or values)
    for key in keys_to_remove:
        pattern = rf"-\s*{re.escape(key)}:\s*.+(?:\n|$)"
        response = re.sub(pattern, '', response, flags=re.IGNORECASE)

    # Clean up excess newlines and spacing
    response = re.sub(r'\n{2,}', '\n', response).strip()
    return response

def strip_standardized_data(text: str) -> str:
    text = text.lower()

    patterns = [
        r'cena do \d{2,5} ?eur',
        r'do \d{2,5} ?eur',

        r'cena \d{2,5} ?eur',

        r'plocha ?\d{1,4} ?m²',
        r'plocha ?\d{1,4} metrov štvorcových',

        r'plocha do \d{1,4} ?m²',
        r'plocha do \d{1,4} metrov štvorcových',

        r'rozloha do \d{1,4} ?m²',
        r'rozloha do \d{1,4} metrov štvorcových',

        r'rozloha \d{1,4} ?m²',
        r'rozloha \d{1,4} metrov štvorcových',

        r's rozlohou do \d{1,4} ?m²',
        r's rozlohou do \d{1,4} metrov štvorcových',

        r's rozlohou \d{1,4} ?m²',
        r's rozlohou \d{1,4} metrov štvorcových',

        r's plochou do \d{1,4} ?m²',
        r's plochou do \d{1,4} metrov štvorcových',

        r's plochou \d{1,4} ?m²',
        r's plochou \d{1,4} metrov štvorcových',

        r'minimálne \d{1,4} ?m²',
        r'minimálne \d{1,4} metrov štvorcových',

        r'\b\d{1,4} ?m²\b',
        r'\b\d{1,4} metrov štvorcových\b',

        r'\b\d{1,4} stvorcov\b',
        r'\b\d{1,4} štvorcov\b',
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text)

    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r',\s*,', ',', text)
    text = text.strip(' ,.')

    return text


import re

def remove_none_or_nie_fields(text: str) -> str:
    text = text.lower()

    # Remove key: none or key: nie
    text = re.sub(r'\b[^:,\n]+:\s*(none|nie|neviem|nevie|nevieme|netreba|nemusí)\b\s*,?', '', text, flags=re.IGNORECASE)

    # Define more targeted and safer patterns
    patterns = [
        r'\bbez\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnie\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnechce(?:m|š|me)?\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnetreba\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnepotrebu(?:je|jem|jeme)\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnevyžaduje(?:m|š|me)?\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnem(?:á|ám|áme)\s+\w+(?:\s+\w+)?[,.]?',
        r'\bneviem(?:e)?\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnemusí(?:a)?\s+\w+(?:\s+\w+)?[,.]?',
        r'\bje mi jedno\s+\w+(?:\s+\w+)?[,.]?',
        r'\b\w+(?:\s+\w+)?\s+nie je dôležit[ýáé][,.]?',
        r'\bneuviedol\s+\w+(?:\s+\w+)?[,.]?',
        r'\bneuvádza\s+\w+(?:\s+\w+)?[,.]?',
        r'\bnevad[iy]\s+\w+(?:\s+\w+)?[,.]?'
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Clean up commas and whitespace
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'^,|,$', '', text)

    return text.strip()
