import { useState, useEffect } from 'react';
import type {
  PlantationSummary,
  SoilObservation,
  RoverSimulatorStatus
} from '../types/telemetry';
import { apiService } from '../services/api';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import {
  Activity,
  Bot,
  Layers,
  Droplets,
  Zap,
  TrendingDown,
  ArrowRight,
  ShieldCheck,
  Globe
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface OverviewViewProps {
  onNavigate: (tab: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<PlantationSummary | null>(null);
  const [samples, setSamples] = useState<SoilObservation[]>([]);
  const [roverStatus, setRoverStatus] = useState<RoverSimulatorStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sumRes, telemetryRes, roverRes] = await Promise.all([
        apiService.getSummary(),
        apiService.getTelemetry(10),
        apiService.getSimulatorStatus()
      ]);
      setSummary(sumRes);
      setSamples(telemetryRes);
      setRoverStatus(roverRes);
    } catch (e) {
      console.error('Error fetching dashboard summary:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-mono text-slate-400">Loading Precision Sericulture Telemetry...</p>
        </div>
      </div>
    );
  }

  const chartData = samples.slice().reverse().map(s => ({
    time: s.sample_id,
    ph: s.ph,
    ec: s.ec,
    moisture: s.moisture,
    n: s.nitrogen,
    p: s.phosphorus,
    k: s.potassium
  }));

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner Hero */}
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-emerald-950/40 p-6 border border-slate-800 shadow-xl overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-emerald-500/10 to-transparent pointer-events-none" />
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="inline-flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full text-xs font-mono mb-3">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>4WD Autonomous Rover • Rack-and-Pinion Probing Active</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white">
              Precision Sericulture Soil Intelligence
            </h2>
            <p className="text-sm text-slate-400 max-w-2xl mt-1">
              Real-time Morus alba agronomy pipeline: automated Modbus RTU RS485 soil probing, spatial neural network interpolation, and targeted fertilizer deficit calculation.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => onNavigate('rover')}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-950/50 flex items-center space-x-2 transition-all"
            >
              <Bot className="w-4 h-4" />
              <span>Control Rover</span>
            </button>
            <button
              onClick={() => onNavigate('spatial')}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-sm flex items-center space-x-2 transition-all"
            >
              <Globe className="w-4 h-4 text-emerald-400" />
              <span>Spatial ML Grid</span>
            </button>
          </div>
        </div>
      </div>

      {/* Primary Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Probed Samples"
          value={summary?.total_samples || 0}
          subtitle={`Across ${summary?.total_missions || 1} Plantation Missions`}
          icon={Layers}
          accentColor="emerald"
          trend="+12 this mission"
        />
        <StatCard
          title="Average Soil pH"
          value={summary?.avg_ph || 6.8}
          unit="pH"
          targetRange="6.5 - 7.5 pH"
          icon={Activity}
          accentColor={summary && summary.avg_ph >= 6.5 && summary.avg_ph <= 7.5 ? 'emerald' : 'amber'}
          trend={summary && summary.avg_ph >= 6.5 && summary.avg_ph <= 7.5 ? 'OPTIMAL' : 'CHECK PH'}
        />
        <StatCard
          title="Electrical Conductivity"
          value={summary?.avg_ec || 0.74}
          unit="dS/m"
          targetRange="< 1.0 dS/m"
          icon={Zap}
          accentColor="cyan"
          trend="NORMAL"
        />
        <StatCard
          title="Total N-P-K Shortfall"
          value={summary ? Math.round(summary.total_n_deficiency + summary.total_p_deficiency + summary.total_k_deficiency) : 0}
          unit="kg/ha"
          subtitle="Mulberry Plantation Deficit"
          icon={TrendingDown}
          accentColor="rose"
          trendColor="rose"
          trend="REQUIRES DOSING"
        />
      </div>

      {/* Middle Section: Active Rover State & Moisture / Telemetry Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Rover State Machine Live Card */}
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between border border-slate-800">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-white text-base">Autonomous Rover State</h3>
              </div>
              <StatusBadge status={roverStatus?.rover_state || summary?.current_rover_state || 'TRANSIT'} type="rover" />
            </div>

            <div className="space-y-3">
              {[
                { name: 'STATE 1 — TRANSIT', desc: 'Driving to target GPS waypoint', code: 'TRANSIT' },
                { name: 'STATE 2 — DEPLOYMENT', desc: 'Rack-and-pinion deploying probe down', code: 'DEPLOYMENT' },
                { name: 'STATE 3 — INTERROGATION', desc: 'Stabilizing & decoding Modbus RS485', code: 'INTERROGATION' },
                { name: 'STATE 4 — RETRACTION', desc: 'Raising probe up to top NC limit switch', code: 'RETRACTION' },
              ].map((st) => {
                const isActive = (roverStatus?.rover_state || summary?.current_rover_state) === st.code;
                return (
                  <div
                    key={st.code}
                    className={`p-3 rounded-xl border transition-all ${
                      isActive
                        ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300 shadow-md shadow-emerald-950/30'
                        : 'bg-slate-950/40 border-slate-800/80 text-slate-400'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className={`font-bold ${isActive ? 'text-emerald-400' : 'text-slate-300'}`}>{st.name}</span>
                      {isActive && <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-ping" />}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5">{st.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-400">Waypoint Target: <strong className="text-emerald-400">{roverStatus?.current_waypoint.id || 'WP-04'}</strong></span>
            <button
              onClick={() => onNavigate('rover')}
              className="text-emerald-400 font-semibold hover:underline flex items-center space-x-1"
            >
              <span>Full Control</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Telemetry Moisture & pH Trend Chart */}
        <div className="glass-panel p-5 rounded-2xl lg:col-span-2 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-bold text-white text-base">Live Soil Sensor Trends</h3>
                <p className="text-xs text-slate-400">pH, Electrical Conductivity (EC), & Soil Moisture (%) readouts</p>
              </div>
              <div className="flex items-center space-x-3 text-xs font-mono">
                <span className="flex items-center space-x-1 text-emerald-400"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"/> pH</span>
                <span className="flex items-center space-x-1 text-cyan-400"><span className="w-2.5 h-2.5 rounded-full bg-cyan-500 inline-block"/> Moisture (%)</span>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="phGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="moistGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                  <Area type="monotone" dataKey="ph" stroke="#22c55e" fillOpacity={1} fill="url(#phGrad)" strokeWidth={2} name="pH" />
                  <Area type="monotone" dataKey="moisture" stroke="#06b6d4" fillOpacity={1} fill="url(#moistGrad)" strokeWidth={2} name="Moisture (%)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Optimal Baseline: <strong className="text-slate-200">pH 6.5–7.5</strong> | <strong className="text-slate-200">Moisture 40–50%</strong></span>
            <button onClick={() => onNavigate('agronomy')} className="text-emerald-400 font-semibold hover:underline flex items-center space-x-1">
              <span>View Agronomy Engine</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Section: Recent Telemetry Log Table */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Droplets className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-white text-base">Recent Field Probing Observations</h3>
          </div>
          <button
            onClick={() => onNavigate('samples')}
            className="text-xs text-emerald-400 hover:underline font-semibold flex items-center space-x-1"
          >
            <span>View All Probes</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Sample ID</th>
                <th className="py-2.5 px-3">Mission</th>
                <th className="py-2.5 px-3">GPS Location</th>
                <th className="py-2.5 px-3">pH</th>
                <th className="py-2.5 px-3">EC (dS/m)</th>
                <th className="py-2.5 px-3">Moisture</th>
                <th className="py-2.5 px-3">N (kg/ha)</th>
                <th className="py-2.5 px-3">P (kg/ha)</th>
                <th className="py-2.5 px-3">K (kg/ha)</th>
                <th className="py-2.5 px-3">State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {samples.slice(0, 5).map(s => (
                <tr key={s.sample_id} className="hover:bg-slate-800/40 transition-colors text-slate-300">
                  <td className="py-3 px-3 font-bold text-emerald-400">{s.sample_id}</td>
                  <td className="py-3 px-3 text-slate-400">{s.mission_id}</td>
                  <td className="py-3 px-3 text-slate-300">{s.latitude.toFixed(4)}°, {s.longitude.toFixed(4)}°</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded font-bold ${
                      s.ph >= 6.5 && s.ph <= 7.5 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {s.ph}
                    </span>
                  </td>
                  <td className="py-3 px-3">{s.ec}</td>
                  <td className="py-3 px-3">{s.moisture}%</td>
                  <td className="py-3 px-3 text-emerald-300">{s.nitrogen}</td>
                  <td className="py-3 px-3 text-teal-300">{s.phosphorus}</td>
                  <td className="py-3 px-3 text-indigo-300">{s.potassium}</td>
                  <td className="py-3 px-3">
                    <StatusBadge status={s.rover_state} type="rover" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
