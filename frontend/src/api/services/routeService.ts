import apiClient from '../client';
import type { VehicleRoute } from '../../types/route';

export const routeService = {
  getActiveRoutes: async (): Promise<VehicleRoute[]> => {
    const response = await apiClient.get('/routes/active');
    // Map backend route format to frontend VehicleRoute format if needed, 
    // or just return if it matches.
    return response.data.map((r: any) => ({
      vehicle_id: r.vehicleId,
      vehicle_name: r.vehicleName,
      locations: r.routeSequence,
      distance: r.totalDistanceKm,
      duration: r.totalDurationMinutes,
      driver_id: r.driverId,
      driver_name: r.driverName,
      status: r.status,
      id: r.id
    }));
  }
};
