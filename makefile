# ==========================================================
# QGIS Automated Preprocessing Makefile
# Preprocess OSM → GeoJSON layers:
# - Fix geometries
# - Reproject to EPSG:4326
# - Clip to Kerala boundary
# - Simplify geometries
# Outputs go to: data/processed/
# ==========================================================

RAW_DIR = database/raw
PROC_DIR = database/processed
BOUNDARY = $(RAW_DIR)/kerala_boundary.geojson

QGIS = qgis_process

# -------------------------------------
# INPUT RAW FILES
# (Update if new layers are added)
# -------------------------------------
ROADS = $(RAW_DIR)/kerala_roads.geojson
HOSPITALS = $(RAW_DIR)/kerala_hospitals.geojson
BUILDINGS = $(RAW_DIR)/kerala_buildings.geojson
WATER = $(RAW_DIR)/kerala_water.geojson
RIVERS = $(RAW_DIR)/kerala_rivers.geojson
SHELTERS = $(RAW_DIR)/kerala_shelters.geojson

# -------------------------------------
# OUTPUT PROCESSED FILES
# -------------------------------------
PROC_ROADS = $(PROC_DIR)/roads_clean.geojson
PROC_HOSPITALS = $(PROC_DIR)/hospitals_clean.geojson
PROC_BUILDINGS = $(PROC_DIR)/buildings_clean.geojson
PROC_WATER = $(PROC_DIR)/water_clean.geojson
PROC_RIVERS = $(PROC_DIR)/rivers_clean.geojson
PROC_SHELTERS = $(PROC_DIR)/shelters_clean.geojson

# -------------------------------------
# QGIS PROCESS COMMANDS (Reusable Macros)
# -------------------------------------

# Fix geometries
define FIX_GEOM
$(QGIS) run native:fixgeometries \
  --INPUT="$1" \
  --OUTPUT="$2"
endef

# Reproject
define REPROJECT
$(QGIS) run native:reprojectlayer \
  --INPUT="$1" \
  --TARGET_CRS="EPSG:4326" \
  --OUTPUT="$2"
endef

# Clip to Kerala boundary
define CLIP
$(QGIS) run native:clip \
  --INPUT="$1" \
  --OVERLAY="$(BOUNDARY)" \
  --OUTPUT="$2"
endef

# Simplify geometry
define SIMPLIFY
$(QGIS) run native:simplifygeometries \
  --INPUT="$1" \
  --METHOD=0 \
  --TOLERANCE=0.0001 \
  --OUTPUT="$2"
endef

# ==========================================================
# DEFAULT TARGET
# ==========================================================
all: $(PROC_ROADS) $(PROC_HOSPITALS) $(PROC_BUILDINGS) $(PROC_WATER) $(PROC_RIVERS) $(PROC_SHELTERS)
	@echo "All preprocessing completed!"

# ==========================================================
# PIPELINES FOR EACH LAYER
# ==========================================================

$(PROC_ROADS): $(ROADS) $(BOUNDARY)
	@echo "Processing ROADS..."
	$(call FIX_GEOM,$(ROADS),$(PROC_DIR)/roads_fixed.geojson)
	$(call REPROJECT,$(PROC_DIR)/roads_fixed.geojson,$(PROC_DIR)/roads_reproj.geojson)
	$(call CLIP,$(PROC_DIR)/roads_reproj.geojson,$(PROC_DIR)/roads_clipped.geojson)
	$(call SIMPLIFY,$(PROC_DIR)/roads_clipped.geojson,$(PROC_ROADS))

$(PROC_HOSPITALS): $(HOSPITALS) $(BOUNDARY)
	@echo "Processing HOSPITALS..."
	$(call FIX_GEOM,$(HOSPITALS),$(PROC_DIR)/hospitals_fixed.geojson)
	$(call REPROJECT,$(PROC_DIR)/hospitals_fixed.geojson,$(PROC_DIR)/hospitals_reproj.geojson)
	$(call CLIP,$(PROC_DIR)/hospitals_reproj.geojson,$(PROC_DIR)/hospitals_clipped.geojson)
	cp $(PROC_DIR)/hospitals_clipped.geojson $(PROC_HOSPITALS)

$(PROC_BUILDINGS): $(BUILDINGS) $(BOUNDARY)
	@echo "Processing BUILDINGS..."
	$(call FIX_GEOM,$(BUILDINGS),$(PROC_DIR)/buildings_fixed.geojson)
	$(call REPROJECT,$(PROC_DIR)/buildings_fixed.geojson,$(PROC_DIR)/buildings_reproj.geojson)
	$(call CLIP,$(PROC_DIR)/buildings_reproj.geojson,$(PROC_DIR)/buildings_clipped.geojson)
	$(call SIMPLIFY,$(PROC_DIR)/buildings_clipped.geojson,$(PROC_BUILDINGS))

$(PROC_WATER): $(WATER) $(BOUNDARY)
	@echo "Processing WATER BODIES..."
	$(call FIX_GEOM,$(WATER),$(PROC_DIR)/water_fixed.geojson)
	$(call REPROJECT,$(PROC_DIR)/water_fixed.geojson,$(PROC_DIR)/water_reproj.geojson)
	$(call CLIP,$(PROC_DIR)/water_reproj.geojson,$(PROC_DIR)/water_clipped.geojson)
	cp $(PROC_DIR)/water_clipped.geojson $(PROC_WATER)

$(PROC_RIVERS): $(RIVERS) $(BOUNDARY)
	@echo "Processing RIVERS..."
	$(call FIX_GEOM,$(RIVERS),$(PROC_DIR)/rivers_fixed.geojson)
	$(call REPROJECT,$(PROC_DIR)/rivers_fixed.geojson,$(PROC_DIR)/rivers_reproj.geojson)
	$(call CLIP,$(PROC_DIR)/rivers_reproj.geojson,$(PROC_DIR)/rivers_clipped.geojson)
	$(call SIMPLIFY,$(PROC_DIR)/rivers_clipped.geojson,$(PROC_RIVERS))

$(PROC_SHELTERS): $(SHELTERS) $(BOUNDARY)
	@echo "Processing SHELTERS..."
	$(call REPROJECT,$(SHELTERS),$(PROC_DIR)/shelters_reproj.geojson)
	$(call CLIP,$(PROC_DIR)/shelters_reproj.geojson,$(PROC_SHELTERS))

# ==========================================================
# CLEAN
# ==========================================================
clean:
	rm -f $(PROC_DIR)/*.geojson
	@echo "Cleaned processed data"
