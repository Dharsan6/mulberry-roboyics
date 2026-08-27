from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database.connection import get_db
from backend.app.database.models import SoilObservationModel, SoilAnalysisModel, MissionModel
from backend.app.schemas.telemetry import SoilTelemetryCreate, SoilTelemetryResponse, AgronomicAnalysisResponse
from backend.app.services.agronomy_service import agronomy_engine
from backend.app.services.modbus_decoder import ZTS3002ModbusDecoder

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.post("", response_model=SoilTelemetryResponse, status_code=201)
def receive_telemetry(payload: SoilTelemetryCreate, db: Session = Depends(get_db)):
    """
    Receives soil telemetry from ROS 2 node, micro-ROS agent, or ESP32 rover.
    Validates range bounds, stores raw observation, and triggers agronomic analysis.
    """
    # Range validation
    valid, msg = ZTS3002ModbusDecoder.validate_reading(payload.model_dump())
    if not valid:
        raise HTTPException(status_code=400, detail=f"Invalid sensor telemetry: {msg}")

    # Ensure mission exists
    mission = db.query(MissionModel).filter(MissionModel.mission_id == payload.mission_id).first()
    if not mission:
        mission = MissionModel(mission_id=payload.mission_id, status="ACTIVE")
        db.add(mission)
        db.commit()

    # Check for existing sample_id
    existing = db.query(SoilObservationModel).filter(SoilObservationModel.sample_id == payload.sample_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Sample ID '{payload.sample_id}' already exists.")

    # Save Soil Observation
    obs = SoilObservationModel(
        sample_id=payload.sample_id,
        mission_id=payload.mission_id,
        timestamp=payload.timestamp or datetime.utcnow(),
        latitude=payload.latitude,
        longitude=payload.longitude,
        altitude=payload.altitude,
        ph=payload.ph,
        ec=payload.ec,
        moisture=payload.moisture,
        nitrogen=payload.nitrogen,
        phosphorus=payload.phosphorus,
        potassium=payload.potassium,
        rover_state=payload.rover_state,
        is_valid=valid
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)

    # Perform Agronomic Analysis
    analysis_res = agronomy_engine.evaluate_sample(payload)
    analysis_rec = SoilAnalysisModel(
        sample_id=payload.sample_id,
        ph_status=analysis_res.ph_status,
        ec_status=analysis_res.ec_status,
        n_deficiency=analysis_res.n_deficiency,
        p_deficiency=analysis_res.p_deficiency,
        k_deficiency=analysis_res.k_deficiency,
        overall_soil_status=analysis_res.overall_soil_status
    )
    db.add(analysis_rec)
    db.commit()

    return obs

@router.get("", response_model=List[SoilTelemetryResponse])
def get_telemetry_list(
    mission_id: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    query = db.query(SoilObservationModel)
    if mission_id:
        query = query.filter(SoilObservationModel.mission_id == mission_id)
    return query.order_by(SoilObservationModel.timestamp.desc()).limit(limit).all()
