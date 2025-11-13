"""
PostGIS Query Functions
=======================
Reusable PostGIS spatial query functions for common operations.
All queries return GeoJSON-compatible results.
"""

from sqlalchemy import text
from backend.db.db_connection import engine



def find_nearest_facilities(lat, lon, facility_table, limit=5, max_distance_km=50):
    """
    Find nearest facilities (hospitals/shelters) to a given point.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        facility_table (str): Table name ('hospitals' or 'shelters')
        limit (int): Maximum number of results
        max_distance_km (float): Maximum search radius in kilometers

    Returns:
        list: List of facilities with distances
    """
    query = text(f"""
        SELECT
            id,
            name,
            address,
            capacity,
            ST_AsGeoJSON(geom)::json as geometry,
            ST_Distance(
                geom,
                ST_SetSRID(ST_Point(:lon, :lat), 4326)::geography
            ) as distance_meters
        FROM {facility_table}
        WHERE ST_DWithin(
            geom,
            ST_SetSRID(ST_Point(:lon, :lat), 4326)::geography,
            :max_distance
        )
        ORDER BY distance_meters
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                'lat': lat,
                'lon': lon,
                'max_distance': max_distance_km * 1000,  # Convert to meters
                'limit': limit
            })

            facilities = []
            for row in result:
                facilities.append({
                    'id': row.id,
                    'name': row.name,
                    'address': row.address,
                    'capacity': row.capacity,
                    'geometry': row.geometry,
                    'distance_meters': round(row.distance_meters, 2),
                    'distance_km': round(row.distance_meters / 1000, 2)
                })

            return facilities

    except Exception as e:
        return []


def check_point_in_disaster_zone(lat, lon):
    """
    Check if a point is within any active disaster zone.

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Disaster zone info if point is in disaster area, None otherwise
    """
    query = text("""
        SELECT
            id,
            name,
            severity,
            status,
            ST_AsGeoJSON(geom)::json as geometry
        FROM flood_zones
        WHERE status = 'active'
        AND ST_Intersects(
            geom,
            ST_SetSRID(ST_Point(:lon, :lat), 4326)::geography
        )
        LIMIT 1
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {'lat': lat, 'lon': lon})
            row = result.fetchone()

            if row:
                return {
                    'id': row.id,
                    'name': row.name,
                    'severity': row.severity,
                    'status': row.status,
                    'geometry': row.geometry,
                    'in_danger': True
                }
            else:
                return {'in_danger': False}

    except Exception as e:
        return {'in_danger': False, 'error': str(e)}


def get_disaster_zones_geojson():
    """
    Get all active disaster zones as GeoJSON FeatureCollection.

    Returns:
        dict: GeoJSON FeatureCollection
    """
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
        ) as geojson
        FROM (
            SELECT
                id,
                name,
                severity,
                status,
                water_level,
                affected_population,
                geom
            FROM flood_zones
            WHERE status = 'active'
        ) as t
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            row = result.fetchone()

            if row and row.geojson:
                return row.geojson
            else:
                return {'type': 'FeatureCollection', 'features': []}

    except Exception as e:
        return {'type': 'FeatureCollection', 'features': []}


def get_roads_in_bbox(min_lon, min_lat, max_lon, max_lat):
    """
    Get all roads within a bounding box.

    Args:
        min_lon, min_lat, max_lon, max_lat: Bounding box coordinates

    Returns:
        dict: GeoJSON FeatureCollection of roads
    """
    query = text("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
        ) as geojson
        FROM (
            SELECT
                id,
                name,
                road_type,
                is_blocked,
                condition,
                geom
            FROM roads
            WHERE ST_Intersects(
                geom,
                ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)::geography
            )
        ) as t
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                'min_lon': min_lon,
                'min_lat': min_lat,
                'max_lon': max_lon,
                'max_lat': max_lat
            })
            row = result.fetchone()

            if row and row.geojson:
                return row.geojson
            else:
                return {'type': 'FeatureCollection', 'features': []}

    except Exception as e:
        return {'type': 'FeatureCollection', 'features': []}


def create_buffer_zone(geom_wkt, buffer_distance_meters):
    """
    Create a buffer zone around a geometry.

    Args:
        geom_wkt (str): WKT representation of geometry
        buffer_distance_meters (float): Buffer distance in meters

    Returns:
        dict: GeoJSON of buffered geometry
    """
    query = text("""
        SELECT ST_AsGeoJSON(
            ST_Buffer(
                ST_GeomFromText(:geom_wkt, 4326)::geography,
                :buffer_distance
            )
        )::json as geometry
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                'geom_wkt': geom_wkt,
                'buffer_distance': buffer_distance_meters
            })
            row = result.fetchone()

            return row.geometry if row else None

    except Exception as e:
        return None


def calculate_affected_population(disaster_geom_wkt):
    """
    Calculate total population affected by a disaster zone.

    Args:
        disaster_geom_wkt (str): WKT representation of disaster area

    Returns:
        int: Estimated affected population
    """
    query = text("""
        SELECT COALESCE(SUM(population), 0) as total_population
        FROM admin_boundaries
        WHERE ST_Intersects(
            geom,
            ST_GeomFromText(:geom_wkt, 4326)::geography
        )
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {'geom_wkt': disaster_geom_wkt})
            row = result.fetchone()

            return row.total_population if row else 0

    except Exception as e:
        return 0


# TODO: Add more spatial query functions:
# - find_safe_zones()
# - get_evacuation_routes()
# - calculate_disaster_impact()
# - find_blocked_roads()
# - get_shelter_capacity()
