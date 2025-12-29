import React from 'react';

interface WireComponentProps {
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

const WireComponent: React.FC<WireComponentProps> = ({ fromX, fromY, toX, toY }) => {
  // Create a smooth curve for the wire
  const midX = (fromX + toX) / 2;
  const path = `M ${fromX} ${fromY} Q ${midX} ${fromY} ${toX} ${toY}`;

  return (
    <g>
      {/* Wire line */}
      <path
        d={path}
        fill="none"
        stroke="#2196F3"
        strokeWidth="3"
        markerEnd="url(#arrowhead)"
      />
      
      {/* Arrow marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3, 0 6"
            fill="#2196F3"
          />
        </marker>
      </defs>
    </g>
  );
};

export default WireComponent;


