"""
Data Loader Module
==================
Functions to load GeoJSON, Shapefiles, and PostGIS layers using GeoPandas.
Handles data import, validation, and transformation.
Updated to support new Kerala processed data directory structure.
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
        print(f'Error loading GeoJSON from {file_path}: {e}')
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
        print(f'Error loading shapefile from {file_path}: {e}')
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
        print(f'Error loading from PostGIS table {table_name}: {e}')
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
        print(f'Error loading from PostGIS query: {e}')
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
        print(f'Error saving to PostGIS table {table_name}: {e}')
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
        print(f'Error converting to GeoJSON: {e}')
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
        gdf = gpd.GeoDataFrame(df, geometry=geometry,
                               crs=f"EPSG:{config.DEFAULT_SRID}")

        return gdf

    except Exception as e:
        print(f'Error creating points from CSV: {e}')
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
            print(
                f'Found {invalid_count} invalid geometries, attempting to fix...')

            # Try to fix invalid geometries
            gdf.loc[invalid, 'geometry'] = gdf.loc[invalid,
                                                   'geometry'].buffer(0)

            # Check again
            still_invalid = ~gdf.geometry.is_valid
            if still_invalid.sum() > 0:
                print(
                    f'Warning: {still_invalid.sum()} geometries could not be fixed')
            else:
                print('All geometries fixed successfully')

        return gdf

    except Exception as e:
        print(f'Error validating geometry: {e}')
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
        print(f'Error filtering by bbox: {e}')
        return gdf


# =============================================================================
# NEW: Kerala-specific Data Loaders (Updated for new directory structure)
# =============================================================================

def load_boundary():
    """
    Load Kerala main boundary from processed data directory.

    Returns:
        GeoDataFrame: Kerala boundary
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        boundary_file = base_path / "kerala_boundary.geojson"

        if boundary_file.exists():
            return load_geojson(str(boundary_file))

        return None

    except Exception as e:
        print(f'Error loading boundary: {e}')
        return None


def load_district():
    """
    Load Kerala district boundaries from processed data directory.

    Returns:
        GeoDataFrame: District boundaries
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        district_file = base_path / "kerala_district.geojson"

        if district_file.exists():
            return load_geojson(str(district_file))

        return None

    except Exception as e:
        print(f'Error loading districts: {e}')
        return None


def load_taluk():
    """
    Load Kerala taluk boundaries from processed data directory.

    Returns:
        GeoDataFrame: Taluk boundaries
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        taluk_file = base_path / "kerala_taluk.geojson"

        if taluk_file.exists():
            return load_geojson(str(taluk_file))

        return None

    except Exception as e:
        print(f'Error loading taluks: {e}')
        return None


def load_village():
    """
    Load Kerala village boundaries from processed data directory.

    Returns:
        GeoDataFrame: Village boundaries
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        village_file = base_path / "kerala_village.geojson"

        if village_file.exists():
            return load_geojson(str(village_file))

        return None

    except Exception as e:
        print(f'Error loading villages: {e}')
        return None


def load_state():
    """
    Load Kerala state boundary from processed data directory.

    Returns:
        GeoDataFrame: State boundary
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        state_file = base_path / "kerala_state.geojson"

        if state_file.exists():
            return load_geojson(str(state_file))

        return None

    except Exception as e:
        print(f'Error loading state: {e}')
        return None


def load_buildings():
    """
    Load Kerala buildings layer from processed data directory.

    Returns:
        GeoDataFrame: Buildings GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        buildings_file = base_path / "kerala_buildings.geojson"

        if buildings_file.exists():
            return load_geojson(str(buildings_file))

        return None

    except Exception as e:
        print(f'Error loading buildings: {e}')
        return None


def load_coastline():
    """
    Load Kerala coastline from processed data directory.

    Returns:
        GeoDataFrame: Coastline GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        coastline_file = base_path / "kerala_coastline.geojson"

        if coastline_file.exists():
            return load_geojson(str(coastline_file))

        return None

    except Exception as e:
        print(f'Error loading coastline: {e}')
        return None


def load_emergency():
    """
    Load Kerala emergency facilities from processed data directory.

    Returns:
        GeoDataFrame: Emergency facilities GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        emergency_file = base_path / "kerala_emergency.geojson"

        if emergency_file.exists():
            return load_geojson(str(emergency_file))

        return None

    except Exception as e:
        print(f'Error loading emergency facilities: {e}')
        return None


def load_hospitals():
    """
    Load Kerala hospitals layer from processed data directory.

    Returns:
        GeoDataFrame: Hospitals GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        hospitals_file = base_path / "kerala_hospitals.geojson"

        if hospitals_file.exists():
            return load_geojson(str(hospitals_file))

        return None

    except Exception as e:
        print(f'Error loading hospitals: {e}')
        return None


