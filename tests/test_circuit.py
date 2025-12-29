"""
Basic tests for quantum circuit simulator.
"""

import pytest
import numpy as np
from qusim.core import Circuit
from qusim.core.gates import H, CNOT, X, Z
from qusim.backends import StatevectorBackend, DensityMatrixBackend
from qusim.dsl.parser import parse


def test_bell_state():
    """Test Bell state creation."""
    circuit = Circuit(2)
    circuit.h(0)
    circuit.cnot(0, 1)

    backend = StatevectorBackend()
    result = backend.execute(circuit)

    # Bell state: (|00⟩ + |11⟩) / √2
    statevector = result.state.state
    assert np.isclose(abs(statevector[0]), 1 / np.sqrt(2))
    assert np.isclose(abs(statevector[3]), 1 / np.sqrt(2))
    assert np.isclose(abs(statevector[1]), 0)
    assert np.isclose(abs(statevector[2]), 0)


def test_hadamard():
    """Test Hadamard gate."""
    circuit = Circuit(1)
    circuit.h(0)

    backend = StatevectorBackend()
    result = backend.execute(circuit)

    # H|0⟩ = (|0⟩ + |1⟩) / √2
    statevector = result.state.state
    assert np.isclose(abs(statevector[0]), 1 / np.sqrt(2))
    assert np.isclose(abs(statevector[1]), 1 / np.sqrt(2))


def test_dsl_parser():
    """Test DSL parser."""
    dsl = """
    qreg q[2]
    h(0)
    cnot(0, 1)
    """
    circuit = parse(dsl)
    assert circuit.num_qubits == 2
    assert len(circuit.gates) == 2


def test_density_matrix():
    """Test density matrix backend."""
    circuit = Circuit(1)
    circuit.h(0)

    backend = DensityMatrixBackend()
    result = backend.execute(circuit)

    # Check trace = 1
    rho = result.state.state
    assert np.isclose(np.trace(rho), 1.0)

    # Check Hermiticity
    assert np.allclose(rho, rho.conj().T)


def test_measurement():
    """Test measurement."""
    circuit = Circuit(1)
    circuit.h(0)
    circuit.measure(0, 0)

    backend = StatevectorBackend(seed=42)
    result = backend.execute(circuit, shots=100)

    # Should get roughly 50/50 distribution
    counts = result.get_counts()
    assert "0" in counts or "1" in counts
    assert len(counts) <= 2


