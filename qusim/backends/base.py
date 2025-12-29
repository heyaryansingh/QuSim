"""
Base classes for quantum simulation backends.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import numpy as np
from qusim.core.circuit import Circuit
from qusim.core.state import QuantumState


class Backend(ABC):
    """Base class for quantum simulation backends."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize backend.

        Args:
            seed: Random seed for deterministic execution
        """
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)

    @abstractmethod
    def execute(
        self,
        circuit: Circuit,
        initial_state: Optional[np.ndarray] = None,
        shots: int = 1,
        return_state_history: bool = False,
    ) -> "ExecutionResult":
        """
        Execute a quantum circuit.

        Args:
            circuit: Circuit to execute
            initial_state: Initial state (default: |00...0⟩)
            shots: Number of measurement shots
            return_state_history: Whether to return state at each step

        Returns:
            ExecutionResult with final state and measurements
        """
        pass

    @abstractmethod
    def can_execute(self, circuit: Circuit) -> tuple[bool, Optional[str]]:
        """
        Check if this backend can execute the circuit.

        Returns:
            (can_execute, reason_if_not)
        """
        pass

    def get_name(self) -> str:
        """Get backend name."""
        return self.__class__.__name__


class ExecutionResult:
    """Result of circuit execution."""

    def __init__(
        self,
        state: QuantumState,
        measurements: List[Dict[str, int]],
        state_history: Optional[List[QuantumState]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize execution result.

        Args:
            state: Final quantum state
            measurements: List of measurement results (one dict per shot)
            state_history: State at each execution step (if requested)
            metadata: Additional execution metadata
        """
        self.state = state
        self.measurements = measurements
        self.state_history = state_history or []
        self.metadata = metadata or {}

    def get_counts(self) -> Dict[str, int]:
        """
        Get measurement counts (for histogram).

        Returns:
            Dictionary mapping bitstrings to counts
        """
        counts: Dict[str, int] = {}
        for measurement in self.measurements:
            # Convert measurement dict to bitstring
            bits = []
            for i in sorted(measurement.keys()):
                bits.append(str(measurement[i]))
            bitstring = "".join(bits)
            counts[bitstring] = counts.get(bitstring, 0) + 1
        return counts

    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities."""
        return self.state.get_probabilities()


