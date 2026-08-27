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
            zone_name=getattr(r, 'zone_name', r.zone_id) or r.zone_id,
            center_lat=r.center_lat,
            center_lon=r.center_lon,
            n_deficiency=r.n_deficiency,
            p_deficiency=r.p_deficiency,
            k_deficiency=r.k_deficiency,
            avg_ph=getattr(r, 'avg_ph', 6.8) or 6.8,
            avg_ec=getattr(r, 'avg_ec', 0.7) or 0.7,
            avg_health_score=getattr(r, 'avg_health_score', 80.0) or 80.0,
            priority=r.priority,
            urea_kg_ha=getattr(r, 'urea_kg_ha', round(r.n_deficiency / 0.46, 1)) or 0.0,
            ssp_kg_ha=getattr(r, 'ssp_kg_ha', round(r.p_deficiency / 0.16, 1)) or 0.0,
            mop_kg_ha=getattr(r, 'mop_kg_ha', round(r.k_deficiency / 0.60, 1)) or 0.0,
            amendment_note=getattr(r, 'amendment_note', "") or "",
            application_schedule=getattr(r, 'application_schedule', "") or "",
            recommendation_note=r.recommendation_note
        )
        for r in records
    ]