def load_rivers():
    """
    Load Kerala rivers layer from processed data directory.

    Returns:
        GeoDataFrame: Rivers GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        rivers_file = base_path / "kerala_rivers.geojson"

        if rivers_file.exists():
            return load_geojson(str(rivers_file))

        return None

    except Exception as e:
        print(f'Error loading rivers: {e}')
        return None


def load_roads():
    """
    Load Kerala roads layer from processed data directory.

    Returns:
        GeoDataFrame: Roads GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        roads_file = base_path / "kerala_roads.geojson"

        if roads_file.exists():
            return load_geojson(str(roads_file))

        return None

    except Exception as e:
        print(f'Error loading roads: {e}')
        return None


def load_shelters():
    """
    Load Kerala emergency shelters layer from processed data directory.

    Returns:
        GeoDataFrame: Shelters GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        shelters_file = base_path / "kerala_shelters.geojson"

        if shelters_file.exists():
            return load_geojson(str(shelters_file))

        return None

    except Exception as e:
        print(f'Error loading shelters: {e}')
        return None


def load_water():
    """
    Load Kerala water bodies layer from processed data directory.

    Returns:
        GeoDataFrame: Water bodies GeoDataFrame
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR)
        water_file = base_path / "kerala_water.geojson"

        if water_file.exists():
            return load_geojson(str(water_file))

        return None

    except Exception as e:
        print(f'Error loading water bodies: {e}')
        return None


def load_landslides_kerala():
    """
    Load and merge ALL Kerala landslide GIS district files.

    NEW: Automatically scans the 'Landslides' directory for all *.geojson files.

    Returns:
        GeoDataFrame: Merged landslide hazard layer for all Kerala districts
    """
    try:
        base_path = Path(config.PROCESSED_DATA_DIR) / "Landslides"

        if not base_path.exists():
            print(f"Warning: Landslides directory not found at {base_path}")
            return None

        # Auto-detect ALL .geojson files
        geojson_files = list(base_path.glob("*.geojson"))

        if len(geojson_files) == 0:
            print("No .geojson landslide files found in Landslides folder.")
            return None

        all_landslides = []

        for file_path in geojson_files:
            try:
                gdf = load_geojson(str(file_path))

                if gdf is not None and len(gdf) > 0:

                    # Extract district name from filename (anything before _GSI_LS)
                    district_name = file_path.stem.replace("_GSI_LS", "")

                    gdf["district"] = district_name
                    gdf["hazard_type"] = "landslide"
                    gdf["disaster_type"] = "landslide"

                    all_landslides.append(gdf)

                    print(
                        f"Loaded {len(gdf)} landslide features from {district_name}")

            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
                continue

        if len(all_landslides) == 0:
            print("No valid landslide layers loaded.")
            return None

        # Merge all landslide GeoDataFrames
        print(f"Merging {len(all_landslides)} district landslide layers...")
        merged_landslides = gpd.GeoDataFrame(
            pd.concat(all_landslides, ignore_index=True),
            crs=f"EPSG:{config.DEFAULT_SRID}"
        )

        # Ensure CRS consistency
        if merged_landslides.crs is None or merged_landslides.crs.to_epsg() != config.DEFAULT_SRID:
            merged_landslides = merged_landslides.to_crs(
                epsg=config.DEFAULT_SRID)

        # Validate geometry
        merged_landslides = validate_geometry(merged_landslides)

        print(
            f"Successfully merged {len(merged_landslides)} total landslide features "
            f"from {len(all_landslides)} files."
        )

        return merged_landslides

    except Exception as e:
        print(f"Error loading Kerala landslides: {e}")
        return None


def load_boundary_layers():
    """
    Load all Kerala boundary layers from processed data directory.

    Returns:
        dict: Dictionary of boundary GeoDataFrames
    """
    try:
        boundaries = {}

        # Load all boundary types
        boundaries['main'] = load_boundary()
        boundaries['districts'] = load_district()
        boundaries['state'] = load_state()
        boundaries['taluks'] = load_taluk()
        boundaries['villages'] = load_village()

        return boundaries

    except Exception as e:
        print(f'Error loading boundary layers: {e}')
        return {}


def load_water_bodies():
    """
    Load Kerala water bodies layer from processed data directory.
    Alias for load_water() for backwards compatibility.

    Returns:
        GeoDataFrame: Water bodies GeoDataFrame
    """
    return load_water()
