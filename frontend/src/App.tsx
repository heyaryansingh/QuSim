import React from 'react';
import { Container, AppBar, Toolbar, Typography } from '@mui/material';
import EnhancedCircuitEditor from './components/EnhancedCircuitEditor';
import './App.css';

function App() {
  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            QuSim - Quantum Circuit Simulator
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <EnhancedCircuitEditor />
      </Container>
    </div>
  );
}

export default App;

