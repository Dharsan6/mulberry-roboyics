import type {
  PlantationSummary,
  SoilObservation,
  AgronomicAnalysis,
  SpatialGridResponse,
  FertilizerPrescriptionZone,
  RoverSimulatorStatus,
  SpatialPredictionPoint
} from '../types/telemetry';

const BASE_LAT = 11.3921;
const BASE_LON = 77.7342;

const generateGridPredictions = (modelType: 'IDW' | 'RandomForest' | 'EfficientNet'): SpatialPredictionPoint[] => {
  const points: SpatialPredictionPoint[] = [];
  const gridSize = 25;

  for (let x = 0; x < gridSize; x++) {
    for (let y = 0; y < gridSize; y++) {
      const lat = BASE_LAT + (y - gridSize / 2) * 0.00015;
      const lon = BASE_LON + (x - gridSize / 2) * 0.00015;

      const distFromCenter = Math.sqrt(Math.pow(x - 12, 2) + Math.pow(y - 12, 2));
      
      let noiseFactor = 1.0;
      if (modelType === 'EfficientNet') {
        noiseFactor = Math.sin(x * 0.3) * 0.2 + Math.cos(y * 0.4) * 0.2 + 1.0;
      } else if (modelType === 'RandomForest') {
        noiseFactor = (Math.floor(x / 5) * 5 + Math.floor(y / 5) * 5) % 3 === 0 ? 1.3 : 0.8;
      } else {
        noiseFactor = 1.0 + (10 - Math.min(distFromCenter, 10)) * 0.08;
      }

      const predicted_n = Math.max(0, Math.min(180, (120 - distFromCenter * 3) * noiseFactor));
      const predicted_p = Math.max(0, Math.min(80, (50 - distFromCenter * 1.5) * noiseFactor));
      const predicted_k = Math.max(0, Math.min(90, (60 - distFromCenter * 1.8) * noiseFactor));
      const predicted_ph = Math.max(5.5, Math.min(8.2, 6.8 + (x % 5 === 0 ? -0.6 : 0.4)));
      const predicted_ec = Math.max(0.2, Math.min(1.8, 0.6 + (y % 4 === 0 ? 0.4 : 0.1)));

      points.push({
        grid_x: x,
        grid_y: y,
        latitude: parseFloat(lat.toFixed(6)),
        longitude: parseFloat(lon.toFixed(6)),
        predicted_n_deficiency: parseFloat(predicted_n.toFixed(1)),
        predicted_p_deficiency: parseFloat(predicted_p.toFixed(1)),
        predicted_k_deficiency: parseFloat(predicted_k.toFixed(1)),
        predicted_ph: parseFloat(predicted_ph.toFixed(2)),
        predicted_ec: parseFloat(predicted_ec.toFixed(2))
      });
    }
  }

  return points;
};

export const MOCK_SUMMARY: PlantationSummary = {
  total_samples: 48,
  total_missions: 6,
  current_rover_state: 'INTERROGATION',
  latest_gps: {
    latitude: BASE_LAT,
    longitude: BASE_LON
  },
  avg_ph: 6.82,
  avg_ec: 0.74,
  avg_moisture: 44.5,
  total_n_deficiency: 2150.4,
  total_p_deficiency: 890.2,
  total_k_deficiency: 1040.6,
  system_status: 'ONLINE (MOCK DEMO)'
};

export const MOCK_SAMPLES: SoilObservation[] = Array.from({ length: 20 }).map((_, i) => {
  const id = 20 - i;
  const ph = Number((6.2 + (i % 7) * 0.25).toFixed(2));
  const ec = Number((0.45 + (i % 5) * 0.18).toFixed(2));
  const n = Number((240 + (i * 7) % 110).toFixed(1));
  const p = Number((90 + (i * 4) % 55).toFixed(1));
  const k = Number((95 + (i * 5) % 50).toFixed(1));

  return {
    id,
    sample_id: `S${String(id).padStart(3, '0')}`,
    mission_id: `MSN-2026-0${Math.floor(i / 5) + 1}`,
    timestamp: new Date(Date.now() - i * 1800000).toISOString(),
    latitude: Number((BASE_LAT + (i % 5 - 2) * 0.0003).toFixed(6)),
    longitude: Number((BASE_LON + (Math.floor(i / 5) - 2) * 0.0003).toFixed(6)),
    altitude: 284.5,
    ph,
    ec,
    moisture: Number((38 + (i * 3) % 25).toFixed(1)),
    nitrogen: n,
    phosphorus: p,
    potassium: k,
    rover_state: i === 0 ? 'INTERROGATION' : 'TRANSIT',
    is_valid: true,
    created_at: new Date(Date.now() - i * 1800000).toISOString()
  };
});

