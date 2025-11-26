"""
Spatial Analysis Module
========================
Core spatial analysis functions using Shapely and GeoPandas.
Includes buffer, intersection, distance, overlay operations.
"""

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
import numpy as np
import config



def create_buffer(gdf, distance_meters):
    """
    Create buffer zones around geometries.

    Args:
        gdf (GeoDataFrame): Input geometries
        distance_meters (float): Buffer distance in meters

    Returns:
        GeoDataFrame: Buffered geometries
    """
    try:

        # Convert to projected CRS for accurate distance calculation
        # Using UTM or local projection would be better, but for simplicity using Web Mercator
        gdf_projected = gdf.to_crs(epsg=3857)

        # Create buffer
        buffered = gdf_projected.copy()
        buffered['geometry'] = gdf_projected.geometry.buffer(distance_meters)

        # Convert back to WGS84
        buffered = buffered.to_crs(epsg=config.DEFAULT_SRID)

        return buffered

    except Exception as e:
        return gdf


def calculate_distance(point1, point2):
    """
    Calculate distance between two points in meters.

    Args:
        point1 (tuple): (lon, lat) of first point
        point2 (tuple): (lon, lat) of second point

    Returns:
        float: Distance in meters
    """
    try:
        # Create Point geometries
        p1 = Point(point1)
        p2 = Point(point2)

        # Create GeoDataFrame for accurate geodesic distance
        gdf = gpd.GeoDataFrame(
            geometry=[p1, p2],
            crs=f"EPSG:{config.DEFAULT_SRID}"
        )

        # Convert to projected CRS
        gdf_proj = gdf.to_crs(epsg=3857)

        # Calculate distance
        distance = gdf_proj.iloc[0].geometry.distance(gdf_proj.iloc[1].geometry)

        return distance

    except Exception as e:
        return None


def find_points_within_distance(points_gdf, target_point, distance_meters):
    """
    Find all points within a specified distance from a target point.

    Args:
        points_gdf (GeoDataFrame): GeoDataFrame of points to search
        target_point (tuple): (lon, lat) of target point
        distance_meters (float): Search radius in meters

    Returns:
        GeoDataFrame: Points within distance
    """
    try:
        # Create target point geometry
        target = gpd.GeoDataFrame(
            geometry=[Point(target_point)],
            crs=f"EPSG:{config.DEFAULT_SRID}"
        )

        # Create buffer around target
        target_buffered = create_buffer(target, distance_meters)

        # Find intersection
        within = points_gdf[points_gdf.geometry.within(target_buffered.iloc[0].geometry)]

        return within

    except Exception as e:
        return gpd.GeoDataFrame()


def spatial_intersection(gdf1, gdf2):
    """
    Find intersection between two GeoDataFrames.

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame
        gdf2 (GeoDataFrame): Second GeoDataFrame

    Returns:
        GeoDataFrame: Intersecting features
    """
    try:

        # Ensure same CRS
        if gdf1.crs != gdf2.crs:
            gdf2 = gdf2.to_crs(gdf1.crs)

        # Perform intersection
        intersection = gpd.overlay(gdf1, gdf2, how='intersection')

        return intersection

    except Exception as e:
        return gpd.GeoDataFrame()


def spatial_difference(gdf1, gdf2):
    """
    Calculate spatial difference (areas in gdf1 not in gdf2).

    Args:
        gdf1 (GeoDataFrame): First GeoDataFrame
        gdf2 (GeoDataFrame): Second GeoDataFrame (to subtract)

    Returns:
        GeoDataFrame: Difference features
    """
    try:

        # Ensure same CRS
        if gdf1.crs != gdf2.crs:
            gdf2 = gdf2.to_crs(gdf1.crs)

        # Perform difference
        difference = gpd.overlay(gdf1, gdf2, how='difference')

        return difference

    except Exception as e:
        return gdf1


def identify_safe_zones(boundary_gdf, disaster_zones_gdf, buffer_distance=5000):
    """
    Identify safe zones by subtracting disaster zones (with buffer) from boundaries.

    Args:
        boundary_gdf (GeoDataFrame): Administrative boundaries
        disaster_zones_gdf (GeoDataFrame): Active disaster zones
        buffer_distance (float): Safety buffer in meters

    Returns:
        GeoDataFrame: Safe zones
    """
    try:

        # Create buffer around disaster zones
        disaster_buffered = create_buffer(disaster_zones_gdf, buffer_distance)

        # Calculate difference (safe zones = boundary - disaster zones)
        safe_zones = spatial_difference(boundary_gdf, disaster_buffered)

        return safe_zones

    except Exception as e:
        return boundary_gdf


def calculate_area(gdf):
    """
    Calculate area of geometries in square kilometers.

    Args:
        gdf (GeoDataFrame): Input geometries

    Returns:
        GeoDataFrame: Input with added 'area_sqkm' column
    """
    try:
        # Convert to projected CRS for area calculation
        gdf_proj = gdf.to_crs(epsg=3857)

        # Calculate area in square meters, convert to square kilometers
        gdf['area_sqkm'] = gdf_proj.geometry.area / 1_000_000

        return gdf

    except Exception as e:
        return gdf


