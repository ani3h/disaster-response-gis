"""
Shelters API Module
===================
API endpoints for shelter and hospital information.
"""

from flask import Blueprint, jsonify, request
from backend.db.postgis_queries import find_nearest_facilities


# Create Blueprint
shelters_bp = Blueprint('shelters', __name__)


@shelters_bp.route('/nearest', methods=['POST'])
def get_nearest_shelters():
    """
    Find nearest shelters to a given location.

    Request Body:
        {
            "latitude": float,
            "longitude": float,
            "limit": int (optional, default: 5),
            "max_distance_km": float (optional, default: 50)
        }

    Returns:
        JSON: List of nearest shelters with distances
    """
    try:
        data = request.get_json()

        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing latitude or longitude'
            }), 400

        lat = float(data['latitude'])
        lon = float(data['longitude'])
        limit = data.get('limit', 5)
        max_distance_km = data.get('max_distance_km', 50)

        # Find nearest shelters using PostGIS query
        shelters = find_nearest_facilities(
            lat, lon,
            'shelters',
            limit=limit,
            max_distance_km=max_distance_km
        )

        return jsonify({
            'status': 'success',
            'data': shelters,
            'count': len(shelters)
        }), 200

    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid coordinate format'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shelters_bp.route('/all', methods=['GET'])
def get_all_shelters():
    """
    Get all shelters as GeoJSON.

    Query Parameters:
        bbox (str, optional): Bounding box filter (minLon,minLat,maxLon,maxLat)
        has_capacity (bool, optional): Filter shelters with available capacity

    Returns:
        JSON: GeoJSON FeatureCollection of shelters
    """
    try:
        # TODO: Query database for all shelters with filters

        # Placeholder response
        geojson = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [78.9629, 20.5937]
                    },
                    'properties': {
                        'id': 1,
                        'name': 'Central Emergency Shelter',
                        'capacity': 500,
                        'current_occupancy': 120,
                        'has_food': True,
                        'has_water': True,
                        'has_medical': True
                    }
                }
            ]
        }

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shelters_bp.route('/capacity', methods=['GET'])
def get_shelter_capacity_summary():
    """
    Get summary of shelter capacity across all shelters.

    Returns:
        JSON: Shelter capacity statistics
    """
    try:
        # TODO: Query database for capacity statistics

        # Placeholder response
        summary = {
            'total_shelters': 25,
            'total_capacity': 12500,
            'current_occupancy': 3420,
            'available_capacity': 9080,
            'occupancy_rate': 27.36,
            'shelters_at_capacity': 2,
            'shelters_with_food': 22,
            'shelters_with_medical': 15
        }

        return jsonify({
            'status': 'success',
            'data': summary
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shelters_bp.route('/hospitals/nearest', methods=['POST'])
def get_nearest_hospitals():
    """
    Find nearest hospitals to a given location.

    Request Body:
        {
            "latitude": float,
            "longitude": float,
            "limit": int (optional, default: 5),
            "emergency_ready": bool (optional, filter for emergency ready)
        }

    Returns:
        JSON: List of nearest hospitals
    """
    try:
        data = request.get_json()

        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing latitude or longitude'
            }), 400

        lat = float(data['latitude'])
        lon = float(data['longitude'])
        limit = data.get('limit', 5)

        # Find nearest hospitals
        hospitals = find_nearest_facilities(
            lat, lon,
            'hospitals',
            limit=limit,
            max_distance_km=100
        )

        return jsonify({
            'status': 'success',
            'data': hospitals,
            'count': len(hospitals)
        }), 200

    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid coordinate format'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@shelters_bp.route('/hospitals/all', methods=['GET'])
def get_all_hospitals():
    """
    Get all hospitals as GeoJSON.

    Returns:
        JSON: GeoJSON FeatureCollection of hospitals
    """
    try:
        # TODO: Query database for all hospitals

        # Placeholder response
        geojson = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [78.9629, 20.5937]
                    },
                    'properties': {
                        'id': 1,
                        'name': 'District General Hospital',
                        'capacity': 200,
                        'emergency_ready': True,
                        'facility_type': 'General'
                    }
                }
            ]
        }

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# TODO: Add more shelter/hospital endpoints:
# - PUT /shelters/<id>/occupancy - Update shelter occupancy
# - POST /shelters/recommend - Recommend best shelter for user
# - GET /shelters/<id>/directions - Get directions to shelter
# - POST /hospitals/emergency - Find emergency-ready hospitals
