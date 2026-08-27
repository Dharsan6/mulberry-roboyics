from fastapi import APIRouter
from backend.app.services.state_machine import RoverStateMachine

router = APIRouter(prefix="/api/simulator", tags=["Simulator Control"])
sim_instance = RoverStateMachine()

@router.get("/status")
def get_simulator_status():
    return sim_instance.get_status()

@router.post("/step")
def step_simulator():
    return sim_instance.step()

@router.post("/reset")
def reset_simulator():
    sim_instance.reset()
    return {"message": "Simulator reset to TRANSIT state"}

@router.post("/estop")
def estop_simulator():
    sim_instance.trigger_estop()
    return {"message": "Emergency Stop activated"}
