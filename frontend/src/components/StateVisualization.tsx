import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js';
import { Box, Typography, Tabs, Tab } from '@mui/material';

interface StateVisualizationProps {
  stateData?: {
    amplitudes?: number[];
    phases?: number[];
    probabilities?: number[];
    basisStates?: string[];
  };
}

const StateVisualization: React.FC<StateVisualizationProps> = ({ stateData }) => {
  const amplitudeRef = useRef<HTMLDivElement>(null);
  const phaseRef = useRef<HTMLDivElement>(null);
  const probabilityRef = useRef<HTMLDivElement>(null);
  const [tabValue, setTabValue] = React.useState(0);

  useEffect(() => {
    if (!stateData) return;

    // Amplitude plot
    if (amplitudeRef.current && stateData.amplitudes && stateData.basisStates) {
      const data: Plotly.Data[] = [
        {
          type: 'bar',
          x: stateData.basisStates,
          y: stateData.amplitudes,
          marker: { color: 'steelblue' },
        },
      ];

      const layout: Partial<Plotly.Layout> = {
        title: 'State Amplitudes',
        xaxis: { title: 'Basis State' },
        yaxis: { title: 'Amplitude' },
        height: 400,
      };

      Plotly.newPlot(amplitudeRef.current, data, layout, { responsive: true });
    }

    // Phase plot
    if (phaseRef.current && stateData.phases && stateData.basisStates) {
      const data: Plotly.Data[] = [
        {
          type: 'bar',
          x: stateData.basisStates,
          y: stateData.phases,
          marker: { color: 'orange' },
        },
      ];

      const layout: Partial<Plotly.Layout> = {
        title: 'State Phases',
        xaxis: { title: 'Basis State' },
        yaxis: { title: 'Phase (radians)' },
        height: 400,
      };

      Plotly.newPlot(phaseRef.current, data, layout, { responsive: true });
    }

    // Probability plot
    if (probabilityRef.current && stateData.probabilities && stateData.basisStates) {
      const data: Plotly.Data[] = [
        {
          type: 'bar',
          x: stateData.basisStates,
          y: stateData.probabilities,
          marker: { color: 'green' },
        },
      ];

      const layout: Partial<Plotly.Layout> = {
        title: 'Measurement Probabilities',
        xaxis: { title: 'Basis State' },
        yaxis: { title: 'Probability' },
        height: 400,
      };

      Plotly.newPlot(probabilityRef.current, data, layout, { responsive: true });
    }

    return () => {
      [amplitudeRef.current, phaseRef.current, probabilityRef.current].forEach((ref) => {
        if (ref) Plotly.purge(ref);
      });
    };
  }, [stateData, tabValue]);

  if (!stateData) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Execute a circuit to see state visualization
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 2 }}>
        <Tab label="Amplitudes" />
        <Tab label="Phases" />
        <Tab label="Probabilities" />
      </Tabs>

      {tabValue === 0 && (
        <div ref={amplitudeRef} style={{ width: '100%', height: '400px' }} />
      )}
      {tabValue === 1 && (
        <div ref={phaseRef} style={{ width: '100%', height: '400px' }} />
      )}
      {tabValue === 2 && (
        <div ref={probabilityRef} style={{ width: '100%', height: '400px' }} />
      )}
    </Box>
  );
};

export default StateVisualization;

