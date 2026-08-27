import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from backend.app.services.state_machine import RoverStateMachine, RoverState

def test_state_machine_sequential_flow():
    sm = RoverStateMachine(stabilization_seconds=0)
    assert sm.current_state == RoverState.TRANSIT

    # Override read_coordinates to return exact target waypoint
    target_wp = sm.waypoints[0]
    sm.gps.read_coordinates = lambda: (target_wp["lat"], target_wp["lon"], 320.0)

    # 1. Step in TRANSIT -> detects waypoint reached -> transitions to DEPLOYMENT
    sm.step()
    assert sm.current_state == RoverState.DEPLOYMENT

    # 2. Step in DEPLOYMENT -> deploys rack -> transitions to INTERROGATION
    sm.step()
    assert sm.current_state == RoverState.INTERROGATION

    # Wait 0.05s to ensure elapsed >= 0.0
    time.sleep(0.05)

    # 3. Step in INTERROGATION -> stabilization (0s) complete -> reads sensor & transitions to RETRACTION
    sm.step()
    assert sm.current_state == RoverState.RETRACTION

    # 4. Step in RETRACTION -> retracts rack -> transitions back to TRANSIT
    sm.step()
    assert sm.current_state == RoverState.TRANSIT

def test_emergency_stop():
    sm = RoverStateMachine()
    sm.trigger_estop()
    assert sm.current_state == RoverState.EMERGENCY_STOP
    
    # Motion should be blocked
    status = sm.step()
    assert sm.current_state == RoverState.EMERGENCY_STOP
