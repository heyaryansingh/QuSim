"""
Quantum gate implementations.

All gates are represented as unitary matrices and can be applied to quantum states.
Gates follow the standard quantum computing conventions.
"""

import numpy as np
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod


class Gate(ABC):
    """Base class for quantum gates."""

    def __init__(self, name: str, num_qubits: int, params: Optional[List[float]] = None):
        """
        Initialize a quantum gate.

        Args:
            name: Gate name
            num_qubits: Number of qubits this gate acts on
            params: Optional parameters (e.g., rotation angles)
        """
        self.name = name
        self.num_qubits = num_qubits
        self.params = params or []

    @abstractmethod
    def matrix(self) -> np.ndarray:
        """Return the unitary matrix representation of the gate."""
        pass

    @abstractmethod
    def apply(self, state: np.ndarray, qubits: List[int], num_qubits: int) -> np.ndarray:
        """
        Apply the gate to a quantum state.

        Args:
            state: Current quantum state (statevector or density matrix)
            qubits: List of qubit indices this gate acts on
            num_qubits: Total number of qubits in the system

        Returns:
            Updated quantum state
        """
        pass

    def __repr__(self) -> str:
        if self.params:
            return f"{self.name}({', '.join(map(str, self.params))})"
        return self.name

    def __str__(self) -> str:
        return self.__repr__()


class SingleQubitGate(Gate):
    """Base class for single-qubit gates."""

    def __init__(self, name: str, params: Optional[List[float]] = None):
        super().__init__(name, 1, params)

    def apply(self, state: np.ndarray, qubits: List[int], num_qubits: int) -> np.ndarray:
        """Apply single-qubit gate to statevector or density matrix."""
        if len(qubits) != 1:
            raise ValueError(f"{self.name} gate requires exactly 1 qubit, got {len(qubits)}")

        qubit = qubits[0]
        gate_matrix = self.matrix()

        # Check if state is statevector or density matrix
        if state.ndim == 1:
            # Statevector: |ψ⟩ -> U|ψ⟩
            return self._apply_to_statevector(state, gate_matrix, qubit, num_qubits)
        elif state.ndim == 2 and state.shape[0] == state.shape[1]:
            # Density matrix: ρ -> U ρ U†
            return self._apply_to_density_matrix(state, gate_matrix, qubit, num_qubits)
        else:
            raise ValueError(f"Invalid state shape: {state.shape}")

    def _apply_to_statevector(
        self, state: np.ndarray, gate_matrix: np.ndarray, qubit: int, num_qubits: int
    ) -> np.ndarray:
        """Apply gate to statevector."""
        # Reshape state to separate target qubit
        dim = 2 ** num_qubits
        if state.shape[0] != dim:
            raise ValueError(f"State dimension {state.shape[0]} doesn't match {dim} qubits")

        # Reshape to separate the target qubit
        state_reshaped = state.reshape([2] * num_qubits)
        gate_reshaped = gate_matrix.reshape(2, 2)

        # Apply gate using einsum
        indices = list(range(num_qubits))
        indices[qubit] = num_qubits  # Output index for target qubit
        state_reshaped = np.einsum(gate_reshaped, [qubit, num_qubits], state_reshaped, indices, indices)

        return state_reshaped.reshape(dim)

    def _apply_to_density_matrix(
        self, state: np.ndarray, gate_matrix: np.ndarray, qubit: int, num_qubits: int
    ) -> np.ndarray:
        """Apply gate to density matrix: ρ -> U ρ U†."""
        dim = 2 ** num_qubits
        if state.shape[0] != dim or state.shape[1] != dim:
            raise ValueError(f"Density matrix dimension {state.shape} doesn't match {dim} qubits")

        # Reshape to separate target qubit
        state_reshaped = state.reshape([2] * (2 * num_qubits))
        gate_reshaped = gate_matrix.reshape(2, 2)
        gate_dagger = gate_matrix.conj().T.reshape(2, 2)

        # Apply U on left, U† on right
        indices = list(range(2 * num_qubits))
        left_idx = qubit
        right_idx = qubit + num_qubits

        # U ρ
        temp = np.einsum(gate_reshaped, [left_idx, 2 * num_qubits], state_reshaped, indices, indices)
        # (U ρ) U†
        result = np.einsum(temp, indices, gate_dagger, [2 * num_qubits, right_idx], indices)

        return result.reshape(dim, dim)