export const MOCK_ANALYSIS_LIST: AgronomicAnalysis[] = MOCK_SAMPLES.map(s => {
  const n_def = Math.max(0, 350 - s.nitrogen);
  const p_def = Math.max(0, 140 - s.phosphorus);
  const k_def = Math.max(0, 140 - s.potassium);
  const defCount = (n_def > 50 ? 1 : 0) + (p_def > 30 ? 1 : 0) + (k_def > 30 ? 1 : 0);

  return {
    sample_id: s.sample_id,
    mission_id: s.mission_id,
    timestamp: s.timestamp,
    latitude: s.latitude,
    longitude: s.longitude,
    ph: s.ph,
    ph_status: s.ph < 6.5 ? 'LOW' : s.ph > 7.5 ? 'HIGH' : 'OPTIMAL',
    ec: s.ec,
    ec_status: s.ec >= 1.0 ? 'HIGH' : 'NORMAL',
    moisture: s.moisture,
    nitrogen: s.nitrogen,
    n_deficiency: Number(n_def.toFixed(1)),
    phosphorus: s.phosphorus,
    p_deficiency: Number(p_def.toFixed(1)),
    potassium: s.potassium,
    k_deficiency: Number(k_def.toFixed(1)),
    overall_soil_status: defCount >= 2 ? 'SEVERE_DEFICIENCY' : defCount === 1 ? 'DEFICIENT' : 'SUFFICIENT'
  };
});

export const MOCK_SPATIAL_RESPONSES: Record<'IDW' | 'RandomForest' | 'EfficientNet', SpatialGridResponse> = {
  IDW: {
    model_type: 'IDW',
    timestamp: new Date().toISOString(),
    total_grid_points: 625,
    predictions: generateGridPredictions('IDW')
  },
  RandomForest: {
    model_type: 'RandomForest',
    timestamp: new Date().toISOString(),
    total_grid_points: 625,
    predictions: generateGridPredictions('RandomForest')
  },
  EfficientNet: {
    model_type: 'EfficientNet',
    timestamp: new Date().toISOString(),
    total_grid_points: 625,
    predictions: generateGridPredictions('EfficientNet')
  }
};

export const MOCK_PRESCRIPTIONS: FertilizerPrescriptionZone[] = [
  {
    zone_id: 'ZONE-A1 (North Mulberry Plot)',
    center_lat: 11.3924,
    center_lon: 77.7345,
    n_deficiency: 110.5,
    p_deficiency: 45.0,
    k_deficiency: 40.0,
    priority: 'HIGH',
    recommendation_note: 'Apply 240 kg/ha Urea + 280 kg/ha Single Super Phosphate (SSP) divided into 2 fertigation cycles post leaf harvest.'
  },
  {
    zone_id: 'ZONE-A2 (Central Demonstration Plot)',
    center_lat: 11.3921,
    center_lon: 77.7342,
    n_deficiency: 45.2,
    p_deficiency: 12.0,
    k_deficiency: 15.5,
    priority: 'LOW',
    recommendation_note: 'Maintenance level organic compost (15 tons/ha) + light nitrogen top-dressing after standard pruning.'
  },
  {
    zone_id: 'ZONE-B1 (South Sericulture Block)',
    center_lat: 11.3918,
    center_lon: 77.7339,
    n_deficiency: 135.0,
    p_deficiency: 62.0,
    k_deficiency: 75.0,
    priority: 'HIGH',
    recommendation_note: 'Critical N-P-K deficit detected. Foliar spray of 1% NPK (19:19:19) baseline + soil application of Muriate of Potash (MOP).'
  },
  {
    zone_id: 'ZONE-B2 (East Mulberry Nursery)',
    center_lat: 11.3923,
    center_lon: 77.7348,
    n_deficiency: 72.0,
    p_deficiency: 25.0,
    k_deficiency: 30.0,
    priority: 'MODERATE',
    recommendation_note: 'Apply Neem-coated Urea @ 150 kg/ha to reduce leaching loss in sandy loam soil segment.'
  },
  {
    zone_id: 'ZONE-C1 (West Terraced Plantation)',
    center_lat: 11.3919,
    center_lon: 77.7336,
    n_deficiency: 95.0,
    p_deficiency: 38.0,
    k_deficiency: 48.0,
    priority: 'MODERATE',
    recommendation_note: 'Incorporate Bio-fertilizers (Azotobacter + PSB) with 200 kg/ha SSP to enhance phosphorus availability.'
  }
];

export const MOCK_ROVER_STATUS: RoverSimulatorStatus = {
  step_index: 3,
  rover_state: 'INTERROGATION',
  current_waypoint: {
    id: 'WP-04',
    latitude: BASE_LAT,
    longitude: BASE_LON
  },
  gps: {
    latitude: BASE_LAT,
    longitude: BASE_LON,
    altitude: 284.5
  },
  actuator: {
    speed_pwm: 90,
    top_limit_switch: false,
    bottom_limit_switch: true
  },
  latest_telemetry: MOCK_SAMPLES[0],
  is_estop: false
};
