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
    logger.info("==================================================================")
    logger.info("  STARTING PRECISION SERICULTURE ADVANCED ML PIPELINE            ")
    logger.info("==================================================================")
    
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
        m_name = row.get("mission_name", f"Mission {m_id}")
        if m_id not in missions_seen:
            mission_rec = MissionModel(
                mission_id=m_id,
                mission_name=m_name,
                status="COMPLETED",
                started_at=datetime.fromisoformat(row["timestamp"])
            )
            db.add(mission_rec)
            missions_seen.add(m_id)

        obs = SoilObservationModel(
            sample_id=row["sample_id"],
            mission_id=row["mission_id"],
            mission_name=m_name,
            timestamp=datetime.fromisoformat(row["timestamp"]),
            latitude=row["latitude"],
            longitude=row["longitude"],
            altitude=row["altitude"],
            ph=row["ph"],
            ec=row["ec"],
            moisture=row["moisture"],
            temperature=row.get("temperature", 26.5),
            nitrogen=row["nitrogen"],
            phosphorus=row["phosphorus"],
            potassium=row["potassium"],
            organic_carbon=row.get("organic_carbon", 0.72),
            soil_health_index=row.get("soil_health_index", 80.0),
            soil_texture=row.get("soil_texture", "Red Sandy Loam"),
            mulberry_variety=row.get("mulberry_variety", "V1 (Victory-1)"),
            probe_depth_cm=row.get("probe_depth_cm", 15.0),
            battery_soc=row.get("battery_soc", 95.0),
            raw_modbus_hex=row.get("raw_modbus_hex"),
            rover_state=row["rover_state"],
            is_valid=True
        )
        db.add(obs)

        # Agronomic evaluation
        t_base = SoilTelemetryBase(
            sample_id=row["sample_id"],
            mission_id=row["mission_id"],
            mission_name=m_name,
            timestamp=datetime.fromisoformat(row["timestamp"]),
            latitude=row["latitude"],
            longitude=row["longitude"],
            ph=row["ph"],
            ec=row["ec"],
            moisture=row["moisture"],
            temperature=row.get("temperature", 26.5),
            nitrogen=row["nitrogen"],
            phosphorus=row["phosphorus"],
            potassium=row["potassium"],
            organic_carbon=row.get("organic_carbon", 0.72),
            soil_health_index=row.get("soil_health_index", 80.0),
            soil_texture=row.get("soil_texture", "Red Sandy Loam"),
            mulberry_variety=row.get("mulberry_variety", "V1 (Victory-1)"),
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
            urea_requirement=analysis_res.urea_requirement,
            ssp_requirement=analysis_res.ssp_requirement,
            mop_requirement=analysis_res.mop_requirement,
            lime_gypsum_requirement=analysis_res.lime_gypsum_requirement,
            fym_requirement=analysis_res.fym_requirement,
            bio_fertilizer_notes=analysis_res.bio_fertilizer_notes,
            overall_soil_status=analysis_res.overall_soil_status,
            sericulture_economic_impact=analysis_res.sericulture_economic_impact
        )
        db.add(analysis_rec)

    db.commit()
    logger.info("Successfully loaded raw telemetry & agronomic analysis into database.")

    # 4. Generate Spatial Interpolation Grid (IDW Baseline)
    logger.info("Generating IDW Spatial Interpolation Grid (50x50)...")
    idw = SpatialIDWInterpolator()
    idw_grid_points = idw.fit_predict_grid(df, grid_size=50)

    for pt in idw_grid_points:
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
            predicted_ec=pt["predicted_ec"],
            predicted_moisture=pt["predicted_moisture"],
            predicted_temperature=pt["predicted_temperature"],
            predicted_soil_health=pt["predicted_soil_health"]
        )
        db.add(sp_rec)
    db.commit()
    logger.info(f"Saved {len(idw_grid_points)} IDW spatial grid points to database.")

    # 5. Train & Evaluate Traditional ML Baseline (Random Forest)
    logger.info("Training Traditional ML Baseline (Random Forest)...")
    rf_baseline = SpatialRandomForestBaseline(n_estimators=100)
    rf_metrics = rf_baseline.train_and_evaluate(df)
    rf_baseline.save("models/baseline/rf_nutrient_model.pkl")
    logger.info(f"Random Forest Baseline Metrics: {json.dumps(rf_metrics, indent=2)}")

    rf_grid_points = rf_baseline.predict_grid(grid_size=50)
    for pt in rf_grid_points:
        sp_rec = SpatialPredictionModel(
            model_type="RandomForest",
            grid_x=pt["grid_x"],
            grid_y=pt["grid_y"],
            latitude=pt["latitude"],
            longitude=pt["longitude"],
            predicted_n_deficiency=pt["predicted_n_deficiency"],
            predicted_p_deficiency=pt["predicted_p_deficiency"],
            predicted_k_deficiency=pt["predicted_k_deficiency"],
            predicted_ph=pt["predicted_ph"],
            predicted_ec=pt["predicted_ec"],
            predicted_moisture=pt["predicted_moisture"],
            predicted_temperature=pt["predicted_temperature"],
            predicted_soil_health=pt["predicted_soil_health"]
        )
        db.add(sp_rec)
    db.commit()
    logger.info(f"Saved {len(rf_grid_points)} Random Forest spatial grid points to database.")

    # 6. Train & Evaluate PyTorch EfficientNet Spatial Network
    logger.info("Training PyTorch EfficientNet Spatial Regression Network...")
    eff_pipeline = EfficientNetPipeline(epochs=35)
    eff_metrics = eff_pipeline.train_and_evaluate(df)
    eff_pipeline.save("models/efficientnet/spatial_regression.pt")
    logger.info(f"EfficientNet Spatial Model Metrics: {json.dumps(eff_metrics, indent=2)}")

    eff_grid_points = eff_pipeline.predict_grid(grid_size=50)
    for pt in eff_grid_points:
        sp_rec = SpatialPredictionModel(
            model_type="EfficientNet",
            grid_x=pt["grid_x"],
            grid_y=pt["grid_y"],
            latitude=pt["latitude"],
            longitude=pt["longitude"],
            predicted_n_deficiency=pt["predicted_n_deficiency"],
            predicted_p_deficiency=pt["predicted_p_deficiency"],
            predicted_k_deficiency=pt["predicted_k_deficiency"],
            predicted_ph=pt["predicted_ph"],
            predicted_ec=pt["predicted_ec"],
            predicted_moisture=pt["predicted_moisture"],
            predicted_temperature=pt["predicted_temperature"],
            predicted_soil_health=pt["predicted_soil_health"]
        )
        db.add(sp_rec)
    db.commit()
    logger.info(f"Saved {len(eff_grid_points)} EfficientNet spatial grid points to database.")

    # Save metrics summary artifact
    os.makedirs("models", exist_ok=True)
    summary_metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "baseline_random_forest": rf_metrics,
        "efficientnet_spatial_regressor": eff_metrics,
        "dataset_statistics": {
            "total_samples": len(df),
            "total_missions": len(missions_seen),
            "avg_ph": round(float(df["ph"].mean()), 2),
            "avg_ec": round(float(df["ec"].mean()), 2),
            "avg_soil_health": round(float(df["soil_health_index"].mean()), 1)
        }
    }
    with open("models/metrics_summary.json", "w") as f:
        json.dump(summary_metrics, f, indent=2)

    # 7. Generate Detailed Zone-by-Zone Fertilizer Prescriptions
    logger.info("Generating Comprehensive Mulberry Fertilizer Prescriptions...")
    zones = [
        {
            "id": "Zone A",
            "name": "North-West (Nitrogen Deficient Sector)",
            "lat": 11.3927, "lon": 77.7336,
            "n": 105.0, "p": 12.0, "k": 15.0,
            "ph": 6.85, "ec": 0.65, "health": 68.0,
            "prio": "HIGH",
            "urea": 228.0, "ssp": 75.0, "mop": 25.0,
            "amend": "Apply 20 t/ha Farmyard Manure (FYM). Soil organic carbon is depressed.",
            "sched": "Split 1 (Basal): 50% Urea + 100% SSP + 50% MOP after pruning. Split 2 (Top Dress): 50% Urea + 50% MOP at 30 days.",
            "note": "Severe Nitrogen Shortfall (>100 kg/ha). Stunting shoot elongation and chlorophyll synthesis in Morus alba. Inoculate with Azotobacter chroococcum."
        },
        {
            "id": "Zone B",
            "name": "North-East (Phosphorus Deficient Sector)",
            "lat": 11.3927, "lon": 77.7348,
            "n": 18.0, "p": 58.0, "k": 12.0,
            "ph": 7.05, "ec": 0.62, "health": 74.0,
            "prio": "HIGH",
            "urea": 40.0, "ssp": 362.0, "mop": 20.0,
            "amend": "Band placement of Single Super Phosphate (SSP) near root feeding zone (15-20cm depth).",
            "sched": "100% SSP applied at bottom of furrow during intercultural operations after crown pruning.",
            "note": "Phosphorus deficiency observed. Hinders root establishment and secondary shoot vigor. Apply Phosphobacteria (PSB) @ 10kg/ha."
        },
        {
            "id": "Zone C",
            "name": "South-East (Potassium Deficient Sector)",
            "lat": 11.3915, "lon": 77.7348,
            "n": 12.0, "p": 14.0, "k": 52.0,
            "ph": 6.90, "ec": 0.60, "health": 76.0,
            "prio": "MODERATE",
            "urea": 26.0, "ssp": 88.0, "mop": 86.0,
            "amend": "Foliar spray of 1% Potassium Nitrate (KNO3) during dry spells to maintain leaf moisture retention for late-age silkworms.",
            "sched": "50% MOP at basal application, 50% at 28-30 days post pruning.",
            "note": "Potassium shortfall reduces drought resilience and succulent leaf moisture content critical for 5th instar silkworms."
        },
        {
            "id": "Zone D",
            "name": "South-West (Saline / High EC Sector)",
            "lat": 11.3915, "lon": 77.7336,
            "n": 22.0, "p": 10.0, "k": 14.0,
            "ph": 7.85, "ec": 1.75, "health": 59.0,
            "prio": "HIGH",
            "urea": 48.0, "ssp": 62.0, "mop": 23.0,
            "amend": "Apply 1.5 t/ha Mineral Gypsum (CaSO4.2H2O) + deep irrigation leaching to flush accumulated salts below root zone.",
            "sched": "Gypsum application 3 weeks before pruning; organic green manure mulching (Crotalaria juncea).",
            "note": "Electrical Conductivity exceeds critical threshold (>1.0 dS/m). Osmotic stress inhibits Mulberry root water absorption."
        },
        {
            "id": "Zone E",
            "name": "Center-West (Acidic Soil Patch)",
            "lat": 11.3921, "lon": 77.7338,
            "n": 28.0, "p": 22.0, "k": 18.0,
            "ph": 5.45, "ec": 0.58, "health": 64.0,
            "prio": "HIGH",
            "urea": 60.0, "ssp": 138.0, "mop": 30.0,
            "amend": "Apply 2.0 t/ha Agricultural Lime (CaCO3) or Dolomite to raise soil pH to 6.8.",
            "sched": "Broadcast agricultural lime evenly and incorporate 4 weeks prior to pruning.",
            "note": "Low pH (<5.8) induces Phosphorus fixation and potential micro-nutrient toxicity. Lime amendment restores nutrient availability."
        },
        {
            "id": "Zone F",
            "name": "Center-East (Optimal High-Yield Benchmark)",
            "lat": 11.3921, "lon": 77.7345,
            "n": 0.0, "p": 0.0, "k": 0.0,
            "ph": 6.95, "ec": 0.55, "health": 94.0,
            "prio": "LOW",
            "urea": 0.0, "ssp": 0.0, "mop": 0.0,
            "amend": "Maintain standard maintenance dosage: 20 t/ha FYM annually.",
            "sched": "Standard maintenance fertilization program.",
            "note": "Soil chemical and biological parameters meet prime CSRTI standards. Leaf yield potential > 55 MT/ha/yr."
        },
        {
            "id": "Zone G",
            "name": "South Central (Drainage Depression)",
            "lat": 11.3913, "lon": 77.7342,
            "n": 15.0, "p": 12.0, "k": 10.0,
            "ph": 6.75, "ec": 0.52, "health": 78.0,
            "prio": "MODERATE",
            "urea": 32.0, "ssp": 75.0, "mop": 16.0,
            "amend": "Construct subsurface ridge-and-furrow drainage channels to alleviate anaerobic root waterlogging.",
            "sched": "Drainage excavation prior to South-West monsoon onset.",
            "note": "Depression retains excess moisture (>65%). High risk of root rot (*Fusarium solani*). Drench with Trichoderma harzianum."
        }
    ]

    for z in zones:
        pz = FertilizerPrescriptionModel(
            zone_id=z["id"],
            zone_name=z["name"],
            center_lat=z["lat"],
            center_lon=z["lon"],
            n_deficiency=z["n"],
            p_deficiency=z["p"],
            k_deficiency=z["k"],
            avg_ph=z["ph"],
            avg_ec=z["ec"],
            avg_health_score=z["health"],
            priority=z["prio"],
            urea_kg_ha=z["urea"],
            ssp_kg_ha=z["ssp"],
            mop_kg_ha=z["mop"],
            amendment_note=z["amend"],
            application_schedule=z["sched"],
            recommendation_note=z["note"]
        )
        db.add(pz)
    db.commit()

    db.close()
    logger.info("==================================================================")
    logger.info("  ML PIPELINE & DATABASE INITIALIZATION COMPLETED!               ")
    logger.info("==================================================================")
    return summary_metrics

if __name__ == "__main__":
    run_full_ml_pipeline(1000)
