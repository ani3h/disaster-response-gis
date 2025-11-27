"""
Layers API Module
=================
API endpoints for map layers and spatial data.
Updated with new Kerala data file paths.
"""

from flask import Blueprint, jsonify, request
from backend.db.postgis_queries import get_roads_in_bbox


# Create Blueprint
layers_bp = Blueprint('layers', __name__)


@layers_bp.route('/', methods=['GET'])
def get_all_layers():
    """
    Get metadata for all available map layers.

    Returns:
        JSON: List of available layers with metadata
    """
    try:
        layers = [
            {
                'id': 'disaster_zones',
                'name': 'Disaster Zones',
                'type': 'polygon',
                'description': 'Active disaster-affected areas',
                'endpoint': '/api/disaster/zones',
                'style': {
                    'fillColor': '#ff0000',
                    'fillOpacity': 0.3,
                    'color': '#ff0000',
                    'weight': 2
                }
            },
            {
                'id': 'shelters',
                'name': 'Emergency Shelters',
                'type': 'point',
                'description': 'Available emergency shelters',
                'endpoint': '/api/shelters/all',
                'style': {
                    'icon': 'shelter',
                    'color': '#0000ff'
                }
            },
            {
                'id': 'hospitals',
                'name': 'Hospitals',
                'type': 'point',
                'description': 'Hospital facilities',
                'endpoint': '/api/shelters/hospitals/all',
                'style': {
                    'icon': 'hospital',
                    'color': '#00ff00'
                }
            },
            {
                'id': 'roads',
                'name': 'Road Network',
                'type': 'linestring',
                'description': 'Road network with traffic status',
                'endpoint': '/api/layers/roads',
                'style': {
                    'color': '#333333',
                    'weight': 2
                }
            },
            {
                'id': 'admin_boundaries',
                'name': 'Administrative Boundaries',
                'type': 'polygon',
                'description': 'District and state boundaries',
                'endpoint': '/api/layers/boundaries',
                'style': {
                    'fillColor': '#cccccc',
                    'fillOpacity': 0.1,
                    'color': '#666666',
                    'weight': 1
                }
            }
        ]

        return jsonify({
            'status': 'success',
            'data': layers,
            'count': len(layers)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/roads', methods=['GET'])
def get_roads_layer():
    """
    Get roads layer as GeoJSON from new Kerala roads file.

    Query Parameters:
        bbox (str, optional): Bounding box (minLon,minLat,maxLon,maxLat)

    Returns:
        JSON: GeoJSON FeatureCollection of roads
    """
    try:
        from backend.core.data_loader import load_roads, convert_to_geojson, filter_by_bbox

        roads_gdf = load_roads()

        if roads_gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            bbox_str = request.args.get('bbox')
            if bbox_str:
                bbox = [float(x) for x in bbox_str.split(',')]
                if len(bbox) == 4:
                    roads_gdf = filter_by_bbox(roads_gdf, *bbox)

            geojson = convert_to_geojson(roads_gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/boundaries', methods=['GET'])
def get_admin_boundaries():
    """
    Get administrative boundaries as GeoJSON from new Kerala boundary files.

    Query Parameters:
        level (str, optional): Admin level (state, districts, taluks, villages)

    Returns:
        JSON: GeoJSON FeatureCollection of boundaries
    """
    try:
        from backend.core.data_loader import (
            load_boundary, load_district, load_state,
            load_taluk, load_village, convert_to_geojson
        )

        level = request.args.get('level', 'districts')

        if level == 'state':
            gdf = load_state()
        elif level == 'districts':
            gdf = load_district()
        elif level == 'taluks':
            gdf = load_taluk()
        elif level == 'villages':
            gdf = load_village()
        else:
            gdf = load_boundary()

        if gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            geojson = convert_to_geojson(gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/cyclone-tracks', methods=['GET'])
def get_cyclone_tracks():
    """
    Get cyclone track data as GeoJSON.

    Returns:
        JSON: GeoJSON FeatureCollection of cyclone tracks
    """
    try:
        from backend.core.spatial_analysis import compute_cyclone_zones

        geojson = compute_cyclone_zones()

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/safe-zones', methods=['POST'])
def calculate_safe_zones():
    """
    Calculate and return safe zones (areas not affected by disasters).

    Request Body:
        {
            "buffer_distance_meters": int (optional, default: 5000)
        }

    Returns:
        JSON: GeoJSON of safe zones
    """
    try:
        data = request.get_json() or {}
        buffer_distance = data.get('buffer_distance_meters', 5000)

        geojson = {
            'type': 'FeatureCollection',
            'features': []
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


@layers_bp.route('/heatmap', methods=['POST'])
def generate_heatmap():
    """
    Generate heatmap data for disaster intensity.

    Request Body:
        {
            "layer": str,
            "bbox": [minLon, minLat, maxLon, maxLat]
        }

    Returns:
        JSON: Heatmap data points
    """
    try:
        data = request.get_json()

        if not data or 'layer' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing layer parameter'
            }), 400

        layer = data['layer']

        heatmap_data = {
            'points': []
        }

        return jsonify({
            'status': 'success',
            'data': heatmap_data
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/buildings', methods=['GET'])
def get_buildings_layer():
    """
    Get buildings layer from new kerala_buildings.geojson file.

    Query Parameters:
        bbox (str, optional): Bounding box

    Returns:
        JSON: GeoJSON FeatureCollection of buildings
    """
    try:
        from backend.core.data_loader import load_buildings, convert_to_geojson, filter_by_bbox

        buildings_gdf = load_buildings()

        if buildings_gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            bbox_str = request.args.get('bbox')
            if bbox_str:
                bbox = [float(x) for x in bbox_str.split(',')]
                if len(bbox) == 4:
                    buildings_gdf = filter_by_bbox(buildings_gdf, *bbox)

            geojson = convert_to_geojson(buildings_gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/coastline', methods=['GET'])
def get_coastline_layer():
    """
    Get coastline layer from new kerala_coastline.geojson file.

    Returns:
        JSON: GeoJSON FeatureCollection of coastline
    """
    try:
        from backend.core.data_loader import load_coastline, convert_to_geojson

        coastline_gdf = load_coastline()

        if coastline_gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            geojson = convert_to_geojson(coastline_gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/landslides', methods=['GET'])
def get_landslides_layer():
    """
    Get landslides layer - merged from all Kerala district files.

    Returns:
        JSON: GeoJSON FeatureCollection of landslide zones
    """
    try:
        from backend.core.data_loader import load_landslides_kerala, convert_to_geojson

        landslides_gdf = load_landslides_kerala()

        if landslides_gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            geojson = convert_to_geojson(landslides_gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/cyclone', methods=['GET'])
def get_cyclone_layer():
    """
    Get cyclone layer as GeoJSON.

    Returns:
        JSON: GeoJSON FeatureCollection of cyclone zones
    """
    try:
        from backend.core.spatial_analysis import compute_cyclone_zones

        geojson = compute_cyclone_zones()

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/affected-zones', methods=['GET'])
def get_affected_zones():
    """
    Get all affected zones (combined hazards) as GeoJSON.

    Returns:
        JSON: GeoJSON FeatureCollection of all affected zones
    """
    try:
        from backend.core.spatial_analysis import compute_cyclone_zones, compute_flood_zones
        from backend.core.data_loader import load_rivers, load_landslides_kerala, convert_to_geojson

        landslides_gdf = load_landslides_kerala()
        landslides = convert_to_geojson(landslides_gdf) if landslides_gdf is not None else {
            'type': 'FeatureCollection', 'features': []
        }

        cyclones = compute_cyclone_zones()

        rivers_gdf = load_rivers()
        floods = compute_flood_zones(rivers_gdf, buffer_distance=1000) if rivers_gdf is not None else {
            'type': 'FeatureCollection', 'features': []
        }

        all_features = []
        all_features.extend(landslides.get('features', []))
        all_features.extend(cyclones.get('features', []))
        all_features.extend(floods.get('features', []))

        combined_geojson = {
            'type': 'FeatureCollection',
            'features': all_features
        }

        return jsonify({
            'status': 'success',
            'data': combined_geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/rivers', methods=['GET'])
def get_rivers_layer():
    """
    Get rivers layer from new kerala_rivers.geojson file.

    Returns:
        JSON: GeoJSON FeatureCollection of rivers
    """
    try:
        from backend.core.data_loader import load_rivers, convert_to_geojson

        rivers_gdf = load_rivers()

        if rivers_gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            geojson = convert_to_geojson(rivers_gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@layers_bp.route('/water', methods=['GET'])
def get_water_layer():
    """
    Get water bodies layer from new kerala_water.geojson file.

    Returns:
        JSON: GeoJSON FeatureCollection of water bodies
    """
    try:
        from backend.core.data_loader import load_water, convert_to_geojson

        water_gdf = load_water()

        if water_gdf is None:
            geojson = {'type': 'FeatureCollection', 'features': []}
        else:
            geojson = convert_to_geojson(water_gdf)

        return jsonify({
            'status': 'success',
            'data': geojson
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
