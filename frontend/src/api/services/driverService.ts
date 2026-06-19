import apiClient from '../client';
import type { Driver } from '../../store/logisticsStore';

export const driverService = {
  getAll: async (): Promise<Driver[]> => {
    const response = await apiClient.get('/drivers/');
    return response.data;
  },

  getById: async (id: string): Promise<Driver> => {
    const response = await apiClient.get(`/drivers/${id}`);
    return response.data;
  },

  create: async (driver: Omit<Driver, 'id'>): Promise<Driver> => {
    const response = await apiClient.post('/drivers/', driver);
    return response.data;
  },

  update: async (id: string, driver: Partial<Driver>): Promise<Driver> => {
    const response = await apiClient.put(`/drivers/${id}`, driver);
    return response.data;
  },

  delete: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/drivers/${id}`);
    return response.data.success;
  }
};
