from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io

from backend.app.database.connection import get_db
from backend.app.database.models import MissionModel, SoilObservationModel, SoilAnalysisModel
from backend.app.schemas.telemetry import MissionSummary

router = APIRouter(prefix="/api/missions", tags=["Missions"])

@router.get("", response_model=List[MissionSummary])
def get_all_missions(db: Session = Depends(get_db)):
    missions = db.query(MissionModel).order_by(MissionModel.started_at.desc()).all()
    res = []
    for m in missions:
        count = db.query(SoilObservationModel).filter(SoilObservationModel.mission_id == m.mission_id).count()
        avg_ph = db.query(func.avg(SoilObservationModel.ph)).filter(SoilObservationModel.mission_id == m.mission_id).scalar() or 6.8
        avg_health = db.query(func.avg(SoilObservationModel.soil_health_index)).filter(SoilObservationModel.mission_id == m.mission_id).scalar() or 80.0
        
        res.append(MissionSummary(
            mission_id=m.mission_id,
            mission_name=getattr(m, 'mission_name', f"Mission {m.mission_id}") or f"Mission {m.mission_id}",
            status=m.status,
            total_samples=count,
            avg_ph=round(avg_ph, 2),
            avg_health_index=round(avg_health, 1),
            started_at=m.started_at,
            completed_at=m.completed_at
        ))
    return res

@router.get("/export/csv")
def export_dataset_csv(db: Session = Depends(get_db)):
    samples = db.query(SoilObservationModel).all()
    rows = []
    for s in samples:
        rows.append({
            "sample_id": s.sample_id,
            "mission_id": s.mission_id,
            "mission_name": getattr(s, 'mission_name', ""),
            "timestamp": s.timestamp.isoformat() if s.timestamp else "",
            "latitude": s.latitude,
            "longitude": s.longitude,
            "altitude": s.altitude,
            "ph": s.ph,
            "ec_ds_m": s.ec,
            "moisture_pct": s.moisture,
            "temperature_c": getattr(s, 'temperature', 26.5),
            "nitrogen_kg_ha": s.nitrogen,
            "phosphorus_kg_ha": s.phosphorus,
            "potassium_kg_ha": s.potassium,
            "organic_carbon_pct": getattr(s, 'organic_carbon', 0.72),
            "soil_health_index": getattr(s, 'soil_health_index', 80.0),
            "soil_texture": getattr(s, 'soil_texture', "Red Sandy Loam"),
            "mulberry_variety": getattr(s, 'mulberry_variety', "V1"),
            "probe_depth_cm": getattr(s, 'probe_depth_cm', 15.0),
            "battery_soc": getattr(s, 'battery_soc', 95.0),
            "raw_modbus_hex": getattr(s, 'raw_modbus_hex', "")
        })
    df = pd.DataFrame(rows)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mulberry_soil_observations.csv"}
    )
