from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

def get_coordinates(place_name, max_retries=3, delay=1.5):
    """Returns the latitude and longitude of a given place with retry and delay logic."""
    geolocator = Nominatim(user_agent="rentbot-geolocator")

    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(place_name, timeout=5)

            if not location:
                # Try cleaned-up fallback if nothing found
                location = geolocator.geocode(place_name.lower().replace("ulica", ""), timeout=5)

            if location:
                return location.latitude, location.longitude
            else:
                return None

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"[retry {attempt+1}] Geocoding error: {e}")
            time.sleep(delay)

    print("Failed to get coordinates after retries.")
    return None
