from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class MissionModel(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    mission_id = Column(String, unique=True, index=True, nullable=False)
    mission_name = Column(String, default="Standard Grid Survey")
    status = Column(String, default="ACTIVE")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    observations = relationship("SoilObservationModel", back_populates="mission")

class RoverLocationModel(Base):
    __tablename__ = "rover_locations"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    altitude = Column(Float, default=320.0)
    heading_deg = Column(Float, default=0.0)
    speed_mps = Column(Float, default=0.0)
    battery_soc = Column(Float, default=100.0)
    rover_state = Column(String, default="TRANSIT")

class SoilObservationModel(Base):
    __tablename__ = "soil_observations"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String, unique=True, index=True, nullable=False)
    mission_id = Column(String, ForeignKey("missions.mission_id"), index=True, nullable=False)
    mission_name = Column(String, default="Standard Grid Survey")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    altitude = Column(Float, default=320.0)
    
    # Measurements
    ph = Column(Float, nullable=False)
    ec = Column(Float, nullable=False)  # dS/m
    moisture = Column(Float, nullable=False)  # %
    temperature = Column(Float, default=26.5)  # °C
    
    nitrogen = Column(Float, nullable=False)  # kg/ha
    phosphorus = Column(Float, nullable=False)  # kg/ha
    potassium = Column(Float, nullable=False)  # kg/ha
    
    organic_carbon = Column(Float, default=0.72)  # % SOC
    soil_health_index = Column(Float, default=85.0)  # 0-100
    soil_texture = Column(String, default="Red Sandy Loam")
    mulberry_variety = Column(String, default="V1 (Victory-1)")
    probe_depth_cm = Column(Float, default=15.0)
    battery_soc = Column(Float, default=95.0)
    raw_modbus_hex = Column(String, nullable=True)
    
    rover_state = Column(String, default="INTERROGATION")
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mission = relationship("MissionModel", back_populates="observations")
    analysis = relationship("SoilAnalysisModel", back_populates="observation", uselist=False)

    __table_args__ = (
        Index("idx_spatial_coords", "latitude", "longitude"),
        Index("idx_sample_mission", "sample_id", "mission_id"),
    )

class SoilAnalysisModel(Base):
    __tablename__ = "soil_analysis"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String, ForeignKey("soil_observations.sample_id"), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    ph_status = Column(String, nullable=False)
    ec_status = Column(String, nullable=False)
    
    n_deficiency = Column(Float, nullable=False)
    p_deficiency = Column(Float, nullable=False)
    k_deficiency = Column(Float, nullable=False)
    
    urea_requirement = Column(Float, default=0.0)
    ssp_requirement = Column(Float, default=0.0)
    mop_requirement = Column(Float, default=0.0)
    lime_gypsum_requirement = Column(Float, default=0.0)
    fym_requirement = Column(Float, default=20.0)
    bio_fertilizer_notes = Column(Text, nullable=True)
    
    overall_soil_status = Column(String, nullable=False)
    sericulture_economic_impact = Column(Text, nullable=True)

    observation = relationship("SoilObservationModel", back_populates="analysis")

class SpatialPredictionModel(Base):
    __tablename__ = "spatial_predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String, index=True)  # IDW, RandomForest, EfficientNet
    created_at = Column(DateTime, default=datetime.utcnow)
    grid_x = Column(Integer)
    grid_y = Column(Integer)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    predicted_n_deficiency = Column(Float)
    predicted_p_deficiency = Column(Float)
    predicted_k_deficiency = Column(Float)
    predicted_ph = Column(Float)
    predicted_ec = Column(Float)
    predicted_moisture = Column(Float, default=45.0)
    predicted_temperature = Column(Float, default=26.5)
    predicted_soil_health = Column(Float, default=80.0)

    __table_args__ = (
        Index("idx_model_grid", "model_type", "grid_x", "grid_y"),
    )

class FertilizerPrescriptionModel(Base):
    __tablename__ = "fertilizer_prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String, index=True)
    zone_name = Column(String, default="Plantation Sector")
    created_at = Column(DateTime, default=datetime.utcnow)
    center_lat = Column(Float)
    center_lon = Column(Float)
    n_deficiency = Column(Float)
    p_deficiency = Column(Float)
    k_deficiency = Column(Float)
    avg_ph = Column(Float, default=6.8)
    avg_ec = Column(Float, default=0.7)
    avg_health_score = Column(Float, default=80.0)
    priority = Column(String)  # HIGH, MODERATE, LOW
    urea_kg_ha = Column(Float, default=0.0)
    ssp_kg_ha = Column(Float, default=0.0)
    mop_kg_ha = Column(Float, default=0.0)
    amendment_note = Column(Text, nullable=True)
    application_schedule = Column(Text, nullable=True)
    recommendation_note = Column(Text)
