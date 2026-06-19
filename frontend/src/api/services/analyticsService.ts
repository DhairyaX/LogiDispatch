import apiClient from '../client';

export interface DashboardMetrics {
  totalDrivers: number;
  availableDrivers: number;
  totalVehicles: number;
  availableVehicles: number;
  totalDeliveries: number;
  pendingDeliveries: number;
}

export const analyticsService = {
  getFleetMetrics: async (): Promise<any> => {
    const response = await apiClient.get('/analytics/fleet');
    return response.data;
  },

  getWorkloadMetrics: async (): Promise<any> => {
    const response = await apiClient.get('/analytics/workload');
    return response.data;
  },

  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    // In a real app we might have a specific endpoint, but we can fetch the lists or fleet metrics
    // The backend provides counts via /analytics endpoints or we can derive them from CRUD data
    const [driversRes, vehiclesRes, deliveriesRes] = await Promise.all([
      apiClient.get('/drivers/'),
      apiClient.get('/vehicles/'),
      apiClient.get('/deliveries/')
    ]);
    
    const drivers = driversRes.data;
    const vehicles = vehiclesRes.data;
    const deliveries = deliveriesRes.data;

    return {
      totalDrivers: drivers.length,
      availableDrivers: drivers.filter((d: any) => d.status === 'Available').length,
      totalVehicles: vehicles.length,
      availableVehicles: vehicles.filter((v: any) => v.status === 'Available').length,
      totalDeliveries: deliveries.length,
      pendingDeliveries: deliveries.filter((d: any) => d.status === 'Pending').length,
    };
  }
};
