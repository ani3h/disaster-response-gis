"""
Routes API Module
=================
API endpoints for route calculation and navigation.
"""

from flask import Blueprint, jsonify, request


# Create Blueprint
routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/safe-route', methods=['POST'])
def calculate_safe_route():
    """
    Calculate a safe evacuation route avoiding disaster zones.

    Request Body:
        {
            "start": {"lat": float, "lon": float},
            "end": {"lat": float, "lon": float} (optional if route_to_safety is true),
            "avoid_disaster_zones": bool (optional, default: true),
            "hazard_types": list (optional, default: ["flood", "landslide", "cyclone"]),
            "route_to_safety": bool (optional, default: false)
        }

    Returns:
        JSON: Route information with geometry and distance
    """
    try:
        from backend.core.route_optimizer import compute_multi_hazard_safe_route, compute_safe_route_to_amenity
        from backend.core.data_loader import load_roads, load_hospitals, load_shelters

        data = request.get_json()

        # Validate request
        if not data or 'start' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing start coordinates'
            }), 400

        start = data['start']

        if 'lat' not in start or 'lon' not in start:
            return jsonify({
                'status': 'error',
                'message': 'Invalid start coordinates'
            }), 400

        avoid_disasters = data.get('avoid_disaster_zones', True)
        hazard_types = data.get('hazard_types', ['flood', 'landslide', 'cyclone'])
        route_to_safety = data.get('route_to_safety', False)

        # Load roads
        roads_gdf = load_roads()

        if roads_gdf is None or len(roads_gdf) == 0:
            return jsonify({
                'status': 'error',
                'message': 'No road data available'
            }), 500

        # Route to nearest safe amenity or specific destination
        if route_to_safety:
            # Load amenities
            hospitals_gdf = load_hospitals()
            shelters_gdf = load_shelters()

            # Combine amenities
            import geopandas as gpd
            import pandas as pd
            amenities = []
            if hospitals_gdf is not None and len(hospitals_gdf) > 0:
                amenities.append(hospitals_gdf)
            if shelters_gdf is not None and len(shelters_gdf) > 0:
                amenities.append(shelters_gdf)

            if len(amenities) == 0:
                return jsonify({
                    'status': 'error',
                    'message': 'No safe amenities available'
                }), 500

            amenities_gdf = gpd.GeoDataFrame(pd.concat(amenities, ignore_index=True))

            # Compute route to nearest safe amenity
            from backend.core.data_loader import load_landslide_layers, load_cyclone_layers, load_rivers
            from backend.core.spatial_analysis import compute_multi_hazard_zones

            hazard_gdfs = []
            if 'landslide' in hazard_types:
                landslides = load_landslide_layers()
                if landslides is not None and len(landslides) > 0:
                    hazard_gdfs.append(landslides)

            if 'cyclone' in hazard_types:
                cyclone_data = load_cyclone_layers()
                if cyclone_data.get('tracks') is not None:
                    hazard_gdfs.append(cyclone_data['tracks'])

            if 'flood' in hazard_types:
                rivers = load_rivers()
                if rivers is not None and len(rivers) > 0:
                    from backend.core.spatial_analysis import create_buffer
                    flood_zones = create_buffer(rivers, 1000)
                    flood_zones['disaster_type'] = 'flood'
                    hazard_gdfs.append(flood_zones)

            combined_hazards = compute_multi_hazard_zones(hazard_gdfs) if len(hazard_gdfs) > 0 else None

            start_point = (start['lon'], start['lat'])
            route = compute_safe_route_to_amenity(roads_gdf, start_point, amenities_gdf, combined_hazards)

        else:
            # Route to specific destination
            end = data.get('end')
            if not end or 'lat' not in end or 'lon' not in end:
                return jsonify({
                    'status': 'error',
                    'message': 'Missing or invalid end coordinates'
                }), 400

            start_point = (start['lon'], start['lat'])
            end_point = (end['lon'], end['lat'])

            if avoid_disasters:
                route = compute_multi_hazard_safe_route(roads_gdf, start_point, end_point, hazard_types)
            else:
                from backend.core.route_optimizer import build_road_network, compute_shortest_path
                graph = build_road_network(roads_gdf)
                route = compute_shortest_path(graph, start_point, end_point)

        if route is None:
            return jsonify({
                'status': 'error',
                'message': 'No route found. Try different start/end points.'
            }), 404

        # Add estimated time (rough estimate: 40 km/h average speed)
        if 'estimated_time_minutes' not in route:
            route['estimated_time_minutes'] = int((route.get('total_distance_km', 0) / 40) * 60)

        return jsonify({
            'status': 'success',
            'data': route
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@routes_bp.route('/alternative-routes', methods=['POST'])
def get_alternative_routes():
    """
    Get multiple alternative routes between two points.

    Request Body:
        {
            "start": {"lat": float, "lon": float},
            "end": {"lat": float, "lon": float},
            "num_routes": int (optional, default: 3)
        }

    Returns:
        JSON: List of alternative routes
    """
    try:
        data = request.get_json()

        if not data or 'start' not in data or 'end' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing start or end coordinates'
            }), 400

        start = data['start']
        end = data['end']
        num_routes = data.get('num_routes', 3)

        # TODO: Use route_optimizer.find_alternative_routes()

        # Placeholder response
        routes = [
            {
                'route_number': 1,
                'total_distance_km': 15.3,
                'estimated_time_minutes': 25,
                'safety_score': 85.5
            },
            {
                'route_number': 2,
                'total_distance_km': 17.8,
                'estimated_time_minutes': 30,
                'safety_score': 92.0
            }
        ]

        return jsonify({
            'status': 'success',
            'data': routes,
            'count': len(routes)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@routes_bp.route('/distance', methods=['POST'])
def calculate_distance():
    """
    Calculate distance between two points.

    Request Body:
        {
            "point1": {"lat": float, "lon": float},
            "point2": {"lat": float, "lon": float}
        }

    Returns:
        JSON: Distance in meters and kilometers
    """
    try:
        data = request.get_json()

        if not data or 'point1' not in data or 'point2' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing point1 or point2'
            }), 400

        point1 = data['point1']
        point2 = data['point2']

        # TODO: Use spatial_analysis.calculate_distance()

        # Placeholder calculation (Haversine formula would be more accurate)
        import math

        lat1, lon1 = point1['lat'], point1['lon']
        lat2, lon2 = point2['lat'], point2['lon']

        # Simple approximation
        dlat = abs(lat2 - lat1) * 111000  # meters
        dlon = abs(lon2 - lon1) * 111000 * math.cos(math.radians((lat1 + lat2) / 2))
        distance_meters = math.sqrt(dlat**2 + dlon**2)

        return jsonify({
            'status': 'success',
            'data': {
                'distance_meters': round(distance_meters, 2),
                'distance_km': round(distance_meters / 1000, 2)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@routes_bp.route('/nearest-road', methods=['POST'])
def find_nearest_road():
    """
    Find the nearest road to a given point.

    Request Body:
        {
            "latitude": float,
            "longitude": float
        }

    Returns:
        JSON: Nearest road information
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

        # TODO: Query PostGIS for nearest road

        # Placeholder response
        road = {
            'id': 1,
            'name': 'Main Street',
            'road_type': 'primary',
            'distance_meters': 45.2,
            'is_blocked': False
        }

        return jsonify({
            'status': 'success',
            'data': road
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# TODO: Add more routing endpoints:
# - POST /optimize-multi-destination - Multi-destination routing
# - GET /road-closures - Get current road closures
# - POST /travel-time - Calculate travel time with traffic
# - POST /evacuation-plan - Generate evacuation plan for area
