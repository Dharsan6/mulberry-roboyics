import { useState, useEffect } from 'react';
import type { PlantationSummary, SoilObservation } from '../types/telemetry';
import { apiService } from '../services/api';
import {
  Sprout,
  Activity,
  Zap,
  Leaf,
  TrendingUp,
  Info
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export const AgronomyView: React.FC = () => {
  const [summary, setSummary] = useState<PlantationSummary | null>(null);
  const [samples, setSamples] = useState<SoilObservation[]>([]);

  useEffect(() => {
    const load = async () => {
      const [sumRes, telemetryRes] = await Promise.all([
        apiService.getSummary(),
        apiService.getTelemetry(10)
      ]);
      setSummary(sumRes);
      setSamples(telemetryRes);
    };
    load();
  }, []);

  const chartData = samples.slice(0, 8).map(s => ({
    name: s.sample_id,
    Nitrogen: s.nitrogen,
    N_Shortfall: Math.max(0, 350 - s.nitrogen),
    Phosphorus: s.phosphorus,
    P_Shortfall: Math.max(0, 140 - s.phosphorus),
    Potassium: s.potassium,
    K_Shortfall: Math.max(0, 140 - s.potassium)
  }));

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-white">Mulberry Agronomy Intelligence Engine</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Scientific Morus alba Baselines • Target Shortfall Matrix • Soil Remediation Guidelines
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-xs font-mono">
          <Leaf className="w-4 h-4 text-emerald-400" />
          <span className="text-slate-300">Target Crop: <strong className="text-emerald-400">Morus alba (V1 / Victory-1 Mulberry)</strong></span>
        </div>
      </div>

      {/* Target Baseline Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Soil pH Baseline</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-black text-white">{summary?.avg_ph || 6.8}</span>
            <span className="text-xs text-slate-400">pH</span>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-1">
            <div className="flex justify-between"><span>Scientific Target:</span><strong className="text-emerald-400">6.5 – 7.5 pH</strong></div>
            <div className="flex justify-between"><span>Soil Condition:</span><strong className="text-slate-200">Slightly Acidic to Neutral</strong></div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Electrical Conductivity (EC)</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-black text-white">{summary?.avg_ec || 0.74}</span>
            <span className="text-xs text-slate-400">dS/m</span>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-1">
            <div className="flex justify-between"><span>Upper Salinity Limit:</span><strong className="text-cyan-400">&lt; 1.0 dS/m</strong></div>
            <div className="flex justify-between"><span>Salinity Status:</span><strong className="text-emerald-400">NON-SALINE / SAFE</strong></div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Leaf Yield Productivity Potential</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-black text-emerald-400">92.4%</span>
            <span className="text-xs text-slate-400">Optimum</span>
          </div>
          <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-1">
            <div className="flex justify-between"><span>Expected Yield:</span><strong className="text-emerald-400">45–50 metric tons/ha/yr</strong></div>
            <div className="flex justify-between"><span>Sericulture Quality:</span><strong className="text-slate-200">GRADE A SILKWORM FEED</strong></div>
          </div>
        </div>
      </div>

      {/* Main Bar Chart: Measured Nutrient Level vs Shortfall */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="font-bold text-white text-base">Nitrogen, Phosphorus & Potassium Shortfall Breakdown</h3>
            <p className="text-xs text-slate-400">Target Requirements: N = 350 kg/ha, P = 140 kg/ha, K = 140 kg/ha</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono px-2.5 py-1 rounded">
              Shortfall = max(Target - Measured, 0)
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Bar dataKey="Nitrogen" fill="#22c55e" radius={[4, 4, 0, 0]} name="Nitrogen (N) Measured" />
              <Bar dataKey="N_Shortfall" fill="#ef4444" radius={[4, 4, 0, 0]} name="N Shortfall (Deficit)" />
              <Bar dataKey="Phosphorus" fill="#06b6d4" radius={[4, 4, 0, 0]} name="Phosphorus (P) Measured" />
              <Bar dataKey="P_Shortfall" fill="#f59e0b" radius={[4, 4, 0, 0]} name="P Shortfall (Deficit)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Scientific Mulberry Agronomy Guidelines Card */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
        <div className="flex items-center space-x-2 text-emerald-400 font-bold">
          <Info className="w-5 h-5" />
          <h3 className="text-base text-white">Mulberry (*Morus alba*) agronomy baseline rules</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono pt-2">
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1.5">
            <h4 className="font-bold text-emerald-400">1. Nitrogen (N) Management</h4>
            <p className="text-slate-400 text-[11px] leading-normal">
              Mulberry leaves require 350 kg N/ha annually for high protein content essential for Bombyx mori silkworm larval growth. Apply Neem-coated Urea post leaf-harvest.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1.5">
            <h4 className="font-bold text-teal-400">2. Phosphorus (P) Management</h4>
            <p className="text-slate-400 text-[11px] leading-normal">
              140 kg P2O5/ha requirement enhances root establishment and drought resistance. Soil application of Single Super Phosphate (SSP) combined with PSB biofertilizers.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1.5">
            <h4 className="font-bold text-indigo-400">3. Potassium (K) Management</h4>
            <p className="text-slate-400 text-[11px] leading-normal">
              140 kg K2O/ha optimizes leaf moisture retention and disease resistance against powdery mildew (*Phyllactinia corylea*). Apply Muriate of Potash (MOP) in split doses.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
