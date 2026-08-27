from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from backend.app.database.connection import get_db
from backend.app.database.models import (
    SoilObservationModel, SoilAnalysisModel, MissionModel,
    SpatialPredictionModel, FertilizerPrescriptionModel
)
from ml.synthetic_generator import SyntheticPlantationGenerator
from ml.pipeline import run_full_ml_pipeline

router = APIRouter(prefix="/api/dataset", tags=["Mock Dataset Management"])

class DatasetGenerateRequest(BaseModel):
    num_samples: int = Field(default=1000, ge=50, le=10000, description="Number of synthetic samples to generate")
    retrain_models: bool = Field(default=True, description="Whether to retrain IDW, Random Forest, and EfficientNet models")

class ZoneInfo(BaseModel):
    zone_id: str
    name: str
    description: str
    center_lat: float
    center_lon: float
    target_deficiencies: List[str]
    dominant_soil_texture: str
    recommended_cultivars: List[str]

@router.get("/zones", response_model=List[ZoneInfo])
def get_agronomic_zones():
    """
    Returns detailed metadata for all 7 scientifically modeled Mulberry agronomic deficiency zones.
    """
    return [
        ZoneInfo(
            zone_id="Zone A",
            name="North-West Sector",
            description="Severe Nitrogen Deficiency causing Mulberry leaf chlorosis and stunted shoot elongation.",
            center_lat=11.3927,
            center_lon=77.7336,
            target_deficiencies=["Nitrogen (N) < 220 kg/ha", "Chlorosis"],
            dominant_soil_texture="Red Sandy Loam",
            recommended_cultivars=["V1 (Victory-1)", "S36"]
        ),
        ZoneInfo(
            zone_id="Zone B",
            name="North-East Sector",
            description="Phosphorus Deficiency leading to restricted root system development and foliar purpling.",
            center_lat=11.3927,
            center_lon=77.7348,
            target_deficiencies=["Phosphorus (P) < 80 kg/ha", "Restricted rooting"],
            dominant_soil_texture="Sandy Clay Loam",
            recommended_cultivars=["Kanva-2", "V1 (Victory-1)"]
        ),
        ZoneInfo(
            zone_id="Zone C",
            name="South-East Sector",
            description="Potassium Deficiency causing marginal necrosis and reduced leaf succulent moisture.",
            center_lat=11.3915,
            center_lon=77.7348,
            target_deficiencies=["Potassium (K) < 85 kg/ha", "Low drought resistance"],
            dominant_soil_texture="Red Sandy Clay",
            recommended_cultivars=["S36", "MR-2"]
        ),
        ZoneInfo(
            zone_id="Zone D",
            name="South-West Sector",
            description="Saline / High Electrical Conductivity patch with sodium and chloride salt accumulation.",
            center_lat=11.3915,
            center_lon=77.7336,
            target_deficiencies=["EC > 1.2 dS/m", "Osmotic stress"],
            dominant_soil_texture="Saline Clay Loam",
            recommended_cultivars=["AR-12", "MR-2"]
        ),
        ZoneInfo(
            zone_id="Zone E",
            name="Center-West Sector",
            description="Soil Acidification patch with pH < 5.8 causing aluminum and manganese toxicity risks.",
            center_lat=11.3921,
            center_lon=77.7338,
            target_deficiencies=["pH < 5.8 (Acidic)", "P-fixation risk"],
            dominant_soil_texture="Acidic Red Sandy Loam",
            recommended_cultivars=["V1 (Victory-1)"]
        ),
        ZoneInfo(
            zone_id="Zone F",
            name="Center-East Sector",
            description="Optimal Benchmark Sericulture Zone with balanced NPK, ideal pH (6.8-7.2), and high SOC.",
            center_lat=11.3921,
            center_lon=77.7346,
            target_deficiencies=["None (Optimal Benchmark)"],
            dominant_soil_texture="Rich Red Loam",
            recommended_cultivars=["V1 (Victory-1)", "S36", "Kanva-2"]
        ),
        ZoneInfo(
            zone_id="Zone G",
            name="South Central Depression",
            description="Poor drainage depression with high soil moisture (>65%) and anaerobic root rot risks.",
            center_lat=11.3913,
            center_lon=77.7342,
            target_deficiencies=["Excess Moisture > 65%", "Anaerobiosis"],
            dominant_soil_texture="Heavy Clay Loam",
            recommended_cultivars=["S36", "Kanva-2"]
        )
    ]

