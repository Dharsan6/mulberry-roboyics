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
    model_type: str = Query(default="IDW", description="IDW, RandomForest, or EfficientNet"),
    db: Session = Depends(get_db)
):
    preds = db.query(SpatialPredictionModel).filter(SpatialPredictionModel.model_type == model_type).all()
    
    points = [
        SpatialPredictionPoint(
            grid_x=p.grid_x,
            grid_y=p.grid_y,
            latitude=p.latitude,
            longitude=p.longitude,
            predicted_n_deficiency=p.predicted_n_deficiency,
            predicted_p_deficiency=p.predicted_p_deficiency,
            predicted_k_deficiency=p.predicted_k_deficiency,
            predicted_ph=p.predicted_ph,
            predicted_ec=p.predicted_ec
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
def get_parameter_heatmap_grid(parameter: str, model_type: str = "IDW", db: Session = Depends(get_db)):
    preds = db.query(SpatialPredictionModel).filter(SpatialPredictionModel.model_type == model_type).all()
    
    param_attr_map = {
        "n_deficiency": "predicted_n_deficiency",
        "p_deficiency": "predicted_p_deficiency",
        "k_deficiency": "predicted_k_deficiency",
        "ph": "predicted_ph",
        "ec": "predicted_ec"
    }
    
    attr = param_attr_map.get(parameter.lower(), "predicted_n_deficiency")
    
    return [
        {
            "lat": p.latitude,
            "lon": p.longitude,
            "val": getattr(p, attr, 0.0)
        }
        for p in preds
    ]
