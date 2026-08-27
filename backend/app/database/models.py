from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

class MissionModel(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    mission_id = Column(String, unique=True, index=True, nullable=False)
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
    altitude = Column(Float, default=0.0)
    rover_state = Column(String, default="TRANSIT")

class SoilObservationModel(Base):
    __tablename__ = "soil_observations"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(String, unique=True, index=True, nullable=False)
    mission_id = Column(String, ForeignKey("missions.mission_id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    altitude = Column(Float, default=0.0)
    
    ph = Column(Float, nullable=False)
    ec = Column(Float, nullable=False)  # dS/m
    moisture = Column(Float, nullable=False)  # %
    
    nitrogen = Column(Float, nullable=False)  # kg/ha
    phosphorus = Column(Float, nullable=False)  # kg/ha
    potassium = Column(Float, nullable=False)  # kg/ha
    
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
    
    overall_soil_status = Column(String, nullable=False)

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

class FertilizerPrescriptionModel(Base):
    __tablename__ = "fertilizer_prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    center_lat = Column(Float)
    center_lon = Column(Float)
    n_deficiency = Column(Float)
    p_deficiency = Column(Float)
    k_deficiency = Column(Float)
    priority = Column(String)  # HIGH, MODERATE, LOW
    recommendation_note = Column(String)
