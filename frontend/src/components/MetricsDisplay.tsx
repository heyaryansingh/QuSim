import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { CheckCircle, Error, Warning, Info } from '@mui/icons-material';

interface MetricsDisplayProps {
  result?: any;
  loading?: boolean;
}

const MetricsDisplay: React.FC<MetricsDisplayProps> = ({ result, loading }) => {
  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          Executing circuit...
        </Typography>
      </Box>
    );
  }

  if (!result) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Execute a circuit to see metrics
        </Typography>
      </Box>
    );
  }

  const counts = result.counts || {};
  const probabilities = result.probabilities || {};
  const fidelity = result.fidelity;
  const entropy = result.entropy;
  const measurements = result.measurements || [];
  const execution_time = result.execution_time || result.metadata?.execution_time;
  const num_qubits = result.num_qubits || result.metadata?.num_qubits;
  const num_gates = result.num_gates || result.metadata?.num_gates;
  const depth = result.depth || result.metadata?.depth;

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={2}>
        {/* Key Metrics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Key Metrics
            </Typography>
            <Grid container spacing={2}>
              {fidelity !== undefined && (
                <Grid item xs={6} sm={3}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Fidelity
                    </Typography>
                    <Typography variant="h5">
                      {fidelity.toFixed(4)}
                    </Typography>
                  </Box>
                </Grid>
              )}
              {entropy !== undefined && (
                <Grid item xs={6} sm={3}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Entropy
                    </Typography>
                    <Typography variant="h5">
                      {entropy.toFixed(4)}
                    </Typography>
                  </Box>
                </Grid>
              )}
              <Grid item xs={6} sm={3}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Shots
                  </Typography>
                  <Typography variant="h5">
                    {result.shots || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Backend
                  </Typography>
                  <Chip
                    label={result.backend || 'Unknown'}
                    size="small"
                    color="primary"
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Measurement Counts */}
        {Object.keys(counts).length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Measurement Counts
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>State</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell align="right">Probability</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(counts)
                      .sort((a, b) => (b[1] as number) - (a[1] as number))
                      .slice(0, 10)
                      .map(([state, count]) => (
                        <TableRow key={state}>
                          <TableCell>
                            <code>{state}</code>
                          </TableCell>
                          <TableCell align="right">{count as number}</TableCell>
                          <TableCell align="right">
                            {probabilities[state]
                              ? `${(probabilities[state] * 100).toFixed(2)}%`
                              : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        )}

        {/* Execution Info */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Execution Information
            </Typography>
            <Box sx={{ mt: 1 }}>
              {execution_time !== undefined && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Execution Time
                  </Typography>
                  <Typography variant="body2">
                    {typeof execution_time === 'number' ? execution_time.toFixed(4) : execution_time}s
                  </Typography>
                </Box>
              )}
              {num_qubits !== undefined && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Number of Qubits
                  </Typography>
                  <Typography variant="body2">{num_qubits}</Typography>
                </Box>
              )}
              {num_gates !== undefined && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Number of Gates
                  </Typography>
                  <Typography variant="body2">{num_gates}</Typography>
                </Box>
              )}
              {depth !== undefined && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Circuit Depth
                  </Typography>
                  <Typography variant="body2">{depth}</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Errors/Warnings */}
        {result.warnings && result.warnings.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2, bgcolor: 'warning.light' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning sx={{ mr: 1 }} />
                <Typography variant="h6">Warnings</Typography>
              </Box>
              {result.warnings.map((warning: string, idx: number) => (
                <Typography key={idx} variant="body2">
                  • {warning}
                </Typography>
              ))}
            </Paper>
          </Grid>
        )}

        {result.error && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2, bgcolor: 'error.light' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Error sx={{ mr: 1 }} />
                <Typography variant="h6">Error</Typography>
              </Box>
              <Typography variant="body2">{result.error}</Typography>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default MetricsDisplay;

