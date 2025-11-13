"""
Disaster API Module
===================
API endpoints for disaster zone information and updates.
"""

from flask import Blueprint, jsonify, request
from backend.db.postgis_queries import get_disaster_zones_geojson, check_point_in_disaster_zone
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
disaster_bp = Blueprint('disaster', __name__)


@disaster_bp.route('/zones', methods=['GET'])
def get_disaster_zones():
    """
    Get all active disaster zones as GeoJSON.

    Query Parameters:
        type (str, optional): Filter by disaster type (flood, cyclone, earthquake)
        severity (str, optional): Filter by severity (low, medium, high, critical)

    Returns:
        JSON: GeoJSON FeatureCollection of disaster zones
    """
    try:
        # Get query parameters
        disaster_type = request.args.get('type')
        severity = request.args.get('severity')

        # Get disaster zones from database
        geojson = get_disaster_zones_geojson()

        # TODO: Apply filters based on query parameters

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        logger.error(f"Error fetching disaster zones: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@disaster_bp.route('/check-location', methods=['POST'])
def check_location_safety():
    """
    Check if a location is within a disaster zone.

    Request Body:
        {
            "latitude": float,
            "longitude": float
        }

    Returns:
        JSON: Safety status and disaster zone info if applicable
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

        # Check if point is in disaster zone
        result = check_point_in_disaster_zone(lat, lon)

        return jsonify({
            'status': 'success',
            'data': result
        }), 200

    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid latitude or longitude format'
        }), 400
    except Exception as e:
        logger.error(f"Error checking location safety: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@disaster_bp.route('/updates', methods=['GET'])
def get_disaster_updates():
    """
    Get recent disaster updates and alerts.

    Query Parameters:
        limit (int, optional): Number of updates to return (default: 10)
        hours (int, optional): Get updates from last N hours (default: 24)

    Returns:
        JSON: List of disaster updates
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        hours = request.args.get('hours', 24, type=int)

        # TODO: Query database for recent disaster updates

        # Placeholder response
        updates = [
            {
                'id': 1,
                'type': 'flood',
                'severity': 'high',
                'title': 'Severe flooding in coastal areas',
                'description': 'Heavy rainfall has caused severe flooding in multiple coastal districts.',
                'affected_areas': ['District A', 'District B'],
                'timestamp': '2024-01-15T10:30:00Z'
            }
        ]

        return jsonify({
            'status': 'success',
            'data': updates,
            'count': len(updates)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching disaster updates: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@disaster_bp.route('/statistics', methods=['GET'])
def get_disaster_statistics():
    """
    Get overall disaster statistics.

    Returns:
        JSON: Aggregated disaster statistics
    """
    try:
        # TODO: Calculate real statistics from database

        # Placeholder response
        stats = {
            'active_disasters': 3,
            'total_affected_area_sqkm': 1250.5,
            'estimated_affected_population': 45000,
            'active_alerts': 5,
            'disaster_types': {
                'flood': 2,
                'cyclone': 1
            }
        }

        return jsonify({
            'status': 'success',
            'data': stats
        }), 200

    except Exception as e:
        logger.error(f"Error fetching disaster statistics: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@disaster_bp.route('/impact-analysis', methods=['POST'])
def analyze_disaster_impact():
    """
    Analyze impact of a disaster zone.

    Request Body:
        {
            "disaster_zone_id": int
        }

    Returns:
        JSON: Comprehensive impact analysis
    """
    try:
        data = request.get_json()

        if not data or 'disaster_zone_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing disaster_zone_id'
            }), 400

        disaster_id = data['disaster_zone_id']

        # TODO: Perform comprehensive impact analysis using impact_analysis module

        # Placeholder response
        impact = {
            'disaster_id': disaster_id,
            'affected_population': 25000,
            'affected_area_sqkm': 450.0,
            'affected_hospitals': 3,
            'affected_shelters': 2,
            'severity': 'high'
        }

        return jsonify({
            'status': 'success',
            'data': impact
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing disaster impact: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# TODO: Add more disaster API endpoints:
# - POST /report - Report new disaster
# - PUT /zones/<id> - Update disaster zone
# - GET /forecast - Get disaster forecast
# - GET /history - Get historical disaster data
