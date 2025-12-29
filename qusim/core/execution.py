"""
Execution utilities for quantum circuits.
"""

import numpy as np
from typing import Dict, List, Optional
from qusim.core.state import QuantumState


def sample_measurements(
    state: QuantumState, shots: int, seed: Optional[int] = None
) -> List[Dict[str, int]]:
    """
    Sample measurement outcomes from a quantum state.

    Args:
        state: Quantum state
        shots: Number of measurement shots
        seed: Random seed

    Returns:
        List of measurement results (one dict per shot)
    """
    if seed is not None:
        np.random.seed(seed)

    probabilities = state.get_probabilities()
    num_qubits = state.num_qubits

    measurements = []
    for _ in range(shots):
        # Sample outcome
        outcome_idx = np.random.choice(len(probabilities), p=probabilities)
        bitstring = format(outcome_idx, f"0{num_qubits}b")

        # Convert to measurement dict
        measurement = {str(i): int(bit) for i, bit in enumerate(bitstring)}
        measurements.append(measurement)

    return measurements


def measurement_counts(measurements: List[Dict[str, int]]) -> Dict[str, int]:
    """
    Convert measurement results to counts histogram.

    Args:
        measurements: List of measurement results

    Returns:
        Dictionary mapping bitstrings to counts
    """
    counts: Dict[str, int] = {}
    for measurement in measurements:
        # Convert to bitstring
        bits = []
        for i in sorted(measurement.keys(), key=int):
            bits.append(str(measurement[i]))
        bitstring = "".join(bits)
        counts[bitstring] = counts.get(bitstring, 0) + 1
    return counts


def expectation_value(
    state: QuantumState, observable: np.ndarray, qubits: Optional[List[int]] = None
) -> float:
    """
    Calculate expectation value of an observable.

    Args:
        state: Quantum state
        observable: Hermitian operator (matrix)
        qubits: Optional qubit subset (if None, uses full state)

    Returns:
        Expectation value: ⟨O⟩ = Tr(ρ O) or ⟨ψ|O|ψ⟩
    """
    if qubits is not None:
        # Calculate reduced density matrix
        from qusim.visualization.bloch import reduced_density_matrix

        if state.is_density_matrix:
            rho = reduced_density_matrix(state, qubits)
        else:
            rho = reduced_density_matrix(state.to_density_matrix(), qubits)
    else:
        if state.is_density_matrix:
            rho = state.state
        else:
            rho = state.to_density_matrix().state

    return np.real(np.trace(rho @ observable))


def pauli_expectation(
    state: QuantumState, pauli_string: str, qubits: Optional[List[int]] = None
) -> float:
    """
    Calculate expectation value of a Pauli operator.

    Args:
        state: Quantum state
        pauli_string: String like "X", "Y", "Z", "XX", "XY", etc.
        qubits: Qubit indices (if None, uses first len(pauli_string) qubits)

    Returns:
        Expectation value
    """
    if qubits is None:
        qubits = list(range(len(pauli_string)))

    if len(qubits) != len(pauli_string):
        raise ValueError(
            f"Number of qubits ({len(qubits)}) doesn't match Pauli string length ({len(pauli_string)})"
        )

    # Pauli matrices
    pauli_matrices = {
        "I": np.array([[1, 0], [0, 1]], dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }

    # Build tensor product
    observable = pauli_matrices[pauli_string[0].upper()]
    for pauli in pauli_string[1:]:
        observable = np.kron(observable, pauli_matrices[pauli.upper()])

    return expectation_value(state, observable, qubits)


