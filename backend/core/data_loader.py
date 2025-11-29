# import os
# import json

# DATA = {}   # <<< GLOBAL dataset container

# def load_geojson(path):
#     """Load a GeoJSON file safely"""
#     if not os.path.exists(path):
#         print(f"[WARN] Missing: {path}")
#         return None

#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         print(f"[LOADED] {os.path.basename(path)} ({len(data.get('features', []))} features)")
#         return data
#     except Exception as e:
#         print(f"[ERROR] Failed to load {path}: {e}")
#         return None


# def load_landslide_folder(folder_path):
#     """Load ALL GeoJSON files inside landslides_processed/"""
#     if not os.path.exists(folder_path):
#         print(f"[WARN] Landslide folder not found: {folder_path}")
#         return []

#     landslide_files = [f for f in os.listdir(folder_path) if f.endswith(".geojson")]
#     output = []

#     for file in landslide_files:
#         full_path = os.path.join(folder_path, file)
#         data = load_geojson(full_path)
#         if data:
#             output.append(data)

#     print(f"[OK] Loaded {len(output)} landslide files.")
#     return output


# def init_data(app):
#     """This runs ONCE when Flask starts"""

#     base = app.config["DATA_PROCESSED_DIR"]

#     global DATA
#     DATA = {}   # reset container

#     # ======================
#     # NORMAL LAYERS
#     # ======================
#     layer_files = {
#         "boundary": "kerala_boundary_area_fixed.geojson",
#         "state": "kerala_state_fixed.geojson",
#         "districts": "kerala_district_fixed.geojson",
#         "taluks": "kerala_taluk_fixed.geojson",
#         "villages": "kerala_village_fixed.geojson",

#         # "roads": "kerala_roads_lines_fixed.geojson",
#         "rivers": "kerala_rivers_lines_fixed.geojson",
#         "waters_area": "kerala_waters_area_fixed.geojson",
#         "waters_lines": "kerala_waters_lines_fixed.geojson",
#         "coastline": "kerala_coastline_lines_fixed.geojson",

#         "hospitals": "kerala_hospitals_fixed.geojson",
#         "shelters": "kerala_shelter_fixed.geojson",

#         # Cyclones
#         "cyclone_lines": "cyclone_lines.geojson",
#         "cyclone_points": "cyclone_points.geojson",
#     }

#     for key, filename in layer_files.items():
#         path = os.path.join(base, filename)
#         DATA[key] = load_geojson(path)

#     # ======================
#     # LANDSLIDES
#     # ======================
#     landslide_folder = os.path.join(base, "landslides_processed")
#     DATA["landslides"] = load_landslide_folder(landslide_folder)

#     print("============================================")
#     print("[INFO] All data loaded into DATA[]")
#     print("============================================")
import os
import json

DATA = {}

def load_geojson(path):
    """Load and validate GeoJSON file."""
    if not os.path.exists(path):
        print(f"[WARN] File missing: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "features" in data:
            print(f"[LOADED] {os.path.basename(path)} ({len(data['features'])} features)")
            return data
        else:
            print(f"[ERROR] Invalid GeoJSON format: {path}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}")
        return None


def load_landslides(folder):
    """Load all landslide GeoJSONs from landslides_processed/"""
    DATA["landslides"] = []

    if not os.path.exists(folder):
        print("[WARN] Landslide folder not found:", folder)
        return

    for file in os.listdir(folder):
        if file.endswith(".geojson"):
            fp = os.path.join(folder, file)
            obj = load_geojson(fp)
            if obj:
                DATA["landslides"].append(obj)
                print("[LANDSLIDE] Loaded:", file)

    print(f"[OK] Total landslide files loaded: {len(DATA['landslides'])}")


def init_data(app):
    """Initialize all GIS datasets."""
    base = app.config["DATA_PROCESSED_DIR"]

    print("========== LOADING GIS DATA FROM", base, "==========")

    fixed_files = {
        "boundary": "kerala_boundary_area_fixed.geojson",
        "state": "kerala_state_fixed.geojson",
        "districts": "kerala_district_fixed.geojson",
        "taluks": "kerala_taluk_fixed.geojson",
        "villages": "kerala_village_fixed.geojson",

        "rivers": "kerala_rivers_lines_fixed.geojson",
        "waters_area": "kerala_waters_area_fixed.geojson",
        "waters_lines": "kerala_waters_lines_fixed.geojson",
        "coastline": "kerala_coastline_lines_fixed.geojson",

        "hospitals": "kerala_hospitals_fixed.geojson",
        "shelters": "kerala_shelter_fixed.geojson",

        # cyclone files (your actual filenames)
        "cyclone_lines": "cyclone_lines.geojson",
        "cyclone_points": "cyclone_points.geojson",
    }

    # Load fixed files
    for key, filename in fixed_files.items():
        full = os.path.join(base, filename)
        DATA[key] = load_geojson(full)

    # Load landslides folder
    landslide_dir = os.path.join(base, "landslides_processed")
    load_landslides(landslide_dir)

    print("========== DATA LOADING COMPLETE ==========")
