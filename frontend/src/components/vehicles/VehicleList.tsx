import React from 'react';
import type { VehicleRoute, VehicleMetrics } from '../../types/route';
import { useRouteStore } from '../../store/routeStore';
import { getVehicleColor } from '../map/RouteMap';
import { Truck, Navigation, Clock, Search, Layers } from 'lucide-react';

interface VehicleListProps {
  routes: VehicleRoute[];
  metricsList: VehicleMetrics[];
}

export const VehicleList: React.FC<VehicleListProps> = ({ routes, metricsList }) => {
  const { 
    selectedVehicleName, 
    setSelectedVehicleName, 
    hoveredLocationId, 
    setHoveredLocationId,
    focusedLocationId,
    setFocusedLocationId,
    searchQuery,
    setSearchQuery 
  } = useRouteStore();

  const getVehicleRoute = (vehicleName: string) => {
    return routes.find((r) => r.vehicle_name === vehicleName);
  };

  const activeRoute = selectedVehicleName ? getVehicleRoute(selectedVehicleName) : null;

  const filteredStops = routes.flatMap((route) => 
    route.locations.filter((loc) => 
      loc.id.toString() !== "0" && loc.name.toLowerCase().includes(searchQuery.toLowerCase())
    ).map(loc => ({
      ...loc,
      vehicleName: route.vehicle_name,
      color: getVehicleColor(route.vehicle_name)
    }))
  );

  const uniqueFilteredStops = Array.from(new Map(filteredStops.map(item => [item.id, item])).values());

  return (
    <div className="w-full h-full flex flex-col space-y-4">
      {/* Selection Filters */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <h2 className="text-sm font-semibold text-neutral-200 flex items-center">
            <Truck className="w-4 h-4 mr-2 text-neutral-400" />
            Fleet Vehicles
          </h2>
          {selectedVehicleName !== null && (
            <button 
              onClick={() => setSelectedVehicleName(null)}
              className="text-[10px] bg-neutral-800 hover:bg-neutral-700 text-neutral-300 font-medium px-2 py-0.5 rounded border border-neutral-700/50 transition-colors"
            >
              Show All Routes
            </button>
          )}
        </div>
        
        {/* Vehicles stack */}
        <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
          {metricsList.map((vm) => {
            const isSelected = selectedVehicleName === vm.vehicle_name;
            const color = getVehicleColor(vm.vehicle_name);
            const isIdle = vm.num_stops === 0;

            return (
              <div
                key={vm.vehicle_id}
                onClick={() => setSelectedVehicleName(isSelected ? null : vm.vehicle_name)}
                className={`p-3 rounded-lg border transition-all duration-200 cursor-pointer flex flex-col space-y-1.5 ${
                  isSelected 
                    ? 'bg-neutral-800/80 border-neutral-600 shadow-md' 
                    : 'bg-neutral-900/40 border-neutral-800/60 hover:bg-neutral-800/30'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex flex-col space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span 
                        className="w-2.5 h-2.5 rounded-full inline-block"
                        style={{ backgroundColor: isIdle ? '#525252' : color }}
                      />
                      <span className="font-semibold text-neutral-200 text-xs">{vm.vehicle_name}</span>
                    </div>
                    {vm.driver_name && (
                      <span className="text-[10px] text-neutral-400 pl-4">{vm.driver_name}</span>
                    )}
                  </div>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                    isIdle 
                      ? 'bg-neutral-800 text-neutral-500' 
                      : 'bg-neutral-800 text-neutral-300 border border-neutral-700'
                  }`}>
                    {vm.num_stops} stops
                  </span>
                </div>
                
                {!isIdle && (
                  <div className="flex items-center justify-between text-[10px] text-neutral-400">
                    <span className="flex items-center">
                      <Navigation className="w-3 h-3 mr-1 text-neutral-500" />
                      {vm.distance.toFixed(1)} km
                    </span>
                    <span className="flex items-center">
                      <Clock className="w-3 h-3 mr-1 text-neutral-500" />
                      {vm.duration.toFixed(0)} mins
                    </span>
                  </div>
                )}
                {isIdle && (
                  <div className="text-[10px] text-neutral-500 italic">
                    Idle / Unassigned
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <hr className="border-neutral-800/80" />

      {/* Details & Search Section */}
      <div className="flex-1 flex flex-col min-h-0 space-y-2">
        <h2 className="text-sm font-semibold text-neutral-200 flex items-center">
          <Layers className="w-4 h-4 mr-2 text-neutral-400" />
          {selectedVehicleName ? 'Route Sequence' : 'Stops Finder'}
        </h2>
        
        {!selectedVehicleName && (
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-neutral-500" />
            <input
              type="text"
              placeholder="Search Gurgaon stops..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-xs bg-neutral-900/60 border border-neutral-800/80 rounded-lg pl-9 pr-4 py-2 text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-neutral-600 transition-colors"
            />
          </div>
        )}

        <div className="flex-1 overflow-y-auto pr-1 text-xs space-y-1">
          {selectedVehicleName && activeRoute ? (
            activeRoute.locations.length > 0 ? (
              activeRoute.locations.map((loc, index) => {
                const isHovered = hoveredLocationId === loc.id;
                const isDepot = loc.id.toString() === "0";

                return (
                  <div
                    key={`${loc.id}-${index}`}
                    onClick={() => {
                      if (!isDepot) {
                        setFocusedLocationId(focusedLocationId === loc.id ? null : loc.id);
                      }
                    }}
                    onMouseEnter={() => !isDepot && setHoveredLocationId(loc.id)}
                    onMouseLeave={() => !isDepot && setHoveredLocationId(null)}
                    className={`p-2 rounded-md transition-all duration-150 border flex items-center justify-between cursor-pointer ${
                      isHovered || focusedLocationId === loc.id
                        ? 'bg-white/10 border-neutral-600 text-neutral-100 font-medium shadow-sm'
                        : isDepot 
                          ? 'bg-neutral-800/20 border-neutral-800/40 text-neutral-300'
                          : 'bg-neutral-900/30 border-neutral-800/50 hover:bg-neutral-800/20 text-neutral-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2 min-w-0">
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] ${
                        isDepot ? 'bg-neutral-700/30 text-neutral-300 border border-neutral-600/30' : 'bg-neutral-800 text-neutral-400'
                      }`}>
                        {index}
                      </span>
                      <span className="truncate">{loc.name}</span>
                    </div>
                    {isDepot && (
                      <span className="text-[9px] bg-neutral-800 text-neutral-300 px-1 py-0.2 rounded font-semibold">
                        HUB
                      </span>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="text-neutral-500 italic p-3 text-center">
                No routes calculated.
              </div>
            )
          ) : (
            uniqueFilteredStops.length > 0 ? (
              uniqueFilteredStops.map((stop) => {
                const isHovered = hoveredLocationId === stop.id;
                return (
                  <div
                    key={stop.id}
                    onClick={() => {
                      setFocusedLocationId(focusedLocationId === stop.id ? null : stop.id);
                      setSelectedVehicleName(stop.vehicleName);
                    }}
                    onMouseEnter={() => setHoveredLocationId(stop.id)}
                    onMouseLeave={() => setHoveredLocationId(null)}
                    className={`p-2 rounded-md transition-all duration-150 border flex items-center justify-between cursor-pointer ${
                      isHovered || focusedLocationId === stop.id
                        ? 'bg-white/10 border-neutral-600 text-neutral-100 shadow-sm'
                        : 'bg-neutral-900/30 border-neutral-800/50 text-neutral-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span 
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: stop.color }}
                      />
                      <span>{stop.name}</span>
                    </div>
                    <span className="text-[9px] text-neutral-500">{stop.vehicleName}</span>
                  </div>
                );
              })
            ) : (
              <div className="text-neutral-500 italic p-3 text-center">
                No matching stops found.
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};
