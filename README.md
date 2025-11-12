# 🌍 Disaster Response GIS

### Real-Time Impact Mapping and Safe Route Visualization for Emergency Management

This project aims to create an **interactive GIS-based disaster response dashboard** that visualizes real-time disaster impact zones, identifies safe evacuation routes, and maps nearby shelters and hospitals. By integrating spatial data, open-source mapping tools, and real-time datasets, the system enhances **situational awareness** and **disaster response coordination**.

---

## Features
- Real-time visualization of disaster impact zones (floods, cyclones, earthquakes)
- Safe route and evacuation path optimization using network analysis
- Mapping of hospitals, shelters, and safe zones
- Integration of open-source datasets (OSM, NDMA, Bhuvan, IMD)
- Interactive web dashboard using **Leaflet/Folium** and **Flask/Django**

---

## Project Objectives
- Develop a real-time GIS dashboard for visualizing disaster impacts  
- Identify optimal evacuation routes using spatial and network analysis  
- Demonstrate the potential of open GIS data for emergency planning

---

## Directory Map

```
disaster-response-gis/
│
├── app/                                 # Core application source code
│   ├── __init__.py                         # Flask app initialization
│   ├── routes.py                           # Defines API endpoints for frontend requests
│   ├── data_processing.py                  # Handles spatial data cleaning and analysis
│   ├── route_optimizer.py                  # Computes safe evacuation routes
│   ├── api_manager.py                      # Fetches live disaster and weather data
│   └── database.py                         # Manages PostGIS database connections and queries
│
├── templates/                           # Frontend HTML templates (Flask + Leaflet)
│   ├── base.html                           # Common layout for all pages
│   └── index.html                          # Interactive dashboard with map and controls
│
├── static/                              # Static frontend assets
│   ├── css/
│   │   └── styles.css                      # Basic styling for the dashboard and map
│   └── js/
│       ├── map.js                          # Leaflet map initialization and user interactions
│       └── api.js                          # Handles frontend-to-backend AJAX requests
│
├── data/                                # Spatial datasets (small, manageable size)
│   ├── flood_zones.geojson                 # Example disaster layer
│   ├── hospitals.geojson                   # Hospitals and medical centers
│   ├── shelters.geojson                    # Safe zones and relief centers
│   └── roads.geojson                       # Road network for route analysis
│
├── database/                            # Minimal database setup
│   └── init.sql                            # PostGIS schema setup for spatial tables
│
├── requirements.txt                        # Python dependencies
├── config.py                               # Configuration file (database URL, API keys)
├── run.py                                  # Flask application entry point
└── README.md                               # Quick setup and usage guide

```

---
