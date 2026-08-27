from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class SoilTelemetryBase(BaseModel):
    sample_id: str = Field(..., example="S001")
    mission_id: str = Field(..., example="M001")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latitude: float = Field(..., ge=-90.0, le=90.0, example=11.3921)
    longitude: float = Field(..., ge=-180.0, le=180.0, example=77.7342)
    altitude: float = Field(default=0.0)
    
    ph: float = Field(..., ge=0.0, le=14.0, example=6.5)
    ec: float = Field(..., ge=0.0, example=0.75)  # dS/m
    moisture: float = Field(..., ge=0.0, le=100.0, example=45.0)  # %
    
    nitrogen: float = Field(..., ge=0.0, example=280.0)  # kg/ha
    phosphorus: float = Field(..., ge=0.0, example=110.0)  # kg/ha
    potassium: float = Field(..., ge=0.0, example=120.0)  # kg/ha
    
    rover_state: str = Field(..., example="INTERROGATION")
    is_valid: bool = Field(default=True)

class SoilTelemetryCreate(SoilTelemetryBase):
    pass

class SoilTelemetryResponse(SoilTelemetryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AgronomicAnalysisResponse(BaseModel):
    sample_id: str
    mission_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    
    ph: float
    ph_status: str  # LOW, OPTIMAL, HIGH
    
    ec: float
    ec_status: str  # NORMAL, HIGH
    
    moisture: float
    
    nitrogen: float
    n_deficiency: float  # kg/ha shortfall
    
    phosphorus: float
    p_deficiency: float  # kg/ha shortfall
    
    potassium: float
    k_deficiency: float  # kg/ha shortfall
    
    overall_soil_status: str  # SUFFICIENT, DEFICIENT, SEVERE_DEFICIENCY

class SpatialPredictionPoint(BaseModel):
    grid_x: int
    grid_y: int
    latitude: float
    longitude: float
    predicted_n_deficiency: float
    predicted_p_deficiency: float
    predicted_k_deficiency: float
    predicted_ph: float
    predicted_ec: float

class SpatialGridResponse(BaseModel):
    model_type: str  # "IDW", "RandomForest", "EfficientNet"
    timestamp: datetime
    total_grid_points: int
    predictions: List[SpatialPredictionPoint]

class FertilizerPrescriptionZone(BaseModel):
    zone_id: str
    center_lat: float
    center_lon: float
    n_deficiency: float
    p_deficiency: float
    k_deficiency: float
    priority: str  # HIGH, MODERATE, LOW
    recommendation_note: str

class PlantationSummaryResponse(BaseModel):
    total_samples: int
    total_missions: int
    current_rover_state: str
    latest_gps: dict
    avg_ph: float
    avg_ec: float
    avg_moisture: float
    total_n_deficiency: float
    total_p_deficiency: float
    total_k_deficiency: float
    system_status: str
