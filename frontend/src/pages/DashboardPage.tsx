import React, { useEffect } from 'react';
import { useLogisticsStore } from '../store/logisticsStore';
import { 
  Users, 
  Truck, 
  MapPin, 
  Compass, 
  PlusCircle, 
  TrendingUp, 
  ShieldAlert, 
  ClipboardList,
  Loader2
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { 
    drivers, 
    vehicles, 
    deliveries, 
    routes, 
    metrics, 
    setActivePage,
    fetchDrivers,
    fetchVehicles,
    fetchDeliveries,
    isLoadingDrivers,
    isLoadingVehicles,
    isLoadingDeliveries
  } = useLogisticsStore();

  useEffect(() => {
    fetchDrivers();
    fetchVehicles();
    fetchDeliveries();
  }, [fetchDrivers, fetchVehicles, fetchDeliveries]);

  const totalDrivers = drivers.length;
  const availableDrivers = drivers.filter(d => d.status === 'Available').length;
  const busyDrivers = drivers.filter(d => d.status === 'Busy').length;

  const totalVehicles = vehicles.length;
  const availableVehicles = vehicles.filter(v => v.status === 'Available').length;
  const inRouteVehicles = vehicles.filter(v => v.status === 'In Route').length;

  const pendingCount = deliveries.filter(d => d.status === 'Pending').length;
  const assignedCount = deliveries.filter(d => d.status === 'Assigned').length;
  const transitCount = deliveries.filter(d => d.status === 'In Transit').length;
  const deliveredCount = deliveries.filter(d => d.status === 'Delivered').length;

  const fleetUtil = metrics?.vehicle_utilization_rate ?? 0;
  const stdDev = metrics?.stop_distribution_stddev ?? 0;

  const stats = [
    { label: 'Drivers Available', value: `${availableDrivers} / ${totalDrivers}`, icon: Users, desc: `${busyDrivers} busy currently` },
    { label: 'Vehicles Active', value: `${inRouteVehicles} / ${totalVehicles}`, icon: Truck, desc: `${availableVehicles} ready in yard` },
    { label: 'Pending Stops', value: pendingCount, icon: MapPin, desc: `${assignedCount} stops in queue` },
    { label: 'Generated Routes', value: routes.filter(r => r.locations.length > 0).length, icon: Compass, desc: `VRP Plan active` },
    { label: 'Fleet Utilization', value: `${fleetUtil.toFixed(0)}%`, icon: TrendingUp, desc: 'Driver deployment rate' },
    { label: 'Workload StdDev', value: stdDev.toFixed(2), icon: ShieldAlert, desc: 'Target deviation balance' },
  ];

  const isAnyLoading = isLoadingDrivers || isLoadingVehicles || isLoadingDeliveries;

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-neutral-100 flex items-center">
          Operations Control Centre
          {isAnyLoading && <Loader2 className="w-4 h-4 ml-3 animate-spin text-neutral-500" />}
        </h1>
        <p className="text-xs text-neutral-500 mt-1">Real-time dispatcher fleet status and actions.</p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="p-5 bg-neutral-900/60 border border-neutral-800/80 rounded-xl flex items-center justify-between">
              <div>
                <span className="text-neutral-400 text-xs font-semibold uppercase tracking-wider block">{stat.label}</span>
                <span className="text-2xl font-bold text-neutral-100 tracking-tight mt-1.5 block">
                  {isAnyLoading && i < 3 ? '-' : stat.value}
                </span>
                <span className="text-[10px] text-neutral-500 block mt-1">{stat.desc}</span>
              </div>
              <div className="p-2.5 rounded-xl border border-neutral-800 bg-neutral-800/50 text-neutral-400">
                <Icon className="w-5 h-5" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions & Recent Queue */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Actions panel */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-neutral-200">Dispatcher Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <button 
              onClick={() => setActivePage('drivers')}
              className="flex items-center justify-center p-3 rounded-lg border border-neutral-800 bg-neutral-900 hover:bg-neutral-800 hover:border-neutral-700 transition-all text-xs font-medium space-x-2 text-neutral-300"
            >
              <PlusCircle className="w-4 h-4 text-neutral-500" />
              <span>Register Driver</span>
            </button>
            <button 
              onClick={() => setActivePage('vehicles')}
              className="flex items-center justify-center p-3 rounded-lg border border-neutral-800 bg-neutral-900 hover:bg-neutral-800 hover:border-neutral-700 transition-all text-xs font-medium space-x-2 text-neutral-300"
            >
              <PlusCircle className="w-4 h-4 text-neutral-500" />
              <span>Provision Vehicle</span>
            </button>
            <button 
              onClick={() => setActivePage('deliveries')}
              className="flex items-center justify-center p-3 rounded-lg border border-neutral-800 bg-neutral-900 hover:bg-neutral-800 hover:border-neutral-700 transition-all text-xs font-medium space-x-2 text-neutral-300"
            >
              <PlusCircle className="w-4 h-4 text-neutral-500" />
              <span>Create Delivery</span>
            </button>
            <button 
              onClick={() => setActivePage('optimization')}
              className="flex items-center justify-center p-3 rounded-lg border border-neutral-700 bg-white hover:bg-neutral-100 transition-all text-xs font-semibold space-x-2 text-neutral-900"
            >
              <Compass className="w-4 h-4" />
              <span>Run Solver</span>
            </button>
          </div>
        </div>

        {/* Deliveries state distribution summary */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-neutral-200">Deliveries State</h2>
            <ClipboardList className="w-4 h-4 text-neutral-500" />
          </div>
          
          <div className="space-y-2.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-neutral-400">Pending optimization queue</span>
              <span className="font-bold text-neutral-200">{isAnyLoading ? '-' : pendingCount}</span>
            </div>
            <div className="w-full bg-neutral-900 h-2 rounded-full overflow-hidden flex">
              <div className="bg-neutral-500 h-full" style={{ width: `${(pendingCount / (deliveries.length || 1)) * 100}%` }} />
              <div className="bg-neutral-400 h-full" style={{ width: `${(assignedCount / (deliveries.length || 1)) * 100}%` }} />
              <div className="bg-neutral-300 h-full" style={{ width: `${(transitCount / (deliveries.length || 1)) * 100}%` }} />
              <div className="bg-white h-full" style={{ width: `${(deliveredCount / (deliveries.length || 1)) * 100}%` }} />
            </div>
            <div className="grid grid-cols-4 gap-1 pt-1.5 text-[9px] text-center font-mono">
              <div>
                <span className="w-1.5 h-1.5 rounded-full inline-block bg-neutral-500 mr-1" />
                <span className="text-neutral-400">Pending ({isAnyLoading ? '-' : pendingCount})</span>
              </div>
              <div>
                <span className="w-1.5 h-1.5 rounded-full inline-block bg-neutral-400 mr-1" />
                <span className="text-neutral-400">Assigned ({isAnyLoading ? '-' : assignedCount})</span>
              </div>
              <div>
                <span className="w-1.5 h-1.5 rounded-full inline-block bg-neutral-300 mr-1" />
                <span className="text-neutral-400">Transit ({isAnyLoading ? '-' : transitCount})</span>
              </div>
              <div>
                <span className="w-1.5 h-1.5 rounded-full inline-block bg-white mr-1" />
                <span className="text-neutral-400">Delivered ({isAnyLoading ? '-' : deliveredCount})</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
