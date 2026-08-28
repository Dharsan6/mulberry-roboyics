import { useState, useEffect } from 'react';
import type { FertilizerPrescriptionZone } from '../types/telemetry';
import { apiService } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import {
  FileSpreadsheet,
  Download,
  MapPin,
  Filter
} from 'lucide-react';

export const PrescriptionsView: React.FC = () => {
  const [prescriptions, setPrescriptions] = useState<FertilizerPrescriptionZone[]>([]);
  const [filterPriority, setFilterPriority] = useState<string>('ALL');

  useEffect(() => {
    const fetchPrescriptions = async () => {
      const res = await apiService.getPrescriptions();
      setPrescriptions(res);
    };
    fetchPrescriptions();
  }, []);

  const filtered = prescriptions.filter(p => {
    if (filterPriority === 'ALL') return true;
    return p.priority === filterPriority;
  });

  const handleExportCSV = () => {
    const headers = ['Zone ID', 'Latitude', 'Longitude', 'N Deficit (kg/ha)', 'P Deficit (kg/ha)', 'K Deficit (kg/ha)', 'Priority', 'Recommendation Note'];
    const rows = prescriptions.map(p => [
      p.zone_id,
      p.center_lat,
      p.center_lon,
      p.n_deficiency,
      p.p_deficiency,
      p.k_deficiency,
      p.priority,
      `"${p.recommendation_note}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `mulberry_fertilizer_prescriptions_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-white">Fertilizer Prescription Management</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Precision Zoning • Dosage Calculations • Targeted Soil Treatment Plans
            </p>
          </div>
        </div>

        <button
          onClick={handleExportCSV}
          className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-950/40 flex items-center space-x-2 transition-all"
        >
          <Download className="w-4 h-4" />
          <span>Export Prescriptions (CSV)</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2">
        <span className="text-xs font-mono text-slate-400 flex items-center space-x-1 mr-2">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter Priority:</span>
        </span>
        {['ALL', 'HIGH', 'MODERATE', 'LOW'].map(p => (
          <button
            key={p}
            onClick={() => setFilterPriority(p)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold border transition-all ${
              filterPriority === p
                ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Prescription Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(p => (
          <div key={p.zone_id} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 hover:border-slate-700 transition-all">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-mono text-slate-400 flex items-center space-x-1">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Lat: {p.center_lat}°, Lon: {p.center_lon}°</span>
                </span>
                <h3 className="font-bold text-white text-base mt-1">{p.zone_id}</h3>
              </div>
              <StatusBadge status={p.priority} type="agronomy" />
            </div>

            <div className="grid grid-cols-3 gap-2 font-mono text-xs">
              <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-[10px] text-slate-500 block">N DEFICIT</span>
                <strong className="text-emerald-400">{p.n_deficiency} kg/ha</strong>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-[10px] text-slate-500 block">P DEFICIT</span>
                <strong className="text-teal-400">{p.p_deficiency} kg/ha</strong>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-[10px] text-slate-500 block">K DEFICIT</span>
                <strong className="text-indigo-400">{p.k_deficiency} kg/ha</strong>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
              <span className="font-bold text-slate-300 block">Agronomic Recommendation:</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">{p.recommendation_note}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
