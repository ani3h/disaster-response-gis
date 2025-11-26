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
from pathlib import Path
import config



def load_geojson(file_path):
    """
    Load a GeoJSON file into a GeoDataFrame.

    Args:
        file_path (str): Path to GeoJSON file

    Returns:
        GeoDataFrame: Loaded spatial data
    """
    try:
        gdf = gpd.read_file(file_path)

        # Ensure CRS is WGS84 (EPSG:4326)
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=config.DEFAULT_SRID)
        elif gdf.crs.to_epsg() != config.DEFAULT_SRID:
            gdf = gdf.to_crs(epsg=config.DEFAULT_SRID)

        return gdf

    except Exception as e:
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
        gdf = gpd.read_file(file_path)

        # Ensure CRS is WGS84
        if gdf.crs.to_epsg() != config.DEFAULT_SRID:
            gdf = gdf.to_crs(epsg=config.DEFAULT_SRID)

        return gdf

    except Exception as e:
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

        # Load entire table
        gdf = gpd.read_postgis(
            f"SELECT * FROM {table_name}",
            conn_str,
            geom_col='geom'
        )

        return gdf

    except Exception as e:
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

        gdf = gpd.read_postgis(
            sql_query,
            conn_str,
            geom_col=geom_col
        )

        return gdf

    except Exception as e:
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

        return True

    except Exception as e:
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
        return geojson

    except Exception as e:
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

        # Load CSV
        df = pd.read_csv(csv_path)

        # Create geometry from lat/lon
        geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=f"EPSG:{config.DEFAULT_SRID}")

        return gdf

    except Exception as e:
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

        # Check for invalid geometries
        invalid = ~gdf.geometry.is_valid
        invalid_count = invalid.sum()

        if invalid_count > 0:

            # Try to fix invalid geometries
            gdf.loc[invalid, 'geometry'] = gdf.loc[invalid, 'geometry'].buffer(0)

            # Check again
            still_invalid = ~gdf.geometry.is_valid
            if still_invalid.sum() > 0:
            else:

        return gdf

    except Exception as e:
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

        return filtered

    except Exception as e:
        return gdf


def load_boundary_layers():
    """
    Load Kerala boundary layers from processed data directory.

    Returns:
        dict: Dictionary of boundary GeoDataFrames
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)

        boundaries = {}

        # Load main boundary
        boundary_file = base_path / "kerala_boundary_fixed.geojson"
        if boundary_file.exists():
            boundaries['main'] = load_geojson(str(boundary_file))

        # Load district boundaries
        district_file = base_path / "kerala_district_fixed.geojson"
        if district_file.exists():
            boundaries['districts'] = load_geojson(str(district_file))

        # Load state boundaries
        state_file = base_path / "kerala_state_fixed.geojson"
        if state_file.exists():
            boundaries['state'] = load_geojson(str(state_file))

        # Load taluk boundaries
        taluk_file = base_path / "kerala_taluk_fixed.geojson"
        if taluk_file.exists():
            boundaries['taluks'] = load_geojson(str(taluk_file))

        # Load village boundaries
        village_file = base_path / "kerala_village_fixed.geojson"
        if village_file.exists():
            boundaries['villages'] = load_geojson(str(village_file))

        return boundaries

    except Exception as e:
        return {}


def load_buildings():
    """
    Load Kerala buildings layer from processed data directory.

    Returns:
        GeoDataFrame: Buildings GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        buildings_file = base_path / "kerala_buildings_fixed.geojson"

        if buildings_file.exists():
            return load_geojson(str(buildings_file))

        return None

    except Exception as e:
        return None


