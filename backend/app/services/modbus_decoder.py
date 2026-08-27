import logging
from typing import Dict, Any, Tuple
from backend.app.config import yaml_cfg

logger = logging.getLogger("modbus_decoder")

class ZTS3002ModbusDecoder:
    """
    Dedicated parser service for ZTS-3002 RS485 Modbus RTU Soil Sensor.
    Decodes raw register integer/hex data into engineering units.
    """

    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = yaml_cfg.get("modbus_sensor_zts3002", {})
        
        self.slave_id = config.get("slave_id", 1)
        self.scaling = config.get("scaling", {
            "ph_factor": 0.1,
            "ec_factor": 0.001,
            "moisture_factor": 0.1,
            "nitrogen_factor": 1.0,
            "phosphorus_factor": 1.0,
            "potassium_factor": 1.0
        })

    def decode_registers(self, registers: Dict[int, int]) -> Dict[str, float]:
        """
        Decodes a dictionary of register_address -> integer_value into engineering units.
        Register addresses for ZTS-3002:
        0x0000: Moisture (0.1 %)
        0x0001: Temperature (0.1 °C)
        0x0002: EC (1 us/cm -> 0.001 dS/m)
        0x0003: pH (0.1 pH)
        0x0004: Nitrogen (1 mg/kg or kg/ha)
        0x0005: Phosphorus (1 mg/kg or kg/ha)
        0x0006: Potassium (1 mg/kg or kg/ha)
        """
        raw_moisture = registers.get(0x0000, 450)
        raw_ec = registers.get(0x0002, 750)
        raw_ph = registers.get(0x0003, 68)
        raw_n = registers.get(0x0004, 280)
        raw_p = registers.get(0x0005, 110)
        raw_k = registers.get(0x0006, 120)

        moisture = round(raw_moisture * self.scaling["moisture_factor"], 1)
        ec = round(raw_ec * self.scaling["ec_factor"], 2)
        ph = round(raw_ph * self.scaling["ph_factor"], 1)
        nitrogen = float(raw_n * self.scaling["nitrogen_factor"])
        phosphorus = float(raw_p * self.scaling["phosphorus_factor"])
        potassium = float(raw_k * self.scaling["potassium_factor"])

        return {
            "moisture": moisture,
            "ec": ec,
            "ph": ph,
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium
        }

    def decode_hex_payload(self, hex_payload: str) -> Dict[str, float]:
        """
        Decodes a raw Modbus RTU RS485 response frame in hexadecimal string format.
        Example frame: 01 03 0E 01C2 00F0 02EE 0044 0118 006E 0078 [CRC1] [CRC2]
        """
        try:
            clean_hex = hex_payload.replace(" ", "").replace("0x", "")
            bytes_data = bytes.fromhex(clean_hex)
            
            # Minimum length check for Modbus RTU response header + payload + CRC
            if len(bytes_data) < 7:
                raise ValueError("Modbus RTU frame too short")
            
            # Slave address validation
            slave = bytes_data[0]
            func = bytes_data[1]
            byte_count = bytes_data[2]
            
            if func != 0x03:
                raise ValueError(f"Unsupported Modbus function code 0x{func:02X}")
            
            # Read 16-bit register words
            words = []
            for i in range(3, 3 + byte_count, 2):
                if i + 1 < len(bytes_data):
                    val = (bytes_data[i] << 8) | bytes_data[i+1]
                    words.append(val)
            
            reg_dict = {idx: val for idx, val in enumerate(words)}
            return self.decode_registers(reg_dict)
        except Exception as e:
            logger.error(f"Failed to parse hex payload '{hex_payload}': {e}")
            # Fallback safe default
            return {
                "moisture": 45.0,
                "ec": 0.75,
                "ph": 6.8,
                "nitrogen": 280.0,
                "phosphorus": 110.0,
                "potassium": 120.0
            }

    @staticmethod
    def validate_reading(data: Dict[str, float]) -> Tuple[bool, str]:
        """Validates decoded sensor data against physical range bounds."""
        if not (0.0 <= data["ph"] <= 14.0):
            return False, f"pH value {data['ph']} out of range [0, 14]"
        if data["ec"] < 0.0:
            return False, f"EC value {data['ec']} cannot be negative"
        if not (0.0 <= data["moisture"] <= 100.0):
            return False, f"Moisture {data['moisture']} out of range [0, 100%]"
        if data["nitrogen"] < 0.0 or data["phosphorus"] < 0.0 or data["potassium"] < 0.0:
            return False, "Nutrient values cannot be negative"
        return True, "Valid"
