import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

class SyntheticPlantationGenerator:
    """
    Generates realistic, scientifically grounded, spatially correlated Mulberry
    plantation soil and rover telemetry data across realistic agronomic deficiency zones:
    
    1. Zone A (North-West): Nitrogen Deficiency (Stunted Mulberry leaf development)
    2. Zone B (North-East): Phosphorus Deficiency (Restricted root growth & purpling)
    3. Zone C (South-East): Potassium Deficiency (Marginal chlorosis, low drought tolerance)
    4. Zone D (South-West): Saline / High EC (>1.2 dS/m, high sodium/calcium salt accumulation)
    5. Zone E (Center-West): Soil Acidification (pH < 6.0, manganese/iron toxicity risk)
    6. Zone F (Center-East): Optimal High-Yield Sericulture Zone (Balanced NPK, pH 6.8-7.2, high SOC)
    7. Zone G (South Depression): Poor Drainage / Waterlogged Depression (Moisture >65%)
    """

    def __init__(self,
                 center_lat: float = 11.3921,
                 center_lon: float = 77.7342,
                 width_meters: float = 200.0,
                 height_meters: float = 200.0):
        self.center_lat = center_lat
        self.center_lon = center_lon
        # Approx 1 deg lat = 111000m, 1 deg lon = 111000 * cos(lat) ~ 108800m
        self.lat_range = (height_meters / 2.0) / 111000.0
        self.lon_range = (width_meters / 2.0) / 108800.0

    def compute_soil_health_index(self, ph: float, ec: float, moisture: float, n: float, p: float, k: float, soc: float) -> float:
        """
        Calculates a composite Soil Health Index (0-100) tailored for Mulberry agronomy.
        Optimal: pH (6.5-7.5), EC (<1.0 dS/m), Moisture (40-55%), N (>320), P (>130), K (>130), SOC (>0.7%).
        """
        # pH score (20 pts)
        if 6.5 <= ph <= 7.5:
            ph_score = 20.0
        else:
            ph_dist = min(abs(ph - 6.5), abs(ph - 7.5))
            ph_score = max(0.0, 20.0 - ph_dist * 12.0)

        # EC score (15 pts)
        if ec < 0.8:
            ec_score = 15.0
        elif ec <= 1.0:
            ec_score = 12.0
        else:
            ec_score = max(0.0, 15.0 - (ec - 0.8) * 8.0)

        # Moisture score (15 pts)
        if 40.0 <= moisture <= 55.0:
            m_score = 15.0
        else:
            m_dist = min(abs(moisture - 40.0), abs(moisture - 55.0))
            m_score = max(0.0, 15.0 - m_dist * 0.5)

        # NPK score (40 pts)
        n_ratio = min(1.0, n / 350.0)
        p_ratio = min(1.0, p / 140.0)
        k_ratio = min(1.0, k / 140.0)
        npk_score = (n_ratio * 18.0) + (p_ratio * 11.0) + (k_ratio * 11.0)

        # SOC score (10 pts)
        soc_score = min(10.0, (soc / 0.8) * 10.0)

        total_score = ph_score + ec_score + m_score + npk_score + soc_score
        return float(np.clip(round(total_score, 1), 5.0, 100.0))

    def generate_modbus_hex(self, moisture: float, temp: float, ec: float, ph: float, n: float, p: float, k: float) -> str:
        """
        Generates realistic ZTS-3002 RS485 Modbus RTU response frame in hex.
        Register mapping:
        0x0000: Moisture * 10
        0x0001: Temp * 10
        0x0002: EC in us/cm (dS/m * 1000)
        0x0003: pH * 10
        0x0004: N * 1
        0x0005: P * 1
        0x0006: K * 1
        """
        r_moist = int(np.clip(round(moisture * 10), 0, 1000))
        r_temp = int(np.clip(round(temp * 10), 0, 1000))
        r_ec = int(np.clip(round(ec * 1000), 0, 10000))
        r_ph = int(np.clip(round(ph * 10), 0, 140))
        r_n = int(np.clip(round(n), 0, 1000))
        r_p = int(np.clip(round(p), 0, 1000))
        r_k = int(np.clip(round(k), 0, 1000))

        # Modbus RTU frame: [Slave=01] [Func=03] [Bytes=0E] [Reg0] [Reg1] [Reg2] [Reg3] [Reg4] [Reg5] [Reg6] [CRC16]
        payload = f"01 03 0E {r_moist:04X} {r_temp:04X} {r_ec:04X} {r_ph:04X} {r_n:04X} {r_p:04X} {r_k:04X}"
        # Synthetic CRC16 checksum
        crc = (r_moist ^ r_temp ^ r_ec ^ r_ph ^ r_n ^ r_p ^ r_k ^ 0xA5C3) & 0xFFFF
        return f"{payload} {crc:04X}"

    def generate_dataset(self, num_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
        """
        Generates full plantation dataset partitioned across realistic robotic survey missions.
        """
        np.random.seed(seed)
        random.seed(seed)

        start_time = datetime.utcnow() - timedelta(days=14)
        rows = []

        mission_names = [
            ("M001", "Grid Sweep Sector A (North-West)"),
            ("M002", "Grid Sweep Sector B (North-East)"),
            ("M003", "Grid Sweep Sector C (South-East)"),
            ("M004", "Grid Sweep Sector D (South-West)"),
            ("M005", "Center Plantation Benchmark"),
            ("M006", "High Salinity Boundary Survey"),
            ("M007", "Drainage Depression Transect"),
            ("M008", "Post-Monsoon Sericulture Audit"),
            ("M009", "Pre-Pruning Soil Health Verification"),
            ("M010", "Full Plantation Master Survey")
        ]

        varieties = ["V1 (Victory-1)", "S36", "Kanva-2", "MR-2"]

        for i in range(1, num_samples + 1):
            sample_id = f"S{i:04d}"
            m_idx = min(len(mission_names) - 1, (i - 1) // (num_samples // len(mission_names)))
            mission_id, mission_desc = mission_names[m_idx]
            
            # Timestamp progression
            timestamp = start_time + timedelta(hours=i * 0.3)
            
            # Spatial distribution (mixture of uniform grid and Gaussian cluster sampling)
            if i % 5 == 0:
                # Dense cluster sampling
                cluster_centers = [(-0.6, 0.6), (0.6, 0.6), (0.6, -0.6), (-0.6, -0.6), (0.0, 0.0)]
                cx, cy = random.choice(cluster_centers)
                norm_x = float(np.clip(cx + np.random.normal(0, 0.15), -1.0, 1.0))
                norm_y = float(np.clip(cy + np.random.normal(0, 0.15), -1.0, 1.0))
            else:
                norm_x = float(np.random.uniform(-1.0, 1.0))
                norm_y = float(np.random.uniform(-1.0, 1.0))

            lat = self.center_lat + norm_y * self.lat_range
            lon = self.center_lon + norm_x * self.lon_range

            # Topographic Elevation (Gentle slope towards South with central depression)
            base_alt = 320.0
            slope_effect = -1.8 * norm_y + 0.9 * norm_x
            depression_effect = -1.2 * np.exp(-(norm_x**2 + (norm_y + 0.4)**2) / 0.2)
            altitude = round(base_alt + slope_effect + depression_effect + np.random.normal(0, 0.1), 1)

            # Base Healthy Mulberry Baseline Values
            ph = 6.85
            ec = 0.62
            moisture = 46.0
            temperature = 26.5 + 2.0 * np.sin(i / 20.0)  # Diurnal temp cycle
            n = 325.0
            p = 135.0
            k = 132.0
            soc = 0.72  # Soil Organic Carbon %

            # --- Spatial Zone Agronomic Effects ---
            # 1. Zone A: NW (norm_x < -0.2, norm_y > 0.2) -> Acute Nitrogen Deficiency
            if norm_x < -0.1 and norm_y > 0.1:
                intensity = np.exp(-((norm_x + 0.55)**2 + (norm_y - 0.55)**2) / 0.25)
                n -= 135.0 * intensity
                soc -= 0.25 * intensity

            # 2. Zone B: NE (norm_x > 0.1, norm_y > 0.1) -> Phosphorus Deficiency
            if norm_x > 0.1 and norm_y > 0.1:
                intensity = np.exp(-((norm_x - 0.55)**2 + (norm_y - 0.55)**2) / 0.25)
                p -= 68.0 * intensity
                ph += 0.2 * intensity

            # 3. Zone C: SE (norm_x > 0.1, norm_y < -0.1) -> Potassium Deficiency
            if norm_x > 0.1 and norm_y < -0.1:
                intensity = np.exp(-((norm_x - 0.55)**2 + (norm_y + 0.55)**2) / 0.25)
                k -= 62.0 * intensity
                moisture -= 5.0 * intensity

            # 4. Zone D: SW (norm_x < -0.1, norm_y < -0.1) -> Saline / High EC
            if norm_x < -0.1 and norm_y < -0.1:
                intensity = np.exp(-((norm_x + 0.55)**2 + (norm_y + 0.55)**2) / 0.25)
                ec += 1.15 * intensity
                ph += 0.7 * intensity
                moisture += 3.0 * intensity

            # 5. Zone E: Center-West (norm_x ~ -0.2, norm_y ~ 0.0) -> Low pH / Acidification
            dist_e = np.sqrt((norm_x + 0.25)**2 + norm_y**2)
            if dist_e < 0.45:
                intensity = 1.0 - (dist_e / 0.45)
                ph -= 1.35 * intensity
                n -= 25.0 * intensity
                p -= 20.0 * intensity

            # 6. Zone F: Center-East (norm_x ~ 0.3, norm_y ~ 0.0) -> High Yield Benchmark
            dist_f = np.sqrt((norm_x - 0.3)**2 + norm_y**2)
            if dist_f < 0.4:
                intensity = 1.0 - (dist_f / 0.4)
                n += 35.0 * intensity
                p += 15.0 * intensity
                k += 15.0 * intensity
                soc += 0.28 * intensity
                ph = ph + 0.1 * intensity

            # 7. Zone G: South Depression (norm_y < -0.3, norm_x ~ 0.0) -> High Moisture
            dist_g = np.sqrt(norm_x**2 + (norm_y + 0.45)**2)
            if dist_g < 0.4:
                intensity = 1.0 - (dist_g / 0.4)
                moisture += 22.0 * intensity
                temperature -= 1.8 * intensity

            # Add sensor Gaussian noise
            ph += np.random.normal(0, 0.06)
            ec += np.random.normal(0, 0.025)
            moisture += np.random.normal(0, 1.8)
            temperature += np.random.normal(0, 0.4)
            n += np.random.normal(0, 6.0)
            p += np.random.normal(0, 3.5)
            k += np.random.normal(0, 3.5)
            soc += np.random.normal(0, 0.03)

            # Physical domain clipping
            ph = float(np.clip(round(ph, 2), 4.8, 8.8))
            ec = float(np.clip(round(ec, 2), 0.15, 3.2))
            moisture = float(np.clip(round(moisture, 1), 15.0, 85.0))
            temperature = float(np.clip(round(temperature, 1), 18.0, 38.0))
            n = float(np.clip(round(n, 1), 60.0, 440.0))
            p = float(np.clip(round(p, 1), 25.0, 210.0))
            k = float(np.clip(round(k, 1), 35.0, 240.0))
            soc = float(np.clip(round(soc, 2), 0.25, 1.45))

            # Composite Health Score
            soil_health = self.compute_soil_health_index(ph, ec, moisture, n, p, k, soc)

            # Modbus Hex String
            raw_hex = self.generate_modbus_hex(moisture, temperature, ec, ph, n, p, k)

            # Battery level simulation (declining per mission, recharged at start of mission)
            mission_sample_offset = (i - 1) % (num_samples // len(mission_names))
            battery_soc = round(max(45.0, 99.0 - (mission_sample_offset * 0.45)), 1)

            # Soil texture classification
            if moisture > 60.0:
                soil_texture = "Clay Loam"
            elif ec > 1.2:
                soil_texture = "Saline Sandy Clay"
            elif soc > 0.8:
                soil_texture = "Rich Humus Loam"
            else:
                soil_texture = "Red Sandy Loam"

            variety = varieties[(i // 25) % len(varieties)]

            rows.append({
                "sample_id": sample_id,
                "mission_id": mission_id,
                "mission_name": mission_desc,
                "timestamp": timestamp.isoformat(),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "altitude": altitude,
                "ph": ph,
                "ec": ec,
                "moisture": moisture,
                "temperature": temperature,
                "nitrogen": n,
                "phosphorus": p,
                "potassium": k,
                "organic_carbon": soc,
                "soil_health_index": soil_health,
                "soil_texture": soil_texture,
                "mulberry_variety": variety,
                "probe_depth_cm": 15.0,
                "battery_soc": battery_soc,
                "raw_modbus_hex": raw_hex,
                "rover_state": "INTERROGATION"
            })

        df = pd.DataFrame(rows)
        return df

if __name__ == "__main__":
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(1000)
    print(f"Generated {len(df)} enhanced Mulberry plantation observations.")
    print(df[["sample_id", "mission_id", "ph", "ec", "nitrogen", "phosphorus", "potassium", "soil_health_index"]].head(10))
