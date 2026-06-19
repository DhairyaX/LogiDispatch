import React from 'react';
import type { FleetMetrics } from '../../types/route';
import { 
  MapPin, 
  Truck, 
  Percent, 
  Navigation, 
  Clock, 
  TrendingUp, 
  CheckCircle,
  Hash
} from 'lucide-react';

interface MetricsGridProps {
  metrics: FleetMetrics;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  const averageStops = (metrics.total_stops / (metrics.vehicles_used || 1)).toFixed(1);

  const cards = [
    {
      title: 'Total Stops',
      value: metrics.total_stops,
      icon: MapPin,
      description: 'Stops to deliver',
    },
    {
      title: 'Vehicles Used',
      value: `${metrics.vehicles_used} / ${metrics.vehicle_count}`,
      icon: Truck,
      description: 'Active drivers',
    },
    {
      title: 'Fleet Utilization',
      value: `${metrics.vehicle_utilization_rate.toFixed(0)}%`,
      icon: Percent,
      description: 'Active fleet ratio',
    },
    {
      title: 'Total Distance',
      value: `${metrics.total_distance.toFixed(1)} km`,
      icon: Navigation,
      description: 'Entire fleet travel',
    },
    {
      title: 'Total Duration',
      value: `${(metrics.total_duration / 60).toFixed(1)} hrs`,
      icon: Clock,
      description: `${metrics.total_duration.toFixed(0)} mins driving`,
    },
    {
      title: 'Avg Stops / Vehicle',
      value: averageStops,
      icon: Hash,
      description: 'Per active driver',
    },
    {
      title: 'Workload StdDev',
      value: metrics.stop_distribution_stddev.toFixed(2),
      icon: TrendingUp,
      description: 'Lower means fairer load',
    },
    {
      title: 'Optimization Engine',
      value: metrics.distance_source.toUpperCase(),
      icon: CheckCircle,
      description: `Targeting: ${metrics.optimization_mode}`,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <div 
            key={i} 
            className="p-4 bg-neutral-900/60 rounded-xl border border-neutral-800/80 hover:border-neutral-700/50 transition-all duration-200"
          >
            <div className="flex justify-between items-start">
              <span className="text-neutral-400 text-xs font-medium uppercase tracking-wider">{card.title}</span>
              <div className="p-1.5 rounded-lg border border-neutral-800 bg-neutral-800/50 text-neutral-400">
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-2 flex items-baseline">
              <span className="text-2xl font-bold tracking-tight text-neutral-100">{card.value}</span>
            </div>
            <p className="text-[10px] text-neutral-500 mt-1">{card.description}</p>
          </div>
        );
      })}
    </div>
  );
};
