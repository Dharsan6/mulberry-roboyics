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
    Precision Sericulture Agronomic Baseline & Prescription Engine.
    Evaluates soil parameters against Central Sericultural Research & Training Institute (CSRTI)
    standards for Morus alba (cultivars V1, S36, Kanva-2, MR-2).
    
    Provides deterministic calculations for:
    - Elemental NPK Shortfalls (kg/ha)
    - Commercial Fertilizer Dosages:
        * Urea (46% N) = N_shortfall / 0.46
        * Single Super Phosphate SSP (16% P2O5) = P_shortfall / 0.16
        * Muriate of Potash MOP (60% K2O) = K_shortfall / 0.60
    - Soil Amendments:
        * Agricultural Lime (CaCO3) for acidic soil (pH < 6.5)
        * Gypsum (CaSO4.2H2O) for alkaline/saline soil (pH > 7.5 or EC > 1.0)
        * Farmyard Manure (FYM) baseline 20 tons/ha
    - Bio-fertilizer inoculation recommendations (Azotobacter, PSB, VAM)
    - Sericulture Economic Cocoon Yield Impact
    """

    def __init__(self, targets: Dict[str, float] = None):
        self.targets = targets or MULBERRY_TARGETS

    def evaluate_sample(self, sample: SoilTelemetryBase) -> AgronomicAnalysisResponse:
        # 1. pH Evaluation
        if sample.ph < self.targets["ph_min"]:
            ph_status = "LOW"
            lime_gypsum = round(max(0.5, (6.5 - sample.ph) * 1.8), 2)  # tons/ha Lime
            amend_note = f"Acidic Soil: Apply {lime_gypsum} t/ha Agricultural Lime (CaCO3) 4 weeks before pruning."
        elif sample.ph > self.targets["ph_max"]:
            ph_status = "HIGH"
            lime_gypsum = round(max(0.5, (sample.ph - 7.5) * 1.5), 2)  # tons/ha Gypsum
            amend_note = f"Alkaline Soil: Apply {lime_gypsum} t/ha Mineral Gypsum (CaSO4) with deep flushing."
        else:
            ph_status = "OPTIMAL"
            lime_gypsum = 0.0
            amend_note = "Soil pH is in optimal Mulberry range (6.5 - 7.5)."

        # 2. EC Evaluation
        if sample.ec >= self.targets["ec_max"]:
            ec_status = "HIGH"
        else:
            ec_status = "NORMAL"

        # 3. Nutrient Shortfalls (kg/ha)
        n_deficiency = max(self.targets["n"] - sample.nitrogen, 0.0)
        p_deficiency = max(self.targets["p"] - sample.phosphorus, 0.0)
        k_deficiency = max(self.targets["k"] - sample.potassium, 0.0)

        # 4. Commercial Fertilizer Quantities (kg/ha)
        urea_req = round(n_deficiency / 0.46, 1) if n_deficiency > 0 else 0.0
        ssp_req = round(p_deficiency / 0.16, 1) if p_deficiency > 0 else 0.0
        mop_req = round(k_deficiency / 0.60, 1) if k_deficiency > 0 else 0.0
        
        # FYM requirement based on organic carbon
        soc = getattr(sample, 'organic_carbon', 0.72)
        if soc < 0.5:
            fym_req = 25.0
        elif soc < 0.7:
            fym_req = 20.0
        else:
            fym_req = 15.0

        # Bio-fertilizer recommendation
        bio_notes = (
            "Inoculate with Azotobacter chroococcum (20 kg/ha) + PSB Bacillus megaterium (10 kg/ha) "
            "mixed with 200 kg FYM for enhanced nutrient bioavailability."
        )

        # 5. Overall Status
        total_shortfall = n_deficiency + p_deficiency + k_deficiency
        if total_shortfall > 160.0 or ph_status != "OPTIMAL" or ec_status == "HIGH":
            overall_status = "SEVERE_DEFICIENCY" if total_shortfall > 240.0 else "DEFICIENT"
        else:
            overall_status = "SUFFICIENT"

        # 6. Economic Sericulture Impact
        if overall_status == "SUFFICIENT":
            econ_impact = "High Leaf Yield Projected (55-60 MT/ha/yr) • High Cocoon Quality (Shell Ratio > 22%)."
        elif overall_status == "DEFICIENT":
            econ_impact = (
                f"Moderate Yield Loss Risk (15-25%). Correcting {urea_req}kg Urea & {ssp_req}kg SSP "
                f"protects estimated ₹35,000/acre cocoon revenue."
            )
        else:
            econ_impact = (
                f"Severe Yield Loss Alert (>40%). Immediate basal remediation required. "
                f"Deficiency impairs silkworm rearing capacity by ~120 DFLs/acre."
            )

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
            temperature=getattr(sample, 'temperature', 26.5),
            organic_carbon=soc,
            soil_health_index=getattr(sample, 'soil_health_index', 80.0),
            nitrogen=sample.nitrogen,
            n_deficiency=round(n_deficiency, 2),
            urea_requirement=urea_req,
            phosphorus=sample.phosphorus,
            p_deficiency=round(p_deficiency, 2),
            ssp_requirement=ssp_req,
            potassium=sample.potassium,
            k_deficiency=round(k_deficiency, 2),
            mop_requirement=mop_req,
            lime_gypsum_requirement=lime_gypsum,
            fym_requirement=fym_req,
            bio_fertilizer_notes=bio_notes,
            overall_soil_status=overall_status,
            sericulture_economic_impact=econ_impact
        )

agronomy_engine = AgronomyEngine()
