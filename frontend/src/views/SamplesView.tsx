import { useState, useEffect } from 'react';
import type { SoilObservation, AgronomicAnalysis } from '../types/telemetry';
import { apiService } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import {
  Database,
  Search,
  Eye,
  X,
  FileText
} from 'lucide-react';

export const SamplesView: React.FC = () => {
  const [samples, setSamples] = useState<SoilObservation[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedSample, setSelectedSample] = useState<SoilObservation | null>(null);
  const [analysis, setAnalysis] = useState<AgronomicAnalysis | null>(null);

  useEffect(() => {
    const fetchSamples = async () => {
      const res = await apiService.getTelemetry(50);
      setSamples(res);
    };
    fetchSamples();
  }, []);

  const handleInspect = async (sample: SoilObservation) => {
    setSelectedSample(sample);
    const analysisRes = await apiService.getSampleAnalysis(sample.sample_id);
    setAnalysis(analysisRes);
  };

  const filteredSamples = samples.filter(s =>
    s.sample_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.mission_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.rover_state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-white">Soil Observation Database</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Probed Telemetry Registry • Modbus Sensor Logs • Agronomic Status Evaluator
            </p>
          </div>
        </div>

        {/* Search bar */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search Sample ID, Mission..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-all font-mono"
          />
        </div>
      </div>

      {/* Main Samples Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Sample ID</th>
                <th className="py-3 px-4">Mission</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Latitude / Longitude</th>
                <th className="py-3 px-4">pH</th>
                <th className="py-3 px-4">EC (dS/m)</th>
                <th className="py-3 px-4">Moisture</th>
                <th className="py-3 px-4">N (kg/ha)</th>
                <th className="py-3 px-4">P (kg/ha)</th>
                <th className="py-3 px-4">K (kg/ha)</th>
                <th className="py-3 px-4 text-center">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredSamples.map(s => (
                <tr key={s.sample_id} className="hover:bg-slate-800/40 transition-colors text-slate-300">
                  <td className="py-3.5 px-4 font-bold text-emerald-400">{s.sample_id}</td>
                  <td className="py-3.5 px-4 text-slate-400">{s.mission_id}</td>
                  <td className="py-3.5 px-4 text-slate-500 text-[11px]">{new Date(s.timestamp).toLocaleTimeString()}</td>
                  <td className="py-3.5 px-4 text-slate-300">{s.latitude.toFixed(4)}°, {s.longitude.toFixed(4)}°</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded font-bold ${
                      s.ph >= 6.5 && s.ph <= 7.5 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {s.ph}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">{s.ec}</td>
                  <td className="py-3.5 px-4">{s.moisture}%</td>
                  <td className="py-3.5 px-4 text-emerald-300">{s.nitrogen}</td>
                  <td className="py-3.5 px-4 text-teal-300">{s.phosphorus}</td>
                  <td className="py-3.5 px-4 text-indigo-300">{s.potassium}</td>
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => handleInspect(s)}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-emerald-500 hover:text-slate-950 text-slate-300 transition-all border border-slate-700"
                      title="Inspect Sample Analysis"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Inspector Drawer */}
      {selectedSample && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              onClick={() => setSelectedSample(null)}
              className="absolute top-4 right-4 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
              <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Sample Inspector: {selectedSample.sample_id}</h3>
                <p className="text-xs text-slate-400 font-mono">Mission: {selectedSample.mission_id}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 text-[10px] block">GPS COORDINATES</span>
                <span className="text-slate-200 font-bold">{selectedSample.latitude}°, {selectedSample.longitude}°</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 text-[10px] block">OVERALL HEALTH STATUS</span>
                <StatusBadge status={analysis?.overall_soil_status || 'SUFFICIENT'} type="agronomy" />
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 text-[10px] block">SOIL PH</span>
                <span className="text-emerald-400 font-bold">{selectedSample.ph} pH ({analysis?.ph_status})</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-slate-500 text-[10px] block">CONDUCTIVITY</span>
                <span className="text-cyan-400 font-bold">{selectedSample.ec} dS/m ({analysis?.ec_status})</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs font-mono">
              <span className="font-bold text-slate-300 block border-b border-slate-800 pb-1">Nutrient Shortfall Matrix:</span>
              <div className="flex justify-between"><span>Nitrogen (N) Deficit:</span><strong className="text-emerald-400">{analysis?.n_deficiency || 0} kg/ha</strong></div>
              <div className="flex justify-between"><span>Phosphorus (P) Deficit:</span><strong className="text-teal-400">{analysis?.p_deficiency || 0} kg/ha</strong></div>
              <div className="flex justify-between"><span>Potassium (K) Deficit:</span><strong className="text-indigo-400">{analysis?.k_deficiency || 0} kg/ha</strong></div>
            </div>

            <button
              onClick={() => setSelectedSample(null)}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 font-bold text-xs text-white"
            >
              Close Inspector
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
