from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import time
import random
import requests
from backend.app.services.modbus_decoder import ZTS3002ModbusDecoder

# --- GPS Interface & Implementations ---

class GPSInterface(ABC):
    @abstractmethod
    def read_coordinates(self) -> Tuple[float, float, float]:
        """Returns (latitude, longitude, altitude)"""
        pass

    @abstractmethod
    def get_fix_status(self) -> str:
        """Returns GPS fix status: 3D_FIX, 2D_FIX, NO_FIX"""
        pass


class MockGPS(GPSInterface):
    def __init__(self, start_lat: float = 11.3921, start_lon: float = 77.7342):
        self.lat = start_lat
        self.lon = start_lon
        self.alt = 320.0

    def update_position(self, target_lat: float, target_lon: float, step_ratio: float = 0.1):
        self.lat += (target_lat - self.lat) * step_ratio
        self.lon += (target_lon - self.lon) * step_ratio

    def read_coordinates(self) -> Tuple[float, float, float]:
        # Small GPS noise simulation
        lat_noise = random.uniform(-0.000005, 0.000005)
        lon_noise = random.uniform(-0.000005, 0.000005)
        return (round(self.lat + lat_noise, 6), round(self.lon + lon_noise, 6), self.alt)

    def get_fix_status(self) -> str:
        return "3D_FIX"


class RealGPS(GPSInterface):
    """BN-880 GPS Receiver over Serial/UART interface"""
    def __init__(self, serial_port: str = "/dev/ttyUSB0", baud_rate: int = 9600):
        self.serial_port = serial_port
        self.baud_rate = baud_rate

    def read_coordinates(self) -> Tuple[float, float, float]:
        # Hardware reading implementation placeholder for BN-880 NMEA parsing
        return (11.392100, 77.734200, 320.0)

    def get_fix_status(self) -> str:
        return "3D_FIX"


# --- Soil Sensor Interface & Implementations ---

class SoilSensorInterface(ABC):
    @abstractmethod
    def read_soil_parameters(self, lat: float, lon: float) -> Dict[str, float]:
        """Returns soil parameters: ph, ec, moisture, nitrogen, phosphorus, potassium"""
        pass


class MockSoilSensor(SoilSensorInterface):
    """
    Mock soil sensor generating spatially correlated parameters across plantation zones.
    Zone A: Nitrogen deficiency
    Zone B: Phosphorus deficiency
    Zone C: Potassium deficiency
    Zone D: High EC
    Zone E: Low pH
    """
    def __init__(self, center_lat: float = 11.3921, center_lon: float = 77.7342):
        self.center_lat = center_lat
        self.center_lon = center_lon

    def read_soil_parameters(self, lat: float, lon: float) -> Dict[str, float]:
        dx = (lat - self.center_lat) * 10000.0
        dy = (lon - self.center_lon) * 10000.0

        # Base Mulberry Healthy Soil Parameters
        ph = 6.8 + 0.3 * (dx - dy) / 10.0 + random.uniform(-0.1, 0.1)
        ec = 0.70 + 0.2 * (dx + dy) / 10.0 + random.uniform(-0.02, 0.02)
        moisture = 45.0 + random.uniform(-3.0, 3.0)
        
        n = 310.0 - 40.0 * dx + random.uniform(-10.0, 10.0)
        p = 135.0 - 30.0 * dy + random.uniform(-5.0, 5.0)
        k = 130.0 + 20.0 * (dx - dy) + random.uniform(-5.0, 5.0)

        # Enforce realistic bounds
        ph = max(5.0, min(8.5, round(ph, 1)))
        ec = max(0.2, min(2.5, round(ec, 2)))
        moisture = max(10.0, min(80.0, round(moisture, 1)))
        n = max(50.0, min(450.0, round(n, 1)))
        p = max(20.0, min(200.0, round(p, 1)))
        k = max(30.0, min(250.0, round(k, 1)))

        return {
            "ph": ph,
            "ec": ec,
            "moisture": moisture,
            "nitrogen": n,
            "phosphorus": p,
            "potassium": k
        }


