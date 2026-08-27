import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
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
    Spatial Neural Network Regression model for nutrient deficiency prediction.
    Features: (latitude, longitude, pH, EC, moisture).
    Outputs: (N_deficiency, P_deficiency, K_deficiency).
    """

    def __init__(self, input_dim: int = 5, output_dim: int = 3):
        super(EfficientNetSpatialRegressor, self).__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.SiLU(),  # Swish activation (as in EfficientNet)
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.SiLU(),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.SiLU(),
        )
        
        self.regression_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.SiLU(),
            nn.Linear(32, output_dim),
            nn.ReLU()  # Nutrient shortfalls are non-negative
        )

    def forward(self, x):
        features = self.encoder(x)
        out = self.regression_head(features)
        return out


class EfficientNetPipeline:
    def __init__(self, epochs: int = 50, batch_size: int = 32, lr: float = 0.003):
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.model = EfficientNetSpatialRegressor()
        self.target_cols = ["n_deficiency", "p_deficiency", "k_deficiency"]

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, Tuple]:
        df = df.copy()
        df["n_deficiency"] = np.maximum(350.0 - df["nitrogen"], 0.0)
        df["p_deficiency"] = np.maximum(140.0 - df["phosphorus"], 0.0)
        df["k_deficiency"] = np.maximum(140.0 - df["potassium"], 0.0)

        feature_cols = ["latitude", "longitude", "ph", "ec", "moisture"]
        X = df[feature_cols].values
        y = df[self.target_cols].values

        # Normalize features
        mean_X = np.mean(X, axis=0)
        std_X = np.std(X, axis=0) + 1e-8
        X_scaled = (X - mean_X) / std_X

        return X_scaled, y, (mean_X, std_X)

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict[str, Any]:
        X, y, norm_params = self.prepare_data(df)
        self.norm_params = norm_params

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        train_dataset = SpatialSoilDataset(X_train, y_train)
        test_dataset = SpatialSoilDataset(X_test, y_test)

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
            prefix = target.split("_")[0].upper()
            y_true_col = y_test[:, idx]
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
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "norm_params": self.norm_params
        }, filepath)

    def load(self, filepath: str):
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.norm_params = checkpoint["norm_params"]
        self.model.eval()
