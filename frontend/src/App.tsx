import React from 'react';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import { Science as ScienceIcon } from '@mui/icons-material';
import EnhancedCircuitEditor from './components/EnhancedCircuitEditor';
import './App.css';

function App() {
  return (
    <div className="App">
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <ScienceIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            QuSim - Quantum Circuit Simulator
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Interactive quantum circuit simulator with QASM editor, visual circuit diagrams, 
            Bloch sphere visualization, and quantum gate execution metrics
          </Typography>
        </Toolbar>
      </AppBar>
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
        <Container maxWidth="xl" sx={{ pt: 4, pb: 4 }}>
          <EnhancedCircuitEditor />
        </Container>
      </Box>
    </div>
  );
}

export default App;

