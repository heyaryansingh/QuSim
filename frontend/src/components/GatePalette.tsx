import React from 'react';
import { Box, Paper, Typography, Button, Grid } from '@mui/material';
import { Gate } from './VisualCircuitEditor';

interface GatePaletteProps {
  onGateAdd: (gateType: string, qubit: number) => void;
  numQubits: number;
}

const GatePalette: React.FC<GatePaletteProps> = ({ onGateAdd, numQubits }) => {
  const gateTypes = [
    { name: 'H', label: 'Hadamard', color: '#4CAF50' },
    { name: 'X', label: 'Pauli-X', color: '#F44336' },
    { name: 'Y', label: 'Pauli-Y', color: '#FF9800' },
    { name: 'Z', label: 'Pauli-Z', color: '#2196F3' },
    { name: 'S', label: 'Phase', color: '#3F51B5' },
    { name: 'T', label: 'T Gate', color: '#009688' },
    { name: 'CNOT', label: 'CNOT', color: '#9C27B0' },
    { name: 'CZ', label: 'CZ', color: '#E91E63' },
    { name: 'SWAP', label: 'SWAP', color: '#00BCD4' },
    { name: 'RX', label: 'RX(θ)', color: '#FF5722' },
    { name: 'RY', label: 'RY(θ)', color: '#795548' },
    { name: 'RZ', label: 'RZ(θ)', color: '#607D8B' },
  ];

  const handleGateClick = (gateType: string) => {
    // For single-qubit gates, add to qubit 0 by default
    // For two-qubit gates, user will need to specify
    if (gateType === 'CNOT' || gateType === 'CZ' || gateType === 'SWAP') {
      // Two-qubit gates need special handling
      onGateAdd(gateType, 0);
    } else {
      onGateAdd(gateType, 0);
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Gate Palette
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
        Click a gate to add it to the circuit
      </Typography>
      <Grid container spacing={1}>
        {gateTypes.map((gate) => (
          <Grid item xs={4} sm={3} md={2} key={gate.name}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => handleGateClick(gate.name)}
              sx={{
                backgroundColor: gate.color,
                color: 'white',
                borderColor: gate.color,
                '&:hover': {
                  backgroundColor: gate.color,
                  opacity: 0.8,
                  borderColor: gate.color,
                },
                minHeight: '60px',
                flexDirection: 'column',
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {gate.name}
              </Typography>
              <Typography variant="caption" sx={{ fontSize: '0.7em' }}>
                {gate.label}
              </Typography>
            </Button>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default GatePalette;


