def process_types_and_rooms_filters(types:str):
    types_list = types.split(',') if "," in types else [types]
    rooms = [int(i[0]) for i in types_list if 'room' in i or 'plus' in i]
    filtered_types = [t for t in types_list if 'room' not in t.lower() and 'plus' not in t.lower()]
    if len(filtered_types) < len(types_list):
        filtered_types.append('flat')

    return {'types':filtered_types,
            'rooms':rooms}


def filter_vector_search_results(vector_search_results:list[dict],
                                 types:list[str],
                                 rooms:list[int],
                                 price_max:int,
                                 size_min:int,
                                 size_max:int):
    filtered_results = []
    for result in vector_search_results:
        if result['property_type'] in types:
            if result['rooms'] in rooms:
                if result['price_total'] <= price_max:
                    if result['size'] >= size_min:
                        if result['size'] <= size_max:
                            filtered_results.append({'source_url':result['source_url'],
                                                     'price_total':result['price_total'],
                                                     'location':result['location']})

    return filtered_results
