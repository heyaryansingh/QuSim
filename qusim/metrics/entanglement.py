"""
Entanglement measures for quantum states.

Includes Von Neumann entropy, mutual information, Schmidt decomposition, and more.
"""

import numpy as np
from typing import List, Tuple, Optional
from qusim.core.state import QuantumState
from qusim.visualization.bloch import reduced_density_matrix


def von_neumann_entropy(
    state: QuantumState, qubits: Optional[List[int]] = None
) -> float:
    """
    Calculate Von Neumann entropy: S(ρ) = -Tr(ρ log ρ).

    Args:
        state: Quantum state
        qubits: Optional qubit subset (if None, uses full state)

    Returns:
        Entropy in bits
    """
    if qubits is not None:
        rho = reduced_density_matrix(state, qubits)
    else:
        if state.is_density_matrix:
            rho = state.state
        else:
            rho = state.to_density_matrix().state

    # Calculate eigenvalues
    eigenvals = np.linalg.eigvalsh(rho)
    eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical zeros

    # Calculate entropy: -Σ λ_i log_2(λ_i)
    if len(eigenvals) == 0:
        return 0.0

    entropy = -np.sum(eigenvals * np.log2(eigenvals))
    return np.real(entropy)


def mutual_information(
    state: QuantumState, qubits_a: List[int], qubits_b: List[int]
) -> float:
    """
    Calculate mutual information: I(A:B) = S(ρ_A) + S(ρ_B) - S(ρ_AB).

    Args:
        state: Quantum state
        qubits_a: Qubits in subsystem A
        qubits_b: Qubits in subsystem B

    Returns:
        Mutual information in bits
    """
    # Check for overlap
    if set(qubits_a) & set(qubits_b):
        raise ValueError("Subsystems A and B must be disjoint")

    # Entropy of subsystem A
    rho_a = reduced_density_matrix(state, qubits_a)
    s_a = von_neumann_entropy(QuantumState(rho_a, len(qubits_a), is_density_matrix=True))

    # Entropy of subsystem B
    rho_b = reduced_density_matrix(state, qubits_b)
    s_b = von_neumann_entropy(QuantumState(rho_b, len(qubits_b), is_density_matrix=True))

    # Entropy of combined system
    qubits_ab = sorted(qubits_a + qubits_b)
    rho_ab = reduced_density_matrix(state, qubits_ab)
    s_ab = von_neumann_entropy(QuantumState(rho_ab, len(qubits_ab), is_density_matrix=True))

    # Mutual information
    return s_a + s_b - s_ab


