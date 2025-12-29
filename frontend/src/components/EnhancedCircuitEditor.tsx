import React, { useState, useCallback, useEffect } from 'react';
import { Box, Tabs, Tab, TextField, Paper, Typography, Button, Grid } from '@mui/material';
import { PlayArrow as PlayIcon, Code as CodeIcon, Build as BuildIcon } from '@mui/icons-material';
import VisualCircuitEditor, { Gate, Wire } from './VisualCircuitEditor';
import GatePalette from './GatePalette';
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

const EnhancedCircuitEditor: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [dslCode, setDslCode] = useState('qreg q[2]\nh(0)\ncnot(0, 1)');
  const [numQubits, setNumQubits] = useState(2);
  const [gates, setGates] = useState<Gate[]>([]);
  const [wires, setWires] = useState<Wire[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [nextGateId, setNextGateId] = useState(1);

  // Convert visual circuit to DSL
  const visualToDSL = useCallback(() => {
    if (gates.length === 0) return 'qreg q[' + numQubits + ']\n';
    
    // Sort gates by x position (left to right)
    const sortedGates = [...gates].sort((a, b) => a.x - b.x);
    
    let dsl = `qreg q[${numQubits}]\n`;
    
    sortedGates.forEach((gate) => {
      const gateName = gate.type.toLowerCase();
      if (gate.type === 'CNOT' || gate.type === 'CZ' || gate.type === 'SWAP') {
        // Two-qubit gates - use control and target qubits
        const wire = wires.find((w) => w.from.gateId === gate.id || w.to.gateId === gate.id);
        const controlQubit = wire ? wire.qubit : (gate.qubit === 0 ? 1 : gate.qubit - 1);
        const targetQubit = gate.qubit;
        dsl += `${gateName}(${controlQubit}, ${targetQubit})\n`;
      } else if (gate.type.startsWith('R')) {
        // Rotation gates
        const angle = gate.params?.[0] || 'pi/2';
        dsl += `${gateName}(${gate.qubit}, ${angle})\n`;
      } else {
        // Single-qubit gates
        dsl += `${gateName}(${gate.qubit})\n`;
      }
    });
    
    return dsl;
  }, [gates, wires, numQubits]);

  // Convert DSL to visual circuit
  const dslToVisual = useCallback((dsl: string) => {
    const lines = dsl.split('\n').filter((line) => line.trim() && !line.trim().startsWith('#'));
    const newGates: Gate[] = [];
    let gateX = 150;
    
    lines.forEach((line) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('qreg')) {
        const match = trimmed.match(/qreg\s+\w+\[(\d+)\]/);
        if (match) {
          setNumQubits(parseInt(match[1]));
        }
      } else {
        const gateMatch = trimmed.match(/(\w+)\(([^)]+)\)/);
        if (gateMatch) {
          const gateName = gateMatch[1].toUpperCase();
          const params = gateMatch[2].split(',').map((p) => p.trim());
          const qubit = parseInt(params[0]);
          
          // For two-qubit gates, use the target qubit (second parameter)
          const targetQubit = (gateName === 'CNOT' || gateName === 'CZ' || gateName === 'SWAP') && params.length > 1
            ? parseInt(params[1])
            : qubit;
          
          const gate: Gate = {
            id: `gate-${nextGateId}`,
            type: gateName,
            x: gateX,
            y: 100 + targetQubit * 80 - 25,
            qubit: targetQubit,
            params: params.length > 1 ? params.slice(1) : undefined,
          };
          
          newGates.push(gate);
          gateX += 120;
          setNextGateId((id) => id + 1);
        }
      }
    });
    
    setGates(newGates);
  }, [nextGateId]);

  // Sync DSL when visual circuit changes
  useEffect(() => {
    if (tabValue === 1) {
      // Only sync if we're on the code tab
      const newDSL = visualToDSL();
      if (newDSL !== dslCode) {
        setDslCode(newDSL);
      }
    }
  }, [gates, wires, visualToDSL, tabValue]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    if (newValue === 0) {
      // Switching to visual editor - convert DSL to visual
      dslToVisual(dslCode);
    } else if (newValue === 1) {
      // Switching to code editor - convert visual to DSL
      setDslCode(visualToDSL());
    }
  };

  const handleGateAdd = (gateType: string, qubit: number) => {
    // For two-qubit gates, place on the lower qubit
    const targetQubit = gateType === 'CNOT' || gateType === 'CZ' || gateType === 'SWAP' 
      ? Math.min(qubit, numQubits - 1) 
      : qubit;
    
    const newGate: Gate = {
      id: `gate-${nextGateId}`,
      type: gateType,
      x: 150 + gates.length * 120,
      y: 100 + targetQubit * 80 - 25,
      qubit: targetQubit,
      params: gateType.startsWith('R') ? ['pi/2'] : undefined,
    };
    
    setGates([...gates, newGate]);
    
    // For two-qubit gates, create a wire to the control qubit
    if (gateType === 'CNOT' || gateType === 'CZ') {
      const controlQubit = targetQubit === 0 ? 1 : targetQubit - 1;
      const newWire: Wire = {
        id: `wire-${nextGateId}`,
        from: { gateId: newGate.id, port: 'output' },
        to: { gateId: newGate.id, port: 'input' },
        qubit: controlQubit,
      };
      setWires([...wires, newWire]);
    }
    
    setNextGateId((id) => id + 1);
  };

  const handleExecute = async () => {
    setLoading(true);
    try {
      const codeToExecute = tabValue === 0 ? visualToDSL() : dslCode;
      const response = await executeCircuit({
        dsl_code: codeToExecute,
        num_qubits: numQubits,
        shots: 1000,
        return_state_history: true,
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
        <Tab icon={<BuildIcon />} label="Visual Editor" />
        <Tab icon={<CodeIcon />} label="Code Editor" />
        <Tab label="State/Bloch" />
        <Tab label="Noise/Error" />
        <Tab label="Entanglement" />
        <Tab label="Resource" />
        <Tab label="Diagnostics" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <GatePalette onGateAdd={handleGateAdd} numQubits={numQubits} />
          </Grid>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Circuit Canvas</Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<PlayIcon />}
                  onClick={handleExecute}
                  disabled={loading}
                >
                  {loading ? 'Executing...' : 'Execute Circuit'}
                </Button>
              </Box>
              <VisualCircuitEditor
                numQubits={numQubits}
                gates={gates}
                wires={wires}
                onGatesChange={setGates}
                onWiresChange={setWires}
                onExecute={handleExecute}
              />
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Circuit Code (DSL)
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={15}
            value={dslCode}
            onChange={(e) => setDslCode(e.target.value)}
            placeholder="Enter circuit DSL code..."
            sx={{ mb: 2, fontFamily: 'monospace' }}
          />
          <Button
            variant="contained"
            onClick={handleExecute}
            disabled={loading}
            startIcon={<PlayIcon />}
          >
            {loading ? 'Executing...' : 'Execute Circuit'}
          </Button>
          {result && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Results</Typography>
              <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>
                {JSON.stringify(result, null, 2)}
              </pre>
            </Box>
          )}
        </Paper>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Typography>Bloch sphere visualization will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Typography>Noise and error analysis will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Typography>Entanglement metrics will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        <Typography>Resource tracking will appear here</Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={6}>
        <Typography>Failure diagnostics will appear here</Typography>
      </TabPanel>
    </Box>
  );
};

export default EnhancedCircuitEditor;

