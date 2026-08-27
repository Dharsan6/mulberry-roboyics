from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import FertilizerPrescriptionModel
from backend.app.schemas.telemetry import FertilizerPrescriptionZone

router = APIRouter(prefix="/api/prescriptions", tags=["Fertilizer Prescriptions"])

@router.get("", response_model=List[FertilizerPrescriptionZone])
def get_prescriptions(db: Session = Depends(get_db)):
    records = db.query(FertilizerPrescriptionModel).all()
    return [
        FertilizerPrescriptionZone(
            zone_id=r.zone_id,
            center_lat=r.center_lat,
            center_lon=r.center_lon,
            n_deficiency=r.n_deficiency,
            p_deficiency=r.p_deficiency,
            k_deficiency=r.k_deficiency,
            priority=r.priority,
            recommendation_note=r.recommendation_note
        )
        for r in records
    ]
