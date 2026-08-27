import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from datetime import datetime
from backend.app.schemas.telemetry import SoilTelemetryBase
from backend.app.services.agronomy_service import AgronomyEngine

def test_agronomy_evaluation_optimal():
    engine = AgronomyEngine()
    sample = SoilTelemetryBase(
        sample_id="S001",
        mission_id="M001",
        timestamp=datetime.utcnow(),
        latitude=11.3921,
        longitude=77.7342,
        ph=6.8,
        ec=0.75,
        moisture=45.0,
        nitrogen=350.0,
        phosphorus=140.0,
        potassium=140.0,
        rover_state="INTERROGATION"
    )
    res = engine.evaluate_sample(sample)
    assert res.ph_status == "OPTIMAL"
    assert res.ec_status == "NORMAL"
    assert res.n_deficiency == 0.0
    assert res.p_deficiency == 0.0
    assert res.k_deficiency == 0.0
    assert res.overall_soil_status == "SUFFICIENT"

def test_agronomy_evaluation_deficiencies():
    engine = AgronomyEngine()
    sample = SoilTelemetryBase(
        sample_id="S002",
        mission_id="M001",
        timestamp=datetime.utcnow(),
        latitude=11.3921,
        longitude=77.7342,
        ph=5.8,  # LOW pH
        ec=1.35, # HIGH EC
        moisture=30.0,
        nitrogen=250.0,  # 100 kg/ha N deficiency
        phosphorus=90.0,   # 50 kg/ha P deficiency
        potassium=100.0,  # 40 kg/ha K deficiency
        rover_state="INTERROGATION"
    )
    res = engine.evaluate_sample(sample)
    assert res.ph_status == "LOW"
    assert res.ec_status == "HIGH"
    assert res.n_deficiency == 100.0
    assert res.p_deficiency == 50.0
    assert res.k_deficiency == 40.0
    assert res.overall_soil_status in ["DEFICIENT", "SEVERE_DEFICIENCY"]
