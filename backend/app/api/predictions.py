from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database.connection import get_db
from backend.app.database.models import SpatialPredictionModel
from backend.app.schemas.telemetry import SpatialPredictionPoint, SpatialGridResponse

router = APIRouter(prefix="/api/predictions", tags=["Spatial Predictions"])

@router.get("", response_model=SpatialGridResponse)
def get_spatial_predictions(
    model_type: str = Query(default="EfficientNet", description="IDW, RandomForest, or EfficientNet"),
    db: Session = Depends(get_db)
):
    preds = db.query(SpatialPredictionModel).filter(SpatialPredictionModel.model_type == model_type).all()
    if not preds:
        # Fallback to IDW if specific model not yet populated
        preds = db.query(SpatialPredictionModel).all()
    
    points = [
        SpatialPredictionPoint(
            grid_x=p.grid_x,
            grid_y=p.grid_y,
            latitude=p.latitude,
            longitude=p.longitude,
            predicted_n_deficiency=p.predicted_n_deficiency or 0.0,
            predicted_p_deficiency=p.predicted_p_deficiency or 0.0,
            predicted_k_deficiency=p.predicted_k_deficiency or 0.0,
            predicted_ph=p.predicted_ph or 6.8,
            predicted_ec=p.predicted_ec or 0.7,
            predicted_moisture=getattr(p, 'predicted_moisture', 45.0) or 45.0,
            predicted_temperature=getattr(p, 'predicted_temperature', 26.5) or 26.5,
            predicted_soil_health=getattr(p, 'predicted_soil_health', 80.0) or 80.0
        )
        for p in preds
    ]
    
    return SpatialGridResponse(
        model_type=model_type,
        timestamp=datetime.utcnow(),
        total_grid_points=len(points),
        predictions=points
    )

@router.get("/{parameter}")
def get_parameter_heatmap_grid(
    parameter: str,
    model_type: str = Query(default="EfficientNet", description="IDW, RandomForest, or EfficientNet"),
    db: Session = Depends(get_db)
):
    preds = db.query(SpatialPredictionModel).filter(SpatialPredictionModel.model_type == model_type).all()
    if not preds:
        preds = db.query(SpatialPredictionModel).filter(SpatialPredictionModel.model_type == "IDW").all()
    if not preds:
        preds = db.query(SpatialPredictionModel).all()
    
    param_attr_map = {
        "n_deficiency": "predicted_n_deficiency",
        "p_deficiency": "predicted_p_deficiency",
        "k_deficiency": "predicted_k_deficiency",
        "ph": "predicted_ph",
        "ec": "predicted_ec",
        "moisture": "predicted_moisture",
        "temperature": "predicted_temperature",
        "soil_health": "predicted_soil_health"
    }
    
    attr = param_attr_map.get(parameter.lower(), "predicted_n_deficiency")
    
    return [
        {
            "lat": p.latitude,
            "lon": p.longitude,
            "val": float(getattr(p, attr, 0.0) or 0.0)
        }
        for p in preds
    ]