def calculate_centroid(gdf):
    """
    Calculate centroids of geometries.

    Args:
        gdf (GeoDataFrame): Input geometries

    Returns:
        GeoDataFrame: Centroids as Point geometries
    """
    try:
        centroids = gdf.copy()
        centroids['geometry'] = gdf.geometry.centroid

        return centroids

    except Exception as e:
        return gdf


def merge_geometries(gdf):
    """
    Merge all geometries in a GeoDataFrame into a single geometry.

    Args:
        gdf (GeoDataFrame): Input geometries

    Returns:
        Shapely geometry: Merged geometry
    """
    try:
        merged = unary_union(gdf.geometry)
        return merged

    except Exception as e:
        return None


def point_in_polygon(point_gdf, polygon_gdf):
    """
    Check which points fall within polygons.

    Args:
        point_gdf (GeoDataFrame): Points to check
        polygon_gdf (GeoDataFrame): Polygons to check against

    Returns:
        GeoDataFrame: Points with polygon attributes joined
    """
    try:

        # Ensure same CRS
        if point_gdf.crs != polygon_gdf.crs:
            polygon_gdf = polygon_gdf.to_crs(point_gdf.crs)

        # Spatial join
        joined = gpd.sjoin(point_gdf, polygon_gdf, how='left', predicate='within')

        return joined

    except Exception as e:
        return point_gdf


def calculate_impact_zone(disaster_center, radius_meters, admin_boundaries_gdf):
    """
    Calculate disaster impact zone and affected administrative areas.

    Args:
        disaster_center (tuple): (lon, lat) of disaster center
        radius_meters (float): Impact radius in meters
        admin_boundaries_gdf (GeoDataFrame): Administrative boundaries

    Returns:
        dict: Impact zone info with affected areas
    """
    try:
        # Create impact zone circle
        center_point = gpd.GeoDataFrame(
            geometry=[Point(disaster_center)],
            crs=f"EPSG:{config.DEFAULT_SRID}"
        )

        impact_zone = create_buffer(center_point, radius_meters)

        # Find intersecting administrative areas
        affected_areas = spatial_intersection(admin_boundaries_gdf, impact_zone)

        # Calculate statistics
        result = {
            'impact_zone_area_sqkm': impact_zone.geometry.area.sum() / 1_000_000,
            'affected_areas_count': len(affected_areas),
            'affected_areas': affected_areas.to_dict('records') if len(affected_areas) > 0 else []
        }

        return result

    except Exception as e:
        return {}


def compute_landslide_zones():
    """
    Compute landslide hazard zones from loaded landslide data.

    Returns:
        dict: GeoJSON FeatureCollection of landslide zones
    """
    try:
        from backend.core.data_loader import load_landslide_layers

        landslides_gdf = load_landslide_layers()

        if landslides_gdf is None or len(landslides_gdf) == 0:
            return {'type': 'FeatureCollection', 'features': []}

        # Ensure valid geometries
        landslides_gdf = validate_geometry(landslides_gdf)

        # Create buffer around landslide zones for safety (500m)
        landslide_zones = create_buffer(landslides_gdf, 500)

        # Add severity information if not present
        if 'severity' not in landslide_zones.columns:
            landslide_zones['severity'] = 'high'

        # Add hazard type
        landslide_zones['disaster_type'] = 'landslide'

        # Convert to GeoJSON
        from backend.core.data_loader import convert_to_geojson
        geojson = convert_to_geojson(landslide_zones)

        return geojson

    except Exception as e:
        return {'type': 'FeatureCollection', 'features': []}


def compute_cyclone_zones():
    """
    Compute cyclone impact zones from loaded cyclone track data.

    Returns:
        dict: GeoJSON FeatureCollection of cyclone zones
    """
    try:
        from backend.core.data_loader import load_cyclone_layers

        cyclone_data = load_cyclone_layers()

        if cyclone_data is None or (cyclone_data.get('tracks') is None and cyclone_data.get('points') is None):
            return {'type': 'FeatureCollection', 'features': []}

        # Prioritize tracks over points
        if cyclone_data.get('tracks') is not None:
            cyclone_gdf = cyclone_data['tracks']
        else:
            cyclone_gdf = cyclone_data['points']

        # Ensure valid geometries
        cyclone_gdf = validate_geometry(cyclone_gdf)

        # Create buffer around cyclone tracks/points for impact zone (50km)
        cyclone_zones = create_buffer(cyclone_gdf, 50000)

        # Add severity information based on cyclone properties if available
        if 'severity' not in cyclone_zones.columns:
            # Check for wind speed or category fields
            if 'USA_WIND' in cyclone_zones.columns:
                # Categorize by wind speed (knots)
                cyclone_zones['severity'] = cyclone_zones['USA_WIND'].apply(
                    lambda x: 'critical' if x > 100 else ('high' if x > 64 else 'medium')
                )
            else:
                cyclone_zones['severity'] = 'high'

        # Add hazard type
        cyclone_zones['disaster_type'] = 'cyclone'

        # Convert to GeoJSON
        from backend.core.data_loader import convert_to_geojson
        geojson = convert_to_geojson(cyclone_zones)

        return geojson

    except Exception as e:
        return {'type': 'FeatureCollection', 'features': []}


