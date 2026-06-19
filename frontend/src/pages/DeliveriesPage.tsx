import React, { useState, useRef, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useLogisticsStore } from '../store/logisticsStore';
import type { Delivery } from '../store/logisticsStore';
import { Search, Plus, Trash2, Calendar, Clipboard, Compass, MapPin, X, Loader2 } from 'lucide-react';

// ─── Gurgaon Location Dictionary ────────────────────────────────────
interface KnownLocation {
  name: string;
  latitude: number;
  longitude: number;
}

const KNOWN_LOCATIONS: KnownLocation[] = [
  { name: 'Cyber City', latitude: 28.4949, longitude: 77.0895 },
  { name: 'Cyber Hub', latitude: 28.4943, longitude: 77.0889 },
  { name: 'MG Road', latitude: 28.4796, longitude: 77.0299 },
  { name: 'Golf Course Road', latitude: 28.4498, longitude: 77.0920 },
  { name: 'Sohna Road', latitude: 28.4140, longitude: 77.0560 },
  { name: 'Udyog Vihar', latitude: 28.5020, longitude: 77.0843 },
  { name: 'Udyog Vihar Phase 1', latitude: 28.5042, longitude: 77.0831 },
  { name: 'Udyog Vihar Phase 4', latitude: 28.5001, longitude: 77.0794 },
  { name: 'Udyog Vihar Phase 5', latitude: 28.4956, longitude: 77.0773 },
  { name: 'Manesar', latitude: 28.3567, longitude: 76.9369 },
  { name: 'IMT Manesar', latitude: 28.3621, longitude: 76.9335 },
  { name: 'DLF Phase 1', latitude: 28.4745, longitude: 77.0929 },
  { name: 'DLF Phase 2', latitude: 28.4812, longitude: 77.0973 },
  { name: 'DLF Phase 3', latitude: 28.4944, longitude: 77.1050 },
  { name: 'DLF Phase 4', latitude: 28.4880, longitude: 77.1081 },
  { name: 'DLF Phase 5', latitude: 28.4702, longitude: 77.1061 },
  { name: 'Sector 4', latitude: 28.4692, longitude: 77.0174 },
  { name: 'Sector 5', latitude: 28.4660, longitude: 77.0202 },
  { name: 'Sector 9', latitude: 28.4630, longitude: 77.0295 },
  { name: 'Sector 10', latitude: 28.4582, longitude: 77.0310 },
  { name: 'Sector 14', latitude: 28.4708, longitude: 77.0266 },
  { name: 'Sector 15', latitude: 28.4660, longitude: 77.0375 },
  { name: 'Sector 17', latitude: 28.4578, longitude: 77.0420 },
  { name: 'Sector 22', latitude: 28.4460, longitude: 77.0410 },
  { name: 'Sector 23', latitude: 28.4530, longitude: 77.0502 },
  { name: 'Sector 29', latitude: 28.4602, longitude: 77.0640 },
  { name: 'Sector 31', latitude: 28.4490, longitude: 77.0485 },
  { name: 'Sector 38', latitude: 28.4400, longitude: 77.0598 },
  { name: 'Sector 40', latitude: 28.4488, longitude: 77.0677 },
  { name: 'Sector 42', latitude: 28.4561, longitude: 77.0723 },
  { name: 'Sector 43', latitude: 28.4533, longitude: 77.0610 },
  { name: 'Sector 44', latitude: 28.4458, longitude: 77.0570 },
  { name: 'Sector 45', latitude: 28.4432, longitude: 77.0708 },
  { name: 'Sector 46', latitude: 28.4408, longitude: 77.0662 },
  { name: 'Sector 47', latitude: 28.4355, longitude: 77.0530 },
  { name: 'Sector 49', latitude: 28.4130, longitude: 77.0505 },
  { name: 'Sector 50', latitude: 28.4190, longitude: 77.0600 },
  { name: 'Sector 51', latitude: 28.4280, longitude: 77.0685 },
  { name: 'Sector 52', latitude: 28.4365, longitude: 77.0750 },
  { name: 'Sector 53', latitude: 28.4305, longitude: 77.0835 },
  { name: 'Sector 54', latitude: 28.4370, longitude: 77.0900 },
  { name: 'Sector 55', latitude: 28.4220, longitude: 77.0860 },
  { name: 'Sector 56', latitude: 28.4240, longitude: 77.0990 },
  { name: 'Sector 57', latitude: 28.4295, longitude: 77.1050 },
  { name: 'Sector 58', latitude: 28.4147, longitude: 77.0950 },
  { name: 'Sector 61', latitude: 28.4110, longitude: 77.0650 },
  { name: 'Sector 62', latitude: 28.4068, longitude: 77.0710 },
  { name: 'Sector 63', latitude: 28.4030, longitude: 77.0780 },
  { name: 'Sector 65', latitude: 28.3990, longitude: 77.0600 },
  { name: 'Sector 67', latitude: 28.3950, longitude: 77.0550 },
  { name: 'Sector 69', latitude: 28.3870, longitude: 77.0430 },
  { name: 'Sector 70', latitude: 28.3810, longitude: 77.0365 },
  { name: 'Sector 72', latitude: 28.3990, longitude: 77.0060 },
  { name: 'Sector 73', latitude: 28.4010, longitude: 77.0145 },
  { name: 'Sector 74', latitude: 28.4055, longitude: 77.0230 },
  { name: 'Sector 76', latitude: 28.4100, longitude: 77.0330 },
  { name: 'Sector 78', latitude: 28.3850, longitude: 76.9990 },
  { name: 'Sector 79', latitude: 28.3810, longitude: 76.9910 },
  { name: 'Sector 80', latitude: 28.3870, longitude: 76.9850 },
  { name: 'Sector 81', latitude: 28.3910, longitude: 76.9900 },
  { name: 'Sector 82', latitude: 28.3945, longitude: 76.9910 },
  { name: 'Sector 83', latitude: 28.3880, longitude: 76.9780 },
  { name: 'Sector 84', latitude: 28.3830, longitude: 76.9710 },
  { name: 'Sector 85', latitude: 28.3780, longitude: 76.9640 },
  { name: 'Sector 86', latitude: 28.3750, longitude: 76.9570 },
  { name: 'Sector 88', latitude: 28.3690, longitude: 76.9520 },
  { name: 'Sector 89', latitude: 28.3710, longitude: 76.9450 },
  { name: 'Sector 90', latitude: 28.3640, longitude: 76.9410 },
  { name: 'Sector 92', latitude: 28.3580, longitude: 76.9350 },
  { name: 'Sector 95', latitude: 28.3500, longitude: 76.9260 },
  { name: 'Sector 102', latitude: 28.3910, longitude: 77.0250 },
  { name: 'Sector 103', latitude: 28.3840, longitude: 77.0180 },
  { name: 'Sector 104', latitude: 28.3930, longitude: 77.0380 },
  { name: 'Sector 106', latitude: 28.3850, longitude: 77.0450 },
  { name: 'Sector 108', latitude: 28.3760, longitude: 77.0340 },
  { name: 'Sector 109', latitude: 28.3700, longitude: 77.0280 },
  { name: 'Sector 110', latitude: 28.3750, longitude: 77.0430 },
  { name: 'Sector 111', latitude: 28.3660, longitude: 77.0380 },
  { name: 'Sector 112', latitude: 28.3610, longitude: 77.0300 },
  { name: 'Sector 113', latitude: 28.3530, longitude: 77.0250 },
  { name: 'Palam Vihar', latitude: 28.5058, longitude: 77.0412 },
  { name: 'South City 1', latitude: 28.4490, longitude: 77.0622 },
  { name: 'South City 2', latitude: 28.4445, longitude: 77.0580 },
  { name: 'Nirvana Country', latitude: 28.4160, longitude: 77.0485 },
  { name: 'Sushant Lok 1', latitude: 28.4650, longitude: 77.0795 },
  { name: 'Sushant Lok 2', latitude: 28.4550, longitude: 77.0865 },
  { name: 'Sushant Lok 3', latitude: 28.4460, longitude: 77.0930 },
  { name: 'Malibu Town', latitude: 28.4470, longitude: 77.0660 },
  { name: 'Greenwood City', latitude: 28.4310, longitude: 77.0535 },
  { name: 'Ardee City', latitude: 28.4348, longitude: 77.0500 },
  { name: 'Sun City', latitude: 28.4200, longitude: 77.0645 },
  { name: 'Vatika City', latitude: 28.4020, longitude: 77.0500 },
  { name: 'Emaar Palm Hills', latitude: 28.4058, longitude: 77.0550 },
  { name: 'Laburnum', latitude: 28.4200, longitude: 77.0440 },
  { name: 'Huda City Centre', latitude: 28.4594, longitude: 77.0723 },
  { name: 'IFFCO Chowk', latitude: 28.4726, longitude: 77.0724 },
  { name: 'Galleria Market', latitude: 28.4614, longitude: 77.0688 },
  { name: 'Ambience Mall', latitude: 28.5047, longitude: 77.0972 },
  { name: 'MGF Metropolitan Mall', latitude: 28.4797, longitude: 77.0370 },
  { name: 'Raheja Mall', latitude: 28.4310, longitude: 77.0535 },
  { name: 'Sadar Bazaar', latitude: 28.4540, longitude: 77.0180 },
  { name: 'Old Gurgaon Railway Station', latitude: 28.4555, longitude: 77.0160 },
  { name: 'Medanta Hospital', latitude: 28.4390, longitude: 77.0420 },
  { name: 'Fortis Hospital', latitude: 28.4458, longitude: 77.0641 },
  { name: 'Leisure Valley Park', latitude: 28.4526, longitude: 77.0560 },
  { name: 'Kingdom of Dreams', latitude: 28.4710, longitude: 77.0752 },
  { name: 'Rapid Metro Station', latitude: 28.4740, longitude: 77.0550 },
  { name: 'Golf Course Extension Road', latitude: 28.4130, longitude: 77.0680 },
  { name: 'SPR Road', latitude: 28.3960, longitude: 77.0420 },
  { name: 'Dwarka Expressway', latitude: 28.5150, longitude: 77.0320 },
  { name: 'NH-48 Service Road', latitude: 28.4520, longitude: 77.0260 },
];

