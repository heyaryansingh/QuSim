import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js';
import { Box, Typography, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

interface BlochSphereProps {
  blochData?: {
    vector: [number, number, number];
    qubit: number;
  };
  numQubits: number;
}

const BlochSphere: React.FC<BlochSphereProps> = ({ blochData, numQubits }) => {
  const plotRef = useRef<HTMLDivElement>(null);
  const [selectedQubit, setSelectedQubit] = React.useState(0);

  useEffect(() => {
    if (!plotRef.current || !blochData || !blochData.vector) return;

    const vec = blochData.vector;
    if (!Array.isArray(vec) || vec.length !== 3) return;
    
    // Create sphere surface
    const u = Array.from({ length: 50 }, (_, i) => (i / 50) * 2 * Math.PI);
    const v = Array.from({ length: 50 }, (_, i) => (i / 50) * Math.PI);
    
    const xSphere: number[][] = [];
    const ySphere: number[][] = [];
    const zSphere: number[][] = [];
    
    for (let i = 0; i < u.length; i++) {
      xSphere[i] = [];
      ySphere[i] = [];
      zSphere[i] = [];
      for (let j = 0; j < v.length; j++) {
        xSphere[i][j] = Math.cos(u[i]) * Math.sin(v[j]);
        ySphere[i][j] = Math.sin(u[i]) * Math.sin(v[j]);
        zSphere[i][j] = Math.cos(v[j]);
      }
    }

    const data: Plotly.Data[] = [
      {
        type: 'surface',
        x: xSphere,
        y: ySphere,
        z: zSphere,
        opacity: 0.3,
        colorscale: 'Blues',
        showscale: false,
      },
      {
        type: 'scatter3d',
        x: [0, vec[0]],
        y: [0, vec[1]],
        z: [0, vec[2]],
        mode: 'lines+markers',
        line: { color: 'red', width: 5 },
        marker: { size: 5, color: 'red' },
        name: 'Bloch Vector',
      },
      {
        type: 'scatter3d',
        x: [-1.2, 1.2],
        y: [0, 0],
        z: [0, 0],
        mode: 'lines',
        line: { color: 'gray', width: 2, dash: 'dash' },
        showlegend: false,
      },
      {
        type: 'scatter3d',
        x: [0, 0],
        y: [-1.2, 1.2],
        z: [0, 0],
        mode: 'lines',
        line: { color: 'gray', width: 2, dash: 'dash' },
        showlegend: false,
      },
      {
        type: 'scatter3d',
        x: [0, 0],
        y: [0, 0],
        z: [-1.2, 1.2],
        mode: 'lines',
        line: { color: 'gray', width: 2, dash: 'dash' },
        showlegend: false,
      },
      {
        type: 'scatter3d',
        x: [1.3, 0, 0],
        y: [0, 1.3, 0],
        z: [0, 0, 1.3],
        mode: 'text',
        text: ['X', 'Y', 'Z'],
        textposition: 'middle center',
        showlegend: false,
      },
    ];

    const layout: Partial<Plotly.Layout> = {
      title: `Bloch Sphere - Qubit ${blochData.qubit}`,
      scene: {
        xaxis: { range: [-1.5, 1.5], title: 'X' },
        yaxis: { range: [-1.5, 1.5], title: 'Y' },
        zaxis: { range: [-1.5, 1.5], title: 'Z' },
        aspectmode: 'cube',
      },
      width: 600,
      height: 600,
      margin: { l: 0, r: 0, t: 50, b: 0 },
    };

    Plotly.newPlot(plotRef.current, data, layout, { responsive: true });

    return () => {
      if (plotRef.current) {
        Plotly.purge(plotRef.current);
      }
    };
  }, [blochData]);

  if (!blochData) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Execute a circuit to see Bloch sphere visualization
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <FormControl sx={{ mb: 2, minWidth: 150 }}>
        <InputLabel>Qubit</InputLabel>
        <Select
          value={selectedQubit}
          onChange={(e) => setSelectedQubit(e.target.value as number)}
          label="Qubit"
        >
          {Array.from({ length: numQubits }, (_, i) => (
            <MenuItem key={i} value={i}>
              Qubit {i}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <div ref={plotRef} style={{ width: '100%', height: '600px' }} />
    </Box>
  );
};

export default BlochSphere;

