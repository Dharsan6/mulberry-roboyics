from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import time
import random
import math
import numpy as np
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

    @abstractmethod
    def get_satellites(self) -> int:
        pass


class MockGPS(GPSInterface):
    def __init__(self, start_lat: float = 11.3921, start_lon: float = 77.7342):
        self.lat = start_lat
        self.lon = start_lon
        self.alt = 320.0
        self.satellites = 14

    def update_position(self, target_lat: float, target_lon: float, step_ratio: float = 0.2):
        self.lat += (target_lat - self.lat) * step_ratio
        self.lon += (target_lon - self.lon) * step_ratio

    def read_coordinates(self) -> Tuple[float, float, float]:
        # Realistic centimeter-level RTK GPS noise simulation
        lat_noise = random.uniform(-0.000003, 0.000003)
        lon_noise = random.uniform(-0.000003, 0.000003)
        alt_noise = random.uniform(-0.05, 0.05)
        return (round(self.lat + lat_noise, 6), round(self.lon + lon_noise, 6), round(self.alt + alt_noise, 1))

    def get_fix_status(self) -> str:
        return "3D_FIX (RTK-FIXED)"

    def get_satellites(self) -> int:
        return self.satellites


class RealGPS(GPSInterface):
    """BN-880 GPS Receiver over Serial/UART interface"""
    def __init__(self, serial_port: str = "/dev/ttyUSB0", baud_rate: int = 9600):
        self.serial_port = serial_port
        self.baud_rate = baud_rate

    def read_coordinates(self) -> Tuple[float, float, float]:
        return (11.392100, 77.734200, 320.0)

    def get_fix_status(self) -> str:
        return "3D_FIX"

    def get_satellites(self) -> int:
        return 12


# --- Soil Sensor Interface & Implementations ---

class SoilSensorInterface(ABC):
    @abstractmethod
    def read_soil_parameters(self, lat: float, lon: float) -> Dict[str, Any]:
        """Returns soil parameters: ph, ec, moisture, temperature, nitrogen, phosphorus, potassium, organic_carbon, raw_hex"""
        pass


class MockSoilSensor(SoilSensorInterface):
    """
    Mock soil sensor generating spatially correlated parameters across plantation zones.
    Zone A: Nitrogen deficiency
    Zone B: Phosphorus deficiency
    Zone C: Potassium deficiency
    Zone D: High EC / Salinity
    Zone E: Low pH / Acidic
    Zone F: Optimal High-Yield
    Zone G: High Moisture Depression
    """
    def __init__(self, center_lat: float = 11.3921, center_lon: float = 77.7342):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.decoder = ZTS3002ModbusDecoder()

    def read_soil_parameters(self, lat: float, lon: float) -> Dict[str, Any]:
        # Normalized coordinates [-1, 1] relative to 200m plantation boundary
        norm_y = (lat - self.center_lat) / (100.0 / 111000.0)
        norm_x = (lon - self.center_lon) / (100.0 / 108800.0)

        # Baseline values
        ph = 6.85
        ec = 0.62
        moisture = 46.0
        temp = 26.8 + random.uniform(-0.5, 0.5)
        n = 325.0
        p = 135.0
        k = 132.0
        soc = 0.72

        # Zone effects
        if norm_x < -0.1 and norm_y > 0.1:
            intensity = np.exp(-((norm_x + 0.55)**2 + (norm_y - 0.55)**2) / 0.25)
            n -= 130.0 * intensity
            soc -= 0.2 * intensity

        if norm_x > 0.1 and norm_y > 0.1:
            intensity = np.exp(-((norm_x - 0.55)**2 + (norm_y - 0.55)**2) / 0.25)
            p -= 65.0 * intensity

        if norm_x > 0.1 and norm_y < -0.1:
            intensity = np.exp(-((norm_x - 0.55)**2 + (norm_y + 0.55)**2) / 0.25)
            k -= 60.0 * intensity

        if norm_x < -0.1 and norm_y < -0.1:
            intensity = np.exp(-((norm_x + 0.55)**2 + (norm_y + 0.55)**2) / 0.25)
            ec += 1.1 * intensity
            ph += 0.6 * intensity

        dist_center = np.sqrt(norm_x**2 + norm_y**2)
        if dist_center < 0.4:
            intensity = 1.0 - (dist_center / 0.4)
            ph -= 1.2 * intensity
            n -= 20.0 * intensity

        # Gaussian Noise
        ph += random.gauss(0, 0.05)
        ec += random.gauss(0, 0.02)
        moisture += random.gauss(0, 1.5)
        n += random.gauss(0, 5.0)
        p += random.gauss(0, 3.0)
        k += random.gauss(0, 3.0)
        soc += random.gauss(0, 0.02)

        ph = float(np.clip(round(ph, 2), 4.8, 8.8))
        ec = float(np.clip(round(ec, 2), 0.15, 3.0))
        moisture = float(np.clip(round(moisture, 1), 15.0, 85.0))
        temp = float(np.clip(round(temp, 1), 18.0, 38.0))
        n = float(np.clip(round(n, 1), 60.0, 440.0))
        p = float(np.clip(round(p, 1), 25.0, 210.0))
        k = float(np.clip(round(k, 1), 35.0, 240.0))
        soc = float(np.clip(round(soc, 2), 0.25, 1.45))

        # Modbus register values
        r_moist = int(round(moisture * 10))
        r_temp = int(round(temp * 10))
        r_ec = int(round(ec * 1000))
        r_ph = int(round(ph * 10))
        r_n = int(round(n))
        r_p = int(round(p))
        r_k = int(round(k))

        raw_hex = f"01 03 0E {r_moist:04X} {r_temp:04X} {r_ec:04X} {r_ph:04X} {r_n:04X} {r_p:04X} {r_k:04X} A5C3"

        return {
            "ph": ph,
            "ec": ec,
            "moisture": moisture,
            "temperature": temp,
            "nitrogen": n,
            "phosphorus": p,
            "potassium": k,
            "organic_carbon": soc,
            "raw_hex": raw_hex
        }


