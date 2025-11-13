"""
Database Models
===============
SQLAlchemy ORM models for all database tables with PostGIS geometry support.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography, Geometry
from datetime import datetime
from backend.db.db_connection import Base
import config


class Hospital(Base):
    """
    Hospital model - stores hospital locations and details
    """
    __tablename__ = 'hospitals'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(50))
    capacity = Column(Integer)  # Number of beds
    emergency_ready = Column(Boolean, default=True)
    facility_type = Column(String(100))  # General, Trauma Center, etc.

    # Spatial column - point geometry
    geom = Column(Geography(geometry_type='POINT', srid=config.DEFAULT_SRID), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Hospital(id={self.id}, name='{self.name}')>"


class Shelter(Base):
    """
    Shelter model - stores emergency shelter locations
    """
    __tablename__ = 'shelters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    capacity = Column(Integer)  # Maximum occupancy
    current_occupancy = Column(Integer, default=0)
    shelter_type = Column(String(100))  # Temporary, Permanent, Relief Camp
    contact_person = Column(String(255))
    phone = Column(String(50))
    has_food = Column(Boolean, default=True)
    has_water = Column(Boolean, default=True)
    has_medical = Column(Boolean, default=False)

    # Spatial column - point geometry
    geom = Column(Geography(geometry_type='POINT', srid=config.DEFAULT_SRID), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Shelter(id={self.id}, name='{self.name}', capacity={self.capacity})>"


class Road(Base):
    """
    Road model - stores road network for routing
    """
    __tablename__ = 'roads'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    road_type = Column(String(50))  # highway, primary, secondary, residential
    surface = Column(String(50))  # paved, unpaved, gravel
    lanes = Column(Integer)
    max_speed = Column(Integer)  # km/h
    length = Column(Float)  # meters
    is_blocked = Column(Boolean, default=False)  # Blocked due to disaster
    condition = Column(String(50))  # good, moderate, poor, impassable

    # Spatial column - linestring geometry
    geom = Column(Geography(geometry_type='LINESTRING', srid=config.DEFAULT_SRID), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Road(id={self.id}, name='{self.name}', type='{self.road_type}')>"


class AdminBoundary(Base):
    """
    Administrative boundary model - stores district/state boundaries
    """
    __tablename__ = 'admin_boundaries'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    admin_level = Column(Integer)  # 1=Country, 2=State, 3=District, 4=Block
    admin_type = Column(String(50))  # state, district, subdistrict
    population = Column(Integer)
    area_sqkm = Column(Float)

    # Spatial column - polygon or multipolygon geometry
    geom = Column(Geography(geometry_type='MULTIPOLYGON', srid=config.DEFAULT_SRID), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AdminBoundary(id={self.id}, name='{self.name}', level={self.admin_level})>"


class FloodZone(Base):
    """
    Flood zone model - stores flood-affected areas
    """
    __tablename__ = 'flood_zones'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    severity = Column(String(50))  # low, medium, high, critical
    water_level = Column(Float)  # meters
    affected_population = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)  # null if ongoing
    status = Column(String(50))  # active, receding, cleared
    description = Column(Text)

    # Spatial column - polygon geometry
    geom = Column(Geography(geometry_type='MULTIPOLYGON', srid=config.DEFAULT_SRID), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FloodZone(id={self.id}, severity='{self.severity}', status='{self.status}')>"


class CycloneTrack(Base):
    """
    Cyclone track model - stores cyclone paths and forecasts
    """
    __tablename__ = 'cyclone_tracks'

    id = Column(Integer, primary_key=True, index=True)
    cyclone_name = Column(String(255), nullable=False)
    category = Column(Integer)  # 1-5 Saffir-Simpson scale
    wind_speed = Column(Integer)  # km/h
    pressure = Column(Integer)  # hPa
    timestamp = Column(DateTime, nullable=False)
    forecast = Column(Boolean, default=False)  # True if forecast, False if actual
    status = Column(String(50))  # forming, active, weakening, dissipated

    # Spatial column - point geometry (cyclone center position)
    geom = Column(Geography(geometry_type='POINT', srid=config.DEFAULT_SRID), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CycloneTrack(id={self.id}, name='{self.cyclone_name}', category={self.category})>"


class DisasterUpdate(Base):
    """
    Disaster update model - stores real-time disaster updates and alerts
    """
    __tablename__ = 'disaster_updates'

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String(50), nullable=False)  # flood, cyclone, earthquake, fire
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(50))  # low, medium, high, critical
    status = Column(String(50))  # active, monitoring, resolved
    affected_areas = Column(Text)  # Comma-separated list of areas
    casualties = Column(Integer, default=0)
    displaced = Column(Integer, default=0)
    source = Column(String(255))  # Data source
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Optional spatial column - can be point or polygon
    geom = Column(Geography(geometry_type='GEOMETRY', srid=config.DEFAULT_SRID), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DisasterUpdate(id={self.id}, type='{self.disaster_type}', severity='{self.severity}')>"


# TODO: Add more models as needed:
# - EarthquakeEvent
# - EvacuationRoute
# - ResourceCenter
# - EmergencyContact
# - WeatherStation
