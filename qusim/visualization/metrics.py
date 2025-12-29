"""
Visualization utilities for quantum metrics.
"""

import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Optional
from qusim.core.state import QuantumState
from qusim.core.execution import measurement_counts


def plot_measurement_histogram(
    measurements: List[Dict[str, int]],
    title: Optional[str] = None,
) -> go.Figure:
    """
    Plot measurement histogram.

    Args:
        measurements: List of measurement results
        title: Plot title

    Returns:
        Plotly figure
    """
    counts = measurement_counts(measurements)

    # Sort by bitstring
    sorted_counts = sorted(counts.items(), key=lambda x: int(x[0], 2))

    bitstrings = [item[0] for item in sorted_counts]
    values = [item[1] for item in sorted_counts]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=bitstrings,
            y=values,
            name="Counts",
            marker_color="steelblue",
        )
    )

    fig.update_layout(
        title=title or "Measurement Histogram",
        xaxis_title="Bitstring",
        yaxis_title="Count",
        showlegend=False,
    )

    return fig


def plot_probability_distribution(
    state: QuantumState,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Plot probability distribution over basis states.

    Args:
        state: Quantum state
        title: Plot title

    Returns:
        Plotly figure
    """
    probabilities = state.get_probabilities()
    num_qubits = state.num_qubits

    # Create basis state labels
    basis_labels = [format(i, f"0{num_qubits}b") for i in range(len(probabilities))]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=basis_labels,
            y=probabilities,
            name="Probability",
            marker_color="steelblue",
        )
    )

    fig.update_layout(
        title=title or f"Probability Distribution ({num_qubits} qubits)",
        xaxis_title="Basis State",
        yaxis_title="Probability",
        yaxis_range=[0, 1.1],
        showlegend=False,
    )

    return fig


def plot_expectation_values(
    state: QuantumState,
    observables: List[str],
    qubits: Optional[List[int]] = None,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Plot expectation values of multiple observables.

    Args:
        state: Quantum state
        observables: List of Pauli strings (e.g., ["X", "Y", "Z"])
        qubits: Qubit indices (if None, uses first qubit for each observable)
        title: Plot title

    Returns:
        Plotly figure
    """
    from qusim.core.execution import pauli_expectation

    if qubits is None:
        qubits = [0] * len(observables)

    if len(qubits) != len(observables):
        raise ValueError(
            f"Number of qubits ({len(qubits)}) doesn't match number of observables ({len(observables)})"
        )

    expectation_values = []
    for obs, q in zip(observables, qubits):
        exp_val = pauli_expectation(state, obs, [q] if isinstance(q, int) else q)
        expectation_values.append(exp_val)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=observables,
            y=expectation_values,
            name="Expectation Value",
            marker_color="steelblue",
        )
    )

    fig.update_layout(
        title=title or "Expectation Values",
        xaxis_title="Observable",
        yaxis_title="⟨O⟩",
        yaxis_range=[-1.1, 1.1],
        showlegend=False,
    )

    return fig


