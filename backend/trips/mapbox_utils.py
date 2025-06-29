import os
import requests
from urllib.parse import quote_plus

MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY')
MAPBOX_DIRECTIONS_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}"
MAPBOX_GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"


def get_coordinates_from_address(address):

    if not MAPBOX_API_KEY:
        print("MAPBOX_API_KEY not found in environment variables. Cannot geocode.")
        return None

    try:
        url = MAPBOX_GEOCODING_URL.format(query=quote_plus(address))
        params = {
            'access_token': MAPBOX_API_KEY,
            'limit': 1
        }

        print(f"DEBUG: Geocoding URL: {url}?access_token=...") 
        response = requests.get(url, params=params)
        response.raise_for_status() 

        data = response.json()
        print(f"DEBUG: Geocoding Response Status: {response.status_code}") 
        print(f"DEBUG: Geocoding Response Data: {data}")

        if data and data.get('features'):
            coords = data['features'][0]['geometry']['coordinates']
            print(f"DEBUG: Geocoded '{address}' to Lon:{coords[0]}, Lat:{coords[1]}")
            return {
                'lon': coords[0],
                'lat': coords[1]
            }
        else:
            print(f"Mapbox Geocoding: No coordinates found for address: '{address}'. Features: {data.get('features')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error geocoding address '{address}' with Mapbox: {e}")
        if e.response is not None:
            print(f"ERROR: Geocoding Response Status: {e.response.status_code}")
            print(f"ERROR: Geocoding Response Text: {e.response.text}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in get_coordinates_from_address: {e}")
        return None


def get_route_directions(origin_address, destination_address):
  
    if not MAPBOX_API_KEY:
        print("MAPBOX_API_KEY not found in environment variables. Cannot get directions.")
        return None

    print(f"DEBUG: Attempting to get route from '{origin_address}' to '{destination_address}'")

    origin_coords = get_coordinates_from_address(origin_address)
    destination_coords = get_coordinates_from_address(destination_address)

    if not origin_coords or not destination_coords:
        print(f"Mapbox Directions: Skipping route due to failed geocoding for '{origin_address}' or '{destination_address}'")
        return None

    coordinates_str = f"{origin_coords['lon']},{origin_coords['lat']};{destination_coords['lon']},{destination_coords['lat']}"
    url = MAPBOX_DIRECTIONS_URL.format(coordinates=coordinates_str)

    params = {
        'alternatives': 'false',
        'geometries': 'geojson',
        'steps': 'true',
        'access_token': MAPBOX_API_KEY
    }

    try:
        print(f"DEBUG: Directions URL: {url}?access_token=...")
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        print(f"DEBUG: Directions Response Status: {response.status_code}") 
        print(f"DEBUG: Directions Response Data: {data}") 

        if not data or not data.get('routes'):
            print(f"Mapbox Directions: No routes found for the given coordinates. Response: {data}")
            return None

        route = data['routes'][0]
        distance_meters = route['distance']
        duration_seconds = route['duration']
        route_geometry_geojson = route['geometry']

        print(f"DEBUG: Route found! Distance: {distance_meters}m, Duration: {duration_seconds}s")

        return {
            'distance_miles': distance_meters / 1609.34,
            'duration_hours': duration_seconds / 3600,
            'route_geojson': route_geometry_geojson
        }

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error fetching directions from Mapbox: {e}")
        if e.response is not None:
            print(f"ERROR: Directions Response Status: {e.response.status_code}")
            print(f"ERROR: Directions Response Text: {e.response.text}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in get_route_directions: {e}")
        return None