def compute_flood_zones(rivers_gdf, buffer_distance=1000):
    """
    Compute flood hazard zones from river data.

    Args:
        rivers_gdf (GeoDataFrame): Rivers GeoDataFrame
        buffer_distance (float): Buffer distance in meters

    Returns:
        dict: GeoJSON FeatureCollection of flood zones
    """
    try:
        if rivers_gdf is None or len(rivers_gdf) == 0:
            return {'type': 'FeatureCollection', 'features': []}

        # Ensure valid geometries
        rivers_gdf = validate_geometry(rivers_gdf)

        # Create buffer around rivers for flood zones
        flood_zones = create_buffer(rivers_gdf, buffer_distance)

        # Add severity information
        if 'severity' not in flood_zones.columns:
            flood_zones['severity'] = 'medium'

        # Add hazard type
        flood_zones['disaster_type'] = 'flood'

        # Convert to GeoJSON
        from backend.core.data_loader import convert_to_geojson
        geojson = convert_to_geojson(flood_zones)

        return geojson

    except Exception as e:
        return {'type': 'FeatureCollection', 'features': []}


def compute_multi_hazard_zones(hazard_gdfs_list):
    """
    Compute combined multi-hazard zones from multiple hazard layers.

    Args:
        hazard_gdfs_list (list): List of hazard GeoDataFrames

    Returns:
        GeoDataFrame: Combined multi-hazard zones
    """
    try:
        valid_gdfs = [gdf for gdf in hazard_gdfs_list if gdf is not None and len(gdf) > 0]

        if len(valid_gdfs) == 0:
            return gpd.GeoDataFrame()

        # Merge all hazard GeoDataFrames
        combined_hazards = gpd.GeoDataFrame(
            pd.concat(valid_gdfs, ignore_index=True),
            crs=f"EPSG:{config.DEFAULT_SRID}"
        )

        # Dissolve overlapping polygons
        combined_hazards = combined_hazards.dissolve(by='disaster_type', aggfunc='first')
        combined_hazards = combined_hazards.reset_index()

        return combined_hazards

    except Exception as e:
        return gpd.GeoDataFrame()


def identify_affected_buildings(buildings_gdf, hazard_zones_gdf):
    """
    Identify buildings affected by disaster zones.

    Args:
        buildings_gdf (GeoDataFrame): Buildings layer
        hazard_zones_gdf (GeoDataFrame): Hazard zones

    Returns:
        GeoDataFrame: Affected buildings with hazard information
    """
    try:
        if buildings_gdf is None or hazard_zones_gdf is None:
            return gpd.GeoDataFrame()

        # Ensure same CRS
        if buildings_gdf.crs != hazard_zones_gdf.crs:
            hazard_zones_gdf = hazard_zones_gdf.to_crs(buildings_gdf.crs)

        # Spatial join to find affected buildings
        affected_buildings = gpd.sjoin(
            buildings_gdf,
            hazard_zones_gdf,
            how='inner',
            predicate='within'
        )

        return affected_buildings

    except Exception as e:
        return gpd.GeoDataFrame()


def find_safe_amenities(amenities_gdf, hazard_zones_gdf, buffer_distance=5000):
    """
    Find safe amenities (hospitals, shelters) outside hazard zones.

    Args:
        amenities_gdf (GeoDataFrame): Amenities (hospitals, shelters)
        hazard_zones_gdf (GeoDataFrame): Hazard zones
        buffer_distance (float): Safety buffer in meters

    Returns:
        GeoDataFrame: Safe amenities
    """
    try:
        if amenities_gdf is None or len(amenities_gdf) == 0:
            return amenities_gdf

        if hazard_zones_gdf is None or len(hazard_zones_gdf) == 0:
            return amenities_gdf

        # Ensure same CRS
        if amenities_gdf.crs != hazard_zones_gdf.crs:
            hazard_zones_gdf = hazard_zones_gdf.to_crs(amenities_gdf.crs)

        # Create buffer around hazard zones
        buffered_hazards = create_buffer(hazard_zones_gdf, buffer_distance)

        # Find amenities outside buffered hazard zones
        safe_amenities = amenities_gdf.copy()

        # Spatial difference - keep only amenities not within hazard zones
        for idx, amenity in safe_amenities.iterrows():
            is_safe = True
            for _, hazard in buffered_hazards.iterrows():
                if amenity.geometry.within(hazard.geometry):
                    is_safe = False
                    break

            if not is_safe:
                safe_amenities = safe_amenities.drop(idx)

        return safe_amenities

    except Exception as e:
        return amenities_gdf


# TODO: Add more spatial analysis functions:
# - nearest_neighbor_analysis()
# - density_analysis()
# - convex_hull()
# - simplify_geometry()
# - interpolate_points_on_line()