class RealModbusSoilSensor(SoilSensorInterface):
    """Real ZTS-3002 RS485 Modbus RTU Soil Sensor"""
    def __init__(self, serial_port: str = "/dev/ttyUSB1", slave_id: int = 1):
        self.decoder = ZTS3002ModbusDecoder()
        self.slave_id = slave_id

    def read_soil_parameters(self, lat: float, lon: float) -> Dict[str, Any]:
        dummy_registers = {
            0x0000: 450,  # 45.0%
            0x0001: 265,  # 26.5 C
            0x0002: 750,  # 0.75 dS/m
            0x0003: 68,   # 6.8 pH
            0x0004: 280,  # 280 N
            0x0005: 110,  # 110 P
            0x0006: 120   # 120 K
        }
        res = self.decoder.decode_registers(dummy_registers)
        res["organic_carbon"] = 0.72
        res["raw_hex"] = "01 03 0E 01C2 0109 02EE 0044 0118 006E 0078 A5C3"
        return res


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
        self.probe_depth_cm = 0.0
        self.bottom_limit = False
        self.top_limit = True
        self.estop = False
        self.battery_soc = 98.5
        self.motor_current_ma = 120
        self.actuator_current_ma = 40
        self.heading_deg = 45.0
        self.wifi_rssi_dbm = -58

    def set_motion(self, linear: float, angular: float) -> bool:
        if self.estop or self.actuator_position != "TOP":
            self.linear_vel = 0.0
            self.angular_vel = 0.0
            self.motor_current_ma = 120
            return False
        
        self.linear_vel = linear
        self.angular_vel = angular
        
        if linear > 0:
            self.motor_current_ma = int(650 + random.randint(-40, 40))
            self.battery_soc = max(10.0, round(self.battery_soc - 0.02, 2))
            self.heading_deg = (self.heading_deg + angular * 5.0) % 360.0
        else:
            self.motor_current_ma = 120
        return True

    def deploy_probe(self) -> bool:
        if self.estop or self.linear_vel != 0.0:
            return False
        self.actuator_position = "BOTTOM"
        self.probe_depth_cm = 15.0
        self.top_limit = False
        self.bottom_limit = True
        self.actuator_current_ma = 380  # Motor resistance load
        self.battery_soc = max(10.0, round(self.battery_soc - 0.05, 2))
        return True

    def retract_probe(self) -> bool:
        if self.estop:
            return False
        self.actuator_position = "TOP"
        self.probe_depth_cm = 0.0
        self.bottom_limit = False
        self.top_limit = True
        self.actuator_current_ma = 40
        self.battery_soc = max(10.0, round(self.battery_soc - 0.03, 2))
        return True

    def emergency_stop(self) -> bool:
        self.estop = True
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        self.motor_current_ma = 0
        self.actuator_current_ma = 0
        return True

    def reset_estop(self):
        self.estop = False
        self.retract_probe()

    def get_hardware_status(self) -> Dict[str, Any]:
        return {
            "linear_vel": round(self.linear_vel, 2),
            "angular_vel": round(self.angular_vel, 2),
            "heading_deg": round(self.heading_deg, 1),
            "actuator_position": self.actuator_position,
            "probe_depth_cm": self.probe_depth_cm,
            "top_limit": self.top_limit,
            "bottom_limit": self.bottom_limit,
            "estop": self.estop,
            "battery_soc": round(self.battery_soc, 1),
            "motor_current_ma": self.motor_current_ma,
            "actuator_current_ma": self.actuator_current_ma,
            "wifi_rssi_dbm": self.wifi_rssi_dbm
        }
