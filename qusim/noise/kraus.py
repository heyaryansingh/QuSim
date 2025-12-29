"""
Kraus operator utilities for quantum noise channels.

A quantum channel is represented by Kraus operators {K_i} such that:
    ε(ρ) = Σ_i K_i ρ K_i†
"""

import numpy as np
from typing import List, Optional


def apply_kraus_operators(rho: np.ndarray, kraus_ops: List[np.ndarray]) -> np.ndarray:
    """
    Apply a quantum channel defined by Kraus operators.

    Args:
        rho: Density matrix
        kraus_ops: List of Kraus operators

    Returns:
        Transformed density matrix: Σ_i K_i ρ K_i†
    """
    result = np.zeros_like(rho)
    for K in kraus_ops:
        result += K @ rho @ K.conj().T
    return result


def verify_kraus_operators(kraus_ops: List[np.ndarray]) -> bool:
    """
    Verify that Kraus operators satisfy completeness: Σ_i K_i† K_i = I.

    Args:
        kraus_ops: List of Kraus operators

    Returns:
        True if valid
    """
    if not kraus_ops:
        return False

    dim = kraus_ops[0].shape[0]
    identity = np.eye(dim, dtype=complex)

    sum_kraus = np.zeros((dim, dim), dtype=complex)
    for K in kraus_ops:
        sum_kraus += K.conj().T @ K

    return np.allclose(sum_kraus, identity)


def tensor_kraus_operators(
    kraus_ops: List[np.ndarray], num_qubits: int, target_qubit: int
) -> List[np.ndarray]:
    """
    Embed single-qubit Kraus operators into multi-qubit space.

    Args:
        kraus_ops: Single-qubit Kraus operators
        num_qubits: Total number of qubits
        target_qubit: Qubit index to apply noise to

    Returns:
        Multi-qubit Kraus operators
    """
    dim = 2 ** num_qubits
    embedded_ops = []

    for K in kraus_ops:
        # Start with identity
        embedded = np.eye(2, dtype=complex)

        # Build tensor product
        for q in range(num_qubits):
            if q == target_qubit:
                embedded = np.kron(embedded, K)
            else:
                embedded = np.kron(embedded, np.eye(2, dtype=complex))

        embedded_ops.append(embedded)

    return embedded_ops