def load_coastline():
    """
    Load Kerala coastline layers from processed data directory.

    Returns:
        dict: Dictionary of coastline GeoDataFrames
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)

        coastlines = {}

        # Load main coastline
        coastline_file = base_path / "kerala_coastline_fixed.geojson"
        if coastline_file.exists():
            coastlines['main'] = load_geojson(str(coastline_file))

        # Load coastline area
        coastline_area_file = base_path / "kerala_coastline_area_fixed.geojson"
        if coastline_area_file.exists():
            coastlines['area'] = load_geojson(str(coastline_area_file))

        # Load coastline lines
        coastline_lines_file = base_path / "kerala_coastline_lines_fixed.geojson"
        if coastline_lines_file.exists():
            coastlines['lines'] = load_geojson(str(coastline_lines_file))

        return coastlines

    except Exception as e:
        return {}


def load_landslide_layers():
    """
    Load all landslide layers from processed data directory and merge them.

    Returns:
        GeoDataFrame: Merged landslide hazard layer
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR) / "Landslides"

        if not base_path.exists():
            return None

        all_landslides = []

        # Get all landslide shp files (these contain the actual geometries)
        landslide_files = list(base_path.glob("*_ls_shp.geojson"))

        for file in landslide_files:
            try:
                gdf = load_geojson(str(file))
                if gdf is not None and len(gdf) > 0:
                    # Add district name from filename
                    district_name = file.stem.replace('_ls_shp', '')
                    gdf['district'] = district_name
                    gdf['hazard_type'] = 'landslide'
                    all_landslides.append(gdf)
            except Exception as e:
                continue

        if len(all_landslides) == 0:
            return None

        # Merge all landslide GeoDataFrames
        merged_landslides = gpd.GeoDataFrame(
            pd.concat(all_landslides, ignore_index=True),
            crs=f"EPSG:{config.DEFAULT_SRID}"
        )

        # Ensure consistent CRS
        if merged_landslides.crs.to_epsg() != config.DEFAULT_SRID:
            merged_landslides = merged_landslides.to_crs(epsg=config.DEFAULT_SRID)

        return merged_landslides

    except Exception as e:
        return None


def load_cyclone_layers():
    """
    Load all cyclone layers from processed data directory and merge them.

    Returns:
        dict: Dictionary containing cyclone tracks (lines) and points
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR) / "cyclone"

        if not base_path.exists():
            return {'tracks': None, 'points': None}

        cyclone_data = {}

        # Load cyclone tracks (lines)
        tracks_file = base_path / "IBTrACS_since1980_lines_shp.geojson"
        if tracks_file.exists():
            tracks_gdf = load_geojson(str(tracks_file))
            if tracks_gdf is not None:
                tracks_gdf['hazard_type'] = 'cyclone'
                cyclone_data['tracks'] = tracks_gdf

        # Load cyclone points
        points_file = base_path / "IBTrACS_since1980_points_shp.geojson"
        if points_file.exists():
            points_gdf = load_geojson(str(points_file))
            if points_gdf is not None:
                points_gdf['hazard_type'] = 'cyclone'
                cyclone_data['points'] = points_gdf

        return cyclone_data

    except Exception as e:
        return {'tracks': None, 'points': None}


def load_roads():
    """
    Load Kerala roads layer from processed data directory.

    Returns:
        GeoDataFrame: Roads GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        roads_file = base_path / "kerala_roads_fixed.geojson"

        if roads_file.exists():
            return load_geojson(str(roads_file))

        return None

    except Exception as e:
        return None


def load_hospitals():
    """
    Load Kerala hospitals layer from processed data directory.

    Returns:
        GeoDataFrame: Hospitals GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        hospitals_file = base_path / "kerala_hospitals_fixed.geojson"

        if hospitals_file.exists():
            return load_geojson(str(hospitals_file))

        return None

    except Exception as e:
        return None


def load_shelters():
    """
    Load Kerala emergency shelters layer from processed data directory.

    Returns:
        GeoDataFrame: Shelters GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        shelters_file = base_path / "kerala_shelter_fixed.geojson"

        if shelters_file.exists():
            return load_geojson(str(shelters_file))

        return None

    except Exception as e:
        return None


def load_rivers():
    """
    Load Kerala rivers layer from processed data directory.

    Returns:
        GeoDataFrame: Rivers GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        rivers_file = base_path / "kerala_rivers_fixed.geojson"

        if rivers_file.exists():
            return load_geojson(str(rivers_file))

        return None

    except Exception as e:
        return None


def load_water_bodies():
    """
    Load Kerala water bodies layer from processed data directory.

    Returns:
        GeoDataFrame: Water bodies GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        waters_file = base_path / "kerala_waters_fixed.geojson"

        if waters_file.exists():
            return load_geojson(str(waters_file))

        return None

    except Exception as e:
        return None


# TODO: Add more data loading functions:
# - load_from_wfs() - Load from Web Feature Service
# - load_from_api() - Load from REST API
# - batch_load_files() - Load multiple files
