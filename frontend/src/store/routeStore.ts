import { create } from 'zustand';
import type { BalancingMode } from '../types/route';

interface RouteState {
  balancingMode: BalancingMode;
  selectedVehicleName: string | null;
  hoveredLocationId: string | null;
  focusedLocationId: string | null;
  searchQuery: string;
  loading: boolean;
  setBalancingMode: (mode: BalancingMode) => void;
  setSelectedVehicleName: (name: string | null) => void;
  setHoveredLocationId: (id: string | null) => void;
  setFocusedLocationId: (id: string | null) => void;
  setSearchQuery: (query: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useRouteStore = create<RouteState>((set) => ({
  balancingMode: 'balanced',
  selectedVehicleName: null,
  hoveredLocationId: null,
  focusedLocationId: null,
  searchQuery: '',
  loading: false,
  setBalancingMode: (mode) => set({ balancingMode: mode, selectedVehicleName: null, focusedLocationId: null }), // reset vehicle filter when mode changes
  setSelectedVehicleName: (name) => set({ selectedVehicleName: name, focusedLocationId: null }),
  setHoveredLocationId: (id) => set({ hoveredLocationId: id }),
  setFocusedLocationId: (id) => set({ focusedLocationId: id }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setLoading: (loading) => set({ loading }),
}));
