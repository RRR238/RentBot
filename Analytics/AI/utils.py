import json
def convert_text_to_dict(llm_output):
    final_dict = {}
    no_spaces = llm_output.strip().replace('/n','').replace(' \n','').replace(' ','')
    final_dict['price_rent'] = no_spaces[no_spaces.find('cena')+len('cena'):no_spaces.find('poloha')].replace(',','').replace('\n','').replace(':','')
    final_dict['rooms'] = no_spaces[no_spaces.find('početizieb') + len('početizieb'):no_spaces.find('rozloha')].replace(',','').replace('\n', '').replace(':', '')
    final_dict['size'] = no_spaces[no_spaces.find('rozloha') + len('rozloha'):no_spaces.find('typnehnuteľnosti')].replace(',', '').replace('\n', '').replace(':', '')
    final_dict['property_type'] = no_spaces[no_spaces.find('typnehnuteľnosti') + len('typnehnuteľnosti'):].replace(',','').replace('\n', '').replace(':', '').replace('.','')

    return final_dict


def processing_dict(key_attributes_dict):
    property_type_mappings = {"dom":"house", "loft":"loft", "mezonet":"flat", "byt":"flat", "garzonka":"studio", "penthouse":"flat"}
    for k,v in key_attributes_dict.items():
        if v == 'None':
            key_attributes_dict[k] = None
        elif k == 'property_type':
            key_attributes_dict[k] = property_type_mappings[v]
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
        if k=='property_type' and v is not None:
            filter.append({"term": {"metadata.property_type.keyword": v}})

    return filter



# with open('get_key_attributes_prompt_testing.json', 'r',encoding="utf-8") as json_file:
#             key_attributes = json.load(json_file)
#
#
# for i in key_attributes:
#     d = convert_text_to_dict(i['response'])
#     processing_dict(d)
#     print(prepare_filters(d))