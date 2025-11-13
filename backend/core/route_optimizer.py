"""
Route Optimizer Module
======================
Network analysis and routing using NetworkX.
Computes shortest safe evacuation routes avoiding disaster zones.
"""

import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, LineString
import numpy as np
from backend.core.spatial_analysis import spatial_intersection
import config



def build_road_network(roads_gdf):
    """
    Build a NetworkX graph from road GeoDataFrame.

    Args:
        roads_gdf (GeoDataFrame): Roads with LineString geometries

    Returns:
        nx.Graph: Road network graph
    """
    try:

        G = nx.Graph()

        for idx, road in roads_gdf.iterrows():
            # Get coordinates from LineString
            coords = list(road.geometry.coords)

            # Add edges between consecutive points
            for i in range(len(coords) - 1):
                start = coords[i]
                end = coords[i + 1]

                # Calculate edge length (weight)
                start_point = Point(start)
                end_point = Point(end)
                length = start_point.distance(end_point) * 111000  # Rough conversion to meters

                # Add edge attributes
                edge_attrs = {
                    'length': length,
                    'road_id': idx,
                    'road_type': road.get('road_type', 'unknown'),
                    'is_blocked': road.get('is_blocked', False),
                    'condition': road.get('condition', 'unknown'),
                    'geometry': LineString([start, end])
                }

                # Add edge to graph
                G.add_edge(start, end, **edge_attrs)

        return G

    except Exception as e:
        return nx.Graph()


def find_nearest_node(graph, point):
    """
    Find the nearest node in the graph to a given point.

    Args:
        graph (nx.Graph): Road network graph
        point (tuple): (lon, lat) coordinates

    Returns:
        tuple: Nearest node coordinates
    """
    try:
        nodes = np.array(list(graph.nodes()))

        if len(nodes) == 0:
            return None

        # Calculate distances
        distances = np.sqrt(
            (nodes[:, 0] - point[0])**2 +
            (nodes[:, 1] - point[1])**2
        )

        # Find nearest
        nearest_idx = np.argmin(distances)
        nearest_node = tuple(nodes[nearest_idx])

        return nearest_node

    except Exception as e:
        return None


def compute_shortest_path(graph, start_point, end_point, algorithm='dijkstra'):
    """
    Compute shortest path between two points.

    Args:
        graph (nx.Graph): Road network graph
        start_point (tuple): (lon, lat) start coordinates
        end_point (tuple): (lon, lat) end coordinates
        algorithm (str): 'dijkstra' or 'astar'

    Returns:
        dict: Path information including coordinates, distance, and geometry
    """
    try:

        # Find nearest nodes
        start_node = find_nearest_node(graph, start_point)
        end_node = find_nearest_node(graph, end_point)

        if start_node is None or end_node is None:
            return None

        # Compute shortest path
        if algorithm == 'astar':
            # A* requires a heuristic function
            def heuristic(n1, n2):
                return np.sqrt((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)

            path = nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight='length')
        else:
            # Dijkstra's algorithm
            path = nx.shortest_path(graph, start_node, end_node, weight='length')

        # Calculate total distance
        total_distance = nx.shortest_path_length(graph, start_node, end_node, weight='length')

        # Create LineString geometry
        path_geometry = LineString(path)

        # Get edge attributes along path
        path_details = []
        for i in range(len(path) - 1):
            edge_data = graph.get_edge_data(path[i], path[i + 1])
            path_details.append({
                'from': path[i],
                'to': path[i + 1],
                'length': edge_data.get('length', 0),
                'road_type': edge_data.get('road_type', 'unknown')
            })

        result = {
            'path': path,
            'path_coordinates': list(path),
            'geometry': path_geometry.__geo_interface__,
            'total_distance_meters': round(total_distance, 2),
            'total_distance_km': round(total_distance / 1000, 2),
            'num_segments': len(path) - 1,
            'path_details': path_details
        }

        return result

    except nx.NetworkXNoPath:
        return None
    except Exception as e:
        return None


