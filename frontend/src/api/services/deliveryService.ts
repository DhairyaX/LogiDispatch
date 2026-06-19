import apiClient from '../client';
import type { Delivery } from '../../store/logisticsStore';

export const deliveryService = {
  getAll: async (): Promise<Delivery[]> => {
    const response = await apiClient.get('/deliveries/');
    return response.data;
  },

  getById: async (id: string): Promise<Delivery> => {
    const response = await apiClient.get(`/deliveries/${id}`);
    return response.data;
  },

  create: async (delivery: Omit<Delivery, 'id' | 'status' | 'createdAt'>): Promise<Delivery> => {
    const response = await apiClient.post('/deliveries/', delivery);
    return response.data;
  },

  update: async (id: string, delivery: Partial<Delivery>): Promise<Delivery> => {
    const response = await apiClient.put(`/deliveries/${id}`, delivery);
    return response.data;
  },

  delete: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete(`/deliveries/${id}`);
    return response.data.success;
  }
};
