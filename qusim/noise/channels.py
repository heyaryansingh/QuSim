"""
Quantum noise channel implementations.

All channels are represented using Kraus operators.
"""

import numpy as np
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from qusim.noise.kraus import apply_kraus_operators, tensor_kraus_operators


class NoiseChannel(ABC):
    """Base class for quantum noise channels."""

    def __init__(self, name: str, params: Optional[Dict[str, float]] = None):
        """
        Initialize noise channel.

        Args:
            name: Channel name
            params: Channel parameters
        """
        self.name = name
        self.params = params or {}

    @abstractmethod
    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """
        Get Kraus operators for the channel.

        Args:
            num_qubits: Number of qubits (for multi-qubit channels)

        Returns:
            List of Kraus operators
        """
        pass

    def apply(self, rho: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
        """
        Apply noise channel to a density matrix.

        Args:
            rho: Density matrix
            qubit: Qubit index to apply noise to
            num_qubits: Total number of qubits

        Returns:
            Transformed density matrix
        """
        # Get single-qubit Kraus operators
        kraus_ops = self.kraus_operators(num_qubits=1)

        # Embed into multi-qubit space
        embedded_ops = tensor_kraus_operators(kraus_ops, num_qubits, qubit)

        # Apply channel
        return apply_kraus_operators(rho, embedded_ops)

    def __repr__(self) -> str:
        if self.params:
            params_str = ", ".join(f"{k}={v}" for k, v in self.params.items())
            return f"{self.name}({params_str})"
        return self.name


class DepolarizingChannel(NoiseChannel):
    """
    Depolarizing channel: random Pauli errors with probability p.

    ε(ρ) = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)
    """

    def __init__(self, p: float):
        """
        Initialize depolarizing channel.

        Args:
            p: Error probability (0 ≤ p ≤ 1)
        """
        if not 0 <= p <= 1:
            raise ValueError(f"Error probability p must be in [0, 1], got {p}")

        super().__init__("Depolarizing", {"p": p})
        self.p = p

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Get Kraus operators for depolarizing channel."""
        if num_qubits != 1:
            raise ValueError("Depolarizing channel is single-qubit only")

        sqrt_p3 = np.sqrt(self.p / 3)
        sqrt_1_p = np.sqrt(1 - self.p)

        # Identity
        K0 = sqrt_1_p * np.eye(2, dtype=complex)

        # Pauli errors
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        Z = np.array([[1, 0], [0, -1]], dtype=complex)

        K1 = sqrt_p3 * X
        K2 = sqrt_p3 * Y
        K3 = sqrt_p3 * Z

        return [K0, K1, K2, K3]


class AmplitudeDampingChannel(NoiseChannel):
    """
    Amplitude damping channel: energy dissipation.

    Models spontaneous emission: |1⟩ -> |0⟩ with probability γ.
    """

    def __init__(self, gamma: float):
        """
        Initialize amplitude damping channel.

        Args:
            gamma: Damping parameter (0 ≤ γ ≤ 1)
        """
        if not 0 <= gamma <= 1:
            raise ValueError(f"Damping parameter γ must be in [0, 1], got {gamma}")

        super().__init__("AmplitudeDamping", {"gamma": gamma})
        self.gamma = gamma

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Get Kraus operators for amplitude damping."""
        if num_qubits != 1:
            raise ValueError("Amplitude damping channel is single-qubit only")

        K0 = np.array([[1, 0], [0, np.sqrt(1 - self.gamma)]], dtype=complex)
        K1 = np.array([[0, np.sqrt(self.gamma)], [0, 0]], dtype=complex)

        return [K0, K1]


class PhaseDampingChannel(NoiseChannel):
    """
    Phase damping channel: loss of phase coherence.

    Models dephasing without energy loss.
    """

    def __init__(self, gamma: float):
        """
        Initialize phase damping channel.

        Args:
            gamma: Damping parameter (0 ≤ γ ≤ 1)
        """
        if not 0 <= gamma <= 1:
            raise ValueError(f"Damping parameter γ must be in [0, 1], got {gamma}")

        super().__init__("PhaseDamping", {"gamma": gamma})
        self.gamma = gamma

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Get Kraus operators for phase damping."""
        if num_qubits != 1:
            raise ValueError("Phase damping channel is single-qubit only")

        sqrt_1_gamma = np.sqrt(1 - self.gamma)
        sqrt_gamma = np.sqrt(self.gamma)

        K0 = sqrt_1_gamma * np.eye(2, dtype=complex)
        K1 = sqrt_gamma * np.array([[1, 0], [0, 0]], dtype=complex)
        K2 = sqrt_gamma * np.array([[0, 0], [0, 1]], dtype=complex)

        return [K0, K1, K2]


class BitFlipChannel(NoiseChannel):
    """Bit-flip channel: X error with probability p."""

    def __init__(self, p: float):
        """
        Initialize bit-flip channel.

        Args:
            p: Error probability (0 ≤ p ≤ 1)
        """
        if not 0 <= p <= 1:
            raise ValueError(f"Error probability p must be in [0, 1], got {p}")

        super().__init__("BitFlip", {"p": p})
        self.p = p

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Get Kraus operators for bit-flip channel."""
        if num_qubits != 1:
            raise ValueError("Bit-flip channel is single-qubit only")

        sqrt_1_p = np.sqrt(1 - self.p)
        sqrt_p = np.sqrt(self.p)

        X = np.array([[0, 1], [1, 0]], dtype=complex)

        K0 = sqrt_1_p * np.eye(2, dtype=complex)
        K1 = sqrt_p * X

        return [K0, K1]


class PhaseFlipChannel(NoiseChannel):
    """Phase-flip channel: Z error with probability p."""

    def __init__(self, p: float):
        """
        Initialize phase-flip channel.

        Args:
            p: Error probability (0 ≤ p ≤ 1)
        """
        if not 0 <= p <= 1:
            raise ValueError(f"Error probability p must be in [0, 1], got {p}")

        super().__init__("PhaseFlip", {"p": p})
        self.p = p

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Get Kraus operators for phase-flip channel."""
        if num_qubits != 1:
            raise ValueError("Phase-flip channel is single-qubit only")

        sqrt_1_p = np.sqrt(1 - self.p)
        sqrt_p = np.sqrt(self.p)

        Z = np.array([[1, 0], [0, -1]], dtype=complex)

        K0 = sqrt_1_p * np.eye(2, dtype=complex)
        K1 = sqrt_p * Z

        return [K0, K1]


class CustomNoiseChannel(NoiseChannel):
    """Custom noise channel defined by Kraus operators."""

    def __init__(self, name: str, kraus_operators: List[np.ndarray]):
        """
        Initialize custom noise channel.

        Args:
            name: Channel name
            kraus_operators: List of Kraus operators (must satisfy completeness)
        """
        from qusim.noise.kraus import verify_kraus_operators

        if not verify_kraus_operators(kraus_operators):
            raise ValueError("Kraus operators do not satisfy completeness condition")

        super().__init__(name)
        self._kraus_ops = kraus_operators

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Get Kraus operators."""
        if num_qubits != 1:
            raise ValueError("Custom channel must be single-qubit for now")

        return self._kraus_ops


class CrosstalkChannel(NoiseChannel):
    """
    Crosstalk channel: correlated noise between qubits.

    Applies noise to multiple qubits simultaneously.
    """

    def __init__(self, base_channel: NoiseChannel, qubits: List[int], correlation: float = 1.0):
        """
        Initialize crosstalk channel.

        Args:
            base_channel: Base noise channel to apply
            qubits: Qubit indices affected
            correlation: Correlation strength (0 ≤ correlation ≤ 1)
        """
        if not 0 <= correlation <= 1:
            raise ValueError(f"Correlation must be in [0, 1], got {correlation}")

        super().__init__("Crosstalk", {"correlation": correlation})
        self.base_channel = base_channel
        self.qubits = qubits
        self.correlation = correlation

    def apply(self, rho: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
        """
        Apply crosstalk noise.

        Note: This is a simplified model. For full crosstalk, we'd need
        to apply correlated noise to all qubits simultaneously.
        """
        # For now, apply base channel with correlation factor
        result = rho
        for q in self.qubits:
            if q == qubit:
                # Apply full noise
                result = self.base_channel.apply(result, q, num_qubits)
            elif np.random.random() < self.correlation:
                # Apply correlated noise
                result = self.base_channel.apply(result, q, num_qubits)

        return result

    def kraus_operators(self, num_qubits: int = 1) -> List[np.ndarray]:
        """Crosstalk doesn't have simple Kraus representation."""
        raise NotImplementedError("Crosstalk channel requires multi-qubit Kraus operators")


