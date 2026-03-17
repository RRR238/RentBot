from Shared.Geolocation import get_bounding_box_from_location


def process_types_and_rooms_filters(types:str):
    types_list = types.split(',') if "," in types else [types]
    rooms = [int(i[0]) for i in types_list if 'room' in i or 'plus' in i]
    filtered_types = [t for t in types_list if 'room' not in t.lower() and 'plus' not in t.lower()]
    if len(filtered_types) < len(types_list):
        filtered_types.append('flat')

    return {'types':filtered_types,
            'rooms':rooms}


def get_bounding_boxes(locations:str)->list[dict]:
    locations_list = locations.split(',')
    bounding_boxes = [get_bounding_box_from_location(location) for location in locations_list]
    filtered_bonding_boxes = [bb for bb in bounding_boxes if bb is not None]
    if filtered_bonding_boxes:
        return bounding_boxes
    else:
        raise ValueError("No valid bounding boxes found for given locations.")