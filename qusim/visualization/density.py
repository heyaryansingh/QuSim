"""
Density matrix visualization utilities.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List
from qusim.core.state import QuantumState


def plot_density_matrix(
    state: QuantumState,
    title: Optional[str] = None,
    show_imaginary: bool = True,
) -> go.Figure:
    """
    Plot density matrix as heatmap.

    Args:
        state: Quantum state (density matrix)
        title: Plot title
        show_imaginary: Whether to show imaginary part as separate plot

    Returns:
        Plotly figure
    """
    if not state.is_density_matrix:
        rho = state.to_density_matrix().state
    else:
        rho = state.state

    num_qubits = state.num_qubits
    dim = 2 ** num_qubits

    # Create basis state labels
    basis_labels = [format(i, f"0{num_qubits}b") for i in range(dim)]

    if show_imaginary:
        # Create subplots for real and imaginary parts
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=["Real Part", "Imaginary Part"],
            horizontal_spacing=0.15,
        )

        # Real part
        fig.add_trace(
            go.Heatmap(
                z=np.real(rho),
                x=basis_labels,
                y=basis_labels,
                colorscale="RdBu",
                zmid=0,
                colorbar=dict(title="Real", x=0.45),
            ),
            row=1,
            col=1,
        )

        # Imaginary part
        fig.add_trace(
            go.Heatmap(
                z=np.imag(rho),
                x=basis_labels,
                y=basis_labels,
                colorscale="RdBu",
                zmid=0,
                colorbar=dict(title="Imaginary", x=1.02),
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title=title or f"Density Matrix ({num_qubits} qubits)",
            width=1000,
            height=500,
        )
    else:
        # Only real part
        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                z=np.real(rho),
                x=basis_labels,
                y=basis_labels,
                colorscale="RdBu",
                zmid=0,
                colorbar=dict(title="Real"),
            )
        )
        fig.update_layout(
            title=title or f"Density Matrix ({num_qubits} qubits)",
            width=600,
            height=600,
        )

    return fig


def plot_purity_evolution(
    state_history: List[QuantumState],
    qubits: Optional[List[int]] = None,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Plot purity evolution over time.

    Args:
        state_history: List of states over time
        qubits: Optional qubit subset (if None, uses full state)
        title: Plot title

    Returns:
        Plotly figure
    """
    from qusim.backends.density_matrix import DensityMatrixBackend

    backend = DensityMatrixBackend()
    purities = []

    for state in state_history:
        if qubits is not None:
            # Calculate reduced density matrix
            from qusim.visualization.bloch import reduced_density_matrix

            rho = reduced_density_matrix(state, qubits)
            purity = np.real(np.trace(rho @ rho))
        else:
            if not state.is_density_matrix:
                rho = state.to_density_matrix().state
            else:
                rho = state.state
            purity = np.real(np.trace(rho @ rho))

        purities.append(purity)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(purities))),
            y=purities,
            mode="lines+markers",
            name="Purity",
            line=dict(width=2),
        )
    )

    fig.update_layout(
        title=title or "Purity Evolution",
        xaxis_title="Step",
        yaxis_title="Purity",
        yaxis_range=[0, 1.1],
    )

    return fig


def plot_entropy_evolution(
    state_history: List[QuantumState],
    qubits: Optional[List[int]] = None,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Plot Von Neumann entropy evolution over time.

    Args:
        state_history: List of states over time
        qubits: Optional qubit subset (if None, uses full state)
        title: Plot title

    Returns:
        Plotly figure
    """
    entropies = []

    for state in state_history:
        if qubits is not None:
            # Calculate reduced density matrix
            from qusim.visualization.bloch import reduced_density_matrix

            rho = reduced_density_matrix(state, qubits)
        else:
            if not state.is_density_matrix:
                rho = state.to_density_matrix().state
            else:
                rho = state.state

        # Calculate eigenvalues
        eigenvals = np.linalg.eigvalsh(rho)
        eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical zeros

        # Calculate entropy: -Σ λ_i log_2(λ_i)
        if len(eigenvals) > 0:
            entropy = -np.sum(eigenvals * np.log2(eigenvals))
        else:
            entropy = 0.0

        entropies.append(np.real(entropy))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(entropies))),
            y=entropies,
            mode="lines+markers",
            name="Von Neumann Entropy",
            line=dict(width=2),
        )
    )

    fig.update_layout(
        title=title or "Von Neumann Entropy Evolution",
        xaxis_title="Step",
        yaxis_title="Entropy (bits)",
    )

    return fig


def compare_states(
    ideal_state: QuantumState,
    noisy_state: QuantumState,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Compare ideal and noisy states side by side.

    Args:
        ideal_state: Ideal (pure) state
        noisy_state: Noisy (mixed) state
        title: Plot title

    Returns:
        Plotly figure
    """
    # Convert to density matrices
    if not ideal_state.is_density_matrix:
        rho_ideal = ideal_state.to_density_matrix().state
    else:
        rho_ideal = ideal_state.state

    if not noisy_state.is_density_matrix:
        rho_noisy = noisy_state.to_density_matrix().state
    else:
        rho_noisy = noisy_state.state

    num_qubits = ideal_state.num_qubits
    dim = 2 ** num_qubits
    basis_labels = [format(i, f"0{num_qubits}b") for i in range(dim)]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Ideal State", "Noisy State"],
        horizontal_spacing=0.15,
    )

    # Ideal state
    fig.add_trace(
        go.Heatmap(
            z=np.real(rho_ideal),
            x=basis_labels,
            y=basis_labels,
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(title="Real", x=0.45),
        ),
        row=1,
        col=1,
    )

    # Noisy state
    fig.add_trace(
        go.Heatmap(
            z=np.real(rho_noisy),
            x=basis_labels,
            y=basis_labels,
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(title="Real", x=1.02),
        ),
        row=1,
        col=2,
    )

    # Calculate fidelity
    from qusim.metrics.fidelity import state_fidelity

    fidelity = state_fidelity(ideal_state, noisy_state)

    fig.update_layout(
        title=title or f"State Comparison (Fidelity: {fidelity:.4f})",
        width=1000,
        height=500,
    )

    return fig


