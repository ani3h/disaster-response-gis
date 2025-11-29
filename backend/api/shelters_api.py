# """
# Shelters API Module
# ===================
# API endpoints for shelter and hospital information (GeoJSON based).
# """

# from flask import Blueprint, jsonify, request, current_app
# from shapely.geometry import Point

# from backend.core.data_loader import get_layer

# shelters_bp = Blueprint("shelters", __name__)


# # ---------- Helpers ----------

# def _nearest_features(gdf, lat, lon, limit=5):
#     """Return GeoJSON FeatureCollection of nearest features."""
#     if gdf is None or gdf.empty:
#         return {"type": "FeatureCollection", "features": []}

#     pt = Point(lon, lat)
#     gdf = gdf.copy()
#     # Rough distance in degrees → km (1° ~ 111km)
#     gdf["__dist"] = gdf.geometry.distance(pt) * 111.0
#     gdf = gdf.sort_values("__dist").head(limit)
#     gdf = gdf.drop(columns="__dist")

#     return gdf.__geo_interface__


# # ---------- API endpoints ----------

# @shelters_bp.route("/nearest", methods=["POST"])
# def get_nearest_shelters():
#     """
#     Find nearest shelters to a given location.
#     """
#     try:
#         data = request.get_json()

#         if not data or "latitude" not in data or "longitude" not in data:
#             return (
#                 jsonify(
#                     {"status": "error", "message": "Missing latitude or longitude"}
#                 ),
#                 400,
#             )

#         lat = float(data["latitude"])
#         lon = float(data["longitude"])
#         limit = data.get("limit", 5)

#         gdf = get_layer("shelters", current_app)
#         geojson = _nearest_features(gdf, lat, lon, limit)

#         return jsonify({"status": "success", "data": geojson}), 200

#     except ValueError:
#         return jsonify(
#             {"status": "error", "message": "Invalid coordinate format"}
#         ), 400
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500


# @shelters_bp.route("/all", methods=["GET"])
# def get_all_shelters():
#     """
#     Get all shelters as GeoJSON.
#     """
#     try:
#         gdf = get_layer("shelters", current_app)
#         if gdf is None:
#             geojson = {"type": "FeatureCollection", "features": []}
#         else:
#             geojson = gdf.__geo_interface__

#         return jsonify({"status": "success", "data": geojson}), 200

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500


# @shelters_bp.route("/hospitals/nearest", methods=["POST"])
# def get_nearest_hospitals():
#     """
#     Find nearest hospitals to a given location.
#     """
#     try:
#         data = request.get_json()

#         if not data or "latitude" not in data or "longitude" not in data:
#             return (
#                 jsonify(
#                     {"status": "error", "message": "Missing latitude or longitude"}
#                 ),
#                 400,
#             )

#         lat = float(data["latitude"])
#         lon = float(data["longitude"])
#         limit = data.get("limit", 5)

#         gdf = get_layer("hospitals", current_app)
#         geojson = _nearest_features(gdf, lat, lon, limit)

#         return jsonify({"status": "success", "data": geojson}), 200

#     except ValueError:
#         return jsonify(
#             {"status": "error", "message": "Invalid coordinate format"}
#         ), 400
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500


# @shelters_bp.route("/hospitals/all", methods=["GET"])
# def get_all_hospitals():
#     """
#     Get all hospitals as GeoJSON.
#     """
#     try:
#         gdf = get_layer("hospitals", current_app)
#         if gdf is None:
#             geojson = {"type": "FeatureCollection", "features": []}
#         else:
#             geojson = gdf.__geo_interface__

#         return jsonify({"status": "success", "data": geojson}), 200

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
"""
Shelters API Module (Direct Loading Version)
===========================================
Loads GeoJSON from DATA[] which is preloaded at startup.
"""

from flask import Blueprint, jsonify, request
from shapely.geometry import Point
from backend.core.data_loader import DATA   # << Direct access

shelters_bp = Blueprint("shelters", __name__)


# ---------- Helper: nearest shelters/hospitals ----------

def _nearest_features(geojson, lat, lon, limit=5):
    """Return nearest features from a loaded GeoJSON (DATA[] version)."""

    if not geojson or "features" not in geojson:
        return {"type": "FeatureCollection", "features": []}

    pt = Point(lon, lat)

    # Convert GeoJSON → list of features with distance
    enriched = []
    for feat in geojson["features"]:
        geom = feat.get("geometry")
        if not geom:
            continue

        try:
            shp = Point(geom["coordinates"][0], geom["coordinates"][1])
            dist = shp.distance(pt) * 111.0   # degrees → km
            enriched.append((dist, feat))
        except:
            continue

    # Sort and return top N
    enriched.sort(key=lambda x: x[0])
    nearest = [f for (_, f) in enriched[:limit]]

    return {
        "type": "FeatureCollection",
        "features": nearest
    }


# ---------- API ENDPOINTS ----------

@shelters_bp.route("/all", methods=["GET"])
def get_all_shelters():
    """Return ALL shelters from DATA."""
    shelters = DATA.get("shelters")

    if shelters is None:
        return jsonify({"status": "success", "data": {"type": "FeatureCollection", "features": []}})

    return jsonify({"status": "success", "data": shelters})


@shelters_bp.route("/hospitals/all", methods=["GET"])
def get_all_hospitals():
    """Return ALL hospitals from DATA."""
    hospitals = DATA.get("hospitals")

    if hospitals is None:
        return jsonify({"status": "success", "data": {"type": "FeatureCollection", "features": []}})

    return jsonify({"status": "success", "data": hospitals})


@shelters_bp.route("/nearest", methods=["POST"])
def get_nearest_shelters():
    """Return nearest shelters to a coordinate."""
    try:
        data = request.get_json()
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        limit = int(data.get("limit", 5))
    except:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    geojson = DATA.get("shelters")
    nearest = _nearest_features(geojson, lat, lon, limit)

    return jsonify({"status": "success", "data": nearest})


@shelters_bp.route("/hospitals/nearest", methods=["POST"])
def get_nearest_hospitals():
    """Return nearest hospitals to a coordinate."""
    try:
        data = request.get_json()
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        limit = int(data.get("limit", 5))
    except:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    geojson = DATA.get("hospitals")
    nearest = _nearest_features(geojson, lat, lon, limit)

    return jsonify({"status": "success", "data": nearest})
