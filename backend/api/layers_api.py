# """
# Layers API Module
# =================
# API endpoints for map layers and spatial data.
# """

# from flask import Blueprint, jsonify, request
# from backend.db.postgis_queries import get_roads_in_bbox


# # Create Blueprint
# layers_bp = Blueprint('layers', __name__)


# @layers_bp.route('/', methods=['GET'])
# def get_all_layers():
#     """
#     Get metadata for all available map layers.

#     Returns:
#         JSON: List of available layers with metadata
#     """
#     try:
#         layers = [
#             {
#                 'id': 'disaster_zones',
#                 'name': 'Disaster Zones',
#                 'type': 'polygon',
#                 'description': 'Active disaster-affected areas',
#                 'endpoint': '/api/disaster/zones',
#                 'style': {
#                     'fillColor': '#ff0000',
#                     'fillOpacity': 0.3,
#                     'color': '#ff0000',
#                     'weight': 2
#                 }
#             },
#             {
#                 'id': 'shelters',
#                 'name': 'Emergency Shelters',
#                 'type': 'point',
#                 'description': 'Available emergency shelters',
#                 'endpoint': '/api/shelters/all',
#                 'style': {
#                     'icon': 'shelter',
#                     'color': '#0000ff'
#                 }
#             },
#             {
#                 'id': 'hospitals',
#                 'name': 'Hospitals',
#                 'type': 'point',
#                 'description': 'Hospital facilities',
#                 'endpoint': '/api/shelters/hospitals/all',
#                 'style': {
#                     'icon': 'hospital',
#                     'color': '#00ff00'
#                 }
#             },
#             {
#                 'id': 'roads',
#                 'name': 'Road Network',
#                 'type': 'linestring',
#                 'description': 'Road network with traffic status',
#                 'endpoint': '/api/layers/roads',
#                 'style': {
#                     'color': '#333333',
#                     'weight': 2
#                 }
#             },
#             {
#                 'id': 'admin_boundaries',
#                 'name': 'Administrative Boundaries',
#                 'type': 'polygon',
#                 'description': 'District and state boundaries',
#                 'endpoint': '/api/layers/boundaries',
#                 'style': {
#                     'fillColor': '#cccccc',
#                     'fillOpacity': 0.1,
#                     'color': '#666666',
#                     'weight': 1
#                 }
#             }
#         ]

#         return jsonify({
#             'status': 'success',
#             'data': layers,
#             'count': len(layers)
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500


# @layers_bp.route('/roads', methods=['GET'])
# def get_roads_layer():
#     """
#     Get roads layer as GeoJSON.

#     Query Parameters:
#         bbox (str, optional): Bounding box (minLon,minLat,maxLon,maxLat)
#         road_type (str, optional): Filter by road type
#         show_blocked (bool, optional): Include blocked roads

#     Returns:
#         JSON: GeoJSON FeatureCollection of roads
#     """
#     try:
#         bbox_str = request.args.get('bbox')

#         if bbox_str:
#             # Parse bounding box
#             bbox = [float(x) for x in bbox_str.split(',')]
#             if len(bbox) != 4:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Invalid bbox format. Use: minLon,minLat,maxLon,maxLat'
#                 }), 400

#             # Get roads in bounding box
#             geojson = get_roads_in_bbox(*bbox)
#         else:
#             # Get all roads (might be slow - should limit in production)
#             # TODO: Implement pagination or require bbox
#             geojson = {'type': 'FeatureCollection', 'features': []}

#         return jsonify({
#             'status': 'success',
#             'data': geojson
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500


# @layers_bp.route('/boundaries', methods=['GET'])
# def get_admin_boundaries():
#     """
#     Get administrative boundaries as GeoJSON.

#     Query Parameters:
#         level (int, optional): Admin level (1=Country, 2=State, 3=District)
#         bbox (str, optional): Bounding box filter

#     Returns:
#         JSON: GeoJSON FeatureCollection of boundaries
#     """
#     try:
#         level = request.args.get('level', type=int)

#         # TODO: Query database for admin boundaries

#         # Placeholder response
#         geojson = {
#             'type': 'FeatureCollection',
#             'features': []
#         }

#         return jsonify({
#             'status': 'success',
#             'data': geojson
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500


# @layers_bp.route('/cyclone-tracks', methods=['GET'])
# def get_cyclone_tracks():
#     """
#     Get cyclone track data as GeoJSON.

#     Query Parameters:
#         active_only (bool, optional): Show only active cyclones
#         forecast (bool, optional): Include forecast tracks

#     Returns:
#         JSON: GeoJSON FeatureCollection of cyclone tracks
#     """
#     try:
#         active_only = request.args.get('active_only', 'false').lower() == 'true'
#         include_forecast = request.args.get('forecast', 'true').lower() == 'true'

