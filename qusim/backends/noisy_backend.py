"""
Noisy backend wrapper that applies noise channels during circuit execution.
"""

import numpy as np
from typing import Optional, List, Dict, Any, Callable
from qusim.backends.base import Backend, ExecutionResult
from qusim.backends.density_matrix import DensityMatrixBackend
from qusim.core.circuit import Circuit
from qusim.core.state import QuantumState
from qusim.noise.channels import NoiseChannel


class NoisyBackend(Backend):
    """
    Backend wrapper that applies noise channels after each gate.

    Uses density matrix backend internally to support mixed states.
    """

    def __init__(
        self,
        base_backend: Optional[Backend] = None,
        noise_model: Optional[Dict[int, List[NoiseChannel]]] = None,
        seed: Optional[int] = None,
    ):
        """
        Initialize noisy backend.

        Args:
            base_backend: Base backend (default: DensityMatrixBackend)
            noise_model: Dictionary mapping qubit indices to noise channels
            seed: Random seed
        """
        super().__init__(seed)
        self.base_backend = base_backend or DensityMatrixBackend(seed=seed)
        self.noise_model = noise_model or {}

    def can_execute(self, circuit: Circuit) -> tuple[bool, Optional[str]]:
        """Check if backend can execute circuit."""
        return self.base_backend.can_execute(circuit)

    def execute(
        self,
        circuit: Circuit,
        initial_state: Optional[np.ndarray] = None,
        shots: int = 1,
        return_state_history: bool = False,
    ) -> ExecutionResult:
        """
        Execute circuit with noise.

        Args:
            circuit: Circuit to execute
            initial_state: Initial state
            shots: Number of measurement shots
            return_state_history: Whether to track state history

        Returns:
            ExecutionResult with noisy state
        """
        # Convert initial state to density matrix if needed
        dim = 2 ** circuit.num_qubits
        if initial_state is None:
            rho = np.zeros((dim, dim), dtype=complex)
            rho[0, 0] = 1.0
        elif initial_state.ndim == 1:
            rho = np.outer(initial_state, initial_state.conj())
        else:
            rho = initial_state.copy()

        quantum_state = QuantumState(rho, circuit.num_qubits, is_density_matrix=True)
        state_history: List[QuantumState] = []
        ideal_state_history: List[QuantumState] = []  # For comparison

        if return_state_history:
            state_history.append(quantum_state.copy())

        # Track noise application
        noise_applications: List[Dict[str, Any]] = []

        # Execute gates with noise
        for gate_idx, (gate, qubits) in enumerate(circuit.gates):
            # Apply gate
            rho = gate.apply(rho, qubits, circuit.num_qubits)
            quantum_state.state = rho

            # Store ideal state for comparison
            if return_state_history:
                ideal_state_history.append(quantum_state.copy())

            # Apply noise to affected qubits
            for qubit in qubits:
                if qubit in self.noise_model:
                    for noise_channel in self.noise_model[qubit]:
                        rho_before = rho.copy()
                        rho = noise_channel.apply(rho, qubit, circuit.num_qubits)

                        # Track noise application
                        noise_applications.append(
                            {
                                "gate_idx": gate_idx,
                                "qubit": qubit,
                                "channel": noise_channel.name,
                                "fidelity_before": self._calculate_fidelity(rho_before, rho),
                            }
                        )

            quantum_state.state = rho

            if return_state_history:
                state_history.append(quantum_state.copy())

        # Perform measurements
        measurements: List[Dict[str, int]] = []

        for shot in range(shots):
            if shot > 0:
                rho = quantum_state.state.copy()
                quantum_state = QuantumState(rho, circuit.num_qubits, is_density_matrix=True)

            shot_measurements: Dict[str, int] = {}

            for qubit, classical_bit in circuit.measurements:
                outcome = quantum_state.measure(qubit, seed=self.seed)
                shot_measurements[str(classical_bit)] = outcome

            measurements.append(shot_measurements)

        if not circuit.measurements:
            measurements = [{}] * shots

        metadata = {
            "backend": "NoisyBackend",
            "base_backend": self.base_backend.get_name(),
            "num_qubits": circuit.num_qubits,
            "num_gates": len(circuit.gates),
            "circuit_depth": circuit.depth(),
            "noise_applications": noise_applications,
            "ideal_state_history": ideal_state_history if return_state_history else None,
        }

        return ExecutionResult(
            state=quantum_state,
            measurements=measurements,
            state_history=state_history if return_state_history else None,
            metadata=metadata,
        )

    def _calculate_fidelity(self, rho1: np.ndarray, rho2: np.ndarray) -> float:
        """Calculate fidelity between two density matrices."""
        from qusim.metrics.fidelity import density_matrix_fidelity

        return density_matrix_fidelity(rho1, rho2)

    def add_noise(self, qubit: int, channel: NoiseChannel):
        """
        Add noise channel to a qubit.

        Args:
            qubit: Qubit index
            channel: Noise channel to apply
        """
        if qubit not in self.noise_model:
            self.noise_model[qubit] = []
        self.noise_model[qubit].append(channel)


