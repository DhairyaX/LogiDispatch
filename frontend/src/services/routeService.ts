import type { OptimizationResult, BalancingMode } from '../types/route';
import mockData from '../mock/routeData.json';

export const routeService = {
  getRouteData: async (mode: BalancingMode): Promise<OptimizationResult> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 300));
    
    // Cast the JSON import
    const data = mockData as any as Record<BalancingMode, OptimizationResult>;
    
    if (data[mode]) {
      return data[mode];
    }
    
    throw new Error(`Balancing mode "${mode}" not found in mock data.`);
  }
};
