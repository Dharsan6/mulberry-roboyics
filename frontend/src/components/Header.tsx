import React, { useState, useEffect } from 'react';
import {
  Wifi,
  WifiOff,
  Radio,
  RefreshCw,
  MapPin,
  Clock,
  Sliders
} from 'lucide-react';
import {
  subscribeConnectionState,
  setForceMockMode,
  checkBackendHealth
} from '../services/api';

interface HeaderProps {
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onRefresh }) => {
  const [isMockMode, setIsMockMode] = useState<boolean>(false);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const unsubscribe = subscribeConnectionState((isMock, connected) => {
      setIsMockMode(isMock);
      setIsConnected(connected);
    });

    checkBackendHealth();
    const interval = setInterval(() => {
      checkBackendHealth();
    }, 5000);

    const clockInterval = setInterval(() => {
      setTimeStr(new Date().toLocaleTimeString());
    }, 1000);
    setTimeStr(new Date().toLocaleTimeString());

    return () => {
      unsubscribe();
      clearInterval(interval);
      clearInterval(clockInterval);
    };
  }, []);

  const handleToggleMock = () => {
    setForceMockMode(!isMockMode);
  };

  const handleRefreshClick = () => {
    setIsRefreshing(true);
    checkBackendHealth();
    if (onRefresh) onRefresh();
    setTimeout(() => setIsRefreshing(false), 600);
  };

  return (
    <header className="h-16 bg-slate-900/60 border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-30 backdrop-blur-md">
      {/* Left: GPS & Plantation Context */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-xs font-mono bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <MapPin className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-slate-300">Lat: <strong className="text-emerald-400">11.3921°N</strong></span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-300">Lon: <strong className="text-emerald-400">77.7342°E</strong></span>
        </div>

        <div className="hidden md:flex items-center space-x-2 text-xs text-slate-400 font-mono">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>{timeStr}</span>
        </div>
      </div>

      {/* Right: API Mode, Health Badge, Refresh */}
      <div className="flex items-center space-x-4">
        {/* Refresh button */}
        <button
          onClick={handleRefreshClick}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 transition-all border border-slate-700/60"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`} />
        </button>

        {/* Backend Status Indicator */}
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border ${
          isMockMode
            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
            : isConnected
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
        }`}>
          {isMockMode ? (
            <>
              <Radio className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
              <span>Realistic Mock Mode</span>
            </>
          ) : isConnected ? (
            <>
              <Wifi className="w-3.5 h-3.5 text-emerald-400" />
              <span>FastAPI Backend Online</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-rose-400" />
              <span>Backend Offline (Auto Mock)</span>
            </>
          )}
        </div>

        {/* Mock Mode Toggle Switch */}
        <div className="flex items-center space-x-2 bg-slate-950/80 p-1.5 rounded-lg border border-slate-800">
          <Sliders className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-300 font-medium">Force Mock</span>
          <button
            onClick={handleToggleMock}
            className={`w-9 h-5 flex items-center rounded-full p-0.5 transition-colors duration-300 ${
              isMockMode ? 'bg-amber-500' : 'bg-slate-700'
            }`}
          >
            <div
              className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                isMockMode ? 'translate-x-4' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>
    </header>
  );
};