@router.get("/statistics")
def get_dataset_statistics(db: Session = Depends(get_db)):
    """
    Computes rich statistical summaries (mean, min, max, std, percentiles) for all mock soil observations.
    """
    observations = db.query(SoilObservationModel).all()
    if not observations:
        raise HTTPException(status_code=404, detail="No soil observations found in dataset.")

    data = [{
        "ph": o.ph,
        "ec": o.ec,
        "moisture": o.moisture,
        "temperature": o.temperature,
        "nitrogen": o.nitrogen,
        "phosphorus": o.phosphorus,
        "potassium": o.potassium,
        "organic_carbon": o.organic_carbon,
        "soil_health_index": o.soil_health_index
    } for o in observations]

    df = pd.DataFrame(data)
    stats = {}
    for col in df.columns:
        stats[col] = {
            "mean": round(float(df[col].mean()), 3),
            "std": round(float(df[col].std()), 3),
            "min": round(float(df[col].min()), 3),
            "p25": round(float(df[col].quantile(0.25)), 3),
            "median": round(float(df[col].median()), 3),
            "p75": round(float(df[col].quantile(0.75)), 3),
            "max": round(float(df[col].max()), 3)
        }

    variety_counts = db.query(SoilObservationModel.mulberry_variety, func.count(SoilObservationModel.id)).group_by(SoilObservationModel.mulberry_variety).all()
    texture_counts = db.query(SoilObservationModel.soil_texture, func.count(SoilObservationModel.id)).group_by(SoilObservationModel.soil_texture).all()

    return {
        "total_records": len(observations),
        "parameters": stats,
        "cultivar_distribution": {v[0]: v[1] for v in variety_counts if v[0]},
        "texture_distribution": {t[0]: t[1] for t in texture_counts if t[0]}
    }

@router.get("/raw")
def get_raw_mock_dataset(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    variety: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Queries raw mock soil observations with pagination, variety filter, and sensor telemetry.
    """
    query = db.query(SoilObservationModel)
    if variety:
        query = query.filter(SoilObservationModel.mulberry_variety.ilike(f"%{variety}%"))

    total = query.count()
    records = query.order_by(SoilObservationModel.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total_records": total,
        "total_pages": (total + limit - 1) // limit,
        "data": [
            {
                "sample_id": r.sample_id,
                "mission_id": r.mission_id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "ph": r.ph,
                "ec": r.ec,
                "moisture": r.moisture,
                "temperature": r.temperature,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "organic_carbon": r.organic_carbon,
                "soil_health_index": r.soil_health_index,
                "soil_texture": r.soil_texture,
                "mulberry_variety": r.mulberry_variety,
                "raw_modbus_hex": r.raw_modbus_hex
            }
            for r in records
        ]
    }

@router.post("/generate")
def generate_custom_mock_dataset(req: DatasetGenerateRequest, background_tasks: BackgroundTasks):
    """
    Triggers dynamic generation of synthetic mock dataset and optionally retrains all ML models.
    """
    def task_generate():
        run_full_ml_pipeline(num_samples=req.num_samples)

    background_tasks.add_task(task_generate)
    return {
        "status": "QUEUED",
        "message": f"Generating {req.num_samples} mock observations and retraining spatial ML pipeline in background."
    }

@router.delete("/clear")
def clear_mock_dataset(db: Session = Depends(get_db)):
    """
    Clears all soil observations, spatial predictions, and prescriptions from the database.
    """
    db.query(SoilAnalysisModel).delete()
    db.query(SoilObservationModel).delete()
    db.query(MissionModel).delete()
    db.query(SpatialPredictionModel).delete()
    db.query(FertilizerPrescriptionModel).delete()
    db.commit()

    return {"status": "SUCCESS", "message": "All mock observations and spatial grids cleared."}
