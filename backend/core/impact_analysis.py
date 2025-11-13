"""
Impact Analysis Module
======================
Analyzes disaster impact on population, infrastructure, and resources.
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import logging
from backend.core.spatial_analysis import spatial_intersection, calculate_area

logger = logging.getLogger(__name__)


def analyze_disaster_impact(disaster_zone_gdf, admin_boundaries_gdf, hospitals_gdf, shelters_gdf, roads_gdf):
    """
    Comprehensive disaster impact analysis.

    Args:
        disaster_zone_gdf (GeoDataFrame): Disaster zone boundaries
        admin_boundaries_gdf (GeoDataFrame): Administrative boundaries with population
        hospitals_gdf (GeoDataFrame): Hospital locations
        shelters_gdf (GeoDataFrame): Shelter locations
        roads_gdf (GeoDataFrame): Road network

    Returns:
        dict: Comprehensive impact analysis results
    """
    try:
        logger.info("Starting comprehensive disaster impact analysis...")

        # Calculate affected area
        disaster_with_area = calculate_area(disaster_zone_gdf)
        total_affected_area = disaster_with_area['area_sqkm'].sum()

        # Find affected administrative areas
        affected_admin = spatial_intersection(admin_boundaries_gdf, disaster_zone_gdf)
        affected_population = affected_admin['population'].sum() if 'population' in affected_admin.columns else 0

        # Find affected hospitals
        affected_hospitals = spatial_intersection(hospitals_gdf, disaster_zone_gdf)

        # Find affected shelters
        affected_shelters = spatial_intersection(shelters_gdf, disaster_zone_gdf)

        # Find affected roads
        affected_roads = spatial_intersection(roads_gdf, disaster_zone_gdf)
        affected_roads_length = affected_roads['length'].sum() if 'length' in affected_roads.columns else 0

        # Compile results
        impact_summary = {
            'affected_area_sqkm': round(total_affected_area, 2),
            'estimated_affected_population': int(affected_population),
            'affected_administrative_areas': len(affected_admin),
            'affected_hospitals': len(affected_hospitals),
            'affected_shelters': len(affected_shelters),
            'affected_roads_km': round(affected_roads_length / 1000, 2),
            'severity_assessment': assess_severity(affected_population, total_affected_area)
        }

        logger.info(f"Impact analysis complete: {affected_population} people affected")
        return impact_summary

    except Exception as e:
        logger.error(f"Error in disaster impact analysis: {e}")
        return {}


def assess_severity(affected_population, affected_area_sqkm):
    """
    Assess disaster severity based on impact metrics.

    Args:
        affected_population (int): Number of affected people
        affected_area_sqkm (float): Affected area in square kilometers

    Returns:
        str: Severity level (low, medium, high, critical)
    """
    if affected_population > 100000 or affected_area_sqkm > 1000:
        return 'critical'
    elif affected_population > 10000 or affected_area_sqkm > 100:
        return 'high'
    elif affected_population > 1000 or affected_area_sqkm > 10:
        return 'medium'
    else:
        return 'low'


def calculate_shelter_capacity_gap(disaster_zone_gdf, shelters_gdf, estimated_affected_population):
    """
    Calculate gap between shelter capacity and affected population.

    Args:
        disaster_zone_gdf (GeoDataFrame): Disaster zones
        shelters_gdf (GeoDataFrame): Available shelters
        estimated_affected_population (int): Estimated affected population

    Returns:
        dict: Shelter capacity analysis
    """
    try:
        # Find shelters near disaster zone (within 50km)
        from backend.core.spatial_analysis import create_buffer

        disaster_buffer = create_buffer(disaster_zone_gdf, 50000)  # 50km
        nearby_shelters = spatial_intersection(shelters_gdf, disaster_buffer)

        # Calculate total capacity
        total_capacity = nearby_shelters['capacity'].sum() if 'capacity' in nearby_shelters.columns else 0
        current_occupancy = nearby_shelters['current_occupancy'].sum() if 'current_occupancy' in nearby_shelters.columns else 0

        available_capacity = total_capacity - current_occupancy
        capacity_gap = estimated_affected_population - available_capacity

        result = {
            'nearby_shelters_count': len(nearby_shelters),
            'total_capacity': int(total_capacity),
            'current_occupancy': int(current_occupancy),
            'available_capacity': int(available_capacity),
            'affected_population': int(estimated_affected_population),
            'capacity_gap': int(capacity_gap),
            'capacity_sufficient': capacity_gap <= 0
        }

        logger.info(f"Shelter capacity gap: {capacity_gap}")
        return result

    except Exception as e:
        logger.error(f"Error calculating shelter capacity: {e}")
        return {}


def identify_vulnerable_infrastructure(disaster_zone_gdf, hospitals_gdf, power_stations_gdf=None):
    """
    Identify critical infrastructure at risk.

    Args:
        disaster_zone_gdf (GeoDataFrame): Disaster zones
        hospitals_gdf (GeoDataFrame): Hospital locations
        power_stations_gdf (GeoDataFrame, optional): Power station locations

    Returns:
        dict: Vulnerable infrastructure analysis
    """
    try:
        vulnerable = {
            'hospitals': [],
            'power_stations': []
        }

        # Check hospitals
        affected_hospitals = spatial_intersection(hospitals_gdf, disaster_zone_gdf)
        vulnerable['hospitals'] = affected_hospitals[['name', 'capacity']].to_dict('records') if len(affected_hospitals) > 0 else []

        # Check power stations if provided
        if power_stations_gdf is not None:
            affected_power = spatial_intersection(power_stations_gdf, disaster_zone_gdf)
            vulnerable['power_stations'] = affected_power.to_dict('records') if len(affected_power) > 0 else []

        logger.info(f"Identified {len(vulnerable['hospitals'])} vulnerable hospitals")
        return vulnerable

    except Exception as e:
        logger.error(f"Error identifying vulnerable infrastructure: {e}")
        return {}


def calculate_economic_impact(disaster_zone_gdf, admin_boundaries_gdf):
    """
    Estimate economic impact of disaster.

    Args:
        disaster_zone_gdf (GeoDataFrame): Disaster zones
        admin_boundaries_gdf (GeoDataFrame): Administrative areas with economic data

    Returns:
        dict: Economic impact estimates
    """
    try:
        # This is a simplified model - real economic impact requires detailed data
        affected_admin = spatial_intersection(admin_boundaries_gdf, disaster_zone_gdf)

        # Placeholder calculations - replace with real economic data
        affected_area = calculate_area(affected_admin)
        total_area = affected_area['area_sqkm'].sum()

        # Rough estimate: $1M per square km (this is just a placeholder)
        estimated_damage_usd = total_area * 1_000_000

        result = {
            'estimated_damage_usd': int(estimated_damage_usd),
            'affected_area_sqkm': round(total_area, 2),
            'note': 'This is a rough estimate. Actual assessment requires detailed survey.'
        }

        logger.info(f"Estimated economic impact: ${estimated_damage_usd:,.0f}")
        return result

    except Exception as e:
        logger.error(f"Error calculating economic impact: {e}")
        return {}


def generate_impact_report(disaster_zone_gdf, all_layers_dict):
    """
    Generate comprehensive impact report.

    Args:
        disaster_zone_gdf (GeoDataFrame): Disaster zones
        all_layers_dict (dict): Dictionary of all GeoDataFrames

    Returns:
        dict: Complete impact report
    """
    try:
        logger.info("Generating comprehensive impact report...")

        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'disaster_summary': {},
            'population_impact': {},
            'infrastructure_impact': {},
            'resource_availability': {},
            'recommendations': []
        }

        # TODO: Implement full report generation
        # This would include all the above functions plus additional analysis

        logger.info("Impact report generated")
        return report

    except Exception as e:
        logger.error(f"Error generating impact report: {e}")
        return {}


# TODO: Add more impact analysis functions:
# - predict_spread() - Predict disaster spread over time
# - calculate_response_time() - Estimate emergency response times
# - prioritize_rescue_operations() - Prioritize areas for rescue
# - assess_environmental_impact() - Environmental damage assessment
