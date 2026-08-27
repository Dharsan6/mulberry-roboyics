from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.connection import get_db
from backend.app.database.models import SoilObservationModel, SoilAnalysisModel, MissionModel
from backend.app.schemas.telemetry import AgronomicAnalysisResponse, PlantationSummaryResponse, SoilTelemetryBase
from backend.app.services.agronomy_service import agronomy_engine

router = APIRouter(tags=["Agronomic Analysis & Summary"])

@router.get("/api/analysis/{sample_id}", response_model=AgronomicAnalysisResponse)
def get_sample_analysis(sample_id: str, db: Session = Depends(get_db)):
    obs = db.query(SoilObservationModel).filter(SoilObservationModel.sample_id == sample_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")
    
    telemetry_base = SoilTelemetryBase(
        sample_id=obs.sample_id,
        mission_id=obs.mission_id,
        mission_name=getattr(obs, 'mission_name', "Standard Grid Survey"),
        timestamp=obs.timestamp,
        latitude=obs.latitude,
        longitude=obs.longitude,
        altitude=obs.altitude,
        ph=obs.ph,
        ec=obs.ec,
        moisture=obs.moisture,
        temperature=getattr(obs, 'temperature', 26.5),
        nitrogen=obs.nitrogen,
        phosphorus=obs.phosphorus,
        potassium=obs.potassium,
        organic_carbon=getattr(obs, 'organic_carbon', 0.72),
        soil_health_index=getattr(obs, 'soil_health_index', 80.0),
        soil_texture=getattr(obs, 'soil_texture', "Red Sandy Loam"),
        mulberry_variety=getattr(obs, 'mulberry_variety', "V1 (Victory-1)"),
        rover_state=obs.rover_state
    )
    return agronomy_engine.evaluate_sample(telemetry_base)

@router.get("/api/plantation/summary", response_model=PlantationSummaryResponse)
def get_plantation_summary(db: Session = Depends(get_db)):
    total_samples = db.query(SoilObservationModel).count()
    total_missions = db.query(MissionModel).count()
    
    latest_obs = db.query(SoilObservationModel).order_by(SoilObservationModel.timestamp.desc()).first()
    
    if total_samples > 0:
        avg_ph = db.query(func.avg(SoilObservationModel.ph)).scalar() or 6.8
        avg_ec = db.query(func.avg(SoilObservationModel.ec)).scalar() or 0.65
        avg_moisture = db.query(func.avg(SoilObservationModel.moisture)).scalar() or 46.0
        avg_temp = db.query(func.avg(SoilObservationModel.temperature)).scalar() or 26.5
        avg_health = db.query(func.avg(SoilObservationModel.soil_health_index)).scalar() or 80.0
        
        sum_n_def = db.query(func.sum(SoilAnalysisModel.n_deficiency)).scalar() or 0.0
        sum_p_def = db.query(func.sum(SoilAnalysisModel.p_deficiency)).scalar() or 0.0
        sum_k_def = db.query(func.sum(SoilAnalysisModel.k_deficiency)).scalar() or 0.0
        sum_urea = db.query(func.sum(SoilAnalysisModel.urea_requirement)).scalar() or 0.0
        sum_ssp = db.query(func.sum(SoilAnalysisModel.ssp_requirement)).scalar() or 0.0
        sum_mop = db.query(func.sum(SoilAnalysisModel.mop_requirement)).scalar() or 0.0
    else:
        avg_ph, avg_ec, avg_moisture, avg_temp, avg_health = 6.85, 0.65, 46.0, 26.5, 82.0
        sum_n_def, sum_p_def, sum_k_def = 0.0, 0.0, 0.0
        sum_urea, sum_ssp, sum_mop = 0.0, 0.0, 0.0

    return PlantationSummaryResponse(
        total_samples=total_samples,
        total_missions=max(1, total_missions),
        current_rover_state=latest_obs.rover_state if latest_obs else "TRANSIT",
        latest_gps={
            "latitude": latest_obs.latitude if latest_obs else 11.3921,
            "longitude": latest_obs.longitude if latest_obs else 77.7342
        },
        avg_ph=round(avg_ph, 2),
        avg_ec=round(avg_ec, 2),
        avg_moisture=round(avg_moisture, 1),
        avg_temperature=round(avg_temp, 1),
        avg_soil_health=round(avg_health, 1),
        total_n_deficiency=round(sum_n_def, 1),
        total_p_deficiency=round(sum_p_def, 1),
        total_k_deficiency=round(sum_k_def, 1),
        total_urea_needed_kg=round(sum_urea, 1),
        total_ssp_needed_kg=round(sum_ssp, 1),
        total_mop_needed_kg=round(sum_mop, 1),
        rover_battery_soc=getattr(latest_obs, 'battery_soc', 95.0) if latest_obs else 95.0,
        system_status="ONLINE"
    )
