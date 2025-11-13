"""
Data Loader Module
==================
Functions to load GeoJSON, Shapefiles, and PostGIS layers using GeoPandas.
Handles data import, validation, and transformation.
"""

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
import json
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)


def load_geojson(file_path):
    """
    Load a GeoJSON file into a GeoDataFrame.

    Args:
        file_path (str): Path to GeoJSON file

    Returns:
        GeoDataFrame: Loaded spatial data
    """
    try:
        logger.info(f"Loading GeoJSON from: {file_path}")
        gdf = gpd.read_file(file_path)

        # Ensure CRS is WGS84 (EPSG:4326)
        if gdf.crs is None:
            logger.warning("No CRS found, assuming EPSG:4326")
            gdf = gdf.set_crs(epsg=config.DEFAULT_SRID)
        elif gdf.crs.to_epsg() != config.DEFAULT_SRID:
            logger.info(f"Reprojecting from {gdf.crs} to EPSG:{config.DEFAULT_SRID}")
            gdf = gdf.to_crs(epsg=config.DEFAULT_SRID)

        logger.info(f"Loaded {len(gdf)} features")
        return gdf

    except Exception as e:
        logger.error(f"Error loading GeoJSON: {e}")
        return None


def load_shapefile(file_path):
    """
    Load a Shapefile into a GeoDataFrame.

    Args:
        file_path (str): Path to shapefile (.shp)

    Returns:
        GeoDataFrame: Loaded spatial data
    """
    try:
        logger.info(f"Loading Shapefile from: {file_path}")
        gdf = gpd.read_file(file_path)

        # Ensure CRS is WGS84
        if gdf.crs.to_epsg() != config.DEFAULT_SRID:
            logger.info(f"Reprojecting from {gdf.crs} to EPSG:{config.DEFAULT_SRID}")
            gdf = gdf.to_crs(epsg=config.DEFAULT_SRID)

        logger.info(f"Loaded {len(gdf)} features from shapefile")
        return gdf

    except Exception as e:
        logger.error(f"Error loading shapefile: {e}")
        return None


def load_from_postgis(table_name, connection_string=None):
    """
    Load a spatial table from PostGIS database.

    Args:
        table_name (str): Name of the PostGIS table
        connection_string (str, optional): Database connection string

    Returns:
        GeoDataFrame: Loaded spatial data
    """
    try:
        conn_str = connection_string or config.DATABASE_URI
        logger.info(f"Loading table '{table_name}' from PostGIS")

        # Load entire table
        gdf = gpd.read_postgis(
            f"SELECT * FROM {table_name}",
            conn_str,
            geom_col='geom'
        )

        logger.info(f"Loaded {len(gdf)} features from {table_name}")
        return gdf

    except Exception as e:
        logger.error(f"Error loading from PostGIS: {e}")
        return None


def load_from_postgis_query(sql_query, connection_string=None, geom_col='geom'):
    """
    Load spatial data from PostGIS using a custom SQL query.

    Args:
        sql_query (str): SQL query to execute
        connection_string (str, optional): Database connection string
        geom_col (str): Name of the geometry column

    Returns:
        GeoDataFrame: Query results as GeoDataFrame
    """
    try:
        conn_str = connection_string or config.DATABASE_URI
        logger.info("Executing custom PostGIS query")

        gdf = gpd.read_postgis(
            sql_query,
            conn_str,
            geom_col=geom_col
        )

        logger.info(f"Query returned {len(gdf)} features")
        return gdf

    except Exception as e:
        logger.error(f"Error executing PostGIS query: {e}")
        return None


def save_to_postgis(gdf, table_name, if_exists='replace', connection_string=None):
    """
    Save a GeoDataFrame to PostGIS database.

    Args:
        gdf (GeoDataFrame): Data to save
        table_name (str): Target table name
        if_exists (str): How to behave if table exists ('fail', 'replace', 'append')
        connection_string (str, optional): Database connection string

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn_str = connection_string or config.DATABASE_URI
        logger.info(f"Saving {len(gdf)} features to {table_name}")

        # Ensure CRS is correct
        if gdf.crs.to_epsg() != config.DEFAULT_SRID:
            gdf = gdf.to_crs(epsg=config.DEFAULT_SRID)

        # Save to PostGIS
        gdf.to_postgis(
            name=table_name,
            con=conn_str,
            if_exists=if_exists,
            index=False
        )

        logger.info(f"Successfully saved data to {table_name}")
        return True

    except Exception as e:
        logger.error(f"Error saving to PostGIS: {e}")
        return False


def convert_to_geojson(gdf):
    """
    Convert a GeoDataFrame to GeoJSON format.

    Args:
        gdf (GeoDataFrame): GeoDataFrame to convert

    Returns:
        dict: GeoJSON FeatureCollection
    """
    try:
        # Convert to GeoJSON
        geojson = json.loads(gdf.to_json())
        logger.info(f"Converted {len(geojson['features'])} features to GeoJSON")
        return geojson

    except Exception as e:
        logger.error(f"Error converting to GeoJSON: {e}")
        return {'type': 'FeatureCollection', 'features': []}


def create_points_from_csv(csv_path, lat_col='latitude', lon_col='longitude'):
    """
    Create a GeoDataFrame from a CSV file with lat/lon columns.

    Args:
        csv_path (str): Path to CSV file
        lat_col (str): Name of latitude column
        lon_col (str): Name of longitude column

    Returns:
        GeoDataFrame: Spatial data with point geometries
    """
    try:
        logger.info(f"Loading CSV from: {csv_path}")

        # Load CSV
        df = pd.read_csv(csv_path)

        # Create geometry from lat/lon
        geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=f"EPSG:{config.DEFAULT_SRID}")

        logger.info(f"Created {len(gdf)} point features from CSV")
        return gdf

    except Exception as e:
        logger.error(f"Error creating points from CSV: {e}")
        return None


def validate_geometry(gdf):
    """
    Validate geometries in a GeoDataFrame and fix if possible.

    Args:
        gdf (GeoDataFrame): GeoDataFrame to validate

    Returns:
        GeoDataFrame: Validated GeoDataFrame
    """
    try:
        logger.info("Validating geometries...")

        # Check for invalid geometries
        invalid = ~gdf.geometry.is_valid
        invalid_count = invalid.sum()

        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} invalid geometries, attempting to fix...")

            # Try to fix invalid geometries
            gdf.loc[invalid, 'geometry'] = gdf.loc[invalid, 'geometry'].buffer(0)

            # Check again
            still_invalid = ~gdf.geometry.is_valid
            if still_invalid.sum() > 0:
                logger.error(f"{still_invalid.sum()} geometries could not be fixed")
            else:
                logger.info("All geometries fixed successfully")

        logger.info("Geometry validation complete")
        return gdf

    except Exception as e:
        logger.error(f"Error validating geometries: {e}")
        return gdf


def filter_by_bbox(gdf, min_lon, min_lat, max_lon, max_lat):
    """
    Filter a GeoDataFrame by bounding box.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame
        min_lon, min_lat, max_lon, max_lat: Bounding box coordinates

    Returns:
        GeoDataFrame: Filtered data
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        filtered = gdf.cx[min_lon:max_lon, min_lat:max_lat]

        logger.info(f"Filtered from {len(gdf)} to {len(filtered)} features")
        return filtered

    except Exception as e:
        logger.error(f"Error filtering by bbox: {e}")
        return gdf


# TODO: Add more data loading functions:
# - load_from_wfs() - Load from Web Feature Service
# - load_from_api() - Load from REST API
# - batch_load_files() - Load multiple files
# - merge_datasets() - Merge multiple GeoDataFrames
