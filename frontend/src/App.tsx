import React from 'react';
import { useLogisticsStore } from './store/logisticsStore';
import { DashboardPage } from './pages/DashboardPage';
import { DriversPage } from './pages/DriversPage';
import { VehiclesPage } from './pages/VehiclesPage';
import { DeliveriesPage } from './pages/DeliveriesPage';
import { OptimizationPage } from './pages/OptimizationPage';
import { RoutesPage } from './pages/RoutesPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { 
  Compass, 
  LayoutDashboard, 
  Users, 
  Truck, 
  MapPin, 
  Sliders, 
  Navigation, 
  BarChart3 
} from 'lucide-react';

const App: React.FC = () => {
  const { activePage, setActivePage } = useLogisticsStore();

  const menuItems = [
    { id: 'dashboard' as const, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'drivers' as const, label: 'Drivers', icon: Users },
    { id: 'vehicles' as const, label: 'Vehicles', icon: Truck },
    { id: 'deliveries' as const, label: 'Deliveries', icon: MapPin },
    { id: 'optimization' as const, label: 'Optimization Center', icon: Sliders },
    { id: 'routes' as const, label: 'Optimized Routes', icon: Navigation },
    { id: 'analytics' as const, label: 'Analytics', icon: BarChart3 },
  ];

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage />;
      case 'drivers':
        return <DriversPage />;
      case 'vehicles':
        return <VehiclesPage />;
      case 'deliveries':
        return <DeliveriesPage />;
      case 'optimization':
        return <OptimizationPage />;
      case 'routes':
        return <RoutesPage />;
      case 'analytics':
        return <AnalyticsPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="flex h-screen bg-neutral-950 text-neutral-100 overflow-hidden font-sans">
      {/* Sidebar navigation */}
      <aside className="w-64 bg-neutral-950 border-r border-neutral-800/60 flex flex-col shrink-0">
        {/* Branding header */}
        <div className="p-5 border-b border-neutral-800/60 flex items-center space-x-3 shrink-0">
          <div className="p-2 bg-neutral-800 rounded-lg text-white">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-neutral-100 tracking-wide text-sm block">LogiDispatch</span>
            <span className="text-[9px] text-neutral-500 font-mono tracking-wider block">FLEET CONTROL v1.5</span>
          </div>
        </div>

        {/* Menu items */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-white text-neutral-950'
                    : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Dispatcher profile footer */}
        <div className="p-4 border-t border-neutral-800/60 shrink-0 text-left">
          <div className="text-[10px] text-neutral-500 uppercase font-bold tracking-wider">Active dispatcher</div>
          <div className="font-bold text-neutral-200 text-xs mt-1 truncate">Admin Terminal</div>
        </div>
      </aside>

      {/* Main content page area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-neutral-950 p-6 relative">
        <div className="relative z-10 h-full">
          {renderActivePage()}
        </div>
      </main>
    </div>
  );
};

export default App;
