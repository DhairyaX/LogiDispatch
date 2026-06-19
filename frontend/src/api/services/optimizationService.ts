import apiClient from '../client';
import type { OptimizationMode, BalancingMode } from '../../types/route';
import type { OptimizationResult } from '../../types/route';

export const optimizationService = {
  generateRoutes: async (optimizationMode: OptimizationMode, balancingMode: BalancingMode): Promise<OptimizationResult> => {
    const response = await apiClient.post('/optimization/generate-routes', {
      optimizationMode,
      balancingMode
    });
    return response.data;
  },
  getLatestRoute: async (): Promise<OptimizationResult> => {
    const response = await apiClient.get('/optimization/latest-route');
    return response.data;
  }
};
