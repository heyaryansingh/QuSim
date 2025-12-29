import React, { useState, useRef } from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { Gate } from './VisualCircuitEditor';

interface CNOTGateComponentProps {
  gate: Gate;
  selected: boolean;
  onMove: (gateId: string, x: number, y: number) => void;
  onDelete: (gateId: string) => void;
  onSelect: (gateId: string) => void;
  controlQubit: number;
  targetQubit: number;
}

const CNOTGateComponent: React.FC<CNOTGateComponentProps> = ({
  gate,
  selected,
  onMove,
  onDelete,
  onSelect,
  controlQubit,
  targetQubit,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const gateRef = useRef<SVGForeignObjectElement>(null);

  const gateWidth = 60;
  const gateHeight = 50;
  const controlY = 100 + controlQubit * 80;
  const targetY = 100 + targetQubit * 80;
  const centerY = (controlY + targetY) / 2;

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    e.preventDefault();
    setIsDragging(true);
    const rect = gateRef.current?.getBoundingClientRect();
    if (rect) {
      setDragOffset({
        x: e.clientX - rect.left - gateWidth / 2,
        y: e.clientY - rect.top - gateHeight / 2,
      });
    }
    onSelect(gate.id);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    e.preventDefault();
    
    const svg = gateRef.current?.ownerSVGElement;
    if (!svg) return;

    const point = svg.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    const svgPoint = point.matrixTransform(svg.getScreenCTM()?.inverse());

    // Snap to target qubit line
    const newY = targetY - gateHeight / 2;
    const newX = Math.max(50, svgPoint.x - dragOffset.x);

    onMove(gate.id, newX, newY);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(gate.id);
  };

  return (
    <g>
      {/* Control qubit line */}
      <line
        x1={gate.x + gateWidth / 2}
        y1={controlY}
        x2={gate.x + gateWidth / 2}
        y2={targetY}
        stroke="#9C27B0"
        strokeWidth="3"
      />
      
      {/* Control qubit dot */}
      <circle
        cx={gate.x + gateWidth / 2}
        cy={controlY}
        r="8"
        fill="#9C27B0"
        stroke="white"
        strokeWidth="2"
      />

      {/* Target gate */}
      <foreignObject
        ref={gateRef}
        x={gate.x}
        y={gate.y}
        width={gateWidth}
        height={gateHeight}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <Box
          sx={{
            width: '100%',
            height: '100%',
            backgroundColor: '#9C27B0',
            border: selected ? '3px solid #FFD700' : '2px solid #333',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.3)' : '0 2px 4px rgba(0,0,0,0.2)',
            transition: 'all 0.2s',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              transform: 'scale(1.1)',
            },
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: 'white',
              fontWeight: 'bold',
              textAlign: 'center',
              userSelect: 'none',
            }}
          >
            ⊕
          </Typography>
          
          {selected && (
            <IconButton
              size="small"
              onClick={handleDelete}
              sx={{
                position: 'absolute',
                top: -8,
                right: -8,
                backgroundColor: 'red',
                color: 'white',
                width: 24,
                height: 24,
                '&:hover': { backgroundColor: 'darkred' },
              }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          )}

          {/* Input port */}
          <Box
            sx={{
              position: 'absolute',
              left: -6,
              top: '50%',
              transform: 'translateY(-50%)',
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: '#333',
              border: '2px solid white',
            }}
          />

          {/* Output port */}
          <Box
            sx={{
              position: 'absolute',
              right: -6,
              top: '50%',
              transform: 'translateY(-50%)',
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: '#333',
              border: '2px solid white',
            }}
          />
        </Box>
      </foreignObject>
    </g>
  );
};

export default CNOTGateComponent;


