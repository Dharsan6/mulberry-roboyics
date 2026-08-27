import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

class SpatialSoilDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class EfficientNetSpatialRegressor(nn.Module):
    """
    Spatial Neural Network Regression model for multi-parameter sericulture soil mapping.
    Inspired by EfficientNet inverted bottleneck & Swish/SiLU activations with residual connections.
    """

    def __init__(self, input_dim: int = 2, output_dim: int = 8):
        super(EfficientNetSpatialRegressor, self).__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.SiLU(),  # Swish activation
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.SiLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.SiLU(),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.SiLU(),
        )
        
        self.regression_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.SiLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        features = self.encoder(x)
        out = self.regression_head(features)
        return out


class EfficientNetPipeline:
    def __init__(self, epochs: int = 35, batch_size: int = 32, lr: float = 0.005):
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.model = EfficientNetSpatialRegressor(input_dim=2, output_dim=8)
        self.feature_cols = ["latitude", "longitude"]
        self.target_cols = ["n_deficiency", "p_deficiency", "k_deficiency", "ph", "ec", "moisture", "temperature", "soil_health_index"]
        self.norm_params = None

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, Tuple]:
        df = df.copy()
        df["n_deficiency"] = np.maximum(350.0 - df["nitrogen"], 0.0)
        df["p_deficiency"] = np.maximum(140.0 - df["phosphorus"], 0.0)
        df["k_deficiency"] = np.maximum(140.0 - df["potassium"], 0.0)
        
        if "temperature" not in df.columns:
            df["temperature"] = 26.5
        if "soil_health_index" not in df.columns:
            df["soil_health_index"] = 80.0

        X = df[self.feature_cols].values
        y = df[self.target_cols].values

        mean_X = np.mean(X, axis=0)
        std_X = np.std(X, axis=0) + 1e-8
        X_scaled = (X - mean_X) / std_X

        return X_scaled, y, (mean_X, std_X)

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        X, y, norm_params = self.prepare_data(df)
        self.norm_params = norm_params

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        train_dataset = SpatialSoilDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        
        criterion = nn.MSELoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=self.lr, weight_decay=1e-4)

        self.model.train()
        for epoch in range(self.epochs):
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                preds = self.model(batch_x)
                loss = criterion(preds, batch_y)
                loss.backward()
                optimizer.step()

        # Evaluation
        self.model.eval()
        with torch.no_grad():
            test_x_tensor = torch.tensor(X_test, dtype=torch.float32)
            y_pred = self.model(test_x_tensor).numpy()

        metrics = {}
        for idx, target in enumerate(self.target_cols):
            prefix = target.upper()
            y_true_col = y_test[:, idx]
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

        raw_X = np.array([[c[2], c[3]] for c in grid_coords])
        if self.norm_params:
            mean_X, std_X = self.norm_params
            scaled_X = (raw_X - mean_X) / std_X
        else:
            scaled_X = raw_X

        self.model.eval()
        with torch.no_grad():
            inp_tensor = torch.tensor(scaled_X, dtype=torch.float32)
            preds = self.model(inp_tensor).numpy()

        points = []
        for idx, (gx, gy, lat, lon) in enumerate(grid_coords):
            p = preds[idx]
            points.append({
                "grid_x": gx,
                "grid_y": gy,
                "latitude": float(round(lat, 6)),
                "longitude": float(round(lon, 6)),
                "predicted_n_deficiency": float(round(max(0.0, float(p[0])), 2)),
                "predicted_p_deficiency": float(round(max(0.0, float(p[1])), 2)),
                "predicted_k_deficiency": float(round(max(0.0, float(p[2])), 2)),
                "predicted_ph": float(round(float(p[3]), 2)),
                "predicted_ec": float(round(max(0.0, float(p[4])), 2)),
                "predicted_moisture": float(round(float(p[5]), 1)),
                "predicted_temperature": float(round(float(p[6]), 1)),
                "predicted_soil_health": float(round(float(p[7]), 1))
            })
        return points

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "norm_params": self.norm_params
        }, filepath)

    def load(self, filepath: str):
        checkpoint = torch.load(filepath, map_location="cpu")
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.norm_params = checkpoint["norm_params"]
        self.model.eval()
