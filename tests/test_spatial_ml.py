import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from ml.synthetic_generator import SyntheticPlantationGenerator
from ml.spatial_idw import SpatialIDWInterpolator
from ml.baseline_model import SpatialRandomForestBaseline
from ml.efficientnet_model import EfficientNetPipeline

def test_synthetic_data_generation():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=100)
    assert len(df) == 100
    assert "ph" in df.columns
    assert "nitrogen" in df.columns

def test_idw_grid():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=50)
    idw = SpatialIDWInterpolator()
    grid = idw.fit_predict_grid(df, grid_size=10)
    assert len(grid) == 100
    assert "predicted_n_deficiency" in grid[0]

def test_rf_baseline():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=100)
    rf = SpatialRandomForestBaseline(n_estimators=10)
    metrics = rf.train_and_evaluate(df)
    assert "N_MAE" in metrics
    assert "P_RMSE" in metrics

def test_efficientnet_pipeline():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=100)
    eff = EfficientNetPipeline(epochs=2)
    metrics = eff.train_and_evaluate(df)
    assert "N_MAE" in metrics
    assert "K_R2" in metrics
