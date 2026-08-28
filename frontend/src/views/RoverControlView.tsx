import { useState, useEffect } from 'react';
import type { RoverSimulatorStatus } from '../types/telemetry';
import { apiService } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import {
  Bot,
  Play,
  RotateCcw,
  OctagonAlert,
  Cpu,
  Zap,
  Compass,
  ArrowDownCircle,
  ArrowUpCircle,
  Gauge,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

export const RoverControlView: React.FC = () => {
  const [status, setStatus] = useState<RoverSimulatorStatus | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);

  const fetchStatus = async () => {
    try {
      const res = await apiService.getSimulatorStatus();
      setStatus(res);
    } catch (e) {
      console.error('Failed to fetch rover status:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStep = async () => {
    setIsExecuting(true);
    try {
      const res = await apiService.stepSimulator();
      setStatus(res);
    } catch (e) {
      console.error('Step execution failed:', e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleReset = async () => {
    setIsExecuting(true);
    try {
      const res = await apiService.resetSimulator();
      setStatus(res);
    } catch (e) {
      console.error('Reset failed:', e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleEstop = async () => {
    setIsExecuting(true);
    try {
      const res = await apiService.estopSimulator();
      setStatus(res);
    } catch (e) {
      console.error('E-stop failed:', e);
    } finally {
      setIsExecuting(false);
    }
  };

  const states = [
    {
      code: 'TRANSIT',
      title: 'STATE 1 — TRANSIT',
      desc: 'Drive to target GPS waypoint (< 0.5m threshold). Rack stays locked UP.',
      icon: Compass,
      color: 'sky'
    },
    {
      code: 'DEPLOYMENT',
      title: 'STATE 2 — DEPLOYMENT',
      desc: 'N20 motor drives rack down until NC Bottom Limit Switch triggers.',
      icon: ArrowDownCircle,
      color: 'amber'
    },
    {
      code: 'INTERROGATION',
      title: 'STATE 3 — INTERROGATION',
      desc: 'Probe stabilizes (3s demo / 3m field). Reads ZTS-3002 Modbus RTU.',
      icon: Gauge,
      color: 'purple'
    },
    {
      code: 'RETRACTION',
      title: 'STATE 4 — RETRACTION',
      desc: 'Reverses N20 motor to raise probe until NC Top Limit Switch triggers.',
      icon: ArrowUpCircle,
      color: 'indigo'
    }
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner Control Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white">Autonomous Rover Control Center</h2>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                4-State Sequential Machine • PETG Rack & Pinion • Modbus RS485 Sensing
              </p>
            </div>
          </div>
        </div>

        {/* Simulator Control Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={handleStep}
            disabled={isExecuting || status?.is_estop}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-950/40 flex items-center space-x-2 transition-all"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Step State ({status?.rover_state || 'TRANSIT'})</span>
          </button>

          <button
            onClick={handleReset}
            disabled={isExecuting}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-sm flex items-center space-x-2 transition-all"
          >
            <RotateCcw className="w-4 h-4 text-slate-400" />
            <span>Reset</span>
          </button>

          <button
            onClick={handleEstop}
            disabled={isExecuting}
            className="px-4 py-2.5 rounded-xl bg-rose-600/90 hover:bg-rose-500 text-white font-bold text-sm shadow-lg shadow-rose-950/50 flex items-center space-x-2 transition-all"
          >
            <OctagonAlert className="w-4 h-4" />
            <span>E-STOP</span>
          </button>
        </div>
      </div>

      {/* Emergency Stop Alert Banner */}
      {status?.is_estop && (
        <div className="p-4 rounded-xl bg-rose-500/10 border-2 border-rose-500/40 text-rose-300 flex items-center justify-between animate-pulse">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-6 h-6 text-rose-400" />
            <div>
              <h4 className="font-bold text-sm">EMERGENCY STOP TRIGGERED</h4>
              <p className="text-xs text-rose-300/80">
                Rover motors locked to ZERO PWM. Actuator safely halted. Press 'Reset' to resume operation.
              </p>
            </div>
          </div>
          <button
            onClick={handleReset}
            className="px-3 py-1.5 rounded-lg bg-rose-500 text-white font-bold text-xs hover:bg-rose-400"
          >
            Reset Rover
          </button>
        </div>
      )}

      {/* 4-State Sequential Diagram */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {states.map((st, i) => {
          const Icon = st.icon;
          const isActive = status?.rover_state === st.code;
          return (
            <div
              key={st.code}
              className={`p-5 rounded-2xl border transition-all duration-300 relative overflow-hidden ${
                isActive
                  ? 'bg-slate-900 border-emerald-500/60 shadow-xl shadow-emerald-950/40 ring-1 ring-emerald-500/30'
                  : 'bg-slate-900/40 border-slate-800/80'
              }`}
            >
              {isActive && (
                <div className="absolute top-0 right-0 left-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-400" />
              )}
              
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono font-bold text-slate-500">0{i+1}</span>
                <div className={`p-2 rounded-xl ${isActive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>

              <h3 className={`font-bold text-sm mb-1 ${isActive ? 'text-emerald-400' : 'text-slate-200'}`}>
                {st.title}
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">{st.desc}</p>

              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono">
                <span className="text-slate-500">State:</span>
                <StatusBadge status={isActive ? st.code : 'WAITING'} type="rover" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Hardware Specifications & ESP32 Pinouts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* ESP32 Pinout Card */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-emerald-400" />
              <h3 className="font-bold text-white text-base">ESP32 Microcontroller Hardware Pinouts</h3>
            </div>
            <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2.5 py-1 rounded-md">
              Hardware UART2 @ 9600 Baud
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-emerald-400 font-bold border-b border-slate-800/60 pb-1.5">
                <span>4WD Skid-Steer Drivers</span>
                <span>L298N H-Bridge</span>
              </div>
              <div className="space-y-1 text-slate-300">
                <div className="flex justify-between"><span>Left PWM (ENA):</span><strong className="text-emerald-400">Pin 33</strong></div>
                <div className="flex justify-between"><span>Left IN1 / IN2:</span><strong className="text-slate-200">Pin 25 / 26</strong></div>
                <div className="flex justify-between"><span>Right PWM (ENB):</span><strong className="text-emerald-400">Pin 32</strong></div>
                <div className="flex justify-between"><span>Right IN3 / IN4:</span><strong className="text-slate-200">Pin 27 / 14</strong></div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-amber-400 font-bold border-b border-slate-800/60 pb-1.5">
                <span>Rack Probing Actuator</span>
                <span>Micro N20 Gear Motor</span>
              </div>
              <div className="space-y-1 text-slate-300">
                <div className="flex justify-between"><span>Actuator IN1 / IN2:</span><strong className="text-amber-400">Pin 22 / 21</strong></div>
                <div className="flex justify-between"><span>Speed PWM Resolution:</span><strong className="text-slate-200">90 (8-bit)</strong></div>
                <div className="flex justify-between">
                  <span>NC Top Limit Switch:</span>
                  <strong className={status?.actuator.top_limit_switch ? 'text-emerald-400' : 'text-slate-500'}>
                    Pin 19 ({status?.actuator.top_limit_switch ? 'TRIGGERED' : 'OPEN'})
                  </strong>
                </div>
                <div className="flex justify-between">
                  <span>NC Bottom Limit Switch:</span>
                  <strong className={status?.actuator.bottom_limit_switch ? 'text-emerald-400' : 'text-slate-500'}>
                    Pin 18 ({status?.actuator.bottom_limit_switch ? 'TRIGGERED' : 'OPEN'})
                  </strong>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-purple-400 font-bold border-b border-slate-800/60 pb-1.5">
                <span>RS485 Modbus RTU</span>
                <span>MAX485 Chipset</span>
              </div>
              <div className="space-y-1 text-slate-300">
                <div className="flex justify-between"><span>UART TX2:</span><strong className="text-purple-400">Pin 17</strong></div>
                <div className="flex justify-between"><span>UART RX2:</span><strong className="text-purple-400">Pin 16</strong></div>
                <div className="flex justify-between"><span>Sensor Model:</span><strong className="text-slate-200">ZTS-3002 7-in-1</strong></div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-sky-400 font-bold border-b border-slate-800/60 pb-1.5">
                <span>GPS Receiver</span>
                <span>BN-880 NMEA</span>
              </div>
              <div className="space-y-1 text-slate-300">
                <div className="flex justify-between"><span>Active Waypoint:</span><strong className="text-sky-400">{status?.current_waypoint.id || 'WP-04'}</strong></div>
                <div className="flex justify-between"><span>Latitude:</span><strong className="text-slate-200">{status?.gps.latitude.toFixed(6)}°</strong></div>
                <div className="flex justify-between"><span>Longitude:</span><strong className="text-slate-200">{status?.gps.longitude.toFixed(6)}°</strong></div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Interrogated Telemetry Reading */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-white text-base">Modbus RTU Sensor Output</h3>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                Live Interrogation
              </span>
            </div>

            {status?.latest_telemetry ? (
              <div className="space-y-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex justify-between items-center">
                  <span className="text-slate-400">Sample ID:</span>
                  <span className="font-bold text-emerald-400">{status.latest_telemetry.sample_id}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300">
                  <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">SOIL PH</span>
                    <strong className="text-sm text-emerald-400">{status.latest_telemetry.ph} pH</strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">CONDUCTIVITY</span>
                    <strong className="text-sm text-cyan-400">{status.latest_telemetry.ec} dS/m</strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">MOISTURE</span>
                    <strong className="text-sm text-sky-400">{status.latest_telemetry.moisture}%</strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">NITROGEN (N)</span>
                    <strong className="text-sm text-emerald-300">{status.latest_telemetry.nitrogen} kg/ha</strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">PHOSPHORUS (P)</span>
                    <strong className="text-sm text-teal-300">{status.latest_telemetry.phosphorus} kg/ha</strong>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-800">
                    <span className="text-slate-500 block text-[10px]">POTASSIUM (K)</span>
                    <strong className="text-sm text-indigo-300">{status.latest_telemetry.potassium} kg/ha</strong>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 text-xs">
                No active probe telemetry yet. Press 'Step State' to lower rack and interrogate sensor.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Hardware Status:</span>
            <span className="text-emerald-400 font-bold flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Limit Switches Healthy</span>
            </span>
          </div>
        </div>

      </div>
    </div>
  );
};
