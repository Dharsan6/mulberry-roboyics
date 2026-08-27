import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_telemetry_post_and_get():
    unique_id = f"S_TEST_{uuid.uuid4().hex[:6]}"
    payload = {
        "sample_id": unique_id,
        "mission_id": "M_TEST_001",
        "timestamp": "2026-08-27T10:00:00Z",
        "latitude": 11.3921,
        "longitude": 77.7342,
        "altitude": 320.0,
        "ph": 6.8,
        "ec": 0.75,
        "moisture": 45.0,
        "nitrogen": 280.0,
        "phosphorus": 110.0,
        "potassium": 120.0,
        "rover_state": "INTERROGATION"
    }
    
    res = client.post("/api/telemetry", json=payload)
    assert res.status_code == 201
    
    get_res = client.get(f"/api/samples/{unique_id}")
    assert get_res.status_code == 200
    assert get_res.json()["sample_id"] == unique_id

def test_invalid_telemetry_range():
    payload = {
        "sample_id": f"INVALID_{uuid.uuid4().hex[:6]}",
        "mission_id": "M001",
        "latitude": 11.3921,
        "longitude": 77.7342,
        "ph": 18.0,  # Invalid pH (>14)
        "ec": 0.5,
        "moisture": 40.0,
        "nitrogen": 200.0,
        "phosphorus": 100.0,
        "potassium": 100.0,
        "rover_state": "INTERROGATION"
    }
    res = client.post("/api/telemetry", json=payload)
    assert res.status_code == 422

def test_plantation_summary():
    res = client.get("/api/plantation/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_samples" in data
    assert "avg_ph" in data
    assert "system_status" in data

def test_prescriptions_endpoint():
    res = client.get("/api/prescriptions")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_predictions_endpoint():
    res = client.get("/api/predictions?model_type=EfficientNet")
    assert res.status_code == 200
    data = res.json()
    assert "predictions" in data

def test_simulator_endpoints():
    status = client.get("/api/simulator/status")
    assert status.status_code == 200
    assert "rover_state" in status.json()

    step_res = client.post("/api/simulator/step")
    assert step_res.status_code == 200

def test_missions_endpoint():
    res = client.get("/api/missions")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