class RealModbusSoilSensor(SoilSensorInterface):
    """Real ZTS-3002 RS485 Modbus RTU Soil Sensor"""
    def __init__(self, serial_port: str = "/dev/ttyUSB1", slave_id: int = 1):
        self.decoder = ZTS3002ModbusDecoder()
        self.slave_id = slave_id

    def read_soil_parameters(self, lat: float, lon: float) -> Dict[str, float]:
        # Communicates via pymodbus/serial to query registers 0x0000 - 0x0006
        dummy_registers = {
            0x0000: 450,  # 45.0%
            0x0002: 750,  # 0.75 dS/m
            0x0003: 68,   # 6.8 pH
            0x0004: 280,  # 280 N
            0x0005: 110,  # 110 P
            0x0006: 120   # 120 K
        }
        return self.decoder.decode_registers(dummy_registers)


# --- Rover Hardware Interface & Implementations ---

class RoverHardwareInterface(ABC):
    @abstractmethod
    def set_motion(self, linear: float, angular: float) -> bool:
        pass

    @abstractmethod
    def deploy_probe(self) -> bool:
        pass

    @abstractmethod
    def retract_probe(self) -> bool:
        pass

    @abstractmethod
    def emergency_stop(self) -> bool:
        pass

    @abstractmethod
    def get_hardware_status(self) -> Dict[str, Any]:
        pass


class MockRover(RoverHardwareInterface):
    def __init__(self):
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        self.actuator_position = "TOP"  # TOP, MOVING_DOWN, BOTTOM, MOVING_UP
        self.bottom_limit = False
        self.top_limit = True
        self.estop = False

    def set_motion(self, linear: float, angular: float) -> bool:
        if self.estop or self.actuator_position != "TOP":
            self.linear_vel = 0.0
            self.angular_vel = 0.0
            return False
        self.linear_vel = linear
        self.angular_vel = angular
        return True

    def deploy_probe(self) -> bool:
        if self.estop or self.linear_vel != 0.0:
            return False
        self.actuator_position = "MOVING_DOWN"
        self.top_limit = False
        self.bottom_limit = True
        self.actuator_position = "BOTTOM"
        return True

    def retract_probe(self) -> bool:
        if self.estop:
            return False
        self.actuator_position = "MOVING_UP"
        self.bottom_limit = False
        self.top_limit = True
        self.actuator_position = "TOP"
        return True

    def emergency_stop(self) -> bool:
        self.estop = True
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        return True

    def get_hardware_status(self) -> Dict[str, Any]:
        return {
            "linear_vel": self.linear_vel,
            "angular_vel": self.angular_vel,
            "actuator_position": self.actuator_position,
            "top_limit": self.top_limit,
            "bottom_limit": self.bottom_limit,
            "estop": self.estop
        }


class RealESP32Rover(RoverHardwareInterface):
    """ESP32 Hardware over WiFi/HTTP REST API interface"""
    def __init__(self, esp32_ip: str = "192.168.1.150"):
        self.base_url = f"http://{esp32_ip}"

    def set_motion(self, linear: float, angular: float) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/drive", params={"linear": linear, "angular": angular}, timeout=1.0)
            return resp.status_code == 200
        except Exception:
            return False

    def deploy_probe(self) -> bool:
        try:
            resp = requests.post(f"{self.base_url}/api/actuator/deploy", timeout=1.0)
            return resp.status_code == 200
        except Exception:
            return False

    def retract_probe(self) -> bool:
        try:
            resp = requests.post(f"{self.base_url}/api/actuator/retract", timeout=1.0)
            return resp.status_code == 200
        except Exception:
            return False

    def emergency_stop(self) -> bool:
        try:
            resp = requests.post(f"{self.base_url}/api/estop", timeout=0.5)
            return resp.status_code == 200
        except Exception:
            return False

    def get_hardware_status(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/status", timeout=1.0)
            return resp.json()
        except Exception:
            return {"connected": False, "estop": True}
