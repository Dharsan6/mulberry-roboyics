import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'rover' | 'agronomy' | 'general';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getBadgeStyle = () => {
    const s = status.toUpperCase();
    
    // Rover States
    if (s === 'TRANSIT') return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
    if (s === 'DEPLOYMENT') return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    if (s === 'INTERROGATION') return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
    if (s === 'RETRACTION') return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
    if (s === 'E_STOP') return 'bg-rose-500/20 text-rose-400 border-rose-500/50 animate-pulse';

    // Agronomy & Health States
    if (s === 'OPTIMAL' || s === 'SUFFICIENT' || s === 'NORMAL' || s === 'ONLINE') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    }
    if (s === 'DEFICIENT' || s === 'MODERATE' || s === 'LOW') {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    }
    if (s === 'SEVERE_DEFICIENCY' || s === 'HIGH' || s === 'CRITICAL' || s === 'OFFLINE') {
      return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }

    return 'bg-slate-800 text-slate-300 border-slate-700';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono font-semibold border ${getBadgeStyle()}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
      {status}
    </span>
  );
};
