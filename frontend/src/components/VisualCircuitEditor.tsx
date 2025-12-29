import React, { useState, useCallback, useRef } from 'react';
import { Box, Paper, Typography, Button, IconButton } from '@mui/material';
import { Delete as DeleteIcon, PlayArrow as PlayIcon } from '@mui/icons-material';
import GateComponent from './GateComponent';
import WireComponent from './WireComponent';

export interface Gate {
  id: string;
  type: string;
  x: number;
  y: number;
  qubit: number;
  params?: any;
}

export interface Wire {
  id: string;
  from: { gateId: string; port: 'output' };
  to: { gateId: string; port: 'input' };
  qubit: number;
}

interface VisualCircuitEditorProps {
  numQubits: number;
  gates: Gate[];
  wires: Wire[];
  onGatesChange: (gates: Gate[]) => void;
  onWiresChange: (wires: Wire[]) => void;
  onExecute: () => void;
}

const VisualCircuitEditor: React.FC<VisualCircuitEditorProps> = ({
  numQubits,
  gates,
  wires,
  onGatesChange,
  onWiresChange,
  onExecute,
}) => {
  const [selectedGate, setSelectedGate] = useState<string | null>(null);
  const [dragging, setDragging] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const handleGateMove = useCallback((gateId: string, newX: number, newY: number) => {
    onGatesChange(
      gates.map((g) => (g.id === gateId ? { ...g, x: newX, y: newY } : g))
    );
  }, [gates, onGatesChange]);

  const handleGateDelete = useCallback((gateId: string) => {
    onGatesChange(gates.filter((g) => g.id !== gateId));
    onWiresChange(wires.filter((w) => w.from.gateId !== gateId && w.to.gateId !== gateId));
  }, [gates, wires, onGatesChange, onWiresChange]);

  const handleGateSelect = useCallback((gateId: string) => {
    setSelectedGate(gateId);
  }, []);

  const qubitLines = Array.from({ length: numQubits }, (_, i) => i);

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '600px', border: '1px solid #ccc', overflow: 'auto' }}>
      <Box sx={{ position: 'absolute', top: 10, right: 10, zIndex: 10 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PlayIcon />}
          onClick={onExecute}
        >
          Execute
        </Button>
      </Box>
      
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        {/* Qubit lines */}
        {qubitLines.map((qubit) => (
          <line
            key={`qubit-${qubit}`}
            x1={50}
            y1={100 + qubit * 80}
            x2="100%"
            y2={100 + qubit * 80}
            stroke="#333"
            strokeWidth="2"
            strokeDasharray="5,5"
          />
        ))}

        {/* Wires between gates */}
        {wires.map((wire) => {
          const fromGate = gates.find((g) => g.id === wire.from.gateId);
          const toGate = gates.find((g) => g.id === wire.to.gateId);
          if (!fromGate || !toGate) return null;

          const yPos = 100 + wire.qubit * 80;
          const gateWidth = fromGate.type === 'CNOT' || fromGate.type === 'CZ' ? 80 : 60;
          const fromX = fromGate.x + gateWidth;
          const toX = toGate.x;

          return (
            <WireComponent
              key={wire.id}
              fromX={fromX}
              fromY={yPos}
              toX={toX}
              toY={yPos}
            />
          );
        })}

        {/* Gate components */}
        {gates.map((gate) => {
          if (gate.type === 'CNOT' || gate.type === 'CZ') {
            // For two-qubit gates, we need to find the connected qubit
            const wire = wires.find((w) => w.from.gateId === gate.id || w.to.gateId === gate.id);
            const otherQubit = wire ? (wire.qubit !== gate.qubit ? wire.qubit : gate.qubit + 1) : gate.qubit + 1;
            
            // Use special CNOT component (simplified - would need separate component)
            return (
              <GateComponent
                key={gate.id}
                gate={gate}
                selected={selectedGate === gate.id}
                onMove={handleGateMove}
                onDelete={handleGateDelete}
                onSelect={handleGateSelect}
              />
            );
          }
          return (
            <GateComponent
              key={gate.id}
              gate={gate}
              selected={selectedGate === gate.id}
              onMove={handleGateMove}
              onDelete={handleGateDelete}
              onSelect={handleGateSelect}
            />
          );
        })}
      </svg>

      {/* Qubit labels */}
      <Box sx={{ position: 'absolute', left: 10, top: 80 }}>
        {qubitLines.map((qubit) => (
          <Typography
            key={qubit}
            variant="caption"
            sx={{
              display: 'block',
              height: '80px',
              lineHeight: '80px',
              fontWeight: 'bold',
            }}
          >
            q[{qubit}]
          </Typography>
        ))}
      </Box>
    </Box>
  );
};

export default VisualCircuitEditor;

