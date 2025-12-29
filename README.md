# QuSim - Quantum Circuit Simulator

A research-grade, interactive, fully-featured quantum circuit simulator for educational and advanced research use.

## Features

- **Circuit Construction**: Text-based DSL and visual drag-and-drop editor
- **Multiple Backends**: Statevector, density matrix, stabilizer, and tensor-network
- **Noise Modeling**: Comprehensive noise channels with Kraus operators
- **Entanglement Tracking**: Von Neumann entropy, mutual information, and more
- **Failure Diagnostics**: Automatic detection of noise dominance and bottlenecks
- **Sensitivity Analysis**: Parameter perturbation and comparative execution
- **QEC Sandbox**: Quantum error correction codes with syndrome tracking
- **Resource Tracking**: Circuit depth, gate counts, and simulation costs
- **Interactive Visualizations**: Bloch spheres, density matrices, entanglement graphs

## Installation

```bash
pip install -e .
```

## Quick Start

### Launch the Application

Simply run:
```bash
python launch.py
```

This will:
- Start the backend API server (port 8000)
- Start the frontend web interface (port 3000)
- Open your browser automatically

Then access the visual circuit editor at **http://localhost:3000**

### Python API Usage

```python
from qusim.core import Circuit
from qusim.backends import StatevectorBackend

# Create a simple circuit
circuit = Circuit(2)
circuit.h(0)
circuit.cnot(0, 1)

# Execute
backend = StatevectorBackend()
result = backend.execute(circuit)
print(result.state)
```

## Documentation

See `docs/` for detailed documentation.

## License

MIT License

