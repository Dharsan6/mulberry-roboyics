import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List

class SyntheticPlantationGenerator:
    """
    Generates realistic, spatially-correlated Mulberry plantation soil data across 5 deficiency zones:
    - Zone A (North-West): Nitrogen Deficiency
    - Zone B (North-East): Phosphorus Deficiency
    - Zone C (South-East): Potassium Deficiency
    - Zone D (South-West): High EC / Salinity
    - Zone E (Center): Low pH / Soil Acidification
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

    def generate_dataset(self, num_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
        np.random.seed(seed)
        random.seed(seed)

        start_time = datetime.utcnow() - timedelta(days=7)
        rows = []

        for i in range(1, num_samples + 1):
            sample_id = f"S{i:04d}"
            mission_id = f"M{(i // 100) + 1:03d}"
            timestamp = start_time + timedelta(minutes=10 * i)
            
            # Uniform random sampling within spatial boundary
            lat = self.center_lat + np.random.uniform(-self.lat_range, self.lat_range)
            lon = self.center_lon + np.random.uniform(-self.lon_range, self.lon_range)
            
            # Normalized coordinates relative to center [-1, 1]
            norm_x = (lon - self.center_lon) / self.lon_range
            norm_y = (lat - self.center_lat) / self.lat_range

            # Base Healthy Mulberry Baseline Values
            ph = 6.8
            ec = 0.65
            moisture = 48.0
            n = 320.0
            p = 135.0
            k = 130.0

            # Spatial Zone Effects
            # Zone A: NW (norm_x < 0, norm_y > 0) -> Nitrogen Deficiency
            if norm_x < -0.2 and norm_y > 0.2:
                n -= 120.0 * np.exp(-((norm_x + 0.6)**2 + (norm_y - 0.6)**2))
            
            # Zone B: NE (norm_x > 0, norm_y > 0) -> Phosphorus Deficiency
            if norm_x > 0.2 and norm_y > 0.2:
                p -= 60.0 * np.exp(-((norm_x - 0.6)**2 + (norm_y - 0.6)**2))

            # Zone C: SE (norm_x > 0, norm_y < 0) -> Potassium Deficiency
            if norm_x > 0.2 and norm_y < 0.2:
                k -= 55.0 * np.exp(-((norm_x - 0.6)**2 + (norm_y + 0.6)**2))

            # Zone D: SW (norm_x < 0, norm_y < 0) -> High EC
            if norm_x < -0.2 and norm_y < -0.2:
                ec += 0.85 * np.exp(-((norm_x + 0.6)**2 + (norm_y + 0.6)**2))

            # Zone E: Center (norm_x ~ 0, norm_y ~ 0) -> Low pH
            dist_center = np.sqrt(norm_x**2 + norm_y**2)
            if dist_center < 0.4:
                ph -= 1.1 * (1.0 - dist_center / 0.4)

            # Add Gaussian noise
            ph += np.random.normal(0, 0.08)
            ec += np.random.normal(0, 0.03)
            moisture += np.random.normal(0, 2.5)
            n += np.random.normal(0, 8.0)
            p += np.random.normal(0, 4.0)
            k += np.random.normal(0, 4.0)

            # Clip to physical domain bounds
            ph = float(np.clip(round(ph, 1), 4.5, 9.0))
            ec = float(np.clip(round(ec, 2), 0.1, 3.5))
            moisture = float(np.clip(round(moisture, 1), 10.0, 85.0))
            n = float(np.clip(round(n, 1), 50.0, 450.0))
            p = float(np.clip(round(p, 1), 20.0, 220.0))
            k = float(np.clip(round(k, 1), 30.0, 250.0))

            rows.append({
                "sample_id": sample_id,
                "mission_id": mission_id,
                "timestamp": timestamp.isoformat(),
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "altitude": 320.0,
                "ph": ph,
                "ec": ec,
                "moisture": moisture,
                "nitrogen": n,
                "phosphorus": p,
                "potassium": k,
                "rover_state": "INTERROGATION"
            })

        df = pd.DataFrame(rows)
        return df

if __name__ == "__main__":
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(1000)
    print(f"Generated {len(df)} synthetic Mulberry plantation observations.")
    print(df.head())
