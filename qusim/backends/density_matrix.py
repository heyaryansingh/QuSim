"""
Density matrix backend for quantum circuit simulation.

Supports mixed states and noise modeling via density matrices.
"""

import numpy as np
from typing import Optional, List, Dict, Any
from qusim.backends.base import Backend, ExecutionResult
from qusim.core.circuit import Circuit
from qusim.core.state import QuantumState


class DensityMatrixBackend(Backend):
    """Backend using density matrix simulation."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize density matrix backend.

        Args:
            seed: Random seed for deterministic execution
        """
        super().__init__(seed)

    def can_execute(self, circuit: Circuit) -> tuple[bool, Optional[str]]:
        """
        Density matrix backend can execute any circuit (up to memory limits).

        Returns:
            (True, None) - can always execute
        """
        # Check memory requirements (density matrix is 4x larger than statevector)
        dim = 2 ** circuit.num_qubits
        memory_gb = (dim * dim * 16) / (1024 ** 3)  # 16 bytes per complex number

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
        Execute circuit using density matrix evolution.

        Args:
            circuit: Circuit to execute
            initial_state: Initial density matrix or statevector (default: |00...0⟩⟨00...0|)
            shots: Number of measurement shots
            return_state_history: Whether to track state at each step

        Returns:
            ExecutionResult
        """
        # Initialize state
        dim = 2 ** circuit.num_qubits

        if initial_state is None:
            # Start in |00...0⟩⟨00...0|
            rho = np.zeros((dim, dim), dtype=complex)
            rho[0, 0] = 1.0
        else:
            if initial_state.ndim == 1:
                # Convert statevector to density matrix
                rho = np.outer(initial_state, initial_state.conj())
            elif initial_state.ndim == 2:
                if initial_state.shape != (dim, dim):
                    raise ValueError(
                        f"Initial state shape {initial_state.shape} doesn't match {dim} qubits"
                    )
                rho = initial_state.copy()
            else:
                raise ValueError(f"Invalid initial state shape: {initial_state.shape}")

        quantum_state = QuantumState(rho, circuit.num_qubits, is_density_matrix=True)
        state_history: List[QuantumState] = []

        if return_state_history:
            state_history.append(quantum_state.copy())

        # Execute gates
        for gate, qubits in circuit.gates:
            # Apply gate: ρ -> U ρ U†
            rho = gate.apply(rho, qubits, circuit.num_qubits)
            quantum_state.state = rho

            if return_state_history:
                state_history.append(quantum_state.copy())

        # Perform measurements
        measurements: List[Dict[str, int]] = []

        for shot in range(shots):
            # For multiple shots, we need to reset state before each measurement
            if shot > 0:
                # Reset to state before measurements
                rho = quantum_state.state.copy()
                quantum_state = QuantumState(rho, circuit.num_qubits, is_density_matrix=True)

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
            "backend": "DensityMatrixBackend",
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

    def get_density_matrix(self, result: ExecutionResult) -> np.ndarray:
        """Extract density matrix from result."""
        return result.state.state

    def partial_trace(self, result: ExecutionResult, keep_qubits: List[int]) -> np.ndarray:
        """
        Calculate partial trace over specified qubits.

        Args:
            result: Execution result
            keep_qubits: Qubit indices to keep

        Returns:
            Reduced density matrix
        """
        from qusim.visualization.bloch import reduced_density_matrix

        return reduced_density_matrix(result.state, keep_qubits)

    def purity(self, result: ExecutionResult, qubits: Optional[List[int]] = None) -> float:
        """
        Calculate purity: Tr(ρ²).

        Args:
            result: Execution result
            qubits: Optional qubit subset (if None, uses full state)

        Returns:
            Purity (1.0 for pure states, < 1.0 for mixed states)
        """
        if qubits is not None:
            rho = self.partial_trace(result, qubits)
        else:
            rho = self.get_density_matrix(result)

        return np.real(np.trace(rho @ rho))

    def von_neumann_entropy(self, result: ExecutionResult, qubits: Optional[List[int]] = None) -> float:
        """
        Calculate Von Neumann entropy: S(ρ) = -Tr(ρ log ρ).

        Args:
            result: Execution result
            qubits: Optional qubit subset (if None, uses full state)

        Returns:
            Entropy in bits
        """
        if qubits is not None:
            rho = self.partial_trace(result, qubits)
        else:
            rho = self.get_density_matrix(result)

        # Calculate eigenvalues
        eigenvals = np.linalg.eigvalsh(rho)
        eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical zeros

        # Calculate entropy: -Σ λ_i log_2(λ_i)
        entropy = -np.sum(eigenvals * np.log2(eigenvals))

        return np.real(entropy)


