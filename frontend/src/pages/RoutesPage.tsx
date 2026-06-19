import React, { useEffect } from 'react';
import { useLogisticsStore } from '../store/logisticsStore';
import { RouteMap } from '../components/map/RouteMap';
import { MetricsGrid } from '../components/metrics/MetricsGrid';
import { VehicleList } from '../components/vehicles/VehicleList';
import { Compass, AlertCircle } from 'lucide-react';

export const RoutesPage: React.FC = () => {
  const { routes, metrics, setActivePage, fetchRoutes } = useLogisticsStore();

  useEffect(() => {
    fetchRoutes();
  }, [fetchRoutes]);

  const activeRoutes = routes.filter(r => r.locations && r.locations.length > 0);

  if (!metrics || activeRoutes.length === 0) {
    return (
      <div className="h-[500px] flex flex-col items-center justify-center space-y-4 bg-neutral-900/10 border border-dashed border-neutral-800 rounded-2xl p-6">
        <AlertCircle className="w-10 h-10 text-neutral-500" />
        <div className="text-center">
          <h3 className="text-sm font-semibold text-neutral-300">No Active Route Plan</h3>
          <p className="text-xs text-neutral-500 mt-1 max-w-xs mx-auto">
            Run the optimization engine to assign pending delivery stops to available vehicles and drivers.
          </p>
        </div>
        <button
          onClick={() => setActivePage('optimization')}
          className="px-4 py-2 bg-white hover:bg-neutral-100 text-neutral-900 rounded-lg text-xs font-semibold"
        >
          Go to Optimization Center
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 flex flex-col min-h-0 h-full">
      {/* Title */}
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-xl font-bold text-neutral-100 flex items-center">
            <Compass className="w-5 h-5 mr-2 text-neutral-400" />
            Optimized Dispatch Plan
          </h1>
          <p className="text-xs text-neutral-500 mt-1">
            Review stops allocation and routing paths per active vehicle.
          </p>
        </div>
        <div className="text-[10px] text-neutral-500 font-mono">
          Balancing: <span className="text-neutral-200 font-bold uppercase">{metrics.balancing_mode}</span>
        </div>
      </div>

      {/* Stats */}
      <div className="shrink-0">
        <MetricsGrid metrics={metrics} />
      </div>

      {/* Map + Sidebar Sequence Workspace */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[420px] overflow-hidden">
        {/* Left Sidebar */}
        <div className="lg:col-span-4 bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-4 flex flex-col overflow-hidden min-h-0">
          <VehicleList 
            routes={routes} 
            metricsList={metrics.vehicle_metrics} 
          />
        </div>

        {/* Right Map Panel */}
        <div className="lg:col-span-8 h-full min-h-[300px]">
          <RouteMap routes={routes} />
        </div>
      </div>
    </div>
  );
};