def schmidt_decomposition(
    state: QuantumState, qubits_a: List[int], qubits_b: List[int]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform Schmidt decomposition: |ψ⟩ = Σ_i λ_i |i_A⟩ ⊗ |i_B⟩.

    Args:
        state: Quantum state (must be pure)
        qubits_a: Qubits in subsystem A
        qubits_b: Qubits in subsystem B

    Returns:
        (schmidt_coeffs, basis_a, basis_b) where:
        - schmidt_coeffs: Schmidt coefficients (singular values)
        - basis_a: Basis states for subsystem A
        - basis_b: Basis states for subsystem B
    """
    # Check for overlap
    if set(qubits_a) & set(qubits_b):
        raise ValueError("Subsystems A and B must be disjoint")

    # Convert to statevector if needed
    if state.is_density_matrix:
        # Check if pure
        purity = np.real(np.trace(state.state @ state.state))
        if not np.isclose(purity, 1.0, atol=1e-6):
            raise ValueError("Schmidt decomposition requires a pure state")
        statevector = state.to_statevector().state
    else:
        statevector = state.state

    num_qubits = state.num_qubits
    dim_a = 2 ** len(qubits_a)
    dim_b = 2 ** len(qubits_b)

    # Reshape statevector to separate subsystems
    state_reshaped = statevector.reshape([2] * num_qubits)

    # Create matrix with A indices as rows and B indices as columns
    # This requires careful indexing
    matrix = np.zeros((dim_a, dim_b), dtype=complex)

    for i in range(dim_a):
        for j in range(dim_b):
            # Convert indices to qubit states
            a_bits = format(i, f"0{len(qubits_a)}b")
            b_bits = format(j, f"0{len(qubits_b)}b")

            # Create full index
            full_index = [0] * num_qubits
            for idx, q in enumerate(qubits_a):
                full_index[q] = int(a_bits[idx])
            for idx, q in enumerate(qubits_b):
                full_index[q] = int(b_bits[idx])

            # Convert to flat index
            flat_idx = sum(2 ** (num_qubits - 1 - k) * full_index[k] for k in range(num_qubits))
            matrix[i, j] = statevector[flat_idx]

    # Perform SVD
    U, s, Vh = np.linalg.svd(matrix, full_matrices=False)

    return s, U, Vh.conj().T


def schmidt_number(state: QuantumState, qubits_a: List[int], qubits_b: List[int]) -> int:
    """
    Calculate Schmidt number (number of non-zero Schmidt coefficients).

    Args:
        state: Quantum state (must be pure)
        qubits_a: Qubits in subsystem A
        qubits_b: Qubits in subsystem B

    Returns:
        Schmidt number
    """
    schmidt_coeffs, _, _ = schmidt_decomposition(state, qubits_a, qubits_b)
    # Count non-zero coefficients (above threshold)
    return np.sum(schmidt_coeffs > 1e-10)


def concurrence(state: QuantumState, qubit1: int, qubit2: int) -> float:
    """
    Calculate concurrence for two qubits.

    Concurrence is an entanglement measure for 2-qubit systems:
    C(ρ) = max(0, λ1 - λ2 - λ3 - λ4) where λi are eigenvalues of
    R = √(√ρ ρ̃ √ρ) in decreasing order, and ρ̃ = (σ_y ⊗ σ_y) ρ* (σ_y ⊗ σ_y).

    Args:
        state: Quantum state
        qubit1: First qubit index
        qubit2: Second qubit index

    Returns:
        Concurrence (0 ≤ C ≤ 1)
    """
    # Get reduced density matrix for two qubits
    rho = reduced_density_matrix(state, [qubit1, qubit2])

    # Pauli-Y matrix
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_y_tensor = np.kron(sigma_y, sigma_y)

    # Calculate ρ̃ = (σ_y ⊗ σ_y) ρ* (σ_y ⊗ σ_y)
    rho_tilde = sigma_y_tensor @ rho.conj() @ sigma_y_tensor

    # Calculate R = √(√ρ ρ̃ √ρ)
    sqrt_rho = _matrix_sqrt(rho)
    product = sqrt_rho @ rho_tilde @ sqrt_rho
    R = _matrix_sqrt(product)

    # Calculate eigenvalues
    eigenvals = np.linalg.eigvalsh(R)
    eigenvals = np.sort(eigenvals)[::-1]  # Sort in descending order

    # Concurrence
    concurrence_val = max(0.0, eigenvals[0] - eigenvals[1] - eigenvals[2] - eigenvals[3])

    return np.real(concurrence_val)


def _matrix_sqrt(matrix: np.ndarray) -> np.ndarray:
    """Calculate matrix square root."""
    eigenvals, eigenvecs = np.linalg.eigh(matrix)
    eigenvals = np.maximum(eigenvals, 0.0)  # Remove negative eigenvalues
    sqrt_eigenvals = np.sqrt(eigenvals)
    return eigenvecs @ np.diag(sqrt_eigenvals) @ eigenvecs.conj().T


def entanglement_entropy_evolution(
    state_history: List[QuantumState], qubits: List[int]
) -> List[float]:
    """
    Calculate entanglement entropy evolution over time.

    Args:
        state_history: List of states over time
        qubits: Qubit subset to calculate entropy for

    Returns:
        List of entropy values
    """
    entropies = []
    for state in state_history:
        entropy = von_neumann_entropy(state, qubits)
        entropies.append(entropy)
    return entropies


def all_pairwise_mutual_information(state: QuantumState) -> np.ndarray:
    """
    Calculate mutual information for all pairs of qubits.

    Args:
        state: Quantum state

    Returns:
        Matrix where M[i, j] = I(qubit_i : qubit_j)
    """
    num_qubits = state.num_qubits
    mi_matrix = np.zeros((num_qubits, num_qubits))

    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            mi = mutual_information(state, [i], [j])
            mi_matrix[i, j] = mi
            mi_matrix[j, i] = mi  # Symmetric

    return mi_matrix