class TwoQubitGate(Gate):
    """Base class for two-qubit gates."""

    def __init__(self, name: str, params: Optional[List[float]] = None):
        super().__init__(name, 2, params)

    def apply(self, state: np.ndarray, qubits: List[int], num_qubits: int) -> np.ndarray:
        """Apply two-qubit gate to statevector or density matrix."""
        if len(qubits) != 2:
            raise ValueError(f"{self.name} gate requires exactly 2 qubits, got {len(qubits)}")

        qubit1, qubit2 = qubits[0], qubits[1]
        gate_matrix = self.matrix()

        if state.ndim == 1:
            return self._apply_to_statevector(state, gate_matrix, qubit1, qubit2, num_qubits)
        elif state.ndim == 2 and state.shape[0] == state.shape[1]:
            return self._apply_to_density_matrix(state, gate_matrix, qubit1, qubit2, num_qubits)
        else:
            raise ValueError(f"Invalid state shape: {state.shape}")

    def _apply_to_statevector(
        self, state: np.ndarray, gate_matrix: np.ndarray, q1: int, q2: int, num_qubits: int
    ) -> np.ndarray:
        """Apply two-qubit gate to statevector."""
        dim = 2 ** num_qubits
        if state.shape[0] != dim:
            raise ValueError(f"State dimension {state.shape[0]} doesn't match {dim} qubits")

        state_reshaped = state.reshape([2] * num_qubits)
        gate_reshaped = gate_matrix.reshape(2, 2, 2, 2)

        indices = list(range(num_qubits))
        indices[q1] = num_qubits
        indices[q2] = num_qubits + 1

        state_reshaped = np.einsum(
            gate_reshaped, [q1, q2, num_qubits, num_qubits + 1], state_reshaped, indices, indices
        )

        return state_reshaped.reshape(dim)

    def _apply_to_density_matrix(
        self, state: np.ndarray, gate_matrix: np.ndarray, q1: int, q2: int, num_qubits: int
    ) -> np.ndarray:
        """Apply two-qubit gate to density matrix."""
        dim = 2 ** num_qubits
        if state.shape[0] != dim or state.shape[1] != dim:
            raise ValueError(f"Density matrix dimension {state.shape} doesn't match {dim} qubits")

        state_reshaped = state.reshape([2] * (2 * num_qubits))
        gate_reshaped = gate_matrix.reshape(2, 2, 2, 2)
        gate_dagger = gate_matrix.conj().T.reshape(2, 2, 2, 2)

        indices = list(range(2 * num_qubits))
        left_q1, left_q2 = q1, q2
        right_q1, right_q2 = q1 + num_qubits, q2 + num_qubits

        # U ρ
        temp = np.einsum(
            gate_reshaped,
            [left_q1, left_q2, 2 * num_qubits, 2 * num_qubits + 1],
            state_reshaped,
            indices,
            indices,
        )
        # (U ρ) U†
        result = np.einsum(
            temp,
            indices,
            gate_dagger,
            [2 * num_qubits, 2 * num_qubits + 1, right_q1, right_q2],
            indices,
        )

        return result.reshape(dim, dim)


# Standard single-qubit gates

class X(SingleQubitGate):
    """Pauli-X (NOT) gate."""

    def __init__(self):
        super().__init__("X")

    def matrix(self) -> np.ndarray:
        return np.array([[0, 1], [1, 0]], dtype=complex)


class Y(SingleQubitGate):
    """Pauli-Y gate."""

    def __init__(self):
        super().__init__("Y")

    def matrix(self) -> np.ndarray:
        return np.array([[0, -1j], [1j, 0]], dtype=complex)


class Z(SingleQubitGate):
    """Pauli-Z gate."""

    def __init__(self):
        super().__init__("Z")

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, -1]], dtype=complex)


class H(SingleQubitGate):
    """Hadamard gate."""

    def __init__(self):
        super().__init__("H")

    def matrix(self) -> np.ndarray:
        return (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)


class S(SingleQubitGate):
    """Phase gate (S gate, π/2 rotation around Z)."""

    def __init__(self):
        super().__init__("S")

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, 1j]], dtype=complex)


class T(SingleQubitGate):
    """T gate (π/4 rotation around Z)."""

    def __init__(self):
        super().__init__("T")

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)


class RX(SingleQubitGate):
    """Rotation around X-axis: RX(θ) = exp(-iθX/2)."""

    def __init__(self, theta: float):
        super().__init__("RX", [theta])
        self.theta = theta

    def matrix(self) -> np.ndarray:
        c = np.cos(self.theta / 2)
        s = np.sin(self.theta / 2)
        return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


class RY(SingleQubitGate):
    """Rotation around Y-axis: RY(θ) = exp(-iθY/2)."""

    def __init__(self, theta: float):
        super().__init__("RY", [theta])
        self.theta = theta

    def matrix(self) -> np.ndarray:
        c = np.cos(self.theta / 2)
        s = np.sin(self.theta / 2)
        return np.array([[c, -s], [s, c]], dtype=complex)