def compute_safe_route(roads_gdf, start_point, end_point, disaster_zones_gdf, buffer_distance=1000):
    """
    Compute a safe evacuation route that avoids disaster zones.

    Args:
        roads_gdf (GeoDataFrame): Road network
        start_point (tuple): (lon, lat) start coordinates
        end_point (tuple): (lon, lat) end coordinates
        disaster_zones_gdf (GeoDataFrame): Active disaster zones
        buffer_distance (float): Safety buffer around disaster zones in meters

    Returns:
        dict: Safe route information
    """
    try:

        # Filter out roads that intersect disaster zones
        if len(disaster_zones_gdf) > 0:
            # Create buffer around disaster zones
            from backend.core.spatial_analysis import create_buffer

            disaster_buffered = create_buffer(disaster_zones_gdf, buffer_distance)

            # Find roads that intersect disaster zones
            unsafe_roads = spatial_intersection(roads_gdf, disaster_buffered)

            # Get indices of unsafe roads
            unsafe_indices = unsafe_roads.index

            # Filter safe roads
            safe_roads = roads_gdf[~roads_gdf.index.isin(unsafe_indices)]

        else:
            safe_roads = roads_gdf

        # Also filter out blocked roads
        safe_roads = safe_roads[safe_roads.get('is_blocked', False) == False]

        if len(safe_roads) == 0:
            return None

        # Build network from safe roads
        graph = build_road_network(safe_roads)

        if graph.number_of_nodes() == 0:
            return None

        # Compute shortest path
        route = compute_shortest_path(graph, start_point, end_point)

        if route:
            route['safety_status'] = 'safe'
            route['avoided_disaster_zones'] = len(disaster_zones_gdf)

        return route

    except Exception as e:
        return None


def find_alternative_routes(graph, start_point, end_point, num_routes=3):
    """
    Find multiple alternative routes between two points.

    Args:
        graph (nx.Graph): Road network graph
        start_point (tuple): Start coordinates
        end_point (tuple): End coordinates
        num_routes (int): Number of alternative routes to find

    Returns:
        list: List of route dictionaries
    """
    try:

        # Find nearest nodes
        start_node = find_nearest_node(graph, start_point)
        end_node = find_nearest_node(graph, end_point)

        if start_node is None or end_node is None:
            return []

        # Find k-shortest paths
        routes = []

        # This is a simple implementation - for production, use more sophisticated algorithms
        # like Yen's k-shortest paths algorithm
        try:
            # Get all simple paths (limited to avoid combinatorial explosion)
            all_paths = nx.all_simple_paths(
                graph,
                start_node,
                end_node,
                cutoff=50  # Limit path length
            )

            # Sort by path length
            paths_with_length = []
            for path in all_paths:
                length = sum(
                    graph[path[i]][path[i + 1]]['length']
                    for i in range(len(path) - 1)
                )
                paths_with_length.append((path, length))

            # Sort and take top k
            paths_with_length.sort(key=lambda x: x[1])

            for i, (path, length) in enumerate(paths_with_length[:num_routes]):
                route = {
                    'path': path,
                    'path_coordinates': list(path),
                    'geometry': LineString(path).__geo_interface__,
                    'total_distance_meters': round(length, 2),
                    'total_distance_km': round(length / 1000, 2),
                    'route_number': i + 1
                }
                routes.append(route)

        except Exception as e:

        return routes

    except Exception as e:
        return []


def calculate_route_safety_score(route_geometry, disaster_zones_gdf):
    """
    Calculate a safety score for a route based on proximity to disaster zones.

    Args:
        route_geometry (LineString): Route geometry
        disaster_zones_gdf (GeoDataFrame): Disaster zones

    Returns:
        float: Safety score (0-100, higher is safer)
    """
    try:
        if len(disaster_zones_gdf) == 0:
            return 100.0

        # Calculate minimum distance to any disaster zone
        route_gdf = gpd.GeoDataFrame(geometry=[route_geometry], crs=f"EPSG:{config.DEFAULT_SRID}")

        min_distance = float('inf')
        for _, disaster in disaster_zones_gdf.iterrows():
            distance = route_gdf.iloc[0].geometry.distance(disaster.geometry)
            min_distance = min(min_distance, distance)

        # Convert distance to safety score (exponential decay)
        # 10km away = 100, 0km = 0
        safety_score = 100 * (1 - np.exp(-min_distance * 111000 / 5000))

        return round(safety_score, 2)

    except Exception as e:
        return 50.0


# TODO: Add more routing functions:
# - compute_evacuation_flow() - Multi-origin to multi-destination routing
# - find_optimal_shelter_assignment() - Assign people to nearest shelters
# - calculate_travel_time() - Time-based routing considering traffic
# - route_optimization_with_constraints() - Consider vehicle type, fuel, etc.
