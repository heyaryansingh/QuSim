"""
Quantum circuit construction and management.
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from qusim.core.gates import Gate, SingleQubitGate, TwoQubitGate, Toffoli
from qusim.core.state import QuantumState


class Circuit:
    """Represents a quantum circuit."""

    def __init__(self, num_qubits: int, num_classical_bits: int = 0):
        """
        Initialize a quantum circuit.

        Args:
            num_qubits: Number of qubits
            num_classical_bits: Number of classical bits for measurement results
        """
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits
        self.gates: List[Tuple[Gate, List[int]]] = []  # (gate, qubit_indices)
        self.measurements: List[Tuple[int, int]] = []  # (qubit, classical_bit)

    def add_gate(self, gate: Gate, qubits: List[int]):
        """
        Add a gate to the circuit.

        Args:
            gate: Gate to add
            qubits: Qubit indices the gate acts on
        """
        # Validate qubit indices
        for q in qubits:
            if q < 0 or q >= self.num_qubits:
                raise ValueError(f"Qubit index {q} out of range [0, {self.num_qubits})")

        if len(qubits) != gate.num_qubits:
            raise ValueError(
                f"Gate {gate.name} requires {gate.num_qubits} qubits, got {len(qubits)}"
            )

        self.gates.append((gate, qubits))

    def measure(self, qubit: int, classical_bit: Optional[int] = None):
        """
        Add a measurement to the circuit.

        Args:
            qubit: Qubit to measure
            classical_bit: Classical bit to store result (auto-assigned if None)
        """
        if qubit < 0 or qubit >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit} out of range [0, {self.num_qubits})")

        if classical_bit is None:
            classical_bit = len(self.measurements)
        elif classical_bit < 0 or classical_bit >= self.num_classical_bits:
            raise ValueError(
                f"Classical bit index {classical_bit} out of range [0, {self.num_classical_bits})"
            )

        self.measurements.append((qubit, classical_bit))

    # Convenience methods for common gates
    def x(self, qubit: int):
        """Add X gate."""
        from qusim.core.gates import X

        self.add_gate(X(), [qubit])
        return self

    def y(self, qubit: int):
        """Add Y gate."""
        from qusim.core.gates import Y

        self.add_gate(Y(), [qubit])
        return self

    def z(self, qubit: int):
        """Add Z gate."""
        from qusim.core.gates import Z

        self.add_gate(Z(), [qubit])
        return self

    def h(self, qubit: int):
        """Add H gate."""
        from qusim.core.gates import H

        self.add_gate(H(), [qubit])
        return self

    def s(self, qubit: int):
        """Add S gate."""
        from qusim.core.gates import S

        self.add_gate(S(), [qubit])
        return self

    def t(self, qubit: int):
        """Add T gate."""
        from qusim.core.gates import T

        self.add_gate(T(), [qubit])
        return self

    def rx(self, qubit: int, theta: float):
        """Add RX gate."""
        from qusim.core.gates import RX

        self.add_gate(RX(theta), [qubit])
        return self

    def ry(self, qubit: int, theta: float):
        """Add RY gate."""
        from qusim.core.gates import RY

        self.add_gate(RY(theta), [qubit])
        return self

    def rz(self, qubit: int, theta: float):
        """Add RZ gate."""
        from qusim.core.gates import RZ

        self.add_gate(RZ(theta), [qubit])
        return self

    def cnot(self, control: int, target: int):
        """Add CNOT gate."""
        from qusim.core.gates import CNOT

        self.add_gate(CNOT(), [control, target])
        return self

    def cz(self, control: int, target: int):
        """Add CZ gate."""
        from qusim.core.gates import CZ

        self.add_gate(CZ(), [control, target])
        return self

    def swap(self, qubit1: int, qubit2: int):
        """Add SWAP gate."""
        from qusim.core.gates import SWAP

        self.add_gate(SWAP(), [qubit1, qubit2])
        return self

    def toffoli(self, control1: int, control2: int, target: int):
        """Add Toffoli gate."""
        from qusim.core.gates import Toffoli

        self.add_gate(Toffoli(), [control1, control2, target])
        return self

    def depth(self) -> int:
        """Calculate circuit depth (number of layers)."""
        if not self.gates:
            return 0

        # Group gates into layers (gates that can execute in parallel)
        layers: List[List[int]] = []
        qubit_layers = [-1] * self.num_qubits  # Last layer each qubit was used

        for i, (gate, qubits) in enumerate(self.gates):
            # Find the earliest layer this gate can be placed
            earliest_layer = max(qubit_layers[q] for q in qubits) + 1

            # Extend layers if needed
            while len(layers) <= earliest_layer:
                layers.append([])

            layers[earliest_layer].append(i)

            # Update qubit layers
            for q in qubits:
                qubit_layers[q] = earliest_layer

        return len(layers)

    def gate_count(self) -> Dict[str, int]:
        """Count gates by type."""
        counts: Dict[str, int] = {}
        for gate, _ in self.gates:
            counts[gate.name] = counts.get(gate.name, 0) + 1
        return counts

    def __repr__(self) -> str:
        return f"Circuit({self.num_qubits} qubits, {len(self.gates)} gates, depth={self.depth()})"

    def __str__(self) -> str:
        return self.__repr__()


