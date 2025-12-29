import React, { useState } from 'react';
import { Box, Tabs, Tab, TextField, Button, Paper, Typography } from '@mui/material';
import { executeCircuit } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CircuitEditor: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [dslCode, setDslCode] = useState('qreg q[2]\nh(0)\ncnot(0, 1)');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleExecute = async () => {
    setLoading(true);
    try {
      const response = await executeCircuit({
        dsl_code: dslCode,
        num_qubits: 2,
        shots: 1000,
      });
      setResult(response);
    } catch (error) {
      console.error('Error executing circuit:', error);
      setResult({ error: String(error) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Tabs value={tabValue} onChange={handleTabChange}>
        <Tab label="Circuit" />
        <Tab label="State/Bloch" />
        <Tab label="Noise/Error" />
        <Tab label="Entanglement" />
        <Tab label="Resource" />
        <Tab label="Diagnostics" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Circuit Editor
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={10}
            value={dslCode}
            onChange={(e) => setDslCode(e.target.value)}
            placeholder="Enter circuit DSL code..."
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            onClick={handleExecute}
            disabled={loading}
          >
            {loading ? 'Executing...' : 'Execute Circuit'}
          </Button>
          {result && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Results</Typography>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </Box>
          )}
        </Paper>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography>Bloch sphere visualization will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Typography>Noise and error analysis will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography>Entanglement metrics will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Typography>Resource tracking will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        <Typography>Failure diagnostics will appear here</Typography>
      </TabPanel>
    </Box>
  );
};

export default CircuitEditor;


