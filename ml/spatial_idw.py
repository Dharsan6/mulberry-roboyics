import numpy as np
import pandas as pd
from typing import Dict, List, Any

class SpatialIDWInterpolator:
    """
    Classical Inverse Distance Weighting (IDW) spatial interpolator baseline.
    Converts sparse GPS-tagged soil observations into dense spatial grids.
    """

    def __init__(self, power: float = 2.0):
        self.power = power

    def fit_predict_grid(self,
                        obs_df: pd.DataFrame,
                        center_lat: float = 11.3921,
                        center_lon: float = 77.7342,
                        grid_size: int = 50,
                        width_meters: float = 200.0,
                        height_meters: float = 200.0) -> List[Dict[str, Any]]:
        
        lat_range = (height_meters / 2.0) / 111000.0
        lon_range = (width_meters / 2.0) / 108800.0

        lats = np.linspace(center_lat - lat_range, center_lat + lat_range, grid_size)
        lons = np.linspace(center_lon - lon_range, center_lon + lon_range, grid_size)

        obs_lats = obs_df["latitude"].values
        obs_lons = obs_df["longitude"].values
        
        obs_n = obs_df["nitrogen"].values
        obs_p = obs_df["phosphorus"].values
        obs_k = obs_df["potassium"].values
        obs_ph = obs_df["ph"].values
        obs_ec = obs_df["ec"].values
        obs_moist = obs_df["moisture"].values
        obs_temp = obs_df["temperature"].values if "temperature" in obs_df.columns else np.full(len(obs_df), 26.5)
        obs_health = obs_df["soil_health_index"].values if "soil_health_index" in obs_df.columns else np.full(len(obs_df), 80.0)

        # Targets (Mulberry)
        target_n, target_p, target_k = 350.0, 140.0, 140.0

        grid_points = []

        for gx, lat in enumerate(lats):
            for gy, lon in enumerate(lons):
                # Calculate Euclidean distance to all observation points (in degrees)
                dists = np.sqrt((obs_lats - lat)**2 + (obs_lons - lon)**2)
                dists = np.maximum(dists, 1e-8)  # Avoid div by zero
                
                weights = 1.0 / (dists ** self.power)
                weights_sum = np.sum(weights)
                
                pred_n = np.sum(weights * obs_n) / weights_sum
                pred_p = np.sum(weights * obs_p) / weights_sum
                pred_k = np.sum(weights * obs_k) / weights_sum
                pred_ph = np.sum(weights * obs_ph) / weights_sum
                pred_ec = np.sum(weights * obs_ec) / weights_sum
                pred_moist = np.sum(weights * obs_moist) / weights_sum
                pred_temp = np.sum(weights * obs_temp) / weights_sum
                pred_health = np.sum(weights * obs_health) / weights_sum

                # Shortfalls
                n_def = float(np.maximum(target_n - pred_n, 0.0))
                p_def = float(np.maximum(target_p - pred_p, 0.0))
                k_def = float(np.maximum(target_k - pred_k, 0.0))

                grid_points.append({
                    "grid_x": gx,
                    "grid_y": gy,
                    "latitude": float(round(lat, 6)),
                    "longitude": float(round(lon, 6)),
                    "predicted_n_deficiency": float(round(n_def, 2)),
                    "predicted_p_deficiency": float(round(p_def, 2)),
                    "predicted_k_deficiency": float(round(k_def, 2)),
                    "predicted_ph": float(round(pred_ph, 2)),
                    "predicted_ec": float(round(pred_ec, 2)),
                    "predicted_moisture": float(round(pred_moist, 1)),
                    "predicted_temperature": float(round(pred_temp, 1)),
                    "predicted_soil_health": float(round(pred_health, 1))
                })

        return grid_points
