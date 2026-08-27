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
    assert "soil_health_index" in df.columns
    assert "raw_modbus_hex" in df.columns

def test_idw_grid():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=50)
    idw = SpatialIDWInterpolator()
    grid = idw.fit_predict_grid(df, grid_size=10)
    assert len(grid) == 100
    assert "predicted_n_deficiency" in grid[0]
    assert "predicted_soil_health" in grid[0]

def test_rf_baseline():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=100)
    rf = SpatialRandomForestBaseline(n_estimators=10)
    metrics = rf.train_and_evaluate(df)
    assert any("N" in k and "MAE" in k for k in metrics.keys())
    assert any("P" in k and "RMSE" in k for k in metrics.keys())
    
    grid = rf.predict_grid(grid_size=10)
    assert len(grid) == 100

def test_efficientnet_pipeline():
    gen = SyntheticPlantationGenerator()
    df = gen.generate_dataset(num_samples=100)
    eff = EfficientNetPipeline(epochs=2)
    metrics = eff.train_and_evaluate(df)
    assert any("N" in k and "MAE" in k for k in metrics.keys())
    
    grid = eff.predict_grid(grid_size=10)
    assert len(grid) == 100
