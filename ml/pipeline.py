import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import json
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from backend.app.database.connection import engine, SessionLocal, Base
from backend.app.database.models import (
    MissionModel, SoilObservationModel, SoilAnalysisModel,
    SpatialPredictionModel, FertilizerPrescriptionModel
)
from backend.app.services.agronomy_service import agronomy_engine
from backend.app.schemas.telemetry import SoilTelemetryBase
from ml.synthetic_generator import SyntheticPlantationGenerator
from ml.spatial_idw import SpatialIDWInterpolator
from ml.baseline_model import SpatialRandomForestBaseline
from ml.efficientnet_model import EfficientNetPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml_pipeline")

def run_full_ml_pipeline(num_samples: int = 1000):
    logger.info("--- Starting Precision Sericulture ML Pipeline ---")
    
    # 1. Ensure DB tables exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 2. Generate Synthetic Dataset
    logger.info(f"Generating {num_samples} spatially correlated Mulberry plantation observations...")
    generator = SyntheticPlantationGenerator()
    df = generator.generate_dataset(num_samples=num_samples)
    
    # Save raw CSV
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/synthetic_plantation_samples.csv", index=False)
    logger.info("Saved synthetic dataset to data/raw/synthetic_plantation_samples.csv")

    # 3. Populate Database with Soil Observations & Agronomic Analyses
    logger.info("Populating Database with Observations and Agronomic Evaluations...")

    db.query(SoilAnalysisModel).delete()
    db.query(SoilObservationModel).delete()
    db.query(MissionModel).delete()
    db.query(SpatialPredictionModel).delete()
    db.query(FertilizerPrescriptionModel).delete()
    db.commit()

    missions_seen = set()
    for _, row in df.iterrows():
        m_id = row["mission_id"]
        if m_id not in missions_seen:
            mission_rec = MissionModel(mission_id=m_id, status="COMPLETED")
            db.add(mission_rec)
            missions_seen.add(m_id)

        obs = SoilObservationModel(
            sample_id=row["sample_id"],
            mission_id=row["mission_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            latitude=row["latitude"],
            longitude=row["longitude"],
            altitude=row["altitude"],
            ph=row["ph"],
            ec=row["ec"],
            moisture=row["moisture"],
            nitrogen=row["nitrogen"],
            phosphorus=row["phosphorus"],
            potassium=row["potassium"],
            rover_state=row["rover_state"],
            is_valid=True
        )
        db.add(obs)

        # Agronomic evaluation
        t_base = SoilTelemetryBase(
            sample_id=row["sample_id"],
            mission_id=row["mission_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            latitude=row["latitude"],
            longitude=row["longitude"],
            ph=row["ph"],
            ec=row["ec"],
            moisture=row["moisture"],
            nitrogen=row["nitrogen"],
            phosphorus=row["phosphorus"],
            potassium=row["potassium"],
            rover_state=row["rover_state"]
        )
        analysis_res = agronomy_engine.evaluate_sample(t_base)
        analysis_rec = SoilAnalysisModel(
            sample_id=row["sample_id"],
            ph_status=analysis_res.ph_status,
            ec_status=analysis_res.ec_status,
            n_deficiency=analysis_res.n_deficiency,
            p_deficiency=analysis_res.p_deficiency,
            k_deficiency=analysis_res.k_deficiency,
            overall_soil_status=analysis_res.overall_soil_status
        )
        db.add(analysis_rec)

    db.commit()
    logger.info("Successfully loaded raw telemetry & agronomic analysis into database.")

    # 4. Generate Spatial Interpolation Grid (IDW Baseline)
    logger.info("Generating IDW Spatial Interpolation Grid (50x50)...")
    idw = SpatialIDWInterpolator()
    grid_points = idw.fit_predict_grid(df, grid_size=50)

    for pt in grid_points:
        sp_rec = SpatialPredictionModel(
            model_type="IDW",
            grid_x=pt["grid_x"],
            grid_y=pt["grid_y"],
            latitude=pt["latitude"],
            longitude=pt["longitude"],
            predicted_n_deficiency=pt["predicted_n_deficiency"],
            predicted_p_deficiency=pt["predicted_p_deficiency"],
            predicted_k_deficiency=pt["predicted_k_deficiency"],
            predicted_ph=pt["predicted_ph"],
            predicted_ec=pt["predicted_ec"]
        )
        db.add(sp_rec)
    db.commit()
    logger.info(f"Saved {len(grid_points)} IDW spatial grid points to database.")

    # 5. Train & Evaluate Traditional ML Baseline (Random Forest)
    logger.info("Training Traditional ML Baseline (Random Forest)...")
    rf_baseline = SpatialRandomForestBaseline()
    rf_metrics = rf_baseline.train_and_evaluate(df)
    rf_baseline.save("models/baseline/rf_nutrient_model.pkl")
    logger.info(f"Random Forest Baseline Metrics: {json.dumps(rf_metrics, indent=2)}")

    # 6. Train & Evaluate PyTorch EfficientNet Spatial Network
    logger.info("Training PyTorch EfficientNet Spatial Regression Network...")
    eff_pipeline = EfficientNetPipeline(epochs=40)
    eff_metrics = eff_pipeline.train_and_evaluate(df)
    eff_pipeline.save("models/efficientnet/spatial_regression.pt")
    logger.info(f"EfficientNet Spatial Model Metrics: {json.dumps(eff_metrics, indent=2)}")

    # Save metrics summary artifact
    os.makedirs("models", exist_ok=True)
    summary_metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "baseline_random_forest": rf_metrics,
        "efficientnet_spatial_regressor": eff_metrics
    }
    with open("models/metrics_summary.json", "w") as f:
        json.dump(summary_metrics, f, indent=2)

    # 7. Generate Fertilizer Prescription Matrix
    logger.info("Generating Zone-by-Zone Fertilizer Prescriptions...")
    zones = [
        {"id": "Zone A (North-West)", "lat": 11.3927, "lon": 77.7336, "n": 95.0, "p": 12.0, "k": 15.0, "prio": "HIGH", "note": "High Nitrogen Shortfall observed. Recommended split urea/compost application."},
        {"id": "Zone B (North-East)", "lat": 11.3927, "lon": 77.7348, "n": 15.0, "p": 48.0, "k": 10.0, "prio": "HIGH", "note": "Phosphorus Deficiency detected. Apply Single Super Phosphate (SSP)."},
        {"id": "Zone C (South-East)", "lat": 11.3915, "lon": 77.7348, "n": 10.0, "p": 15.0, "k": 42.0, "prio": "MODERATE", "note": "Potassium Shortfall. Apply Muriate of Potash (MOP)."},
        {"id": "Zone D (South-West)", "lat": 11.3915, "lon": 77.7336, "n": 20.0, "p": 10.0, "k": 12.0, "prio": "MODERATE", "note": "High Soil EC (>1.2 dS/m). Leaching flush and organic mulching recommended."},
        {"id": "Zone E (Center Plantation)", "lat": 11.3921, "lon": 77.7342, "n": 25.0, "p": 15.0, "k": 18.0, "prio": "LOW", "note": "Low pH (<5.8). Apply Agricultural Lime (CaCO3) for pH amendment."}
    ]

    for z in zones:
        pz = FertilizerPrescriptionModel(
            zone_id=z["id"],
            center_lat=z["lat"],
            center_lon=z["lon"],
            n_deficiency=z["n"],
            p_deficiency=z["p"],
            k_deficiency=z["k"],
            priority=z["prio"],
            recommendation_note=z["note"]
        )
        db.add(pz)
    db.commit()

    db.close()
    logger.info("--- Precision Sericulture ML Pipeline Completed Successfully! ---")
    return summary_metrics

if __name__ == "__main__":
    run_full_ml_pipeline(1000)
