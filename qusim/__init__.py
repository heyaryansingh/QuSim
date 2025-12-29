"""
QuSim - Quantum Circuit Simulator

A research-grade quantum circuit simulator with noise modeling,
entanglement tracking, and advanced diagnostics.
"""

__version__ = "0.1.0"

from qusim.core.circuit import Circuit
from qusim.core.gates import Gate, X, Y, Z, H, S, T, RX, RY, RZ, CNOT, CZ, SWAP, Toffoli

__all__ = [
    "Circuit",
    "Gate",
    "X",
    "Y",
    "Z",
    "H",
    "S",
    "T",
    "RX",
    "RY",
    "RZ",
    "CNOT",
    "CZ",
    "SWAP",
    "Toffoli",
]


