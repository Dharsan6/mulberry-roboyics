import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

class SpatialRandomForestBaseline:
    """
    Traditional Machine Learning Baseline using Multi-output Random Forest Regressor.
    Predicts (N_deficiency, P_deficiency, K_deficiency) from (latitude, longitude, pH, EC, moisture).
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        self.feature_cols = ["latitude", "longitude", "ph", "ec", "moisture"]
        self.target_cols = ["n_deficiency", "p_deficiency", "k_deficiency"]

    def prepare_features_and_targets(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = df.copy()
        df["n_deficiency"] = np.maximum(350.0 - df["nitrogen"], 0.0)
        df["p_deficiency"] = np.maximum(140.0 - df["phosphorus"], 0.0)
        df["k_deficiency"] = np.maximum(140.0 - df["potassium"], 0.0)

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
            prefix = target.split("_")[0].upper()  # N, P, or K
            y_true_col = y_test.iloc[:, idx]
            y_pred_col = y_pred[:, idx]

            mae = float(mean_absolute_error(y_true_col, y_pred_col))
            rmse = float(root_mean_squared_error(y_true_col, y_pred_col))
            r2 = float(r2_score(y_true_col, y_pred_col))

            metrics[f"{prefix}_MAE"] = round(mae, 3)
            metrics[f"{prefix}_RMSE"] = round(rmse, 3)
            metrics[f"{prefix}_R2"] = round(r2, 3)

        return metrics

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, filepath: str):
        with open(filepath, "rb") as f:
            self.model = pickle.load(f)
