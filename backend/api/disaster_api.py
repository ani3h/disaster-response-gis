from flask import Blueprint, jsonify
from backend.core.data_loader import DATA

disaster_bp = Blueprint("disaster", __name__)


@disaster_bp.route("/cyclones", methods=["GET"])
def get_cyclones():
    try:
        return jsonify({
            "status": "success",
            "lines": DATA.get("cyclone_lines", {}),
            "points": DATA.get("cyclone_points", {})
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@disaster_bp.route("/landslides", methods=["GET"])
def get_landslides():
    return jsonify(DATA.get("landslides", []))

@disaster_bp.route("/api/disaster/landslides", methods=["GET"])
def get_all_landslides():
    return jsonify({
        "status": "success",
        "count": len(DATA.get("landslides", [])),
        "files": DATA.get("landslides", [])
    })

@disaster_bp.route("/statistics", methods=["GET"])
def get_disaster_statistics():

    total_landslides = 0
    for ls in DATA.get("landslides", []):
        total_landslides += len(ls.get("features", []))

    return jsonify({
        "cyclone_lines": len(DATA.get("cyclone_lines", {}).get("features", [])) if DATA.get("cyclone_lines") else 0,
        "cyclone_points": len(DATA.get("cyclone_points", {}).get("features", [])) if DATA.get("cyclone_points") else 0,
        "landslides": total_landslides
    })
