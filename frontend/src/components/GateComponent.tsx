import React, { useState, useRef } from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { Gate } from './VisualCircuitEditor';

interface GateComponentProps {
  gate: Gate;
  selected: boolean;
  onMove: (gateId: string, x: number, y: number) => void;
  onDelete: (gateId: string) => void;
  onSelect: (gateId: string) => void;
}

const GateComponent: React.FC<GateComponentProps> = ({
  gate,
  selected,
  onMove,
  onDelete,
  onSelect,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const gateRef = useRef<SVGForeignObjectElement>(null);

  const gateColors: { [key: string]: string } = {
    H: '#4CAF50',
    X: '#F44336',
    Y: '#FF9800',
    Z: '#2196F3',
    CNOT: '#9C27B0',
    CZ: '#E91E63',
    SWAP: '#00BCD4',
    RX: '#FF5722',
    RY: '#795548',
    RZ: '#607D8B',
    S: '#3F51B5',
    T: '#009688',
  };

  const gateColor = gateColors[gate.type] || '#757575';
  const gateWidth = gate.type === 'CNOT' || gate.type === 'CZ' ? 80 : 60;
  const gateHeight = 50;

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only left mouse button
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

    // Snap to qubit line
    const qubitY = 100 + gate.qubit * 80;
    const newY = qubitY - gateHeight / 2;
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
            backgroundColor: gateColor,
            border: selected ? '3px solid #FFD700' : '2px solid #333',
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.3)' : '0 2px 4px rgba(0,0,0,0.2)',
            transition: 'all 0.2s',
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              transform: 'scale(1.05)',
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
            {gate.type}
            {gate.params && gate.params.length > 0 && (
              <Typography component="span" variant="caption" sx={{ display: 'block', fontSize: '0.7em' }}>
                {gate.params.map((p: any) => typeof p === 'number' ? p.toFixed(2) : p).join(', ')}
              </Typography>
            )}
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

export default GateComponent;


