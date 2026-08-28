export interface SoilObservation {
  id?: number;
  sample_id: string;
  mission_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  altitude: number;
  ph: number;
  ec: number;
  moisture: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  rover_state: 'TRANSIT' | 'DEPLOYMENT' | 'INTERROGATION' | 'RETRACTION' | 'E_STOP';
  is_valid: boolean;
  created_at?: string;
}

export interface AgronomicAnalysis {
  sample_id: string;
  mission_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  ph: number;
  ph_status: 'LOW' | 'OPTIMAL' | 'HIGH';
  ec: number;
  ec_status: 'NORMAL' | 'HIGH';
  moisture: number;
  nitrogen: number;
  n_deficiency: number;
  phosphorus: number;
  p_deficiency: number;
  potassium: number;
  k_deficiency: number;
  overall_soil_status: 'SUFFICIENT' | 'DEFICIENT' | 'SEVERE_DEFICIENCY';
}

export interface SpatialPredictionPoint {
  grid_x: number;
  grid_y: number;
  latitude: number;
  longitude: number;
  predicted_n_deficiency: number;
  predicted_p_deficiency: number;
  predicted_k_deficiency: number;
  predicted_ph: number;
  predicted_ec: number;
}

export interface SpatialGridResponse {
  model_type: 'IDW' | 'RandomForest' | 'EfficientNet';
  timestamp: string;
  total_grid_points: number;
  predictions: SpatialPredictionPoint[];
}

export interface FertilizerPrescriptionZone {
  zone_id: string;
  center_lat: number;
  center_lon: number;
  n_deficiency: number;
  p_deficiency: number;
  k_deficiency: number;
  priority: 'HIGH' | 'MODERATE' | 'LOW';
  recommendation_note: string;
}

export interface PlantationSummary {
  total_samples: number;
  total_missions: number;
  current_rover_state: string;
  latest_gps: {
    latitude: number;
    longitude: number;
  };
  avg_ph: number;
  avg_ec: number;
  avg_moisture: number;
  total_n_deficiency: number;
  total_p_deficiency: number;
  total_k_deficiency: number;
  system_status: string;
}

export interface RoverSimulatorStatus {
  step_index: number;
  rover_state: string;
  current_waypoint: {
    id: string;
    latitude: number;
    longitude: number;
  };
  gps: {
    latitude: number;
    longitude: number;
    altitude: number;
  };
  actuator: {
    speed_pwm: number;
    top_limit_switch: boolean;
    bottom_limit_switch: boolean;
  };
  latest_telemetry?: SoilObservation;
  is_estop: boolean;
}
