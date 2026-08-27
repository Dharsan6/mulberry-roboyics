from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.services.state_machine import RoverStateMachine
from backend.app.database.connection import get_db
from backend.app.database.models import SoilObservationModel, SoilAnalysisModel, MissionModel
from backend.app.services.agronomy_service import agronomy_engine
from backend.app.schemas.telemetry import SoilTelemetryBase

router = APIRouter(prefix="/api/simulator", tags=["Simulator Control"])
sim_instance = RoverStateMachine(stabilization_seconds=0)

@router.get("/status")
def get_simulator_status():
    return sim_instance.get_status()

@router.post("/step")
def step_simulator(db: Session = Depends(get_db)):
    status = sim_instance.step()
    
    # If a new telemetry point was generated during INTERROGATION, save to DB
    if status.get("latest_telemetry"):
        t = status["latest_telemetry"]
        existing = db.query(SoilObservationModel).filter(SoilObservationModel.sample_id == t["sample_id"]).first()
        if not existing:
            # Ensure mission exists
            mission = db.query(MissionModel).filter(MissionModel.mission_id == t["mission_id"]).first()
            if not mission:
                mission = MissionModel(mission_id=t["mission_id"], mission_name="Live Autonomous Rover Mission", status="ACTIVE")
                db.add(mission)
                db.commit()

            obs = SoilObservationModel(
                sample_id=t["sample_id"],
                mission_id=t["mission_id"],
                mission_name=t.get("mission_name", "Live Rover Mission"),
                timestamp=datetime.utcnow(),
                latitude=t["latitude"],
                longitude=t["longitude"],
                altitude=t["altitude"],
                ph=t["ph"],
                ec=t["ec"],
                moisture=t["moisture"],
                temperature=t.get("temperature", 26.5),
                nitrogen=t["nitrogen"],
                phosphorus=t["phosphorus"],
                potassium=t["potassium"],
                organic_carbon=t.get("organic_carbon", 0.72),
                soil_health_index=t.get("soil_health_index", 80.0),
                soil_texture=t.get("soil_texture", "Red Sandy Loam"),
                mulberry_variety=t.get("mulberry_variety", "V1 (Victory-1)"),
                probe_depth_cm=t.get("probe_depth_cm", 15.0),
                battery_soc=t.get("battery_soc", 95.0),
                raw_modbus_hex=t.get("raw_modbus_hex"),
                rover_state=t["rover_state"],
                is_valid=True
            )
            db.add(obs)
            db.commit()

            # Agronomic analysis
            t_base = SoilTelemetryBase(**t)
            res = agronomy_engine.evaluate_sample(t_base)
            analysis_rec = SoilAnalysisModel(
                sample_id=t["sample_id"],
                ph_status=res.ph_status,
                ec_status=res.ec_status,
                n_deficiency=res.n_deficiency,
                p_deficiency=res.p_deficiency,
                k_deficiency=res.k_deficiency,
                urea_requirement=res.urea_requirement,
                ssp_requirement=res.ssp_requirement,
                mop_requirement=res.mop_requirement,
                lime_gypsum_requirement=res.lime_gypsum_requirement,
                fym_requirement=res.fym_requirement,
                bio_fertilizer_notes=res.bio_fertilizer_notes,
                overall_soil_status=res.overall_soil_status,
                sericulture_economic_impact=res.sericulture_economic_impact
            )
            db.add(analysis_rec)
            db.commit()

    return status

@router.post("/run_cycle")
def run_full_cycle(db: Session = Depends(get_db)):
    """Runs a complete 4-state cycle: TRANSIT -> DEPLOYMENT -> INTERROGATION -> RETRACTION -> TRANSIT"""
    steps_log = []
    for _ in range(5):
        st = step_simulator(db)
        steps_log.append({"state": st["rover_state"], "waypoint": st["current_waypoint"]["id"]})
        if st["rover_state"] == "TRANSIT":
            break
    return {"message": "Completed automated sampling cycle", "cycle_history": steps_log, "status": sim_instance.get_status()}

@router.post("/reset")
def reset_simulator():
    sim_instance.reset()
    return {"message": "Simulator reset to TRANSIT state"}

@router.post("/estop")
def estop_simulator():
    sim_instance.trigger_estop()
    return {"message": "Emergency Stop activated"}
