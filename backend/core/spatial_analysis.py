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
import logging
import config

logger = logging.getLogger(__name__)


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
        logger.info(f"Creating {distance_meters}m buffer...")

        # Convert to projected CRS for accurate distance calculation
        # Using UTM or local projection would be better, but for simplicity using Web Mercator
        gdf_projected = gdf.to_crs(epsg=3857)

        # Create buffer
        buffered = gdf_projected.copy()
        buffered['geometry'] = gdf_projected.geometry.buffer(distance_meters)

        # Convert back to WGS84
        buffered = buffered.to_crs(epsg=config.DEFAULT_SRID)

        logger.info(f"Buffer created for {len(buffered)} features")
        return buffered

    except Exception as e:
        logger.error(f"Error creating buffer: {e}")
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
        logger.error(f"Error calculating distance: {e}")
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

        logger.info(f"Found {len(within)} points within {distance_meters}m")
        return within

    except Exception as e:
        logger.error(f"Error finding points within distance: {e}")
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
        logger.info("Calculating spatial intersection...")

        # Ensure same CRS
        if gdf1.crs != gdf2.crs:
            gdf2 = gdf2.to_crs(gdf1.crs)

        # Perform intersection
        intersection = gpd.overlay(gdf1, gdf2, how='intersection')

        logger.info(f"Found {len(intersection)} intersecting features")
        return intersection

    except Exception as e:
        logger.error(f"Error calculating intersection: {e}")
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
        logger.info("Calculating spatial difference...")

        # Ensure same CRS
        if gdf1.crs != gdf2.crs:
            gdf2 = gdf2.to_crs(gdf1.crs)

        # Perform difference
        difference = gpd.overlay(gdf1, gdf2, how='difference')

        logger.info(f"Difference contains {len(difference)} features")
        return difference

    except Exception as e:
        logger.error(f"Error calculating difference: {e}")
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
        logger.info("Identifying safe zones...")

        # Create buffer around disaster zones
        disaster_buffered = create_buffer(disaster_zones_gdf, buffer_distance)

        # Calculate difference (safe zones = boundary - disaster zones)
        safe_zones = spatial_difference(boundary_gdf, disaster_buffered)

        logger.info(f"Identified {len(safe_zones)} safe zones")
        return safe_zones

    except Exception as e:
        logger.error(f"Error identifying safe zones: {e}")
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

        logger.info(f"Calculated area for {len(gdf)} features")
        return gdf

    except Exception as e:
        logger.error(f"Error calculating area: {e}")
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

        logger.info(f"Calculated centroids for {len(centroids)} features")
        return centroids

    except Exception as e:
        logger.error(f"Error calculating centroids: {e}")
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
        logger.info(f"Merged {len(gdf)} geometries into one")
        return merged

    except Exception as e:
        logger.error(f"Error merging geometries: {e}")
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
        logger.info("Performing point-in-polygon spatial join...")

        # Ensure same CRS
        if point_gdf.crs != polygon_gdf.crs:
            polygon_gdf = polygon_gdf.to_crs(point_gdf.crs)

        # Spatial join
        joined = gpd.sjoin(point_gdf, polygon_gdf, how='left', predicate='within')

        logger.info(f"Joined {len(joined)} points with polygons")
        return joined

    except Exception as e:
        logger.error(f"Error in point-in-polygon: {e}")
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

        logger.info(f"Impact zone affects {len(affected_areas)} administrative areas")
        return result

    except Exception as e:
        logger.error(f"Error calculating impact zone: {e}")
        return {}


# TODO: Add more spatial analysis functions:
# - nearest_neighbor_analysis()
# - density_analysis()
# - convex_hull()
# - simplify_geometry()
# - interpolate_points_on_line()
