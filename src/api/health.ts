import { http } from './client';

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export function getApiHealth(): Promise<HealthResponse> {
  return http<HealthResponse>('/health');
}