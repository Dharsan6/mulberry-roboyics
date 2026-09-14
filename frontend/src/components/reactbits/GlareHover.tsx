import React, { useRef, useState, useEffect } from 'react';
import './GlareHover.css';

interface GlareHoverProps {
  children: React.ReactNode;
  className?: string;
  glareOpacity?: number;
  glareColor?: string;
  glareSize?: number;
  scale?: number;
}

export const GlareHover: React.FC<GlareHoverProps> = ({
  children,
  className = '',
  glareOpacity = 0.15,
  glareColor = 'rgba(16, 185, 129, 0.5)', // emerald tint default
  glareSize = 250,
  scale = 1.02
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [position, setPosition] = useState({ x: 50, y: 50 });
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(() => 
    typeof window !== 'undefined' ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (prefersReducedMotion || !ref.current) return;
    
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Calculate percentage for glare position (0 to 100)
    const px = (x / rect.width) * 100;
    const py = (y / rect.height) * 100;
    setPosition({ x: px, y: py });

    // Calculate tilt (-1 to 1)
    const tiltX = (y / rect.height) * 2 - 1;
    const tiltY = (x / rect.width) * 2 - 1;
    setTilt({ x: -tiltX * 5, y: tiltY * 5 }); // 5 degrees max tilt
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setTilt({ x: 0, y: 0 });
    setPosition({ x: 50, y: 50 });
  };

  const transformStyle = isHovered && !prefersReducedMotion
    ? `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale(${scale})`
    : 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';

  return (
    <div
      ref={ref}
      className={`glare-hover-container ${className}`}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: transformStyle,
        transition: isHovered ? 'none' : 'transform 0.5s ease-out'
      }}
    >
      {children}
      
      {/* Glare layer */}
      {!prefersReducedMotion && (
        <div
          className="glare-hover-overlay"
          style={{
            background: `radial-gradient(circle ${glareSize}px at ${position.x}% ${position.y}%, ${glareColor}, transparent)`,
            opacity: isHovered ? glareOpacity : 0
          }}
        />
      )}
    </div>
  );
};
