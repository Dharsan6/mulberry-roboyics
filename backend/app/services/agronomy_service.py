from typing import Dict, Any
from backend.app.config import settings
from backend.app.schemas.telemetry import AgronomicAnalysisResponse, SoilTelemetryBase

MULBERRY_TARGETS = {
    "ph_min": settings.MULBERRY_PH_MIN,
    "ph_max": settings.MULBERRY_PH_MAX,
    "ec_max": settings.MULBERRY_EC_MAX,
    "n": settings.MULBERRY_TARGET_N,
    "p": settings.MULBERRY_TARGET_P,
    "k": settings.MULBERRY_TARGET_K
}

class AgronomyEngine:
    """
    Mulberry agronomic baseline comparator and nutrient shortfall calculation engine.
    Calculates deterministic soil nutrient shortfalls against established agronomic targets.
    """

    def __init__(self, targets: Dict[str, float] = None):
        self.targets = targets or MULBERRY_TARGETS

    def evaluate_sample(self, sample: SoilTelemetryBase) -> AgronomicAnalysisResponse:
        # pH evaluation
        if sample.ph < self.targets["ph_min"]:
            ph_status = "LOW"
        elif sample.ph > self.targets["ph_max"]:
            ph_status = "HIGH"
        else:
            ph_status = "OPTIMAL"

        # EC evaluation
        if sample.ec >= self.targets["ec_max"]:
            ec_status = "HIGH"
        else:
            ec_status = "NORMAL"

        # Nutrient deficiency shortfall calculations (kg/ha)
        n_deficiency = max(self.targets["n"] - sample.nitrogen, 0.0)
        p_deficiency = max(self.targets["p"] - sample.phosphorus, 0.0)
        k_deficiency = max(self.targets["k"] - sample.potassium, 0.0)

        # Overall soil status flag
        total_shortfall = n_deficiency + p_deficiency + k_deficiency
        if total_shortfall > 150.0 or ph_status != "OPTIMAL" or ec_status == "HIGH":
            overall_status = "SEVERE_DEFICIENCY" if total_shortfall > 250.0 else "DEFICIENT"
        else:
            overall_status = "SUFFICIENT"

        return AgronomicAnalysisResponse(
            sample_id=sample.sample_id,
            mission_id=sample.mission_id,
            timestamp=sample.timestamp,
            latitude=sample.latitude,
            longitude=sample.longitude,
            ph=sample.ph,
            ph_status=ph_status,
            ec=sample.ec,
            ec_status=ec_status,
            moisture=sample.moisture,
            nitrogen=sample.nitrogen,
            n_deficiency=round(n_deficiency, 2),
            phosphorus=sample.phosphorus,
            p_deficiency=round(p_deficiency, 2),
            potassium=sample.potassium,
            k_deficiency=round(k_deficiency, 2),
            overall_soil_status=overall_status
        )

agronomy_engine = AgronomyEngine()
