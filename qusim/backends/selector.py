"""
Backend selection logic.

Automatically selects the best backend for a given circuit.
"""

from typing import Optional, List, Tuple
from qusim.backends.base import Backend
from qusim.backends.statevector import StatevectorBackend
from qusim.backends.density_matrix import DensityMatrixBackend
from qusim.backends.stabilizer import StabilizerBackend, detect_clifford_circuit
from qusim.backends.noisy_backend import NoisyBackend
from qusim.core.circuit import Circuit


class BackendSelector:
    """Automatically selects and manages backends."""

    def __init__(self):
        """Initialize backend selector."""
        self.available_backends = {
            "statevector": StatevectorBackend,
            "density_matrix": DensityMatrixBackend,
            "stabilizer": StabilizerBackend,
        }

    def select_backend(
        self,
        circuit: Circuit,
        use_noise: bool = False,
        noise_model: Optional[dict] = None,
        preferred_backend: Optional[str] = None,
    ) -> Tuple[Backend, str]:
        """
        Select the best backend for a circuit.

        Args:
            circuit: Circuit to execute
            use_noise: Whether to use noisy backend
            noise_model: Noise model (if use_noise is True)
            preferred_backend: User-specified backend preference

        Returns:
            (backend, explanation)
        """
        # Check user preference first
        if preferred_backend:
            if preferred_backend not in self.available_backends:
                raise ValueError(
                    f"Unknown backend: {preferred_backend}. Available: {list(self.available_backends.keys())}"
                )

            backend_class = self.available_backends[preferred_backend]
            backend = backend_class()

            if use_noise:
                backend = NoisyBackend(base_backend=backend, noise_model=noise_model)

            return (
                backend,
                f"Using user-specified backend: {preferred_backend}",
            )

        # Auto-select based on circuit properties
        # Check if Clifford circuit
        is_clifford, reason = detect_clifford_circuit(circuit)

        if is_clifford:
            backend = StabilizerBackend()
            explanation = "Circuit is Clifford - using Stabilizer backend (efficient for Clifford circuits)"
        else:
            # Check memory requirements
            dim = 2 ** circuit.num_qubits
            memory_gb = (dim * 16) / (1024 ** 3)

            if memory_gb < 0.1:  # < 100MB
                backend = StatevectorBackend()
                explanation = f"Using Statevector backend (circuit requires ~{memory_gb:.2f}GB memory)"
            else:
                # For larger circuits, might want to use tensor network or other optimizations
                # For now, still use statevector with warning
                backend = StatevectorBackend()
                explanation = f"Using Statevector backend (circuit requires ~{memory_gb:.2f}GB memory - consider optimizations)"

        if use_noise:
            backend = NoisyBackend(base_backend=backend, noise_model=noise_model)
            explanation += " with noise model"

        return (backend, explanation)

    def get_backend_info(self, backend_name: str) -> dict:
        """
        Get information about a backend.

        Args:
            backend_name: Name of backend

        Returns:
            Dictionary with backend information
        """
        if backend_name not in self.available_backends:
            raise ValueError(f"Unknown backend: {backend_name}")

        backend_class = self.available_backends[backend_name]
        backend = backend_class()

        info = {
            "name": backend_name,
            "can_execute": backend.can_execute,
            "description": self._get_backend_description(backend_name),
        }

        return info

    def _get_backend_description(self, backend_name: str) -> str:
        """Get human-readable description of backend."""
        descriptions = {
            "statevector": "Full statevector simulation. Supports any circuit but memory scales as 2^n.",
            "density_matrix": "Density matrix simulation. Supports mixed states and noise. Memory scales as 4^n.",
            "stabilizer": "Stabilizer formalism. Efficient for Clifford circuits only. Memory scales as n^2.",
        }
        return descriptions.get(backend_name, "Unknown backend")


