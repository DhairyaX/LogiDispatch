import React, { useState } from 'react';
import { useLogisticsStore } from '../store/logisticsStore';
import { Compass, Scale, ShieldCheck, Zap, AlertTriangle, PlayCircle } from 'lucide-react';

export const OptimizationPage: React.FC = () => {
  const { 
    drivers, 
    vehicles, 
    deliveries, 
    optimizationMode, 
    setOptimizationMode, 
    balancingMode, 
    setBalancingMode, 
    runSolver 
  } = useLogisticsStore();

  const [error, setError] = useState<string | null>(null);
  const [solving, setSolving] = useState(false);

  const availableDriversCount = drivers.filter(d => d.status === 'Available' || d.status === 'Busy').length;
  const availableVehiclesCount = vehicles.filter(v => v.status === 'Available' || v.status === 'In Route').length;
  const pendingDeliveriesCount = deliveries.filter(d => d.status === 'Pending' || d.status === 'Assigned').length;

  const handleRunSolver = async () => {
    setError(null);
    setSolving(true);

    try {
      const res = await runSolver();
      if (!res.success) {
        setError(res.error || 'Failed to solve route optimization problem.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to solve route optimization problem.');
    } finally {
      setSolving(false);
    }
  };

  const isFleetDeficient = availableDriversCount === 0 || availableVehiclesCount === 0;
  const isDeliveriesDeficient = pendingDeliveriesCount === 0;

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-neutral-100">Optimization Center</h1>
        <p className="text-xs text-neutral-500 mt-1">Configure solver weights and dispatch resources.</p>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-4 bg-neutral-900 border border-neutral-700 rounded-xl flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-neutral-400 shrink-0 mt-0.5" />
          <div>
            <h3 className="text-xs font-semibold text-neutral-200">Optimization Failed</h3>
            <p className="text-[10px] text-neutral-400 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Summary card */}
      <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-neutral-200">Resources Verification</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-neutral-950 p-4 border border-neutral-800 rounded-lg">
            <span className="text-neutral-500 text-[9px] uppercase font-bold tracking-wider">Ready Drivers</span>
            <span className="text-xl font-bold text-neutral-100 block mt-1">{availableDriversCount}</span>
          </div>
          <div className="bg-neutral-950 p-4 border border-neutral-800 rounded-lg">
            <span className="text-neutral-500 text-[9px] uppercase font-bold tracking-wider">Ready Vehicles</span>
            <span className="text-xl font-bold text-neutral-100 block mt-1">{availableVehiclesCount}</span>
          </div>
          <div className="bg-neutral-950 p-4 border border-neutral-800 rounded-lg">
            <span className="text-neutral-500 text-[9px] uppercase font-bold tracking-wider">Pending Stops</span>
            <span className="text-xl font-bold text-neutral-100 block mt-1">{pendingDeliveriesCount}</span>
          </div>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 space-y-5">
        <h2 className="text-sm font-semibold text-neutral-200">Engine Configuration</h2>

        {/* Optimisation Mode */}
        <div className="space-y-2">
          <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block">Optimization Mode</label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setOptimizationMode('distance')}
              className={`p-4 rounded-xl border text-left flex flex-col justify-between h-24 transition-all ${
                optimizationMode === 'distance'
                  ? 'border-white bg-white/5 text-neutral-100'
                  : 'border-neutral-800/60 bg-neutral-950/20 text-neutral-400 hover:border-neutral-700'
              }`}
            >
              <Compass className="w-5 h-5 text-neutral-400" />
              <div>
                <span className="text-xs font-bold block">Distance Optimal</span>
                <span className="text-[9px] text-neutral-500 mt-0.5 block">Minimise total fleet travel mileage.</span>
              </div>
            </button>

            <button
              onClick={() => setOptimizationMode('duration')}
              className={`p-4 rounded-xl border text-left flex flex-col justify-between h-24 transition-all ${
                optimizationMode === 'duration'
                  ? 'border-white bg-white/5 text-neutral-100'
                  : 'border-neutral-800/60 bg-neutral-950/20 text-neutral-400 hover:border-neutral-700'
              }`}
            >
              <Zap className="w-5 h-5 text-neutral-400" />
              <div>
                <span className="text-xs font-bold block">Duration Optimal</span>
                <span className="text-[9px] text-neutral-500 mt-0.5 block">Minimise driving minutes & service times.</span>
              </div>
            </button>
          </div>
        </div>

        {/* Balancing Mode */}
        <div className="space-y-2">
          <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block">Workload Balancing Mode</label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              onClick={() => setBalancingMode('distance_optimal')}
              className={`p-4 rounded-xl border text-left flex flex-col justify-between h-28 transition-all ${
                balancingMode === 'distance_optimal'
                  ? 'border-white bg-white/5 text-neutral-100'
                  : 'border-neutral-800/60 bg-neutral-950/20 text-neutral-400 hover:border-neutral-700'
              }`}
            >
              <Zap className="w-5 h-5 text-neutral-400" />
              <div>
                <span className="text-xs font-bold block">Unbalanced</span>
                <span className="text-[9px] text-neutral-500 mt-1 block">Maximum distance efficiency. Drivers may remain idle.</span>
              </div>
            </button>

            <button
              onClick={() => setBalancingMode('balanced')}
              className={`p-4 rounded-xl border text-left flex flex-col justify-between h-28 transition-all ${
                balancingMode === 'balanced'
                  ? 'border-white bg-white/5 text-neutral-100'
                  : 'border-neutral-800/60 bg-neutral-950/20 text-neutral-400 hover:border-neutral-700'
              }`}
            >
              <Scale className="w-5 h-5 text-neutral-400" />
              <div>
                <span className="text-xs font-bold block">Balanced Workload</span>
                <span className="text-[9px] text-neutral-500 mt-1 block">Soft bounds to share workload evenly between active drivers.</span>
              </div>
            </button>

            <button
              onClick={() => setBalancingMode('strict')}
              className={`p-4 rounded-xl border text-left flex flex-col justify-between h-28 transition-all ${
                balancingMode === 'strict'
                  ? 'border-white bg-white/5 text-neutral-100'
                  : 'border-neutral-800/60 bg-neutral-950/20 text-neutral-400 hover:border-neutral-700'
              }`}
            >
              <ShieldCheck className="w-5 h-5 text-neutral-400" />
              <div>
                <span className="text-xs font-bold block">Strict Equal</span>
                <span className="text-[9px] text-neutral-500 mt-1 block">Forces mathematically identical stop counts across vehicles.</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Solver trigger */}
      <button
        onClick={handleRunSolver}
        disabled={isFleetDeficient || isDeliveriesDeficient || solving}
        className={`w-full py-4 rounded-xl flex items-center justify-center font-bold text-xs transition-all space-x-2 ${
          isFleetDeficient || isDeliveriesDeficient
            ? 'bg-neutral-800 border border-neutral-700/50 text-neutral-500 cursor-not-allowed'
            : solving
              ? 'bg-neutral-700 text-white cursor-wait'
              : 'bg-white hover:bg-neutral-100 text-neutral-900'
        }`}
      >
        {solving ? (
          <>
            <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
            <span>Running OR-Tools VRP Core...</span>
          </>
        ) : (
          <>
            <PlayCircle className="w-4 h-4" />
            <span>Generate Optimized Route Plan</span>
          </>
        )}
      </button>

      {(isFleetDeficient || isDeliveriesDeficient) && (
        <p className="text-[10px] text-neutral-500 text-center italic">
          * Requirements check: register at least 1 Available Driver & 1 Available Vehicle, with 1+ Pending Deliveries.
        </p>
      )}
    </div>
  );
};