#         # TODO: Query database for cyclone tracks

#         # Placeholder response
#         geojson = {
#             'type': 'FeatureCollection',
#             'features': []
#         }

#         return jsonify({
#             'status': 'success',
#             'data': geojson
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500


# @layers_bp.route('/safe-zones', methods=['POST'])
# def calculate_safe_zones():
#     """
#     Calculate and return safe zones (areas not affected by disasters).

#     Request Body:
#         {
#             "buffer_distance_meters": int (optional, default: 5000)
#         }

#     Returns:
#         JSON: GeoJSON of safe zones
#     """
#     try:
#         data = request.get_json() or {}
#         buffer_distance = data.get('buffer_distance_meters', 5000)

#         # TODO: Use spatial_analysis.identify_safe_zones()

#         # Placeholder response
#         geojson = {
#             'type': 'FeatureCollection',
#             'features': []
#         }

#         return jsonify({
#             'status': 'success',
#             'data': geojson
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500


# @layers_bp.route('/heatmap', methods=['POST'])
# def generate_heatmap():
#     """
#     Generate heatmap data for disaster intensity.

#     Request Body:
#         {
#             "layer": str (e.g., "flood_severity", "population_density"),
#             "bbox": [minLon, minLat, maxLon, maxLat]
#         }

#     Returns:
#         JSON: Heatmap data points
#     """
#     try:
#         data = request.get_json()

#         if not data or 'layer' not in data:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Missing layer parameter'
#             }), 400

#         layer = data['layer']

#         # TODO: Generate heatmap data based on layer type

#         # Placeholder response
#         heatmap_data = {
#             'points': [
#                 {'lat': 20.5937, 'lon': 78.9629, 'intensity': 0.8}
#             ]
#         }

#         return jsonify({
#             'status': 'success',
#             'data': heatmap_data
#         }), 200

#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         }), 500


# # TODO: Add more layer endpoints:
# # - GET /layers/weather - Weather overlay data
# # - GET /layers/population - Population density layer
# # - GET /layers/elevation - Elevation/terrain layer
# # - POST /layers/upload - Upload custom GeoJSON layer
"""
Layers API Module
=================
API endpoints for map layers and spatial data (GeoJSON based, no DB).
"""

from flask import Blueprint, jsonify, current_app, request
from shapely.geometry import box
from backend.core.data_loader import DATA

layers_bp = Blueprint("layers", __name__)


@layers_bp.route("/", methods=["GET"])
def get_all_layers():
    """Metadata for all visible layers (no disaster_zones)."""

    layers = [
        {
            "id": "roads",
            "name": "Road Network",
            "type": "linestring",
            "endpoint": "/api/layers/roads",
        },
        {
            "id": "boundaries",
            "name": "Administrative Boundaries",
            "type": "polygon",
            "endpoint": "/api/layers/boundaries",
        }
    ]

    return jsonify({"status": "success", "data": layers}), 200


@layers_bp.route("/roads", methods=["GET"])
def get_roads_layer():
    # """Return roads from DATA as GeoJSON."""

    # roads = DATA.get("roads")
    # if roads is None:
    #     return jsonify({"status": "success", "data": {"type": "FeatureCollection", "features": []}})

    # # Optional bbox clipping
    # bbox_str = request.args.get("bbox")
    # if bbox_str:
    #     try:
    #         minx, miny, maxx, maxy = map(float, bbox_str.split(","))
    #         bbox_geom = box(minx, miny, maxx, maxy)
    #         from shapely.geometry import shape
    #         clipped = []

    #         for f in roads["features"]:
    #             geom = shape(f["geometry"])
    #             if geom.intersects(bbox_geom):
    #                 clipped.append(f)

    #         return jsonify({
    #             "status": "success",
    #             "data": {"type": "FeatureCollection", "features": clipped}
    #         })
    #     except:
    #         pass

    # return jsonify({"status": "success", "data": roads})
    return jsonify({"status": "success", "data": {"type": "FeatureCollection", "features": []}})



@layers_bp.route("/boundaries", methods=["GET"])
def get_boundaries():
    """Return administrative boundaries based on ?level="""

    level = request.args.get("level", default=2, type=int)

    key = {
        1: "state",
        2: "districts",
        3: "taluks",
        4: "villages"
    }.get(level)

    if key is None:
        return jsonify({"status": "error", "message": "Invalid level"}), 400

    layer = DATA.get(key)
    if layer is None:
        return jsonify({"status": "success", "data": {"type": "FeatureCollection", "features": []}})

    return jsonify({"status": "success", "data": layer})

