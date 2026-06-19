import apiClient from '../client';
import type { Vehicle } from '../../store/logisticsStore';

export const vehicleService = {
  getAll: async (): Promise<Vehicle[]> => {
    const response = await apiClient.get('/vehicles/');
    return response.data;
  },

  getById: async (id: string): Promise<Vehicle> => {
    const response = await apiClient.get(`/vehicles/${id}`);
    return response.data;
  },

  create: async (vehicle: Omit<Vehicle, 'id'>): Promise<Vehicle> => {
    const response = await apiClient.post('/vehicles/', vehicle);
    return response.data;
  },

  update: async (id: string, vehicle: Partial<Vehicle>): Promise<Vehicle> => {
    const response = await apiClient.put(`/vehicles/${id}`, vehicle);
    return response.data;
  },

  delete: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/vehicles/${id}`);
    return response.data.success;
  }
};
