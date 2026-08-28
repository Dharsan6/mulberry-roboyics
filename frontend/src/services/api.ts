import type {
  PlantationSummary,
  SoilObservation,
  AgronomicAnalysis,
  SpatialGridResponse,
  FertilizerPrescriptionZone,
  RoverSimulatorStatus
} from '../types/telemetry';
import {
  MOCK_SUMMARY,
  MOCK_SAMPLES,
  MOCK_ANALYSIS_LIST,
  MOCK_SPATIAL_RESPONSES,
  MOCK_PRESCRIPTIONS,
  MOCK_ROVER_STATUS
} from '../mock/mockData';

const API_BASE_URL = 'http://localhost:8000';

let forceMockMode = false;
let isBackendReachable = false;
let mockRoverState = { ...MOCK_ROVER_STATUS };

const listeners: Array<(isMock: boolean, isConnected: boolean) => void> = [];

export const subscribeConnectionState = (fn: (isMock: boolean, isConnected: boolean) => void) => {
  listeners.push(fn);
  fn(forceMockMode, isBackendReachable);
  return () => {
    const idx = listeners.indexOf(fn);
    if (idx !== -1) listeners.splice(idx, 1);
  };
};

const notifyListeners = () => {
  listeners.forEach(fn => fn(forceMockMode, isBackendReachable));
};

export const setForceMockMode = (val: boolean) => {
  forceMockMode = val;
  notifyListeners();
};

export const getForceMockMode = () => forceMockMode;
export const getIsBackendConnected = () => isBackendReachable;

export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(id);
    if (res.ok) {
      isBackendReachable = true;
      notifyListeners();
      return true;
    }
  } catch (e) {
    // Backend unreachable
  }
  isBackendReachable = false;
  notifyListeners();
  return false;
};

export const apiService = {
  getSummary: async (): Promise<PlantationSummary> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/plantation/summary`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend call failed, falling back to mock dataset');
      }
    }
    return MOCK_SUMMARY;
  },

  getTelemetry: async (limit: number = 100): Promise<SoilObservation[]> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/telemetry?limit=${limit}`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend telemetry call failed, falling back to mock dataset');
      }
    }
    return MOCK_SAMPLES.slice(0, limit);
  },

  getSampleAnalysis: async (sampleId: string): Promise<AgronomicAnalysis | null> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/analysis/${sampleId}`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend analysis call failed');
      }
    }
    const found = MOCK_ANALYSIS_LIST.find(a => a.sample_id === sampleId);
    return found || MOCK_ANALYSIS_LIST[0];
  },

  getSpatialPredictions: async (modelType: 'IDW' | 'RandomForest' | 'EfficientNet'): Promise<SpatialGridResponse> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/predictions?model_type=${modelType}`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend spatial predictions call failed');
      }
    }
    return MOCK_SPATIAL_RESPONSES[modelType] || MOCK_SPATIAL_RESPONSES.IDW;
  },

  getPrescriptions: async (): Promise<FertilizerPrescriptionZone[]> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/prescriptions`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend prescriptions call failed');
      }
    }
    return MOCK_PRESCRIPTIONS;
  },

  getSimulatorStatus: async (): Promise<RoverSimulatorStatus> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/simulator/status`);
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend simulator status call failed');
      }
    }
    return mockRoverState;
  },

  stepSimulator: async (): Promise<RoverSimulatorStatus> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/simulator/step`, { method: 'POST' });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn('Backend simulator step call failed');
      }
    }
    
    const states: ('TRANSIT' | 'DEPLOYMENT' | 'INTERROGATION' | 'RETRACTION')[] = [
      'TRANSIT', 'DEPLOYMENT', 'INTERROGATION', 'RETRACTION'
    ];
    const currentIndex = states.indexOf(mockRoverState.rover_state as any);
    const nextState = states[(currentIndex + 1) % states.length];
    
    mockRoverState = {
      ...mockRoverState,
      step_index: mockRoverState.step_index + 1,
      rover_state: nextState,
      actuator: {
        speed_pwm: 90,
        top_limit_switch: nextState === 'TRANSIT',
        bottom_limit_switch: nextState === 'INTERROGATION'
      },
      is_estop: false
    };

    return mockRoverState;
  },

  resetSimulator: async (): Promise<RoverSimulatorStatus> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/simulator/reset`, { method: 'POST' });
        if (res.ok) return await apiService.getSimulatorStatus();
      } catch (e) {
        console.warn('Backend simulator reset call failed');
      }
    }
    mockRoverState = { ...MOCK_ROVER_STATUS, rover_state: 'TRANSIT', step_index: 0, is_estop: false };
    return mockRoverState;
  },

  estopSimulator: async (): Promise<RoverSimulatorStatus> => {
    if (!forceMockMode && isBackendReachable) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/simulator/estop`, { method: 'POST' });
        if (res.ok) return await apiService.getSimulatorStatus();
      } catch (e) {
        console.warn('Backend E-Stop call failed');
      }
    }
    mockRoverState = { ...mockRoverState, rover_state: 'E_STOP', is_estop: true };
    return mockRoverState;
  }
};
