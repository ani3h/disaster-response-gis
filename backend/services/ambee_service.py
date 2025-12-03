"""
Ambee Natural Disaster API Service
===================================
Integrates with Ambee API for real-time disaster alerts.
FIXED: Uses correct Ambee API format with lat/lng queries.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import config

# Kerala center point
KERALA_CENTER = {
    'lat': 10.352874,
    'lng': 76.512039
}

# Search radius in km
SEARCH_RADIUS_KM = 250

# Ambee API configuration
AMBEE_API_KEY = os.getenv('AMBEE_API_KEY', '')
AMBEE_BASE_URL = 'https://api.ambeedata.com/latest/by-lat-lng'

# Cache directory
LIVE_DISASTERS_DIR = Path(config.PROCESSED_DATA_DIR) / 'live_disasters'
LIVE_DISASTERS_DIR.mkdir(parents=True, exist_ok=True)

# Cache duration (1 hour to respect API limits)
CACHE_DURATION = timedelta(hours=1)


def get_cache_file(disaster_type):
    """Get cache file path for a disaster type."""
    return LIVE_DISASTERS_DIR / f'{disaster_type}.json'


def is_cache_valid(cache_file):
    """Check if cache file exists and is less than 1 hour old."""
    if not cache_file.exists():
        return False

    modified_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
    age = datetime.now() - modified_time

    return age < CACHE_DURATION


def load_from_cache(disaster_type):
    """Load cached disaster data."""
    cache_file = get_cache_file(disaster_type)

    if is_cache_valid(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f'Error loading cache for {disaster_type}: {e}')
            return None

    return None


def save_to_cache(disaster_type, data):
    """Save disaster data to cache."""
    cache_file = get_cache_file(disaster_type)

    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'Cached {disaster_type} data to {cache_file}')
    except Exception as e:
        print(f'Error saving cache for {disaster_type}: {e}')


def fetch_ambee_data(disaster_type):
    """
    Fetch disaster data from Ambee API using correct format.

    Args:
        disaster_type (str): Type of disaster (flood, landslide, cyclone)

    Returns:
        dict: GeoJSON FeatureCollection
    """
    if not AMBEE_API_KEY:
        print('Warning: AMBEE_API_KEY not set in environment')
        return {'type': 'FeatureCollection', 'features': []}

    try:
        headers = {
            'x-api-key': AMBEE_API_KEY,
            'Content-type': 'application/json'
        }

        # Correct Ambee API format
        params = {
            'lat': KERALA_CENTER['lat'],
            'lng': KERALA_CENTER['lng'],
            'type': disaster_type,
            'radius': SEARCH_RADIUS_KM
        }

        print(f'Fetching {disaster_type} data from Ambee API...')
        print(f'Request: {AMBEE_BASE_URL} with params {params}')

        response = requests.get(AMBEE_BASE_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        print(f'Ambee API response for {disaster_type}: {json.dumps(data)[:200]}...')

        # Convert to GeoJSON
        geojson = convert_ambee_to_geojson(data, disaster_type)

        print(f'Converted to {len(geojson["features"])} GeoJSON features')

        return geojson

    except requests.exceptions.RequestException as e:
        print(f'Error fetching Ambee {disaster_type} data: {e}')
        return {'type': 'FeatureCollection', 'features': []}
    except Exception as e:
        print(f'Unexpected error in fetch_ambee_data({disaster_type}): {e}')
        return {'type': 'FeatureCollection', 'features': []}


def convert_ambee_to_geojson(ambee_data, disaster_type):
    """
    Convert Ambee API response to GeoJSON FeatureCollection.

    Args:
        ambee_data (dict): Raw Ambee API response
        disaster_type (str): Type of disaster (flood, landslide, cyclone)

    Returns:
        dict: GeoJSON FeatureCollection
    """
    features = []

    try:
        # Check if data exists in response
        if not ambee_data or 'data' not in ambee_data:
            print(f'No data in Ambee response for {disaster_type}')
            return {'type': 'FeatureCollection', 'features': []}

        data_items = ambee_data['data']

        # Handle both single object and array responses
        if not isinstance(data_items, list):
            data_items = [data_items]

        for data_item in data_items:
            if not data_item:
                continue

            # Extract coordinates
            lat = data_item.get('lat', KERALA_CENTER['lat'])
            lng = data_item.get('lng', KERALA_CENTER['lng'])

            # Create feature based on disaster type
            feature = None

            if disaster_type == 'flood':
                flood_risk = data_item.get('floodRisk', 'unknown')
                water_level = data_item.get('waterLevel', 0)

                # Only add if there's actual flood risk
                if flood_risk not in ['low', 'unknown', None] or water_level > 0:
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [lng, lat]
                        },
                        'properties': {
                            'disaster_type': 'flood',
                            'hazard_type': 'flood',
                            'severity': flood_risk if flood_risk not in ['unknown', None] else 'medium',
                            'water_level': water_level,
                            'source': 'Ambee API',
                            'timestamp': datetime.now().isoformat(),
                            'description': f'Flood risk: {flood_risk}, Water level: {water_level}m'
                        }
                    }

            elif disaster_type == 'cyclone':
                wind_speed = data_item.get('windSpeed', 0)
                pressure = data_item.get('pressure', 0)

                # Consider cyclone risk if wind speed is high
                if wind_speed > 50:  # km/h
                    severity = 'high' if wind_speed > 100 else 'medium'
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [lng, lat]
                        },
                        'properties': {
                            'disaster_type': 'cyclone',
                            'hazard_type': 'cyclone',
                            'severity': severity,
                            'wind_speed': wind_speed,
                            'pressure': pressure,
                            'source': 'Ambee API',
                            'timestamp': datetime.now().isoformat(),
                            'description': f'High wind speed: {wind_speed} km/h'
                        }
                    }

            elif disaster_type == 'landslide':
                soil_moisture = data_item.get('soilMoisture', 0)
                landslide_risk = data_item.get('landslideRisk', 'unknown')

                # High soil moisture or explicit landslide risk indicates danger
                if soil_moisture > 70 or landslide_risk not in ['low', 'unknown', None]:
                    severity = 'high' if soil_moisture > 85 or landslide_risk == 'high' else 'medium'
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [lng, lat]
                        },
                        'properties': {
                            'disaster_type': 'landslide',
                            'hazard_type': 'landslide',
                            'severity': severity,
                            'soil_moisture': soil_moisture,
                            'landslide_risk': landslide_risk,
                            'source': 'Ambee API',
                            'timestamp': datetime.now().isoformat(),
                            'description': f'Landslide risk: {landslide_risk}, Soil moisture: {soil_moisture}%'
                        }
                    }

            if feature:
                features.append(feature)

    except Exception as e:
        print(f'Error converting Ambee data to GeoJSON: {e}')

    return {
        'type': 'FeatureCollection',
        'features': features
    }


def get_live_flood_data():
    """
    Get live flood data from cache or fetch from Ambee API.

    Returns:
        dict: GeoJSON FeatureCollection
    """
    # Try cache first
    cached = load_from_cache('flood')
    if cached:
        print('Using cached flood data')
        return cached

    # Fetch fresh data
    print('Fetching fresh flood data from Ambee API')
    data = fetch_ambee_data('flood')

    # Save to cache
    save_to_cache('flood', data)

    return data


def get_live_cyclone_data():
    """
    Get live cyclone data from cache or fetch from Ambee API.

    Returns:
        dict: GeoJSON FeatureCollection
    """
    # Try cache first
    cached = load_from_cache('cyclone')
    if cached:
        print('Using cached cyclone data')
        return cached

    # Fetch fresh data
    print('Fetching fresh cyclone data from Ambee API')
    data = fetch_ambee_data('cyclone')

    # Save to cache
    save_to_cache('cyclone', data)

    return data


def get_live_landslide_data():
    """
    Get live landslide data from cache or fetch from Ambee API.

    Returns:
        dict: GeoJSON FeatureCollection
    """
    # Try cache first
    cached = load_from_cache('landslide')
    if cached:
        print('Using cached landslide data')
        return cached

    # Fetch fresh data
    print('Fetching fresh landslide data from Ambee API')
    data = fetch_ambee_data('landslide')

    # Save to cache
    save_to_cache('landslide', data)

    return data


def refresh_all_live_data():
    """
    Force refresh all live disaster data from Ambee API.

    Returns:
        dict: Summary of refreshed data
    """
    print('Refreshing all live disaster data from Ambee API...')

    flood_data = fetch_ambee_data('flood')
    save_to_cache('flood', flood_data)

    cyclone_data = fetch_ambee_data('cyclone')
    save_to_cache('cyclone', cyclone_data)

    landslide_data = fetch_ambee_data('landslide')
    save_to_cache('landslide', landslide_data)

    return {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'flood_alerts': len(flood_data.get('features', [])),
        'cyclone_alerts': len(cyclone_data.get('features', [])),
        'landslide_alerts': len(landslide_data.get('features', []))
    }
