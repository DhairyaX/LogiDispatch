import React, { useEffect } from 'react';
import { useLogisticsStore } from '../store/logisticsStore';
import { getVehicleColor } from '../components/map/RouteMap';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell, 
  PieChart, 
  Pie, 
  LineChart, 
  Line, 
  Legend 
} from 'recharts';
import { BarChart3, TrendingUp, Users, Truck, AlertCircle, Loader2 } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const { drivers, vehicles, metrics, fetchDrivers, fetchVehicles, isLoadingDrivers, isLoadingVehicles } = useLogisticsStore();

  useEffect(() => {
    fetchDrivers();
    fetchVehicles();
  }, [fetchDrivers, fetchVehicles]);

  const isAnyLoading = isLoadingDrivers || isLoadingVehicles;

  if (!metrics) {
    return (
      <div className="h-[500px] flex flex-col items-center justify-center space-y-4 bg-neutral-900/10 border border-dashed border-neutral-800 rounded-2xl p-6 relative">
        {isAnyLoading && (
           <div className="absolute top-4 right-4 text-neutral-500">
             <Loader2 className="w-5 h-5 animate-spin" />
           </div>
        )}
        <AlertCircle className="w-10 h-10 text-neutral-500" />
        <div className="text-center">
          <h3 className="text-sm font-semibold text-neutral-300">No Analytics Data</h3>
          <p className="text-xs text-neutral-500 mt-1 max-w-xs mx-auto">
            Please run optimization first to compile fleet dispatch analytics.
          </p>
        </div>
      </div>
    );
  }

  // 1. Pair up driver status counts
  const driverStatusData = [
    { name: 'Available', value: drivers.filter(d => d.status === 'Available').length, color: '#e5e5e5' },
    { name: 'Busy', value: drivers.filter(d => d.status === 'Busy').length, color: '#a3a3a3' },
    { name: 'On Leave', value: drivers.filter(d => d.status === 'On Leave').length, color: '#737373' },
    { name: 'Offline', value: drivers.filter(d => d.status === 'Offline').length, color: '#404040' },
  ].filter(d => d.value > 0);

  // 2. Vehicle status counts
  const vehicleStatusData = [
    { name: 'Available', value: vehicles.filter(v => v.status === 'Available').length, color: '#e5e5e5' },
    { name: 'In Route', value: vehicles.filter(v => v.status === 'In Route').length, color: '#a3a3a3' },
    { name: 'Maintenance', value: vehicles.filter(v => v.status === 'Maintenance').length, color: '#737373' },
    { name: 'Unavailable', value: vehicles.filter(v => v.status === 'Unavailable').length, color: '#404040' },
  ].filter(v => v.value > 0);

  // 3. Workload sorted list
  const sortedMetrics = [...metrics.vehicle_metrics].sort((a: any, b: any) => {
    // In Python MongoDB string vs number, comparing strings might differ. 
    // Usually vehicle_id is string now, but let's compare logically or just sort by name.
    return String(a.vehicle_id).localeCompare(String(b.vehicle_id));
  });

  // 4. Line Chart: Cumulative distance contribution
  let cumulativeDist = 0;
  const cumulativeData = sortedMetrics.map((sm) => {
    cumulativeDist += sm.distance;
    return {
      vehicle_name: sm.vehicle_name,
      distance: sm.distance,
      cumulative: Number(cumulativeDist.toFixed(1))
    };
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-neutral-100 flex items-center">
          Fleet Operations Analytics
          {isAnyLoading && <Loader2 className="w-4 h-4 ml-3 animate-spin text-neutral-500" />}
        </h1>
        <p className="text-xs text-neutral-500 mt-1">Operational charts, distributions and utilization summaries.</p>
      </div>

      {/* Primary Bar Chart Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stops per active driver */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 flex flex-col h-64">
          <div className="flex items-center space-x-2 mb-3">
            <BarChart3 className="w-4 h-4 text-neutral-400" />
            <span className="text-neutral-400 text-xs font-semibold uppercase tracking-wider">Stops per Vehicle</span>
          </div>
          <div className="flex-1 w-full text-[9px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sortedMetrics} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
                <XAxis dataKey="vehicle_name" stroke="#737373" tickLine={false} />
                <YAxis stroke="#737373" tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(160, 160, 160, 0.05)' }} contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', color: '#e5e5e5' }} />
                <Bar dataKey="num_stops" fill="#a3a3a3" radius={[4, 4, 0, 0]}>
                  {sortedMetrics.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={getVehicleColor(entry.vehicle_id)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distance per active driver */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 flex flex-col h-64">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="w-4 h-4 text-neutral-400" />
            <span className="text-neutral-400 text-xs font-semibold uppercase tracking-wider">Distance per Vehicle (km)</span>
          </div>
          <div className="flex-1 w-full text-[9px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sortedMetrics} margin={{ top: 10, right: 5, left: -20, bottom: 0 }}>
                <XAxis dataKey="vehicle_name" stroke="#737373" tickLine={false} />
                <YAxis stroke="#737373" tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(160, 160, 160, 0.05)' }} contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', color: '#e5e5e5' }} />
                <Bar dataKey="distance" fill="#d4d4d4" radius={[4, 4, 0, 0]}>
                  {sortedMetrics.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={getVehicleColor(entry.vehicle_id)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cumulative Mileage line */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 flex flex-col h-64">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="w-4 h-4 text-neutral-400" />
            <span className="text-neutral-400 text-xs font-semibold uppercase tracking-wider">Cumulative Mileage (km)</span>
          </div>
          <div className="flex-1 w-full text-[9px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={cumulativeData} margin={{ top: 10, right: 15, left: -20, bottom: 0 }}>
                <XAxis dataKey="vehicle_name" stroke="#737373" tickLine={false} />
                <YAxis stroke="#737373" tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', color: '#e5e5e5' }} />
                <Line type="monotone" dataKey="cumulative" stroke="#e5e5e5" strokeWidth={2} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="distance" stroke="#737373" strokeWidth={1} strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Secondary Row: Pie Chart Distributions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Driver Distribution */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 flex flex-col h-64 justify-between">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-4 h-4 text-neutral-400" />
            <span className="text-neutral-400 text-xs font-semibold uppercase tracking-wider">Drivers Status Allocation</span>
          </div>
          <div className="flex-1 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={driverStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {driverStatusData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', fontSize: '10px', color: '#e5e5e5' }} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '10px', color: '#a3a3a3' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Vehicle Fleet Status */}
        <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 flex flex-col h-64 justify-between">
          <div className="flex items-center space-x-2 mb-2">
            <Truck className="w-4 h-4 text-neutral-400" />
            <span className="text-neutral-400 text-xs font-semibold uppercase tracking-wider">Fleet Status Allocation</span>
          </div>
          <div className="flex-1 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={vehicleStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {vehicleStatusData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', fontSize: '10px', color: '#e5e5e5' }} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '10px', color: '#a3a3a3' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