// ─── Custom Map Marker Icons ────────────────────────────────────────
const getWarehouseIcon = () => {
  return L.divIcon({
    html: `<div class="flex items-center justify-center w-7 h-7 rounded-full border-2 border-neutral-950 bg-neutral-300 text-neutral-900 shadow"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-3.5 h-3.5"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg></div>`,
    className: 'picker-warehouse-icon',
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
};

const getTargetIcon = () => {
  return L.divIcon({
    html: `<div class="flex items-center justify-center w-7 h-7 rounded-full border-2 border-neutral-950 bg-white text-neutral-900 shadow animate-bounce"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-3.5 h-3.5"><path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z"/><circle cx="12" cy="10" r="3"/></svg></div>`,
    className: 'picker-target-icon',
    iconSize: [28, 28],
    iconAnchor: [14, 28],
  });
};

// ─── Map Utilities ──────────────────────────────────────────────────
interface MapClickHandlerProps {
  onLocationSelect: (lat: number, lng: number) => void;
}

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onLocationSelect }) => {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

const MapFlyTo: React.FC<{ lat: number; lng: number }> = ({ lat, lng }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lng], 15, { duration: 0.8 });
  }, [lat, lng, map]);
  return null;
};

// ─── Main Component ─────────────────────────────────────────────────
export const DeliveriesPage: React.FC = () => {
  const { deliveries, fetchDeliveries, addDelivery, deleteDelivery, isLoadingDeliveries } = useLogisticsStore();
  const [search, setSearch] = useState('');
  const [filterPriority, setFilterPriority] = useState<string>('All');
  const [filterStatus, setFilterStatus] = useState<string>('All');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchDeliveries();
  }, [fetchDeliveries]);

  // Form states
  const [customerName, setCustomerName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [address, setAddress] = useState('');
  const [priority, setPriority] = useState<'Low' | 'Medium' | 'High'>('Medium');
  const [packageWeight, setPackageWeight] = useState(2.0);
  const [latitude, setLatitude] = useState<number | ''>('');
  const [longitude, setLongitude] = useState<number | ''>('');

  // Location search states
  const [locationQuery, setLocationQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIdx, setHighlightedIdx] = useState(-1);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const locationInputRef = useRef<HTMLInputElement>(null);

  const suggestions = useMemo(() => {
    if (locationQuery.trim().length < 1) return [];
    const q = locationQuery.toLowerCase();
    return KNOWN_LOCATIONS.filter((loc) => loc.name.toLowerCase().includes(q)).slice(0, 8);
  }, [locationQuery]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target as Node) &&
          locationInputRef.current && !locationInputRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const selectLocation = (loc: KnownLocation) => {
    setLocationQuery(loc.name);
    setAddress(`${loc.name}, Gurgaon`);
    setLatitude(loc.latitude);
    setLongitude(loc.longitude);
    setShowSuggestions(false);
    setHighlightedIdx(-1);
  };

  const handleLocationKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIdx((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIdx((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter' && highlightedIdx >= 0) {
      e.preventDefault();
      selectLocation(suggestions[highlightedIdx]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const clearLocation = () => {
    setLocationQuery('');
    setLatitude('');
    setLongitude('');
    setAddress('');
    setShowSuggestions(false);
    locationInputRef.current?.focus();
  };

  const handleLocationSelect = (lat: number, lng: number) => {
    setLatitude(Number(lat.toFixed(6)));
    setLongitude(Number(lng.toFixed(6)));
    let nearest: KnownLocation | null = null;
    let minDist = Infinity;
    for (const loc of KNOWN_LOCATIONS) {
      const dist = Math.sqrt(Math.pow(loc.latitude - lat, 2) + Math.pow(loc.longitude - lng, 2));
      if (dist < minDist) { minDist = dist; nearest = loc; }
    }
    if (nearest && minDist < 0.005) {
      setLocationQuery(nearest.name);
      setAddress(`${nearest.name}, Gurgaon`);
    } else {
      setLocationQuery('');
      setAddress(`Pinned location (${lat.toFixed(4)}, ${lng.toFixed(4)})`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName || !phoneNumber || !address || latitude === '' || longitude === '') return;

    setIsSubmitting(true);
    try {
      await addDelivery({
        customerName,
        phoneNumber,
        address,
        priority,
        packageWeight,
        latitude: Number(latitude),
        longitude: Number(longitude)
      });

      setCustomerName('');
      setPhoneNumber('');
      setAddress('');
      setPriority('Medium');
      setPackageWeight(2.0);
      setLatitude('');
      setLongitude('');
      setLocationQuery('');
    } catch (err) {
      console.error(err);
      alert('Failed to add delivery stop');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this delivery?')) {
      try {
        await deleteDelivery(id);
      } catch (err) {
        console.error(err);
        alert('Failed to delete delivery');
      }
    }
  };

  const filteredDeliveries = deliveries.filter((d) => {
    const matchesSearch = d.customerName.toLowerCase().includes(search.toLowerCase()) || 
                          d.address.toLowerCase().includes(search.toLowerCase());
    const matchesPriority = filterPriority === 'All' || d.priority === filterPriority;
    const matchesStatus = filterStatus === 'All' || d.status === filterStatus;
    return matchesSearch && matchesPriority && matchesStatus;
  });

  const getPriorityBadge = (p: Delivery['priority']) => {
    const classes = {
      High: 'bg-neutral-800 text-white border-neutral-700',
      Medium: 'bg-neutral-800 text-neutral-300 border-neutral-700',
      Low: 'bg-neutral-900 text-neutral-500 border-neutral-800',
    };
    return (
      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${classes[p]}`}>
        {p}
      </span>
    );
  };

  const getStatusBadge = (status: Delivery['status']) => {
    const classes = {
      Pending: 'bg-neutral-800 text-neutral-300 border-neutral-700',
      Assigned: 'bg-neutral-800 text-neutral-300 border-neutral-700',
      'In Transit': 'bg-neutral-800 text-neutral-300 border-neutral-700',
      Delivered: 'bg-neutral-800 text-white border-neutral-700',
    };
    return (
      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${classes[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-neutral-100">Delivery Intake</h1>
        <p className="text-xs text-neutral-500 mt-1">Book new deliveries and review pending queues.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-neutral-200 flex items-center">
            <Clipboard className="w-4 h-4 mr-2 text-neutral-400" />
            New Delivery Details
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">Customer Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Ramesh Patel"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">Phone Number</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 9988776655"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                />
              </div>
            </div>

            {/* Location Search with Autocomplete */}
            <div className="relative">
              <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">
                Delivery Location
              </label>
              <div className="relative">
                <MapPin className="w-3.5 h-3.5 absolute left-3 top-3 text-neutral-500" />
                <input
                  ref={locationInputRef}
                  type="text"
                  placeholder="Type a location name… e.g. Sector 29, DLF Phase 3, Cyber Hub"
                  value={locationQuery}
                  onChange={(e) => {
                    setLocationQuery(e.target.value);
                    setShowSuggestions(true);
                    setHighlightedIdx(-1);
                  }}
                  onFocus={() => { if (locationQuery.trim().length > 0) setShowSuggestions(true); }}
                  onKeyDown={handleLocationKeyDown}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg pl-9 pr-9 py-2.5 text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-neutral-600 transition-colors"
                />
                {locationQuery && (
                  <button
                    type="button"
                    onClick={clearLocation}
                    className="absolute right-3 top-2.5 text-neutral-500 hover:text-neutral-300 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {showSuggestions && suggestions.length > 0 && (
                <div
                  ref={suggestionsRef}
                  className="absolute z-50 w-full mt-1 bg-neutral-900 border border-neutral-700 rounded-lg shadow-2xl shadow-black/40 overflow-hidden"
                >
                  {suggestions.map((loc, idx) => (
                    <button
                      key={loc.name}
                      type="button"
                      onClick={() => selectLocation(loc)}
                      className={`w-full flex items-center px-3 py-2.5 text-left transition-colors ${
                        idx === highlightedIdx
                          ? 'bg-white/10 text-white'
                          : 'text-neutral-300 hover:bg-neutral-800'
                      }`}
                    >
                      <MapPin className={`w-3 h-3 mr-2.5 shrink-0 ${idx === highlightedIdx ? 'text-white' : 'text-neutral-500'}`} />
                      <span className="text-xs font-medium truncate">{loc.name}</span>
                      <span className="ml-auto text-[9px] text-neutral-500 font-mono shrink-0 pl-3">
                        {loc.latitude.toFixed(4)}, {loc.longitude.toFixed(4)}
                      </span>
                    </button>
                  ))}
                </div>
              )}

              {showSuggestions && locationQuery.trim().length >= 2 && suggestions.length === 0 && (
                <div className="absolute z-50 w-full mt-1 bg-neutral-900 border border-neutral-700 rounded-lg shadow-2xl p-3">
                  <p className="text-[10px] text-neutral-500 italic text-center">
                    No matching location found. You can click on the map below to pin a custom location.
                  </p>
                </div>
              )}
            </div>

            {/* Selected location confirmation */}
            {latitude !== '' && longitude !== '' && (
              <div className="flex items-center gap-3 bg-neutral-800/30 border border-neutral-700/50 rounded-lg px-4 py-2.5">
                <div className="w-2 h-2 rounded-full bg-white animate-pulse shrink-0" />
                <div className="min-w-0">
                  <p className="text-[10px] font-semibold text-neutral-300 uppercase tracking-wider">Location Set</p>
                  <p className="text-xs text-neutral-300 truncate">{address}</p>
                </div>
                <span className="ml-auto text-[9px] text-neutral-500 font-mono shrink-0">
                  {Number(latitude).toFixed(4)}, {Number(longitude).toFixed(4)}
                </span>
              </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="col-span-2">
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">Weight (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={packageWeight}
                  onChange={(e) => setPackageWeight(Number(e.target.value))}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                />
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>

            <div>
              <p className="text-[10px] text-neutral-500 italic mb-1.5">
                Or click on the map to pin a custom delivery location.
              </p>
              <div className="h-64 rounded-lg overflow-hidden border border-neutral-800 shadow-inner relative z-10">
                <MapContainer
                  center={[28.4949, 77.0895]}
                  zoom={12}
                  className="w-full h-full"
                  zoomControl={false}
                >
                  <TileLayer
                    attribution='&copy; OpenStreetMap'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  />
                  <Marker position={[28.4949, 77.0895]} icon={getWarehouseIcon()} />
                  {latitude !== '' && longitude !== '' && (
                    <>
                      <Marker position={[Number(latitude), Number(longitude)]} icon={getTargetIcon()} />
                      <MapFlyTo lat={Number(latitude)} lng={Number(longitude)} />
                    </>
                  )}
                  <MapClickHandler onLocationSelect={handleLocationSelect} />
                </MapContainer>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center py-3 bg-white hover:bg-neutral-100 text-neutral-900 rounded-lg text-xs font-semibold space-x-2 transition-all disabled:opacity-50"
            >
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              <span>{isSubmitting ? 'Registering...' : 'Register Delivery Stop'}</span>
            </button>
          </form>
        </div>

        <div className="lg:col-span-5 flex flex-col min-h-0 bg-neutral-900/40 border border-neutral-800/80 rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-semibold text-neutral-200 flex items-center">
              <Compass className="w-4 h-4 mr-2 text-neutral-400" />
              Queue ({filteredDeliveries.length})
              {isLoadingDeliveries && <Loader2 className="w-3.5 h-3.5 ml-2 animate-spin text-neutral-500" />}
            </h2>
            <div className="flex space-x-1.5">
              <select 
                value={filterPriority} 
                onChange={(e) => setFilterPriority(e.target.value)}
                className="bg-neutral-950 border border-neutral-800 rounded px-1 py-0.5 text-[9px] text-neutral-400 focus:outline-none"
              >
                <option value="All">All Priority</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
              <select 
                value={filterStatus} 
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-neutral-950 border border-neutral-800 rounded px-1 py-0.5 text-[9px] text-neutral-400 focus:outline-none"
              >
                <option value="All">All Status</option>
                <option value="Pending">Pending</option>
                <option value="Assigned">Assigned</option>
                <option value="In Transit">Transit</option>
                <option value="Delivered">Delivered</option>
              </select>
            </div>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-neutral-500" />
            <input
              type="text"
              placeholder="Search address or client..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full text-xs bg-neutral-950 border border-neutral-800 rounded-lg pl-9 pr-4 py-2 text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-neutral-600 transition-colors"
            />
          </div>

          <div className="space-y-2.5 overflow-y-auto max-h-[550px] pr-1">
            {filteredDeliveries.map((del) => (
              <div 
                key={del.id}
                className="p-3 bg-neutral-900/60 border border-neutral-800 rounded-lg hover:border-neutral-700 transition-all text-xs flex justify-between items-start"
              >
                <div className="space-y-1 min-w-0 pr-2">
                  <div className="flex items-center space-x-1.5">
                    <span className="font-semibold text-neutral-200 truncate">{del.customerName}</span>
                    {getPriorityBadge(del.priority)}
                  </div>
                  <p className="text-[10px] text-neutral-400 truncate">{del.address}</p>
                  <div className="flex items-center space-x-3 text-[9px] text-neutral-500 pt-1">
                    <span className="font-mono">{del.packageWeight} kg</span>
                    <span className="flex items-center">
                      <Calendar className="w-2.5 h-2.5 mr-0.5" />
                      {del.createdAt && new Date(del.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
                <div className="flex flex-col items-end justify-between h-full space-y-3 shrink-0">
                  {getStatusBadge(del.status)}
                  <button 
                    onClick={() => handleDelete(del.id)}
                    className="text-neutral-500 hover:text-neutral-300 transition-colors p-1"
                    title="Remove Stop"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
            {!isLoadingDeliveries && filteredDeliveries.length === 0 && (
              <div className="p-8 text-center text-neutral-500 italic text-xs">
                Queue is empty.
              </div>
            )}
            {isLoadingDeliveries && deliveries.length === 0 && (
              <div className="p-8 text-center text-neutral-500 italic text-xs">
                Loading deliveries...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
