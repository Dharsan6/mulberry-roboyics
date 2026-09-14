import React, { useEffect, useRef, useState } from 'react';
import './DotField.css';

interface DotFieldProps {
  className?: string;
  gradientFrom?: string;
  gradientTo?: string;
  glowColor?: string;
  dotSize?: number;
  spacing?: number;
}

export const DotField: React.FC<DotFieldProps> = ({
  className = '',
  gradientFrom = 'rgba(16, 185, 129, 0.4)', // emerald-500 equivalent
  gradientTo = 'rgba(6, 182, 212, 0.25)',  // cyan-500 equivalent
  glowColor = '#0f172a',                   // slate-900 equivalent
  dotSize = 1.5,
  spacing = 24
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState({ x: -1000, y: -1000 });

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = 0;
    let height = 0;

    const resize = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      canvas.width = width;
      canvas.height = height;
    };

    window.addEventListener('resize', resize);
    resize();

    // Mouse movement
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      setMousePos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    };
    
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!prefersReducedMotion) {
      window.addEventListener('mousemove', handleMouseMove);
    }

    let time = 0;
    
    const draw = () => {
      time += 0.01;
      ctx.clearRect(0, 0, width, height);

      // Create gradient base for the dots
      const gradient = ctx.createLinearGradient(0, 0, width, height);
      gradient.addColorStop(0, gradientFrom);
      gradient.addColorStop(1, gradientTo);

      ctx.fillStyle = gradient;

      const cols = Math.floor(width / spacing);
      const rows = Math.floor(height / spacing);

      for (let i = 0; i <= cols; i++) {
        for (let j = 0; j <= rows; j++) {
          const cx = i * spacing;
          const cy = j * spacing;

          // Wave effect
          const waveX = Math.sin(time + j * 0.1) * 2;
          const waveY = Math.cos(time + i * 0.1) * 2;
          
          let x = cx + waveX;
          let y = cy + waveY;

          // Mouse interaction (repel / glow)
          const dx = mousePos.x - x;
          const dy = mousePos.y - y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const maxDist = 150;
          
          let currentSize = dotSize;
          
          if (!prefersReducedMotion && dist < maxDist) {
            const force = (maxDist - dist) / maxDist;
            x -= dx * force * 0.1;
            y -= dy * force * 0.1;
            
            // Sparkle effect
            if (Math.random() > 0.95) {
              currentSize = dotSize * (1 + force * 2);
              
              // Glow
              ctx.shadowBlur = 10;
              ctx.shadowColor = glowColor;
            } else {
              currentSize = dotSize * (1 + force);
              ctx.shadowBlur = 0;
            }
          } else {
            ctx.shadowBlur = 0;
          }

          ctx.beginPath();
          ctx.arc(x, y, currentSize, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [mousePos.x, mousePos.y, gradientFrom, gradientTo, glowColor, dotSize, spacing]);

  return (
    <div ref={containerRef} className={`dot-field-container ${className}`}>
      <canvas ref={canvasRef} className="dot-field-canvas" />
    </div>
  );
};
