import { create } from 'zustand';
import type { VehicleRoute, FleetMetrics, BalancingMode, OptimizationMode } from '../types/route';
import { driverService } from '../api/services/driverService';
import { vehicleService } from '../api/services/vehicleService';
import { deliveryService } from '../api/services/deliveryService';
import { optimizationService } from '../api/services/optimizationService';

export interface Driver {
  id: string;
  name: string;
  phone: string;
  status: 'Available' | 'Busy' | 'On Leave' | 'Offline';
}

export interface Vehicle {
  id: string;
  name: string;
  vehicleNumber: string;
  status: 'Available' | 'In Route' | 'Maintenance' | 'Unavailable';
}

export interface Delivery {
  id: string;
  customerName: string;
  phoneNumber: string;
  address: string;
  latitude: number;
  longitude: number;
  priority: 'Low' | 'Medium' | 'High';
  status: 'Pending' | 'Assigned' | 'In Transit' | 'Delivered';
  packageWeight: number;
  createdAt?: string;
}

interface LogisticsState {
  // Navigation
  activePage: 'dashboard' | 'drivers' | 'vehicles' | 'deliveries' | 'optimization' | 'routes' | 'analytics';
  setActivePage: (page: 'dashboard' | 'drivers' | 'vehicles' | 'deliveries' | 'optimization' | 'routes' | 'analytics') => void;

  // Data
  drivers: Driver[];
  vehicles: Vehicle[];
  deliveries: Delivery[];
  
  // Loading states
  isLoadingDrivers: boolean;
  isLoadingVehicles: boolean;
  isLoadingDeliveries: boolean;

  // Async Actions
  fetchDrivers: () => Promise<void>;
  addDriver: (driver: Omit<Driver, 'id'>) => Promise<void>;
  editDriver: (driver: Driver) => Promise<void>;
  deleteDriver: (id: string) => Promise<void>;

  fetchVehicles: () => Promise<void>;
  addVehicle: (vehicle: Omit<Vehicle, 'id'>) => Promise<void>;
  editVehicle: (vehicle: Vehicle) => Promise<void>;
  deleteVehicle: (id: string) => Promise<void>;

  fetchDeliveries: () => Promise<void>;
  addDelivery: (delivery: Omit<Delivery, 'id' | 'status' | 'createdAt'>) => Promise<void>;
  editDelivery: (delivery: Delivery) => Promise<void>;
  deleteDelivery: (id: string) => Promise<void>;

  // Optimization config
  optimizationMode: OptimizationMode;
  balancingMode: BalancingMode;
  setOptimizationMode: (mode: OptimizationMode) => void;
  setBalancingMode: (mode: BalancingMode) => void;

  // Results
  routes: VehicleRoute[];
  metrics: FleetMetrics | null;
  selectedVehicleId: string | null;
  setSelectedVehicleId: (id: string | null) => void;
  hoveredLocationId: string | null;
  setHoveredLocationId: (id: string | null) => void;
  
  fetchRoutes: () => Promise<void>;

  isSolving: boolean;
  runSolver: () => Promise<{ success: boolean; error?: string }>;
}

export const useLogisticsStore = create<LogisticsState>((set, get) => ({
  activePage: 'dashboard',
  setActivePage: (page) => set({ activePage: page }),

  drivers: [],
  vehicles: [],
  deliveries: [],

  isLoadingDrivers: false,
  isLoadingVehicles: false,
  isLoadingDeliveries: false,

  // Drivers
  fetchDrivers: async () => {
    set({ isLoadingDrivers: true });
    try {
      const drivers = await driverService.getAll();
      set({ drivers });
    } catch (e) {
      console.error(e);
    } finally {
      set({ isLoadingDrivers: false });
    }
  },
  addDriver: async (driver) => {
    await driverService.create(driver);
    await get().fetchDrivers();
  },
  editDriver: async (driver) => {
    await driverService.update(driver.id, driver);
    await get().fetchDrivers();
  },
  deleteDriver: async (id) => {
    await driverService.delete(id);
    await get().fetchDrivers();
  },

  // Vehicles
  fetchVehicles: async () => {
    set({ isLoadingVehicles: true });
    try {
      const vehicles = await vehicleService.getAll();
      set({ vehicles });
    } catch (e) {
      console.error(e);
    } finally {
      set({ isLoadingVehicles: false });
    }
  },
  addVehicle: async (vehicle) => {
    await vehicleService.create(vehicle);
    await get().fetchVehicles();
  },
  editVehicle: async (vehicle) => {
    await vehicleService.update(vehicle.id, vehicle);
    await get().fetchVehicles();
  },
  deleteVehicle: async (id) => {
    await vehicleService.delete(id);
    await get().fetchVehicles();
  },

  // Deliveries
  fetchDeliveries: async () => {
    set({ isLoadingDeliveries: true });
    try {
      const deliveries = await deliveryService.getAll();
      set({ deliveries });
    } catch (e) {
      console.error(e);
    } finally {
      set({ isLoadingDeliveries: false });
    }
  },
  addDelivery: async (delivery) => {
    await deliveryService.create(delivery);
    await get().fetchDeliveries();
  },
  editDelivery: async (delivery) => {
    await deliveryService.update(delivery.id, delivery);
    await get().fetchDeliveries();
  },
  deleteDelivery: async (id) => {
    await deliveryService.delete(id);
    await get().fetchDeliveries();
  },

  optimizationMode: 'distance',
  balancingMode: 'balanced',
  setOptimizationMode: (mode) => set({ optimizationMode: mode }),
  setBalancingMode: (mode) => set({ balancingMode: mode }),

  routes: [],
  metrics: null,
  selectedVehicleId: null,
  setSelectedVehicleId: (id) => set({ selectedVehicleId: id }),
  hoveredLocationId: null,
  setHoveredLocationId: (id) => set({ hoveredLocationId: id }),

  fetchRoutes: async () => {
    try {
      const { routeService } = await import('../api/services/routeService');
      const { optimizationService } = await import('../api/services/optimizationService');
      
      const activeRoutes = await routeService.getActiveRoutes();
      set({ routes: activeRoutes });

      // If we have active routes, fetch the latest metrics snapshot so the UI can render
      if (activeRoutes.length > 0) {
        const latest = await optimizationService.getLatestRoute();
        if (latest && latest.metrics) {
          set({ metrics: latest.metrics });
        }
      } else {
        set({ metrics: null });
      }
    } catch (e) {
      console.error(e);
    }
  },

  isSolving: false,
  runSolver: async () => {
    set({ isSolving: true });
    try {
      const { optimizationMode, balancingMode } = get();
      const result = await optimizationService.generateRoutes(optimizationMode, balancingMode);
      set({
        metrics: result.metrics || null,
        selectedVehicleId: null,
        activePage: 'routes'
      });
      // Optionally refresh entities to show new statuses
      await get().fetchDrivers();
      await get().fetchVehicles();
      await get().fetchDeliveries();
      await get().fetchRoutes();
      return { success: true };
    } catch (error: any) {
      console.error('Optimization failed', error);
      return { success: false, error: error.message || 'Optimization failed' };
    } finally {
      set({ isSolving: false });
    }
  }
}));
