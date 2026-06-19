export interface Location {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface VehicleMetrics {
  vehicle_id: string;
  vehicle_name: string;
  driver_id?: string;
  driver_name?: string;
  num_stops: number;
  distance: number;
  duration: number;
}

export interface FleetMetrics {
  total_stops: number;
  total_distance: number;
  average_distance_per_stop: number;
  execution_time: number;
  total_duration: number;
  average_duration_per_stop: number;
  distance_source: string;
  optimization_mode: string;
  vehicle_count: number;
  vehicles_used: number;
  vehicle_metrics: VehicleMetrics[];
  max_stops_per_vehicle: number;
  min_stops_per_vehicle: number;
  stop_distribution_stddev: number;
  vehicle_utilization_rate: number;
  balancing_mode: string;
}

export interface VehicleRoute {
  vehicle_id: string;
  vehicle_name: string;
  driver_id?: string;
  driver_name?: string;
  locations: Location[];
  distance: number;
  duration: number;
}

export interface OptimizationResult {
  metrics: FleetMetrics;
  routes: VehicleRoute[];
}

export type BalancingMode = 'strict' | 'balanced' | 'distance_optimal';
export type OptimizationMode = 'distance' | 'duration';
