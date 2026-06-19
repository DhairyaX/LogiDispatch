import React, { useEffect, useState } from 'react';
import { useRouteStore } from '../store/routeStore';
import { routeService } from '../services/routeService';
import type { OptimizationResult, BalancingMode } from '../types/route';
import { MetricsGrid } from '../components/metrics/MetricsGrid';
import { VehicleList } from '../components/vehicles/VehicleList';
import { RouteMap } from '../components/map/RouteMap';
import { AnalyticsCharts } from '../components/dashboard/AnalyticsCharts';
import { Compass, RefreshCw, BarChart2, ShieldCheck, Scale, Zap } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { balancingMode, setBalancingMode, loading, setLoading } = useRouteStore();
  const [data, setData] = useState<OptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (mode: BalancingMode) => {
    setLoading(true);
    setError(null);
    try {
      const result = await routeService.getRouteData(mode);
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load route optimization data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(balancingMode);
  }, [balancingMode]);

  return (
    <div className="flex flex-col h-screen bg-[#080b13] text-slate-100 overflow-hidden">
      {/* Top Header Navbar */}
      <header className="flex items-center justify-between px-6 py-4 bg-slate-900/80 border-b border-slate-800 backdrop-blur-md z-30">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-600 rounded-lg text-white shadow-lg shadow-indigo-600/30 animate-pulse">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight bg-gradient-to-r from-indigo-200 via-slate-100 to-indigo-400 bg-clip-text text-transparent">
              Logistics Route Optimizer
            </h1>
            <p className="text-[10px] text-indigo-400/80 font-mono tracking-widest uppercase">Multi-Vehicle VRP Engine</p>
          </div>
        </div>

        {/* Balancing Mode Toggles */}
        <div className="flex items-center space-x-2">
          <span className="text-[10px] uppercase font-bold text-slate-400 mr-2 tracking-wider hidden sm:inline-block">
            Balancing Mode
          </span>
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setBalancingMode('distance_optimal')}
              className={`flex items-center px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                balancingMode === 'distance_optimal'
                  ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className="w-3 h-3 mr-1.5" />
              Distance Optimal
            </button>
            <button
              onClick={() => setBalancingMode('balanced')}
              className={`flex items-center px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                balancingMode === 'balanced'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Scale className="w-3 h-3 mr-1.5" />
              Balanced
            </button>
            <button
              onClick={() => setBalancingMode('strict')}
              className={`flex items-center px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                balancingMode === 'strict'
                  ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ShieldCheck className="w-3 h-3 mr-1.5" />
              Strict
            </button>
          </div>
          
          <button 
            onClick={() => fetchData(balancingMode)}
            className="p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors"
            title="Reload Optimization"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 flex min-h-0 overflow-hidden relative">
        {error && (
          <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center z-50 p-6">
            <div className="bg-slate-900 border border-rose-500/30 p-6 rounded-xl max-w-md text-center">
              <p className="text-rose-400 font-semibold text-sm mb-2">Error Loading Data</p>
              <p className="text-slate-400 text-xs">{error}</p>
              <button 
                onClick={() => fetchData(balancingMode)}
                className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold"
              >
                Retry Fetch
              </button>
            </div>
          </div>
        )}

        {/* Left Sidebar */}
        <aside className="w-80 bg-slate-950/50 border-r border-slate-800/80 p-4 flex flex-col min-h-0 backdrop-blur-sm">
          {data ? (
            <VehicleList 
              routes={data.routes} 
              metricsList={data.metrics.vehicle_metrics} 
            />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="animate-pulse flex flex-col items-center space-y-2">
                <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
                <span className="text-xs text-slate-500">Loading sidebar...</span>
              </div>
            </div>
          )}
        </aside>

        {/* Right Content Area (Map, Stats Grid, Charts) */}
        <section className="flex-1 flex flex-col overflow-y-auto p-6 space-y-6 min-w-0">
          {loading ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-4">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 rounded-full border-4 border-slate-800" />
                <div className="absolute inset-0 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-300">Running VRP Optimization Engine</p>
                <p className="text-[10px] text-slate-500 font-mono text-center">Applying balancing mode span costs...</p>
              </div>
            </div>
          ) : data ? (
            <>
              {/* Stats Grid */}
              <MetricsGrid metrics={data.metrics} />

              {/* Map Layout & Route Sequence Details */}
              <div className="flex-1 min-h-[380px] grid grid-cols-1 gap-6 relative">
                <RouteMap routes={data.routes} />
              </div>

              {/* Workload Analytics Charts */}
              <div className="bg-slate-900/20 border border-slate-900 p-6 rounded-2xl">
                <div className="flex items-center space-x-2 mb-4">
                  <BarChart2 className="w-4 h-4 text-indigo-400" />
                  <h2 className="text-xs font-bold uppercase tracking-wider text-indigo-300">Workload & Metrics Analytics</h2>
                </div>
                <AnalyticsCharts vehicleMetrics={data.metrics.vehicle_metrics} />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-500">
              No data loaded.
            </div>
          )}
        </section>
      </main>
    </div>
  );
};
