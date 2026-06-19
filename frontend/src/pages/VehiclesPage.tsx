import React, { useState, useEffect } from 'react';
import { useLogisticsStore } from '../store/logisticsStore';
import type { Vehicle } from '../store/logisticsStore';
import { Search, Plus, Trash2, Edit2, Truck, Clipboard, Loader2 } from 'lucide-react';

export const VehiclesPage: React.FC = () => {
  const { vehicles, fetchVehicles, addVehicle, editVehicle, deleteVehicle, isLoadingVehicles } = useLogisticsStore();
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('All');
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [modalVehicle, setModalVehicle] = useState<Partial<Vehicle> | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchVehicles();
  }, [fetchVehicles]);

  // Filter & Search
  const filteredVehicles = vehicles.filter((v) => {
    const matchesSearch = v.name.toLowerCase().includes(search.toLowerCase()) || 
                          v.vehicleNumber.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterStatus === 'All' || v.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalVehicle?.name || !modalVehicle?.vehicleNumber) return;

    setIsSubmitting(true);
    try {
      if (modalVehicle.id) {
        await editVehicle(modalVehicle as Vehicle);
      } else {
        await addVehicle({
          name: modalVehicle.name,
          vehicleNumber: modalVehicle.vehicleNumber,
          status: modalVehicle.status || 'Available'
        });
      }
      setShowModal(false);
      setModalVehicle(null);
    } catch (err) {
      console.error(err);
      alert('Failed to save vehicle');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this vehicle?')) {
      try {
        await deleteVehicle(id);
      } catch (err) {
        console.error(err);
        alert('Failed to delete vehicle');
      }
    }
  };

  const openAddModal = () => {
    setModalVehicle({ name: '', vehicleNumber: '', status: 'Available' });
    setShowModal(true);
  };

  const openEditModal = (vehicle: Vehicle) => {
    setModalVehicle(vehicle);
    setShowModal(true);
  };

  const getStatusBadge = (status: Vehicle['status']) => {
    const classes = {
      Available: 'bg-neutral-800 text-white border-neutral-700',
      'In Route': 'bg-neutral-800 text-neutral-300 border-neutral-700',
      Maintenance: 'bg-neutral-800 text-neutral-400 border-neutral-700',
      Unavailable: 'bg-neutral-900 text-neutral-500 border-neutral-800',
    };
    return (
      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${classes[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-neutral-100 flex items-center">
            Vehicle Fleet
            {isLoadingVehicles && <Loader2 className="w-4 h-4 ml-3 animate-spin text-neutral-500" />}
          </h1>
          <p className="text-xs text-neutral-500 mt-1">Manage delivery trucks, vans, and utility assets.</p>
        </div>
        <button
          onClick={openAddModal}
          className="flex items-center px-4 py-2 bg-white hover:bg-neutral-100 text-neutral-900 rounded-lg text-xs font-semibold space-x-2 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Provision Vehicle</span>
        </button>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-neutral-500" />
          <input
            type="text"
            placeholder="Search fleet by model name or vehicle number..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full text-xs bg-neutral-900/60 border border-neutral-800/80 rounded-xl pl-10 pr-4 py-3 text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-neutral-600 transition-colors"
          />
        </div>
        {/* Filters */}
        <div className="flex space-x-2">
          {['All', 'Available', 'In Route', 'Maintenance', 'Unavailable'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`text-xs px-3 py-2 rounded-xl border font-semibold transition-all ${
                filterStatus === st
                  ? 'bg-white text-neutral-900 border-neutral-300'
                  : 'bg-neutral-900/40 border-neutral-800/60 text-neutral-400 hover:text-neutral-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-neutral-900/40 border border-neutral-800/80 rounded-xl overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-neutral-800/80 bg-neutral-900/60 text-neutral-400 font-semibold">
              <th className="p-4">Vehicle Model</th>
              <th className="p-4">Plate Number</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-800/50">
            {filteredVehicles.map((vehicle) => (
              <tr key={vehicle.id} className="hover:bg-neutral-900/20 text-neutral-300">
                <td className="p-4 font-semibold text-neutral-200 flex items-center space-x-2.5">
                  <div className="p-2 bg-neutral-800 rounded-lg text-neutral-400">
                    <Truck className="w-3.5 h-3.5" />
                  </div>
                  <span>{vehicle.name}</span>
                </td>
                <td className="p-4 text-neutral-400 font-mono uppercase">{vehicle.vehicleNumber}</td>
                <td className="p-4">{getStatusBadge(vehicle.status)}</td>
                <td className="p-4 text-right space-x-2">
                  <button
                    onClick={() => openEditModal(vehicle)}
                    className="p-1.5 bg-neutral-900 hover:bg-neutral-800 rounded-lg border border-neutral-800 hover:border-neutral-700 text-neutral-400 hover:text-neutral-200 transition-colors inline-block"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(vehicle.id)}
                    className="p-1.5 bg-neutral-900 hover:bg-neutral-800 rounded-lg border border-neutral-800 text-neutral-400 hover:text-neutral-200 transition-colors inline-block"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
            {!isLoadingVehicles && filteredVehicles.length === 0 && (
              <tr>
                <td colSpan={4} className="p-8 text-center text-neutral-500 italic">
                  No vehicles matching criteria.
                </td>
              </tr>
            )}
            {isLoadingVehicles && vehicles.length === 0 && (
              <tr>
                <td colSpan={4} className="p-8 text-center text-neutral-500 italic">
                  Loading vehicles...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Dialog */}
      {showModal && modalVehicle && (
        <div className="fixed inset-0 bg-neutral-950/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <form 
            onSubmit={handleSubmit}
            className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl w-full max-w-sm space-y-4 shadow-2xl"
          >
            <h2 className="text-sm font-bold text-neutral-200 flex items-center">
              <Clipboard className="w-4 h-4 mr-2 text-neutral-400" />
              {modalVehicle.id ? 'Edit Vehicle Details' : 'Provision Vehicle'}
            </h2>
            
            <div className="space-y-3.5">
              <div>
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">Model Name</label>
                <input
                  type="text"
                  required
                  value={modalVehicle.name || ''}
                  onChange={(e) => setModalVehicle({ ...modalVehicle, name: e.target.value })}
                  placeholder="e.g. E-Truck 01"
                  className="w-full text-xs bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">License Plate / Vehicle Number</label>
                <input
                  type="text"
                  required
                  value={modalVehicle.vehicleNumber || ''}
                  onChange={(e) => setModalVehicle({ ...modalVehicle, vehicleNumber: e.target.value })}
                  placeholder="e.g. HR-26-AB-1234"
                  className="w-full text-xs bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider block mb-1">Operational Status</label>
                <select
                  value={modalVehicle.status || 'Available'}
                  onChange={(e) => setModalVehicle({ ...modalVehicle, status: e.target.value as Vehicle['status'] })}
                  className="w-full text-xs bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-neutral-200 focus:outline-none focus:border-neutral-600"
                >
                  <option value="Available">Available</option>
                  <option value="In Route">In Route</option>
                  <option value="Maintenance">Maintenance</option>
                  <option value="Unavailable">Unavailable</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                disabled={isSubmitting}
                className="px-4 py-2 bg-neutral-950 hover:bg-neutral-800 border border-neutral-800 rounded-lg text-xs font-semibold text-neutral-400 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center px-4 py-2 bg-white hover:bg-neutral-100 text-neutral-900 rounded-lg text-xs font-semibold disabled:opacity-50"
              >
                {isSubmitting && <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />}
                {isSubmitting ? 'Saving...' : 'Save Details'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
