import React, { useRef, useEffect, useState } from 'react';
import type { SpatialPredictionPoint } from '../types/telemetry';

interface HeatmapCanvasProps {
  predictions: SpatialPredictionPoint[];
  parameter: 'predicted_n_deficiency' | 'predicted_p_deficiency' | 'predicted_k_deficiency' | 'predicted_ph' | 'predicted_ec';
  modelType: string;
}

export const HeatmapCanvas: React.FC<HeatmapCanvasProps> = ({ predictions, parameter, modelType }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<SpatialPredictionPoint | null>(null);

  // Compute color based on normalized value
  const getColorForVal = (val: number, param: string) => {
    let norm = 0;
    if (param === 'predicted_n_deficiency') norm = Math.min(1, Math.max(0, val / 150));
    else if (param === 'predicted_p_deficiency') norm = Math.min(1, Math.max(0, val / 80));
    else if (param === 'predicted_k_deficiency') norm = Math.min(1, Math.max(0, val / 90));
    else if (param === 'predicted_ph') norm = Math.min(1, Math.max(0, (val - 5.5) / 3.0));
    else if (param === 'predicted_ec') norm = Math.min(1, Math.max(0, val / 2.0));

    // Green (low deficiency / good) to Red (high deficiency / critical)
    if (param.includes('deficiency')) {
      const r = Math.floor(255 * norm);
      const g = Math.floor(255 * (1 - norm));
      const b = 50;
      return `rgb(${r}, ${g}, ${b})`;
    } else if (param === 'predicted_ph') {
      if (val < 6.5) return `rgb(59, 130, 246)`;
      if (val <= 7.5) return `rgb(34, 197, 94)`;
      return `rgb(239, 68, 68)`;
    } else {
      const r = Math.floor(245 * norm);
      const g = Math.floor(158 * norm);
      const b = Math.floor(212 * (1 - norm));
      return `rgb(${r}, ${g}, ${b})`;
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !predictions || predictions.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const maxX = Math.max(...predictions.map(p => p.grid_x), 24);
    const maxY = Math.max(...predictions.map(p => p.grid_y), 24);

    const cellWidth = width / (maxX + 1);
    const cellHeight = height / (maxY + 1);

    predictions.forEach(p => {
      const val = p[parameter];
      ctx.fillStyle = getColorForVal(val, parameter);
      ctx.fillRect(p.grid_x * cellWidth, (maxY - p.grid_y) * cellHeight, cellWidth + 0.5, cellHeight + 0.5);
    });

    ctx.strokeStyle = 'rgba(15, 23, 42, 0.2)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= width; x += cellWidth * 5) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y <= height; y += cellHeight * 5) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

  }, [predictions, parameter, modelType]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !predictions.length) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const maxX = Math.max(...predictions.map(p => p.grid_x), 24);
    const maxY = Math.max(...predictions.map(p => p.grid_y), 24);

    const gx = Math.floor(mouseX / (rect.width / (maxX + 1)));
    const gy = maxY - Math.floor(mouseY / (rect.height / (maxY + 1)));

    const found = predictions.find(p => p.grid_x === gx && p.grid_y === gy);
    setHoveredPoint(found || null);
  };

  const getParamLabel = () => {
    switch (parameter) {
      case 'predicted_n_deficiency': return 'Nitrogen (N) Deficiency (kg/ha)';
      case 'predicted_p_deficiency': return 'Phosphorus (P) Deficiency (kg/ha)';
      case 'predicted_k_deficiency': return 'Potassium (K) Deficiency (kg/ha)';
      case 'predicted_ph': return 'Predicted Soil pH';
      case 'predicted_ec': return 'Predicted Electrical Conductivity (dS/m)';
    }
  };

  return (
    <div className="flex flex-col items-center w-full">
      <div className="w-full flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-slate-200">{getParamLabel()}</h4>
        <span className="text-xs font-mono bg-slate-800 text-emerald-400 px-2 py-0.5 rounded">
          Model: {modelType}
        </span>
      </div>

      <div className="relative w-full aspect-square max-w-lg rounded-xl overflow-hidden border border-slate-700/80 shadow-2xl bg-slate-950">
        <canvas
          ref={canvasRef}
          width={500}
          height={500}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoveredPoint(null)}
          className="w-full h-full cursor-crosshair block"
        />

        {hoveredPoint && (
          <div className="absolute bottom-3 left-3 right-3 bg-slate-900/95 border border-slate-700 p-3 rounded-lg text-xs font-mono shadow-xl backdrop-blur-md">
            <div className="flex items-center justify-between font-bold text-emerald-400 mb-1">
              <span>Grid ({hoveredPoint.grid_x}, {hoveredPoint.grid_y})</span>
              <span>Lat: {hoveredPoint.latitude} | Lon: {hoveredPoint.longitude}</span>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-slate-300">
              <div>N Deficit: <strong className="text-white">{hoveredPoint.predicted_n_deficiency} kg/ha</strong></div>
              <div>P Deficit: <strong className="text-white">{hoveredPoint.predicted_p_deficiency} kg/ha</strong></div>
              <div>K Deficit: <strong className="text-white">{hoveredPoint.predicted_k_deficiency} kg/ha</strong></div>
              <div>pH: <strong className="text-white">{hoveredPoint.predicted_ph}</strong> | EC: <strong className="text-white">{hoveredPoint.predicted_ec} dS/m</strong></div>
            </div>
          </div>
        )}
      </div>

      <div className="w-full max-w-lg mt-3 flex items-center justify-between text-xs text-slate-400">
        <span>Low Deficit / Optimal</span>
        <div className="h-2.5 flex-1 mx-3 rounded-full bg-gradient-to-r from-emerald-500 via-yellow-500 to-rose-500 shadow-inner" />
        <span>Severe Deficit / Critical</span>
      </div>
    </div>
  );
};