class RZ(SingleQubitGate):
    """Rotation around Z-axis: RZ(θ) = exp(-iθZ/2)."""

    def __init__(self, theta: float):
        super().__init__("RZ", [theta])
        self.theta = theta

    def matrix(self) -> np.ndarray:
        return np.array(
            [[np.exp(-1j * self.theta / 2), 0], [0, np.exp(1j * self.theta / 2)]], dtype=complex
        )


# Two-qubit gates

class CNOT(TwoQubitGate):
    """Controlled-NOT gate (CX)."""

    def __init__(self):
        super().__init__("CNOT")

    def matrix(self) -> np.ndarray:
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
            ],
            dtype=complex,
        )


class CZ(TwoQubitGate):
    """Controlled-Z gate."""

    def __init__(self):
        super().__init__("CZ")

    def matrix(self) -> np.ndarray:
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1],
            ],
            dtype=complex,
        )


class SWAP(TwoQubitGate):
    """SWAP gate."""

    def __init__(self):
        super().__init__("SWAP")

    def matrix(self) -> np.ndarray:
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
            ],
            dtype=complex,
        )


# Three-qubit gates

class Toffoli(Gate):
    """Toffoli gate (CCNOT)."""

    def __init__(self):
        super().__init__("Toffoli", 3)

    def matrix(self) -> np.ndarray:
        """8x8 matrix for Toffoli gate."""
        matrix = np.eye(8, dtype=complex)
        # Swap |110> and |111>
        matrix[6, 6] = 0
        matrix[6, 7] = 1
        matrix[7, 6] = 1
        matrix[7, 7] = 0
        return matrix

    def apply(self, state: np.ndarray, qubits: List[int], num_qubits: int) -> np.ndarray:
        """Apply Toffoli gate."""
        if len(qubits) != 3:
            raise ValueError(f"Toffoli gate requires exactly 3 qubits, got {len(qubits)}")

        gate_matrix = self.matrix()

        if state.ndim == 1:
            dim = 2 ** num_qubits
            if state.shape[0] != dim:
                raise ValueError(f"State dimension {state.shape[0]} doesn't match {dim} qubits")

            state_reshaped = state.reshape([2] * num_qubits)
            gate_reshaped = gate_matrix.reshape([2] * 6)  # 3 qubits in, 3 qubits out

            indices = list(range(num_qubits))
            for i, q in enumerate(qubits):
                indices[q] = num_qubits + i

            state_reshaped = np.einsum(
                gate_reshaped,
                qubits + [num_qubits, num_qubits + 1, num_qubits + 2],
                state_reshaped,
                indices,
                indices,
            )

            return state_reshaped.reshape(dim)
        else:
            raise NotImplementedError("Toffoli gate for density matrices not yet implemented")


class CustomGate(Gate):
    """Custom gate defined by a matrix."""

    def __init__(self, name: str, matrix: np.ndarray, num_qubits: int):
        """
        Initialize custom gate.

        Args:
            name: Gate name
            matrix: Unitary matrix (must be 2^n x 2^n for n qubits)
            num_qubits: Number of qubits
        """
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Gate matrix must be square")
        expected_dim = 2 ** num_qubits
        if matrix.shape[0] != expected_dim:
            raise ValueError(f"Matrix dimension {matrix.shape[0]} doesn't match {num_qubits} qubits")

        # Verify unitarity
        if not np.allclose(matrix @ matrix.conj().T, np.eye(expected_dim)):
            raise ValueError("Gate matrix must be unitary")

        super().__init__(name, num_qubits)
        self._matrix = matrix

    def matrix(self) -> np.ndarray:
        return self._matrix

    def apply(self, state: np.ndarray, qubits: List[int], num_qubits: int) -> np.ndarray:
        """Apply custom gate."""
        if len(qubits) != self.num_qubits:
            raise ValueError(
                f"{self.name} gate requires {self.num_qubits} qubits, got {len(qubits)}"
            )

        gate_matrix = self.matrix()

        if state.ndim == 1:
            # Statevector: apply gate matrix directly
            dim = 2 ** num_qubits
            if state.shape[0] != dim:
                raise ValueError(f"State dimension {state.shape[0]} doesn't match {dim} qubits")

            # For now, apply as full matrix (can be optimized later)
            return gate_matrix @ state
        elif state.ndim == 2:
            # Density matrix: ρ -> U ρ U†
            dim = 2 ** num_qubits
            if state.shape[0] != dim or state.shape[1] != dim:
                raise ValueError(f"Density matrix dimension {state.shape} doesn't match {dim} qubits")

            return gate_matrix @ state @ gate_matrix.conj().T
        else:
            raise ValueError(f"Invalid state shape: {state.shape}")


