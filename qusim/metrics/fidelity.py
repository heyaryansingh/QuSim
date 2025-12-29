"""
State fidelity calculations.

Fidelity measures how close two quantum states are.
"""

import numpy as np
from qusim.core.state import QuantumState


def state_fidelity(state1: QuantumState, state2: QuantumState) -> float:
    """
    Calculate fidelity between two quantum states.

    For pure states: F(|ψ⟩, |φ⟩) = |⟨ψ|φ⟩|²
    For mixed states: F(ρ, σ) = Tr(√(√ρ σ √ρ))²

    Args:
        state1: First quantum state
        state2: Second quantum state

    Returns:
        Fidelity (0 ≤ F ≤ 1, where 1 means identical states)
    """
    # Convert both to density matrices
    if not state1.is_density_matrix:
        rho1 = state1.to_density_matrix().state
    else:
        rho1 = state1.state

    if not state2.is_density_matrix:
        rho2 = state2.to_density_matrix().state
    else:
        rho2 = state2.state

    return density_matrix_fidelity(rho1, rho2)


def density_matrix_fidelity(rho1: np.ndarray, rho2: np.ndarray) -> float:
    """
    Calculate fidelity between two density matrices.

    F(ρ, σ) = Tr(√(√ρ σ √ρ))²

    Args:
        rho1: First density matrix
        rho2: Second density matrix

    Returns:
        Fidelity
    """
    # Handle pure states efficiently
    if np.allclose(rho1, rho1.conj().T @ rho1):
        # rho1 is pure
        eigenvals, eigenvecs = np.linalg.eigh(rho1)
        max_idx = np.argmax(eigenvals)
        psi1 = eigenvecs[:, max_idx]

        if np.allclose(rho2, rho2.conj().T @ rho2):
            # Both pure
            eigenvals2, eigenvecs2 = np.linalg.eigh(rho2)
            max_idx2 = np.argmax(eigenvals2)
            psi2 = eigenvecs2[:, max_idx2]
            return abs(np.vdot(psi1, psi2)) ** 2
        else:
            # rho1 pure, rho2 mixed
            return np.real(psi1.conj() @ rho2 @ psi1)

    if np.allclose(rho2, rho2.conj().T @ rho2):
        # rho2 is pure
        eigenvals, eigenvecs = np.linalg.eigh(rho2)
        max_idx = np.argmax(eigenvals)
        psi2 = eigenvecs[:, max_idx]
        return np.real(psi2.conj() @ rho1 @ psi2)

    # Both mixed: use general formula
    # F(ρ, σ) = Tr(√(√ρ σ √ρ))²
    sqrt_rho1 = _matrix_sqrt(rho1)
    product = sqrt_rho1 @ rho2 @ sqrt_rho1
    sqrt_product = _matrix_sqrt(product)
    fidelity = np.real(np.trace(sqrt_product)) ** 2

    return max(0.0, min(1.0, fidelity))  # Clamp to [0, 1]


def _matrix_sqrt(matrix: np.ndarray) -> np.ndarray:
    """Calculate matrix square root: M = √A such that M² = A."""
    eigenvals, eigenvecs = np.linalg.eigh(matrix)
    # Remove negative eigenvalues (numerical errors)
    eigenvals = np.maximum(eigenvals, 0.0)
    sqrt_eigenvals = np.sqrt(eigenvals)
    return eigenvecs @ np.diag(sqrt_eigenvals) @ eigenvecs.conj().T


