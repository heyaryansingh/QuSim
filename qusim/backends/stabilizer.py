"""
Stabilizer backend for Clifford circuits.

Uses stabilizer formalism for efficient simulation of Clifford circuits.
Clifford gates: H, S, CNOT, CZ, and Pauli gates.
"""

import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from qusim.backends.base import Backend, ExecutionResult
from qusim.core.circuit import Circuit
from qusim.core.state import QuantumState
from qusim.core.gates import H, S, CNOT, CZ, X, Y, Z


class StabilizerBackend(Backend):
    """
    Backend using stabilizer formalism for Clifford circuits.

    Only supports Clifford gates: H, S, CNOT, CZ, and Pauli gates (X, Y, Z).
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize stabilizer backend.

        Args:
            seed: Random seed
        """
        super().__init__(seed)

    def can_execute(self, circuit: Circuit) -> tuple[bool, Optional[str]]:
        """
        Check if circuit contains only Clifford gates.

        Returns:
            (can_execute, reason_if_not)
        """
        clifford_gates = {"H", "S", "CNOT", "CZ", "X", "Y", "Z", "SWAP"}

        for gate, _ in circuit.gates:
            if gate.name not in clifford_gates:
                return (
                    False,
                    f"Non-Clifford gate '{gate.name}' detected. Stabilizer backend only supports Clifford gates.",
                )

        return (True, None)

    def execute(
        self,
        circuit: Circuit,
        initial_state: Optional[np.ndarray] = None,
        shots: int = 1,
        return_state_history: bool = False,
    ) -> ExecutionResult:
        """
        Execute Clifford circuit using stabilizer formalism.

        For now, falls back to statevector simulation but validates Clifford property.
        A full stabilizer implementation would use tableau representation.

        Args:
            circuit: Circuit to execute (must be Clifford)
            initial_state: Initial state
            shots: Number of measurement shots
            return_state_history: Whether to track state history

        Returns:
            ExecutionResult
        """
        # Validate circuit
        can_execute, reason = self.can_execute(circuit)
        if not can_execute:
            raise ValueError(f"Cannot execute circuit: {reason}")

        # For now, use statevector backend (full stabilizer implementation is complex)
        # This validates the circuit is Clifford but doesn't use the efficiency benefits
        from qusim.backends.statevector import StatevectorBackend

        statevector_backend = StatevectorBackend(seed=self.seed)
        result = statevector_backend.execute(
            circuit, initial_state, shots, return_state_history
        )

        # Update metadata
        result.metadata["backend"] = "StabilizerBackend"
        result.metadata["note"] = "Using statevector simulation (full stabilizer tableau not yet implemented)"

        return result

    def is_clifford_gate(self, gate_name: str) -> bool:
        """Check if a gate is a Clifford gate."""
        clifford_gates = {"H", "S", "CNOT", "CZ", "X", "Y", "Z", "SWAP", "RX", "RY", "RZ"}
        # Note: RX, RY, RZ are only Clifford for specific angles (π/2, π, etc.)
        # For simplicity, we only accept H, S, CNOT, CZ, and Pauli gates
        return gate_name in {"H", "S", "CNOT", "CZ", "X", "Y", "Z", "SWAP"}


def detect_clifford_circuit(circuit: Circuit) -> Tuple[bool, Optional[str]]:
    """
    Detect if a circuit is a Clifford circuit.

    Args:
        circuit: Circuit to check

    Returns:
        (is_clifford, reason_if_not)
    """
    backend = StabilizerBackend()
    return backend.can_execute(circuit)


