"""
Statevector backend for quantum circuit simulation.

Implements statevector evolution: |ψ(t+1)⟩ = U_g |ψ(t)⟩
"""

import numpy as np
from typing import Optional, List, Dict, Any
from qusim.backends.base import Backend, ExecutionResult
from qusim.core.circuit import Circuit
from qusim.core.state import QuantumState


class StatevectorBackend(Backend):
    """Backend using statevector simulation."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize statevector backend.

        Args:
            seed: Random seed for deterministic execution
        """
        super().__init__(seed)

    def can_execute(self, circuit: Circuit) -> tuple[bool, Optional[str]]:
        """
        Statevector backend can execute any circuit (up to memory limits).

        Returns:
            (True, None) - can always execute
        """
        # Check memory requirements
        dim = 2 ** circuit.num_qubits
        memory_gb = (dim * 16) / (1024 ** 3)  # 16 bytes per complex number

        if memory_gb > 10:  # Warn if > 10GB
            return (
                True,
                f"Warning: Circuit requires ~{memory_gb:.2f}GB memory for {circuit.num_qubits} qubits",
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
        Execute circuit using statevector evolution.

        Args:
            circuit: Circuit to execute
            initial_state: Initial statevector (default: |00...0⟩)
            shots: Number of measurement shots
            return_state_history: Whether to track state at each step

        Returns:
            ExecutionResult
        """
        # Initialize state
        dim = 2 ** circuit.num_qubits
        if initial_state is None:
            # Start in |00...0⟩
            state = np.zeros(dim, dtype=complex)
            state[0] = 1.0
        else:
            if initial_state.shape != (dim,):
                raise ValueError(
                    f"Initial state shape {initial_state.shape} doesn't match {dim} qubits"
                )
            state = initial_state.copy()

        quantum_state = QuantumState(state, circuit.num_qubits, is_density_matrix=False)
        state_history: List[QuantumState] = []

        if return_state_history:
            state_history.append(quantum_state.copy())

        # Execute gates
        for gate, qubits in circuit.gates:
            # Apply gate
            state = gate.apply(state, qubits, circuit.num_qubits)
            quantum_state.state = state

            if return_state_history:
                state_history.append(quantum_state.copy())

        # Perform measurements
        measurements: List[Dict[str, int]] = []

        for shot in range(shots):
            # For multiple shots, we need to reset state before each measurement
            if shot > 0:
                # Reset to state before measurements
                state = quantum_state.state.copy()
                quantum_state = QuantumState(state, circuit.num_qubits, is_density_matrix=False)

            shot_measurements: Dict[str, int] = {}

            for qubit, classical_bit in circuit.measurements:
                # Measure qubit
                outcome = quantum_state.measure(qubit, seed=self.seed)
                shot_measurements[str(classical_bit)] = outcome

            measurements.append(shot_measurements)

        # If no measurements, return final state
        if not circuit.measurements:
            measurements = [{}] * shots

        metadata = {
            "backend": "StatevectorBackend",
            "num_qubits": circuit.num_qubits,
            "num_gates": len(circuit.gates),
            "circuit_depth": circuit.depth(),
        }

        return ExecutionResult(
            state=quantum_state,
            measurements=measurements,
            state_history=state_history if return_state_history else None,
            metadata=metadata,
        )

    def get_statevector(self, result: ExecutionResult) -> np.ndarray:
        """Extract statevector from result."""
        return result.state.state

    def get_amplitudes(self, result: ExecutionResult) -> Dict[str, complex]:
        """
        Get amplitude for each basis state.

        Returns:
            Dictionary mapping bitstrings to amplitudes
        """
        statevector = self.get_statevector(result)
        num_qubits = result.state.num_qubits
        amplitudes: Dict[str, complex] = {}

        for i, amp in enumerate(statevector):
            bitstring = format(i, f"0{num_qubits}b")
            amplitudes[bitstring] = amp

        return amplitudes


