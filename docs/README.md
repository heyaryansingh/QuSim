# QuSim Documentation

## Overview

QuSim is a research-grade quantum circuit simulator with comprehensive features for circuit construction, noise modeling, entanglement tracking, and advanced diagnostics.

## Architecture

The simulator is built with a modular architecture:

- **Core**: Circuit construction, gates, state evolution
- **Backends**: Statevector, density matrix, stabilizer simulation
- **Noise**: Noise channel framework with Kraus operators
- **Metrics**: Entanglement measures, fidelity, purity
- **Diagnostics**: Failure detection and assumption tracking
- **QEC**: Quantum error correction codes
- **API**: FastAPI backend for web interface
- **Frontend**: React + TypeScript web UI

## Mathematical Foundations

### State Evolution

Quantum states evolve according to:
- **Statevector**: |ψ(t+1)⟩ = U_g |ψ(t)⟩
- **Density Matrix**: ρ(t+1) = U_g ρ(t) U_g†

### Measurement

Measurement collapses the state according to quantum postulates:
- Probability of outcome i: P(i) = |⟨i|ψ⟩|² (statevector) or Tr(P_i ρ) (density matrix)
- Post-measurement state: |ψ⟩ → P_i |ψ⟩ / √P(i)

### Noise Channels

Noise is modeled using Kraus operators:
- ε(ρ) = Σ_i K_i ρ K_i†
- Completeness: Σ_i K_i† K_i = I

### Entanglement Measures

- **Von Neumann Entropy**: S(ρ) = -Tr(ρ log ρ)
- **Mutual Information**: I(A:B) = S(ρ_A) + S(ρ_B) - S(ρ_AB)
- **Fidelity**: F(ρ, σ) = Tr(√(√ρ σ √ρ))²

## Usage

### Basic Circuit

```python
from qusim.core import Circuit
from qusim.backends import StatevectorBackend

circuit = Circuit(2)
circuit.h(0)
circuit.cnot(0, 1)

backend = StatevectorBackend()
result = backend.execute(circuit)
print(result.get_probabilities())
```

### DSL Syntax

```python
from qusim.dsl.parser import parse

dsl = """
qreg q[2]
h(0)
cnot(0, 1)
measure(0, 0)
"""
circuit = parse(dsl)
```

### Noise Modeling

```python
from qusim.backends import NoisyBackend
from qusim.noise.channels import DepolarizingChannel

noise_model = {0: [DepolarizingChannel(p=0.01)]}
backend = NoisyBackend(noise_model=noise_model)
result = backend.execute(circuit)
```

## API Reference

See the API documentation for detailed endpoint specifications.

## Examples

See the `notebooks/` directory for example notebooks demonstrating various features.


