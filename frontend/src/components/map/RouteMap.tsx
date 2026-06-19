import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { VehicleRoute } from '../../types/route';
import { useRouteStore } from '../../store/routeStore';

// Helper to assign a distinct color to each vehicle based on its name
export const getVehicleColor = (vehicleName: string): string => {
  const colors = [
    '#3b82f6', // Blue-500
    '#10b981', // Emerald-500
    '#f59e0b', // Amber-500
    '#8b5cf6', // Violet-500
    '#ef4444', // Red-500
    '#ec4899', // Pink-500
    '#06b6d4', // Cyan-500
    '#84cc16', // Lime-500
  ];
  
  // Simple string hash
  let hash = 0;
  for (let i = 0; i < vehicleName.length; i++) {
    hash = vehicleName.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
};

// Depot custom marker icon
const getDepotIcon = () => {
  return L.divIcon({
    html: `
      <div class="flex items-center justify-center w-8 h-8 rounded-full border-2 border-neutral-950 bg-white text-neutral-900 shadow-lg hover:scale-110 transition-transform duration-200">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>
    `,
    className: 'custom-depot-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

// Stop custom marker icon with vehicle color-coded ring and sequence number
const getStopIcon = (sequenceNum: number, color: string, isHovered: boolean) => {
  const scaleClass = isHovered ? 'scale-125 z-50 ring-4 ring-white' : 'hover:scale-110 z-10';
  return L.divIcon({
    html: `
      <div class="flex items-center justify-center w-6 h-6 rounded-full border border-neutral-950 text-neutral-900 font-bold text-xs shadow-md transition-all duration-200 ${scaleClass}" 
           style="background-color: ${color}">
        ${sequenceNum}
      </div>
    `,
    className: 'custom-stop-icon',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

// Map controller to fit map viewport around active route bounds dynamically
const MapBoundsController: React.FC<{ 
  routes: VehicleRoute[]; 
  selectedName: string | null;
  focusedLocationId: string | null;
}> = ({ routes, selectedName, focusedLocationId }) => {
  const map = useMap();

  useEffect(() => {
    // If a specific location is focused, fly directly to it
    if (focusedLocationId) {
      let foundLoc: any = null;
      routes.forEach(route => {
        route.locations.forEach(loc => {
          if (loc.id.toString() === focusedLocationId.toString()) {
            foundLoc = loc;
          }
        });
      });
      
      if (foundLoc) {
        map.flyTo([foundLoc.latitude, foundLoc.longitude], 16, { animate: true, duration: 1.5 });
        return;
      }
    }

    // Otherwise, fit bounds to the selected route or all routes
    const coords: [number, number][] = [];

    routes.forEach((route) => {
      if (selectedName === null || route.vehicle_name === selectedName) {
        route.locations.forEach((loc) => {
          coords.push([loc.latitude, loc.longitude]);
        });
      }
    });

    if (coords.length > 0) {
      const bounds = L.latLngBounds(coords);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14, animate: true });
    }
  }, [routes, selectedName, focusedLocationId, map]);

  return null;
};

interface RouteMapProps {
  routes: VehicleRoute[];
}

export const RouteMap: React.FC<RouteMapProps> = ({ routes }) => {
  const { selectedVehicleName, hoveredLocationId, setHoveredLocationId, focusedLocationId } = useRouteStore();

  const depot = routes[0]?.locations[0];

  // Get active routes for legend
  const activeRoutes = routes.filter(r => r.locations.length > 1);

  return (
    <div className="w-full h-full relative rounded-xl overflow-hidden border border-neutral-800 shadow-2xl">
      {/* Legend Overlay */}
      <div className="absolute bottom-6 right-6 z-[400] bg-neutral-900/90 backdrop-blur-md border border-neutral-700 p-4 rounded-xl shadow-xl max-w-xs">
        <h4 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">Route Legend</h4>
        <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
          {activeRoutes.map(route => {
            const isHidden = selectedVehicleName !== null && selectedVehicleName !== route.vehicle_name;
            if (isHidden) return null;
            return (
              <div key={route.vehicle_id} className="flex items-center gap-3">
                <div 
                  className="w-4 h-4 rounded-full border border-neutral-950 flex-shrink-0" 
                  style={{ backgroundColor: getVehicleColor(route.vehicle_name) }}
                />
                <div className="flex flex-col truncate">
                  <span className="text-sm text-neutral-200 font-medium truncate">{route.vehicle_name}</span>
                  {route.driver_name && (
                    <span className="text-xs text-neutral-400 truncate">{route.driver_name}</span>
                  )}
                </div>
              </div>
            );
          })}
          {activeRoutes.length === 0 && (
            <div className="text-xs text-neutral-500">No active routes</div>
          )}
        </div>
      </div>

      <MapContainer
        center={[28.4949, 77.0895]}
        zoom={12}
        className="w-full h-full"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <MapBoundsController 
          routes={routes} 
          selectedName={selectedVehicleName} 
          focusedLocationId={focusedLocationId}
        />

        {depot && (
          <Marker position={[depot.latitude, depot.longitude]} icon={getDepotIcon()}>
            <Popup>
              <div className="text-neutral-200">
                <span className="font-semibold text-neutral-100 block">Central Hub</span>
                <span className="text-xs">{depot.name}</span>
              </div>
            </Popup>
          </Marker>
        )}

        {routes.map((route) => {
          const isSelected = selectedVehicleName === null || selectedVehicleName === route.vehicle_name;
          const color = getVehicleColor(route.vehicle_name);

          if (!isSelected || route.locations.length === 0) return null;

          const positions: [number, number][] = route.locations.map((loc) => [
            loc.latitude,
            loc.longitude,
          ]);

          return (
            <React.Fragment key={route.vehicle_id}>
              <Polyline
                positions={positions}
                pathOptions={{
                  color,
                  weight: selectedVehicleName === route.vehicle_name ? 5 : 3.5,
                  opacity: selectedVehicleName === route.vehicle_name ? 0.95 : 0.65,
                  dashArray: selectedVehicleName === null ? undefined : undefined,
                }}
              />

              {route.locations.map((loc, index) => {
                const isDepot = loc.id.toString() === "0";
                if (isDepot) return null;

                const isHovered = hoveredLocationId === loc.id || focusedLocationId === loc.id;

                return (
                  <Marker
                    key={`${route.vehicle_id}-${loc.id}-${index}`}
                    position={[loc.latitude, loc.longitude]}
                    icon={getStopIcon(index, color, isHovered)}
                    eventHandlers={{
                      mouseover: () => setHoveredLocationId(loc.id),
                      mouseout: () => setHoveredLocationId(null),
                    }}
                  >
                    <Popup>
                      <div className="text-neutral-100 text-sm">
                        <div className="font-semibold text-neutral-200 block mb-1">
                          {loc.name}
                        </div>
                        <div className="text-xs text-neutral-400">
                          <span className="font-medium text-neutral-300">Vehicle:</span>{' '}
                          {route.vehicle_name}
                        </div>
                        <div className="text-xs text-neutral-400">
                          <span className="font-medium text-neutral-300">Stop Sequence:</span>{' '}
                          {index}
                        </div>
                        <div className="text-xs text-neutral-400">
                          <span className="font-medium text-neutral-300">Coords:</span>{' '}
                          {loc.latitude.toFixed(4)}, {loc.longitude.toFixed(4)}
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
};
