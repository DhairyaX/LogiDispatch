import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import type { VehicleMetrics } from '../../types/route';
import { getVehicleColor } from '../map/RouteMap';
import { BarChart3, TrendingUp, Hourglass } from 'lucide-react';

interface AnalyticsChartsProps {
  vehicleMetrics: VehicleMetrics[];
}

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ vehicleMetrics }) => {
  // Sort vehicle metrics by vehicle name
  const sortedData = [...vehicleMetrics].sort((a, b) => a.vehicle_name.localeCompare(b.vehicle_name));

  // Custom tooltips
  const CustomTooltip = ({ active, payload, label, unit }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as VehicleMetrics;
      const color = getVehicleColor(data.vehicle_name);
      return (
        <div className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg shadow-xl text-xs">
          <p className="font-bold text-slate-200 mb-1" style={{ color }}>{label}</p>
          <p className="text-slate-400">
            <span className="font-semibold text-slate-300">{payload[0].name}:</span> {payload[0].value} {unit}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
      {/* Stops Distribution */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col h-64">
        <div className="flex items-center space-x-2 mb-3">
          <BarChart3 className="w-4 h-4 text-indigo-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Stops per Vehicle</h3>
        </div>
        <div className="flex-1 w-full text-[10px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sortedData} margin={{ top: 10, right: 5, left: -25, bottom: 0 }}>
              <XAxis dataKey="vehicle_name" stroke="#64748b" tickLine={false} />
              <YAxis stroke="#64748b" tickLine={false} />
              <Tooltip content={<CustomTooltip unit="stops" />} cursor={{ fill: 'rgba(148, 163, 184, 0.05)' }} />
              <Bar dataKey="num_stops" fill="#6366f1" radius={[4, 4, 0, 0]} name="Stops">
                {sortedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getVehicleColor(entry.vehicle_name)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Distance Distribution */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col h-64">
        <div className="flex items-center space-x-2 mb-3">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Distance per Vehicle</h3>
        </div>
        <div className="flex-1 w-full text-[10px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sortedData} margin={{ top: 10, right: 5, left: -20, bottom: 0 }}>
              <XAxis dataKey="vehicle_name" stroke="#64748b" tickLine={false} />
              <YAxis stroke="#64748b" tickLine={false} />
              <Tooltip content={<CustomTooltip unit="km" />} cursor={{ fill: 'rgba(148, 163, 184, 0.05)' }} />
              <Bar dataKey="distance" fill="#10b981" radius={[4, 4, 0, 0]} name="Distance">
                {sortedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getVehicleColor(entry.vehicle_name)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Duration Distribution */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col h-64">
        <div className="flex items-center space-x-2 mb-3">
          <Hourglass className="w-4 h-4 text-rose-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Duration per Vehicle</h3>
        </div>
        <div className="flex-1 w-full text-[10px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sortedData} margin={{ top: 10, right: 5, left: -20, bottom: 0 }}>
              <XAxis dataKey="vehicle_name" stroke="#64748b" tickLine={false} />
              <YAxis stroke="#64748b" tickLine={false} />
              <Tooltip content={<CustomTooltip unit="mins" />} cursor={{ fill: 'rgba(148, 163, 184, 0.05)' }} />
              <Bar dataKey="duration" fill="#f43f5e" radius={[4, 4, 0, 0]} name="Duration">
                {sortedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getVehicleColor(entry.vehicle_name)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
