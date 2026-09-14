import React, { useRef, useState, useEffect } from 'react';
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion';
import './Dock.css';

interface DockItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  onClick?: () => void;
  href?: string;
}

interface DockProps {
  items: DockItem[];
  activeId?: string;
  className?: string;
  baseItemSize?: number;
  magnification?: number;
  distance?: number;
  panelHeight?: number;
}

export const Dock: React.FC<DockProps> = ({
  items,
  activeId,
  className = '',
  baseItemSize = 50,
  magnification = 70,
  distance = 150,
  panelHeight = 68
}) => {
  const mouseX = useMotionValue(-Infinity);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(() => 
    typeof window !== 'undefined' ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return (
    <motion.div
      className={`dock-container ${className}`}
      onMouseMove={(e) => mouseX.set(e.pageX)}
      onMouseLeave={() => mouseX.set(-Infinity)}
      style={{ height: panelHeight }}
    >
      <div className="dock-panel">
        {items.map((item) => {
          const isActive = activeId === item.id;
          return (
            <DockIcon
              key={item.id}
              item={item}
              mouseX={mouseX}
              isActive={isActive}
              isHovered={hoveredId === item.id}
              onHoverStart={() => setHoveredId(item.id)}
              onHoverEnd={() => setHoveredId(null)}
              baseItemSize={baseItemSize}
              magnification={magnification}
              distance={distance}
              prefersReducedMotion={prefersReducedMotion}
            />
          );
        })}
      </div>
    </motion.div>
  );
};

interface DockIconProps {
  item: DockItem;
  mouseX: any;
  isActive: boolean;
  isHovered: boolean;
  onHoverStart: () => void;
  onHoverEnd: () => void;
  baseItemSize: number;
  magnification: number;
  distance: number;
  prefersReducedMotion: boolean;
}

const DockIcon: React.FC<DockIconProps> = ({
  item,
  mouseX,
  isActive,
  isHovered,
  onHoverStart,
  onHoverEnd,
  baseItemSize,
  magnification,
  distance,
  prefersReducedMotion
}) => {
  const ref = useRef<HTMLButtonElement | HTMLAnchorElement>(null);

  const distanceCalc = useTransform(mouseX, (val: number) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { x: 0, width: 0 };
    return val - bounds.x - bounds.width / 2;
  });

  const widthSync = useTransform(distanceCalc, [-distance, 0, distance], [baseItemSize, magnification, baseItemSize]);

  const width = useSpring(widthSync, { mass: 0.1, stiffness: 150, damping: 12 });

  const handleClick = (e: React.MouseEvent) => {
    if (item.onClick) {
      e.preventDefault();
      item.onClick();
    }
  };

  const Component = item.href && !item.onClick ? 'a' : 'button';
  const props = item.href && !item.onClick ? { href: item.href } : { onClick: handleClick };

  const content = (
    <motion.div
      className={`dock-icon-inner ${isActive ? 'active' : ''}`}
      whileHover={{ y: -5 }}
      whileTap={{ scale: 0.95 }}
    >
      {item.icon}
      
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 2, scale: 0.8 }}
            transition={{ duration: 0.15 }}
            className="dock-tooltip"
          >
            {item.label}
          </motion.div>
        )}
      </AnimatePresence>
      
      {isActive && (
        <motion.div 
          layoutId="active-indicator"
          className="dock-active-indicator"
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      )}
    </motion.div>
  );

  return React.createElement(
    Component as any,
    {
      ...props,
      ref,
      className: `dock-item-wrapper ${isActive ? 'active-item' : ''}`,
      style: { 
        width: prefersReducedMotion ? baseItemSize : width,
        height: prefersReducedMotion ? baseItemSize : width
      },
      onMouseEnter: onHoverStart,
      onMouseLeave: onHoverEnd,
      onFocus: onHoverStart,
      onBlur: onHoverEnd,
    },
    content
  );
};
