import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  unit?: string;
  icon: LucideIcon;
  trend?: string;
  trendColor?: 'emerald' | 'amber' | 'cyan' | 'rose';
  accentColor?: 'emerald' | 'cyan' | 'indigo' | 'amber' | 'rose';
  targetRange?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  unit,
  icon: Icon,
  trend,
  trendColor = 'emerald',
  accentColor = 'emerald',
  targetRange
}) => {
  const accentClasses = {
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    indigo: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    rose: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
  };

  return (
    <div className="glass-panel p-5 rounded-xl relative overflow-hidden transition-all duration-300 hover:border-slate-700">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 tracking-wide uppercase">{title}</p>
          <div className="flex items-baseline space-x-1.5 mt-2">
            <span className="text-2xl font-extrabold tracking-tight text-white">{value}</span>
            {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
          </div>
        </div>

        <div className={`p-3 rounded-xl border ${accentClasses[accentColor]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs">
        {subtitle ? (
          <span className="text-slate-400">{subtitle}</span>
        ) : targetRange ? (
          <span className="text-slate-500 font-mono text-[11px]">Target: {targetRange}</span>
        ) : null}

        {trend && (
          <span className={`font-medium px-2 py-0.5 rounded-md ${
            trendColor === 'emerald' ? 'bg-emerald-500/10 text-emerald-400' :
            trendColor === 'amber' ? 'bg-amber-500/10 text-amber-400' :
            trendColor === 'rose' ? 'bg-rose-500/10 text-rose-400' : 'bg-cyan-500/10 text-cyan-400'
          }`}>
            {trend}
          </span>
        )}
      </div>
    </div>
  );
};
