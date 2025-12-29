import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface CircuitRequest {
  dsl_code?: string;
  gates?: any[];
  num_qubits: number;
  backend?: string;
  shots?: number;
  return_state_history?: boolean;
  noise_model?: any;
}

export const executeCircuit = async (request: CircuitRequest) => {
  const response = await axios.post(`${API_BASE_URL}/execute`, request);
  return response.data;
};

export const analyzeCircuit = async (request: CircuitRequest) => {
  const response = await axios.post(`${API_BASE_URL}/analyze`, request);
  return response.data;
};

export const getVisualizationData = async (circuitDsl: string, type: string, qubit?: number) => {
  const response = await axios.post(`${API_BASE_URL}/api/visualize`, {
    circuit_dsl: circuitDsl,
    visualization_type: type,
    qubit,
  });
  return response.data;
};

export const getEntanglementMetrics = async (circuitDsl: string) => {
  const response = await axios.get(`${API_BASE_URL}/api/metrics/entanglement`, {
    params: { circuit_dsl: circuitDsl },
  });
  return response.data;
};


