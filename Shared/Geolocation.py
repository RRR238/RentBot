from geopy.geocoders import Nominatim

def get_coordinates(place_name):
    """Returns the latitude and longitude of a given place."""
    geolocator = Nominatim(user_agent="geo_finder")
    location = geolocator.geocode(place_name)
    if not location:
        location = geolocator.geocode(place_name.lower(
                                    ).replace('ulica',''))

    if location:
        return location.latitude, location.longitude
    else:
        return None
