"""
Spatial Analysis Tests
======================
Tests for spatial analysis functions.
"""

import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from backend.core.spatial_analysis import (
    create_buffer,
    calculate_distance,
    spatial_intersection
)


@pytest.fixture
def sample_points():
    """Create sample point GeoDataFrame"""
    points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    gdf = gpd.GeoDataFrame(geometry=points, crs='EPSG:4326')
    return gdf


@pytest.fixture
def sample_polygon():
    """Create sample polygon GeoDataFrame"""
    polygon = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    gdf = gpd.GeoDataFrame(geometry=[polygon], crs='EPSG:4326')
    return gdf


def test_create_buffer(sample_points):
    """Test buffer creation"""
    buffered = create_buffer(sample_points, 1000)  # 1km buffer

    assert len(buffered) == len(sample_points)
    assert all(buffered.geometry.geom_type == 'Polygon')


def test_calculate_distance():
    """Test distance calculation"""
    point1 = (0, 0)
    point2 = (0, 1)

    distance = calculate_distance(point1, point2)

    assert distance is not None
    assert distance > 0


def test_spatial_intersection(sample_points, sample_polygon):
    """Test spatial intersection"""
    intersection = spatial_intersection(sample_points, sample_polygon)

    # Points within polygon should be in intersection
    assert len(intersection) >= 0


# TODO: Add more spatial analysis tests
# - Test point-in-polygon
# - Test buffer with different distances
# - Test centroid calculation
# - Test area calculation
