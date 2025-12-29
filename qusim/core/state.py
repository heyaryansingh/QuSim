"""
Quantum state representation.

Supports both statevectors and density matrices.
"""

import numpy as np
from typing import Union, Optional


class QuantumState:
    """Represents a quantum state (statevector or density matrix)."""

    def __init__(
        self,
        state: np.ndarray,
        num_qubits: int,
        is_density_matrix: bool = False,
        classical_bits: Optional[dict] = None,
    ):
        """
        Initialize quantum state.

        Args:
            state: Statevector (1D) or density matrix (2D)
            num_qubits: Number of qubits
            is_density_matrix: Whether state is a density matrix
            classical_bits: Dictionary of classical register values
        """
        self.state = state
        self.num_qubits = num_qubits
        self.is_density_matrix = is_density_matrix
        self.classical_bits = classical_bits or {}

        # Validate dimensions
        if is_density_matrix:
            expected_dim = 2 ** num_qubits
            if state.shape != (expected_dim, expected_dim):
                raise ValueError(
                    f"Density matrix shape {state.shape} doesn't match {num_qubits} qubits"
                )
        else:
            expected_dim = 2 ** num_qubits
            if state.shape != (expected_dim,):
                raise ValueError(
                    f"Statevector shape {state.shape} doesn't match {num_qubits} qubits"
                )

    def to_density_matrix(self) -> "QuantumState":
        """Convert statevector to density matrix: ρ = |ψ⟩⟨ψ|."""
        if self.is_density_matrix:
            return self

        rho = np.outer(self.state, self.state.conj())
        return QuantumState(rho, self.num_qubits, is_density_matrix=True)

    def to_statevector(self) -> "QuantumState":
        """Extract statevector from pure density matrix."""
        if not self.is_density_matrix:
            return self

        # For pure states, can extract statevector
        # Check if pure: Tr(ρ²) = 1
        purity = np.trace(self.state @ self.state)
        if not np.isclose(purity, 1.0, atol=1e-6):
            raise ValueError("Cannot extract statevector from mixed state")

        # Get eigenvector with eigenvalue 1
        eigenvals, eigenvecs = np.linalg.eigh(self.state)
        max_idx = np.argmax(eigenvals)
        statevector = eigenvecs[:, max_idx]

        return QuantumState(statevector, self.num_qubits, is_density_matrix=False)

    def measure(self, qubit: int, seed: Optional[int] = None) -> int:
        """
        Measure a qubit and collapse the state.

        Args:
            qubit: Qubit index to measure
            seed: Random seed for deterministic measurement

        Returns:
            Measurement outcome (0 or 1)
        """
        if seed is not None:
            np.random.seed(seed)

        if self.is_density_matrix:
            return self._measure_density_matrix(qubit)
        else:
            return self._measure_statevector(qubit)

    def _measure_statevector(self, qubit: int) -> int:
        """Measure qubit in statevector, collapse state."""
        # Calculate probabilities
        dim = 2 ** self.num_qubits
        state_reshaped = self.state.reshape([2] * self.num_qubits)

        # Probability of measuring |0⟩
        prob_0 = 0.0
        for idx in np.ndindex(*[2] * self.num_qubits):
            if idx[qubit] == 0:
                flat_idx = sum(2 ** (self.num_qubits - 1 - i) * idx[i] for i in range(self.num_qubits))
                prob_0 += abs(self.state[flat_idx]) ** 2

        # Sample measurement outcome
        outcome = np.random.choice([0, 1], p=[prob_0, 1 - prob_0])

        # Collapse state
        state_reshaped = self.state.reshape([2] * self.num_qubits)
        for idx in np.ndindex(*[2] * self.num_qubits):
            if idx[qubit] != outcome:
                flat_idx = sum(2 ** (self.num_qubits - 1 - i) * idx[i] for i in range(self.num_qubits))
                state_reshaped.flat[flat_idx] = 0

        # Renormalize
        norm = np.linalg.norm(state_reshaped)
        if norm > 0:
            state_reshaped = state_reshaped / norm

        self.state = state_reshaped.reshape(dim)

        return outcome

    def _measure_density_matrix(self, qubit: int) -> int:
        """Measure qubit in density matrix, collapse state."""
        # Measurement operator: P_0 = |0⟩⟨0|, P_1 = |1⟩⟨1|
        dim = 2 ** self.num_qubits

        # Construct measurement operators
        P0 = np.zeros((dim, dim), dtype=complex)
        P1 = np.zeros((dim, dim), dtype=complex)

        for i in range(dim):
            # Check if qubit is |0⟩ or |1⟩
            binary = format(i, f"0{self.num_qubits}b")
            if binary[qubit] == "0":
                P0[i, i] = 1
            else:
                P1[i, i] = 1

        # Calculate probabilities
        prob_0 = np.real(np.trace(P0 @ self.state))
        prob_1 = np.real(np.trace(P1 @ self.state))

        # Sample outcome
        outcome = np.random.choice([0, 1], p=[prob_0, prob_1])

        # Collapse: ρ -> P_i ρ P_i / Tr(P_i ρ)
        if outcome == 0:
            self.state = (P0 @ self.state @ P0) / prob_0
        else:
            self.state = (P1 @ self.state @ P1) / prob_1

        return outcome

    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities for all basis states."""
        if self.is_density_matrix:
            return np.real(np.diag(self.state))
        else:
            return np.abs(self.state) ** 2

    def expectation_value(self, observable: np.ndarray) -> float:
        """
        Calculate expectation value: ⟨O⟩ = Tr(ρ O) or ⟨ψ|O|ψ⟩.

        Args:
            observable: Hermitian operator (matrix)

        Returns:
            Expectation value
        """
        if self.is_density_matrix:
            return np.real(np.trace(self.state @ observable))
        else:
            return np.real(self.state.conj() @ observable @ self.state)

    def copy(self) -> "QuantumState":
        """Create a copy of the state."""
        return QuantumState(
            self.state.copy(),
            self.num_qubits,
            self.is_density_matrix,
            self.classical_bits.copy() if self.classical_bits else None,
        )


