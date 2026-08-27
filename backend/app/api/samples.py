from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import SoilObservationModel
from backend.app.schemas.telemetry import SoilTelemetryResponse

router = APIRouter(prefix="/api/samples", tags=["Samples"])

@router.get("", response_model=List[SoilTelemetryResponse])
def get_all_samples(db: Session = Depends(get_db)):
    return db.query(SoilObservationModel).order_by(SoilObservationModel.created_at.desc()).all()

@router.get("/{sample_id}", response_model=SoilTelemetryResponse)
def get_sample_by_id(sample_id: str, db: Session = Depends(get_db)):
    sample = db.query(SoilObservationModel).filter(SoilObservationModel.sample_id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")
    return sample
