import React from 'react';
import {
  LayoutDashboard,
  Bot,
  Sprout,
  MapPin,
  FileSpreadsheet,
  Database,
  Cpu
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onReturnHome?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onReturnHome }) => {
  const navItems = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'rover', label: 'Rover Telemetry & State', icon: Bot },
    { id: 'agronomy', label: 'Mulberry Agronomy', icon: Sprout },
    { id: 'spatial', label: 'Spatial ML Predictions', icon: MapPin },
    { id: 'prescriptions', label: 'Fertilizer Prescriptions', icon: FileSpreadsheet },
    { id: 'samples', label: 'Soil Observations', icon: Database },
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col justify-between h-screen sticky top-0 z-40">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-900/40 text-slate-950 font-extrabold text-xl">
              <Sprout className="w-6 h-6 text-slate-950" />
            </div>
            <div>
              <h1 className="font-bold text-white tracking-wide text-base leading-tight">PRECISION</h1>
              <p className="text-xs text-emerald-400 font-semibold tracking-wider">SERICULTURE AI</p>
            </div>
          </div>
          
          {onReturnHome && (
            <button 
              onClick={onReturnHome}
              className="p-2 bg-slate-800/50 hover:bg-slate-700/80 rounded-lg text-slate-400 hover:text-emerald-400 transition-colors"
              title="Return to Landing Page"
            >
              <LayoutDashboard className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Subtitle */}
        <div className="px-5 py-3 bg-slate-950/50 border-b border-slate-800/50 text-[11px] text-slate-400 flex items-center justify-between">
          <span className="font-medium text-slate-400">Mulberry (*Morus alba*)</span>
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded font-mono">4WD Rover</span>
        </div>

        {/* Nav Items */}
        <nav className="p-3 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-md shadow-emerald-950/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Metadata */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span className="font-mono text-[11px]">Hardware State Machine</span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1">Rack & Pinion Modbus RTU RS485</p>
      </div>
    </aside>
  );
};
