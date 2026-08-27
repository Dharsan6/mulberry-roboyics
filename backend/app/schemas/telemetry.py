from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class SoilTelemetryBase(BaseModel):
    sample_id: str = Field(..., json_schema_extra={"example": "S0001"})
    mission_id: str = Field(..., json_schema_extra={"example": "M001"})
    mission_name: Optional[str] = Field(default="Grid Sweep Sector A")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latitude: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 11.3921})
    longitude: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 77.7342})
    altitude: float = Field(default=320.0)
    
    # Core Sensor Measurements (ZTS-3002 Modbus RTU)
    ph: float = Field(..., ge=0.0, le=14.0, json_schema_extra={"example": 6.85})
    ec: float = Field(..., ge=0.0, json_schema_extra={"example": 0.65})  # dS/m
    moisture: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 46.0})  # %
    temperature: float = Field(default=26.5, ge=-10.0, le=60.0, json_schema_extra={"example": 26.5})  # °C
    
    # Macro-Nutrients (kg/ha)
    nitrogen: float = Field(..., ge=0.0, json_schema_extra={"example": 325.0})  # kg/ha
    phosphorus: float = Field(..., ge=0.0, json_schema_extra={"example": 135.0})  # kg/ha
    potassium: float = Field(..., ge=0.0, json_schema_extra={"example": 132.0})  # kg/ha
    
    # Agronomic & Environmental Context
    organic_carbon: float = Field(default=0.72, ge=0.0, le=5.0)  # SOC %
    soil_health_index: float = Field(default=85.0, ge=0.0, le=100.0)
    soil_texture: str = Field(default="Red Sandy Loam")
    mulberry_variety: str = Field(default="V1 (Victory-1)")
    probe_depth_cm: float = Field(default=15.0)
    battery_soc: float = Field(default=95.0)
    raw_modbus_hex: Optional[str] = Field(default=None)
    
    rover_state: str = Field(..., json_schema_extra={"example": "INTERROGATION"})
    is_valid: bool = Field(default=True)

class SoilTelemetryCreate(SoilTelemetryBase):
    pass

class SoilTelemetryResponse(SoilTelemetryBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

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
    temperature: float
    organic_carbon: float
    soil_health_index: float
    
    nitrogen: float
    n_deficiency: float  # kg/ha shortfall
    urea_requirement: float  # kg/ha commercial urea needed
    
    phosphorus: float
    p_deficiency: float  # kg/ha shortfall
    ssp_requirement: float  # kg/ha SSP needed
    
    potassium: float
    k_deficiency: float  # kg/ha shortfall
    mop_requirement: float  # kg/ha MOP needed
    
    lime_gypsum_requirement: float  # tons/ha for pH amendment
    fym_requirement: float  # tons/ha farmyard manure
    bio_fertilizer_notes: str
    
    overall_soil_status: str  # SUFFICIENT, DEFICIENT, SEVERE_DEFICIENCY
    sericulture_economic_impact: str

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
    predicted_moisture: float
    predicted_temperature: float
    predicted_soil_health: float

class SpatialGridResponse(BaseModel):
    model_type: str  # "IDW", "RandomForest", "EfficientNet"
    timestamp: datetime
    total_grid_points: int
    predictions: List[SpatialPredictionPoint]

class FertilizerPrescriptionZone(BaseModel):
    zone_id: str
    zone_name: str
    center_lat: float
    center_lon: float
    n_deficiency: float
    p_deficiency: float
    k_deficiency: float
    avg_ph: float
    avg_ec: float
    avg_health_score: float
    priority: str  # HIGH, MODERATE, LOW
    urea_kg_ha: float
    ssp_kg_ha: float
    mop_kg_ha: float
    amendment_note: str
    application_schedule: str
    recommendation_note: str

class MissionSummary(BaseModel):
    mission_id: str
    mission_name: str
    status: str
    total_samples: int
    avg_ph: float
    avg_health_index: float
    started_at: datetime
    completed_at: Optional[datetime]

class PlantationSummaryResponse(BaseModel):
    total_samples: int
    total_missions: int
    current_rover_state: str
    latest_gps: dict
    avg_ph: float
    avg_ec: float
    avg_moisture: float
    avg_temperature: float
    avg_soil_health: float
    total_n_deficiency: float
    total_p_deficiency: float
    total_k_deficiency: float
    total_urea_needed_kg: float
    total_ssp_needed_kg: float
    total_mop_needed_kg: float
    rover_battery_soc: float
    system_status: str
