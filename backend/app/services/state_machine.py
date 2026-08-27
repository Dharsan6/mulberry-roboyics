import time
import logging
import math
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
        
        # 8 Comprehensive Plantation Waypoints
        self.waypoints = [
            {"lat": 11.3927, "lon": 77.7336, "id": "WP_NW01", "desc": "Zone A: Nitrogen Deficiency Sector"},
            {"lat": 11.3927, "lon": 77.7348, "id": "WP_NE02", "desc": "Zone B: Phosphorus Deficiency Sector"},
            {"lat": 11.3921, "lon": 77.7345, "id": "WP_CE03", "desc": "Zone F: High-Yield Benchmark Sector"},
            {"lat": 11.3915, "lon": 77.7348, "id": "WP_SE04", "desc": "Zone C: Potassium Deficiency Sector"},
            {"lat": 11.3913, "lon": 77.7342, "id": "WP_SC05", "desc": "Zone G: Drainage Depression Sector"},
            {"lat": 11.3915, "lon": 77.7336, "id": "WP_SW06", "desc": "Zone D: Saline / High EC Sector"},
            {"lat": 11.3921, "lon": 77.7338, "id": "WP_CW07", "desc": "Zone E: Low pH Acidification Sector"},
            {"lat": 11.3921, "lon": 77.7342, "id": "WP_CT08", "desc": "Plantation Center Baseline Point"},
        ]
        
        self.active = False
        self.current_telemetry: Optional[SoilTelemetryBase] = None
        self.last_state_change = datetime.utcnow()
        self.logs: List[Dict[str, str]] = []

    def log(self, message: str, level: str = "INFO"):
        now_str = datetime.utcnow().strftime("%H:%M:%S")
        entry = {"time": now_str, "message": message, "level": level, "state": self.current_state.value}
        self.logs.append(entry)
        if len(self.logs) > 60:
            self.logs.pop(0)
        logger.info(f"[{level}] {message}")

    def trigger_estop(self):
        self.current_state = RoverState.EMERGENCY_STOP
        self.hardware.emergency_stop()
        self.log("EMERGENCY STOP TRIGGERED! Locomotion & Actuator Halted.", level="ERROR")

    def reset(self):
        self.current_state = RoverState.TRANSIT
        if hasattr(self.hardware, "reset_estop"):
            self.hardware.reset_estop()
        else:
            self.hardware.retract_probe()
        self.log("State Machine Reset to TRANSIT.", level="INFO")

    def step(self) -> Dict[str, Any]:
        """
        Advances the state machine by one discrete evaluation step.
        """
        if self.current_state == RoverState.EMERGENCY_STOP:
            return self.get_status()

        target_wp = self.waypoints[self.current_waypoint_index]
        cur_lat, cur_lon, cur_alt = self.gps.read_coordinates()

        if self.current_state == RoverState.TRANSIT:
            lat_diff = abs(target_wp["lat"] - cur_lat)
            lon_diff = abs(target_wp["lon"] - cur_lon)
            
            # Waypoint reached threshold ~0.5 meter in coords (~0.00003 deg)
            if lat_diff < 0.00003 and lon_diff < 0.00003:
                self.hardware.set_motion(0.0, 0.0)
                self.current_state = RoverState.DEPLOYMENT
                self.last_state_change = datetime.utcnow()
                self.log(f"Arrived at Waypoint [{target_wp['id']}] ({target_wp['desc']}). Velocity = 0 m/s. Entering DEPLOYMENT.")
            else:
                # Calculate heading angle
                d_lon = target_wp["lon"] - cur_lon
                d_lat = target_wp["lat"] - cur_lat
                angle_rad = math.atan2(d_lon, d_lat)
                heading = (math.degrees(angle_rad) + 360) % 360
                
                if isinstance(self.gps, MockGPS):
                    self.gps.update_position(target_wp["lat"], target_wp["lon"], step_ratio=0.35)
                
                self.hardware.set_motion(1.0, 0.0)
                if hasattr(self.hardware, "heading_deg"):
                    self.hardware.heading_deg = heading
                self.log(f"Navigating in TRANSIT towards [{target_wp['id']}]. Distance delta: {(lat_diff+lon_diff)*111000:.1f}m.")

        elif self.current_state == RoverState.DEPLOYMENT:
            self.hardware.set_motion(0.0, 0.0)
            success = self.hardware.deploy_probe()
            if success:
                self.current_state = RoverState.INTERROGATION
                self.last_state_change = datetime.utcnow()
                self.log(f"Linear Rack deployed. Probe depth 15cm reached. Bottom Limit Switch NC triggered. Entering INTERROGATION.")
            else:
                self.trigger_estop()

        elif self.current_state == RoverState.INTERROGATION:
            self.hardware.set_motion(0.0, 0.0)
            elapsed = (datetime.utcnow() - self.last_state_change).total_seconds()
            
            if elapsed >= self.stabilization_seconds:
                raw_reading = self.sensor.read_soil_parameters(cur_lat, cur_lon)
                sample_id = f"S_ROV_{self.sample_counter:04d}"
                
                # Compute composite health score
                ph = raw_reading["ph"]
                ec = raw_reading["ec"]
                moisture = raw_reading["moisture"]
                temp = raw_reading.get("temperature", 26.5)
                n = raw_reading["nitrogen"]
                p = raw_reading["phosphorus"]
                k = raw_reading["potassium"]
                soc = raw_reading.get("organic_carbon", 0.72)
                
                npk_ratio = (min(1.0, n/350)*18 + min(1.0, p/140)*11 + min(1.0, k/140)*11)
                ph_pts = 20 if 6.5 <= ph <= 7.5 else max(0, 20 - abs(ph - 7.0)*10)
                ec_pts = 15 if ec < 0.9 else max(0, 15 - (ec - 0.9)*10)
                m_pts = 15 if 40 <= moisture <= 55 else max(0, 15 - abs(moisture - 47)*0.5)
                health_idx = round(npk_ratio + ph_pts + ec_pts + m_pts + min(10, soc*12), 1)

                self.current_telemetry = SoilTelemetryBase(
                    sample_id=sample_id,
                    mission_id=self.mission_id,
                    mission_name="Live Autonomous Rover Mission",
                    timestamp=datetime.utcnow(),
                    latitude=cur_lat,
                    longitude=cur_lon,
                    altitude=cur_alt,
                    ph=ph,
                    ec=ec,
                    moisture=moisture,
                    temperature=temp,
                    nitrogen=n,
                    phosphorus=p,
                    potassium=k,
                    organic_carbon=soc,
                    soil_health_index=health_idx,
                    soil_texture="Red Sandy Loam",
                    mulberry_variety="V1 (Victory-1)",
                    probe_depth_cm=15.0,
                    battery_soc=getattr(self.hardware, "battery_soc", 95.0),
                    raw_modbus_hex=raw_reading.get("raw_hex"),
                    rover_state=self.current_state.value
                )
                
                self.sample_counter += 1
                self.log(f"ZTS-3002 Interrogation Complete for [{sample_id}]: pH={ph}, EC={ec}dS/m, NPK=({n:.0f},{p:.0f},{k:.0f}). Entering RETRACTION.")
                self.current_state = RoverState.RETRACTION
                self.last_state_change = datetime.utcnow()

        elif self.current_state == RoverState.RETRACTION:
            self.hardware.set_motion(0.0, 0.0)
            success = self.hardware.retract_probe()
            if success:
                self.log(f"Top Limit Switch NC Triggered. Probe retracted to TOP. Resuming TRANSIT.")
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
            "total_waypoints": len(self.waypoints),
            "gps": {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt,
                "fix": self.gps.get_fix_status(),
                "satellites": self.gps.get_satellites() if hasattr(self.gps, "get_satellites") else 14
            },
            "hardware": hw_status,
            "latest_telemetry": self.current_telemetry.model_dump() if self.current_telemetry else None,
            "logs": self.logs[-15:]
        }
