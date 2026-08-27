import time
import logging
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.app.schemas.telemetry import SoilTelemetryBase
from backend.app.services.hardware_interface import GPSInterface, SoilSensorInterface, RoverHardwareInterface, MockGPS, MockSoilSensor, MockRover
from backend.app.config import settings

logger = logging.getLogger("rover_state_machine")

class RoverState(str, Enum):
    TRANSIT = "TRANSIT"
    DEPLOYMENT = "DEPLOYMENT"
    INTERROGATION = "INTERROGATION"
    RETRACTION = "RETRACTION"
    EMERGENCY_STOP = "EMERGENCY_STOP"

class RoverStateMachine:
    """
    Strict 4-state sequential rover state machine:
    TRANSIT -> DEPLOYMENT -> INTERROGATION -> RETRACTION -> TRANSIT
    Maintains safety interlocks, limit switch monitoring, stabilization countdowns, and telemetry generation.
    """

    def __init__(self,
                 gps: Optional[GPSInterface] = None,
                 sensor: Optional[SoilSensorInterface] = None,
                 hardware: Optional[RoverHardwareInterface] = None,
                 stabilization_seconds: int = None):
        self.gps = gps or MockGPS()
        self.sensor = sensor or MockSoilSensor()
        self.hardware = hardware or MockRover()
        self.stabilization_seconds = stabilization_seconds if stabilization_seconds is not None else settings.MOCK_STABILIZATION_SECONDS
        
        self.current_state = RoverState.TRANSIT
        self.mission_id = "M001"
        self.sample_counter = 1
        self.current_waypoint_index = 0
        
        self.waypoints = [
            {"lat": 11.3925, "lon": 77.7338, "id": "WP_001"},
            {"lat": 11.3928, "lon": 77.7345, "id": "WP_002"},
            {"lat": 11.3918, "lon": 77.7349, "id": "WP_003"},
            {"lat": 11.3915, "lon": 77.7340, "id": "WP_004"},
        ]
        
        self.active = False
        self.current_telemetry: Optional[SoilTelemetryBase] = None
        self.last_state_change = datetime.utcnow()
        self.logs: List[str] = []

    def log(self, message: str):
        entry = f"[{datetime.utcnow().strftime('%H:%M:%S')}] {message}"
        self.logs.append(entry)
        if len(self.logs) > 50:
            self.logs.pop(0)
        logger.info(message)

    def trigger_estop(self):
        self.current_state = RoverState.EMERGENCY_STOP
        self.hardware.emergency_stop()
        self.log("EMERGENCY STOP TRIGGERED! System halted safely.")

    def reset(self):
        self.current_state = RoverState.TRANSIT
        self.hardware.retract_probe()
        self.log("State machine reset to TRANSIT.")

    def step(self) -> Dict[str, Any]:
        """
        Advances the state machine step by step.
        """
        if self.current_state == RoverState.EMERGENCY_STOP:
            return self.get_status()

        target_wp = self.waypoints[self.current_waypoint_index]
        cur_lat, cur_lon, cur_alt = self.gps.read_coordinates()

        if self.current_state == RoverState.TRANSIT:
            # Check distance to waypoint
            lat_diff = abs(target_wp["lat"] - cur_lat)
            lon_diff = abs(target_wp["lon"] - cur_lon)
            
            if lat_diff < 0.00002 and lon_diff < 0.00002:
                # Waypoint reached! Velocity = 0
                self.hardware.set_motion(0.0, 0.0)
                self.current_state = RoverState.DEPLOYMENT
                self.last_state_change = datetime.utcnow()
                self.log(f"WAYPOINT {target_wp['id']} REACHED. Velocity set to 0. Transitioning to DEPLOYMENT.")
            else:
                # Update simulated position towards waypoint
                if isinstance(self.gps, MockGPS):
                    self.gps.update_position(target_wp["lat"], target_wp["lon"], step_ratio=0.3)
                self.hardware.set_motion(1.0, 0.0)

        elif self.current_state == RoverState.DEPLOYMENT:
            # Velocity must remain 0
            self.hardware.set_motion(0.0, 0.0)
            success = self.hardware.deploy_probe()
            if success:
                self.current_state = RoverState.INTERROGATION
                self.last_state_change = datetime.utcnow()
                self.log("BOTTOM LIMIT SWITCH TRIGGERED. Rack deployed. Transitioning to INTERROGATION.")
            else:
                self.trigger_estop()

        elif self.current_state == RoverState.INTERROGATION:
            self.hardware.set_motion(0.0, 0.0)
            elapsed = (datetime.utcnow() - self.last_state_change).total_seconds()
            
            if elapsed >= self.stabilization_seconds:
                # Interrogate soil sensor via Modbus RTU interface
                raw_reading = self.sensor.read_soil_parameters(cur_lat, cur_lon)
                sample_id = f"S{self.sample_counter:03d}"
                
                self.current_telemetry = SoilTelemetryBase(
                    sample_id=sample_id,
                    mission_id=self.mission_id,
                    timestamp=datetime.utcnow(),
                    latitude=cur_lat,
                    longitude=cur_lon,
                    altitude=cur_alt,
                    ph=raw_reading["ph"],
                    ec=raw_reading["ec"],
                    moisture=raw_reading["moisture"],
                    nitrogen=raw_reading["nitrogen"],
                    phosphorus=raw_reading["phosphorus"],
                    potassium=raw_reading["potassium"],
                    rover_state=self.current_state.value
                )
                
                self.sample_counter += 1
                self.log(f"SOIL INTERROGATION COMPLETE for {sample_id}. Sensor data retrieved & validated. Transitioning to RETRACTION.")
                self.current_state = RoverState.RETRACTION
                self.last_state_change = datetime.utcnow()

        elif self.current_state == RoverState.RETRACTION:
            self.hardware.set_motion(0.0, 0.0)
            success = self.hardware.retract_probe()
            if success:
                self.log("TOP LIMIT SWITCH TRIGGERED. Probe clear of ground. Transitioning to TRANSIT.")
                # Advance to next waypoint
                self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.waypoints)
                self.current_state = RoverState.TRANSIT
                self.last_state_change = datetime.utcnow()
            else:
                self.trigger_estop()

        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        lat, lon, alt = self.gps.read_coordinates()
        target_wp = self.waypoints[self.current_waypoint_index]
        hw_status = self.hardware.get_hardware_status()
        
        return {
            "rover_state": self.current_state.value,
            "mission_id": self.mission_id,
            "current_waypoint": target_wp,
            "waypoint_index": self.current_waypoint_index,
            "gps": {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt,
                "fix": self.gps.get_fix_status()
            },
            "hardware": hw_status,
            "latest_telemetry": self.current_telemetry.dict() if self.current_telemetry else None,
            "logs": self.logs[-10:]
        }
