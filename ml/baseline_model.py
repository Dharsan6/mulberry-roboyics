import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

class SpatialRandomForestBaseline:
    """
    Traditional Machine Learning Baseline using Multi-output Random Forest Regressor.
    Predicts (N_deficiency, P_deficiency, K_deficiency, pH, EC) from (latitude, longitude, moisture, temperature).
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)
        self.feature_cols = ["latitude", "longitude"]
        self.target_cols = ["n_deficiency", "p_deficiency", "k_deficiency", "ph", "ec", "moisture", "temperature", "soil_health_index"]

    def prepare_features_and_targets(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = df.copy()
        df["n_deficiency"] = np.maximum(350.0 - df["nitrogen"], 0.0)
        df["p_deficiency"] = np.maximum(140.0 - df["phosphorus"], 0.0)
        df["k_deficiency"] = np.maximum(140.0 - df["potassium"], 0.0)
        
        if "temperature" not in df.columns:
            df["temperature"] = 26.5
        if "soil_health_index" not in df.columns:
            df["soil_health_index"] = 80.0

        X = df[self.feature_cols]
        y = df[self.target_cols]
        return X, y

    def train_and_evaluate(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict[str, Any]:
        X, y = self.prepare_features_and_targets(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        metrics = {}
        for idx, target in enumerate(self.target_cols):
            prefix = target.upper()
            y_true_col = y_test.iloc[:, idx]
            y_pred_col = y_pred[:, idx]

            mae = float(mean_absolute_error(y_true_col, y_pred_col))
            rmse = float(root_mean_squared_error(y_true_col, y_pred_col))
            r2 = float(r2_score(y_true_col, y_pred_col))

            metrics[f"{prefix}_MAE"] = round(mae, 3)
            metrics[f"{prefix}_RMSE"] = round(rmse, 3)
            metrics[f"{prefix}_R2"] = round(r2, 3)

        return metrics

    def predict_grid(self,
                     center_lat: float = 11.3921,
                     center_lon: float = 77.7342,
                     grid_size: int = 50,
                     width_meters: float = 200.0,
                     height_meters: float = 200.0) -> List[Dict[str, Any]]:
        lat_range = (height_meters / 2.0) / 111000.0
        lon_range = (width_meters / 2.0) / 108800.0

        lats = np.linspace(center_lat - lat_range, center_lat + lat_range, grid_size)
        lons = np.linspace(center_lon - lon_range, center_lon + lon_range, grid_size)

        grid_coords = []
        for gx, lat in enumerate(lats):
            for gy, lon in enumerate(lons):
                grid_coords.append((gx, gy, lat, lon))

        coord_df = pd.DataFrame([{"latitude": c[2], "longitude": c[3]} for c in grid_coords])
        preds = self.model.predict(coord_df)

        points = []
        for idx, (gx, gy, lat, lon) in enumerate(grid_coords):
            p = preds[idx]
            points.append({
                "grid_x": gx,
                "grid_y": gy,
                "latitude": float(round(lat, 6)),
                "longitude": float(round(lon, 6)),
                "predicted_n_deficiency": float(round(max(0.0, p[0]), 2)),
                "predicted_p_deficiency": float(round(max(0.0, p[1]), 2)),
                "predicted_k_deficiency": float(round(max(0.0, p[2]), 2)),
                "predicted_ph": float(round(p[3], 2)),
                "predicted_ec": float(round(p[4], 2)),
                "predicted_moisture": float(round(p[5], 1)),
                "predicted_temperature": float(round(p[6], 1)),
                "predicted_soil_health": float(round(p[7], 1))
            })
        return points

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            self.model = pickle.load(f)
