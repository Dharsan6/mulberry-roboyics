import React, { useRef, useEffect, useState } from 'react';
import { Renderer, Camera, Transform, Plane, Program, Mesh } from 'ogl';
import type { HTMLMotionProps } from 'framer-motion';
import { motion } from 'framer-motion';
import './SpecularButton.css';

interface SpecularButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode;
  lineColor?: string;
  baseColor?: string;
  intensity?: number;
  speed?: number;
  followMouse?: boolean;
  radius?: number;
  className?: string;
}

export const SpecularButton: React.FC<SpecularButtonProps> = ({
  children,
  lineColor = '#34d399',
  baseColor = '#0f172a',
  intensity = 0.8,
  speed = 0.4,
  followMouse = true,
  radius = 12,
  className = '',
  ...props
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const mousePos = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 });

  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return;

    const canvas = canvasRef.current;
    const renderer = new Renderer({ canvas, alpha: true, dpr: window.devicePixelRatio, antialias: true });
    const gl = renderer.gl;

    const camera = new Camera(gl, { near: 0.1, far: 100 });
    camera.position.z = 1;

    const scene = new Transform();

    // Parse colors to RGB vectors
    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? [
        parseInt(result[1], 16) / 255,
        parseInt(result[2], 16) / 255,
        parseInt(result[3], 16) / 255
      ] : [1, 1, 1];
    };

    const program = new Program(gl, {
      vertex: `
        attribute vec2 uv;
        attribute vec2 position;
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = vec4(position, 0, 1);
        }
      `,
      fragment: `
        precision highp float;
        uniform float uTime;
        uniform vec2 uResolution;
        uniform vec2 uMouse;
        uniform vec3 uLineColor;
        uniform vec3 uBaseColor;
        uniform float uIntensity;
        varying vec2 vUv;
        
        void main() {
            vec2 st = gl_FragCoord.xy / uResolution.xy;
            float aspect = uResolution.x / uResolution.y;
            st.x *= aspect;
            vec2 mouse = uMouse;
            mouse.x *= aspect;

            // Simple edge glow distance
            float dist = distance(st, mouse);
            float glow = smoothstep(0.5, 0.0, dist) * uIntensity;
            
            // Subtle wave based on time
            float wave = sin(vUv.x * 10.0 + uTime * 2.0) * 0.5 + 0.5;
            
            vec3 color = mix(uBaseColor, uLineColor, glow + (wave * 0.1 * uIntensity));
            
            gl_FragColor = vec4(color, 1.0);
        }
      `,
      uniforms: {
        uTime: { value: 0 },
        uResolution: { value: [1, 1] },
        uMouse: { value: [0.5, 0.5] },
        uLineColor: { value: hexToRgb(lineColor) },
        uBaseColor: { value: hexToRgb(baseColor) },
        uIntensity: { value: intensity }
      },
    });

    const geometry = new Plane(gl, { width: 2, height: 2 });
    const mesh = new Mesh(gl, { geometry, program });
    mesh.setParent(scene);

    let animationId: number;
    let time = 0;

    const resize = () => {
      const { clientWidth, clientHeight } = containerRef.current!;
      renderer.setSize(clientWidth, clientHeight);
      program.uniforms.uResolution.value = [clientWidth, clientHeight];
    };

    const update = () => {
      time += 0.01 * speed;
      program.uniforms.uTime.value = time;

      // Smooth mouse interpolation
      if (followMouse) {
        mousePos.current.x += (mousePos.current.targetX - mousePos.current.x) * 0.1;
        mousePos.current.y += (mousePos.current.targetY - mousePos.current.y) * 0.1;
        program.uniforms.uMouse.value = [mousePos.current.x, mousePos.current.y];
      }

      // Smooth intensity interpolation for hover
      const targetIntensity = isHovered ? intensity : intensity * 0.3;
      program.uniforms.uIntensity.value += (targetIntensity - program.uniforms.uIntensity.value) * 0.1;

      renderer.render({ scene, camera });
      animationId = requestAnimationFrame(update);
    };

    resize();
    window.addEventListener('resize', resize);
    animationId = requestAnimationFrame(update);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
      gl.getExtension('WEBGL_lose_context')?.loseContext();
    };
  }, [lineColor, baseColor, intensity, speed, followMouse, isHovered]);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current || !followMouse) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    // Y is inverted in WebGL
    const y = 1.0 - (e.clientY - rect.top) / rect.height;
    mousePos.current.targetX = x;
    mousePos.current.targetY = y;
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    // Center the glow when not hovering
    mousePos.current.targetX = 0.5;
    mousePos.current.targetY = 0.5;
  };

  return (
    <motion.button
      {...props}
      className={`specular-button ${className}`}
      style={{ borderRadius: radius }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div 
        ref={containerRef}
        className="specular-button-bg-container"
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={handleMouseLeave}
        style={{ borderRadius: radius }}
      >
        <canvas ref={canvasRef} className="specular-button-canvas" />
      </div>
      
      {/* Glossy overlay to give physical feel */}
      <div className="specular-button-gloss" style={{ borderRadius: radius }} />
      
      {/* Content */}
      <span className="specular-button-content">
        {children}
      </span>
    </motion.button>
  );
};
