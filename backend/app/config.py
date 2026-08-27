import os
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_yaml_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

yaml_cfg = load_yaml_config()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = yaml_cfg.get("system", {}).get("log_level", "INFO")
    
    API_HOST: str = yaml_cfg.get("network", {}).get("api_host", "0.0.0.0")
    API_PORT: int = yaml_cfg.get("network", {}).get("api_port", 8000)
    DASHBOARD_PORT: int = yaml_cfg.get("network", {}).get("dashboard_port", 8501)
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'precision_sericulture.db'}"
    
    ESP32_IP: str = yaml_cfg.get("network", {}).get("esp32_ip", "192.168.1.150")
    ESP32_PORT: int = yaml_cfg.get("network", {}).get("esp32_port", 80)
    WIFI_SSID: str = yaml_cfg.get("network", {}).get("wifi_ssid", "Mulberry_Agronomy_Mesh")
    WIFI_PASSWORD: str = "SericulturePass2026"
    
    ROS_DOMAIN_ID: int = yaml_cfg.get("ros2", {}).get("domain_id", 42)
    ROS_TELEMETRY_TOPIC: str = yaml_cfg.get("ros2", {}).get("telemetry_topic", "/rover/soil_telemetry")
    
    MULBERRY_PH_MIN: float = yaml_cfg.get("agronomy_targets", {}).get("ph_min", 6.5)
    MULBERRY_PH_MAX: float = yaml_cfg.get("agronomy_targets", {}).get("ph_max", 7.5)
    MULBERRY_EC_MAX: float = yaml_cfg.get("agronomy_targets", {}).get("ec_max", 1.0)
    MULBERRY_TARGET_N: float = yaml_cfg.get("agronomy_targets", {}).get("target_n", 350.0)
    MULBERRY_TARGET_P: float = yaml_cfg.get("agronomy_targets", {}).get("target_p", 140.0)
    MULBERRY_TARGET_K: float = yaml_cfg.get("agronomy_targets", {}).get("target_k", 140.0)
    
    MOCK_MODE: bool = yaml_cfg.get("system", {}).get("mock_mode", True)
    MOCK_STABILIZATION_SECONDS: int = yaml_cfg.get("state_machine", {}).get("mock_stabilization_seconds", 3)
    
    CENTER_LATITUDE: float = yaml_cfg.get("plantation", {}).get("center_latitude", 11.3921)
    CENTER_LONGITUDE: float = yaml_cfg.get("plantation", {}).get("center_longitude", 77.7342)
    MOCK_PLANTATION_LAT: float = 11.3921
    MOCK_PLANTATION_LON: float = 77.7342

settings = Settings()
