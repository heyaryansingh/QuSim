"""
Bloch sphere visualization for single qubits.

Uses Plotly for interactive 3D visualization.
"""

import numpy as np
import plotly.graph_objects as go
from typing import List, Optional, Dict, Any
from qusim.core.state import QuantumState


def bloch_vector(state: QuantumState, qubit: int) -> np.ndarray:
    """
    Calculate Bloch vector for a single qubit.

    For a qubit in state |ψ⟩ = α|0⟩ + β|1⟩, the Bloch vector is:
        r = (⟨X⟩, ⟨Y⟩, ⟨Z⟩)
    where ⟨O⟩ = ⟨ψ|O|ψ⟩.

    Args:
        state: Quantum state
        qubit: Qubit index

    Returns:
        Bloch vector [x, y, z]
    """
    if state.is_density_matrix:
        # Extract reduced density matrix for this qubit
        rho = reduced_density_matrix(state, [qubit])
    else:
        # Convert to density matrix
        rho = state.to_density_matrix().state
        # Extract single qubit
        rho = reduced_density_matrix(
            QuantumState(rho, state.num_qubits, is_density_matrix=True), [qubit]
        )

    # Pauli matrices
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    # Calculate expectation values
    x = np.real(np.trace(rho @ X))
    y = np.real(np.trace(rho @ Y))
    z = np.real(np.trace(rho @ Z))

    return np.array([x, y, z])


def reduced_density_matrix(state: QuantumState, qubits: List[int]) -> np.ndarray:
    """
    Calculate reduced density matrix for specified qubits.

    Args:
        state: Full quantum state
        qubits: Qubit indices to keep

    Returns:
        Reduced density matrix
    """
    if not state.is_density_matrix:
        rho = state.to_density_matrix().state
    else:
        rho = state.state.copy()

    num_qubits = state.num_qubits
    dim = 2 ** num_qubits

    # Trace out qubits not in the list
    keep_qubits = sorted(qubits)
    trace_qubits = [q for q in range(num_qubits) if q not in keep_qubits]

    if not trace_qubits:
        return rho

    # Reshape density matrix
    rho_reshaped = rho.reshape([2] * (2 * num_qubits))

    # Trace out unwanted qubits
    # Sum over indices corresponding to traced-out qubits
    indices = list(range(2 * num_qubits))
    sum_indices = []
    for q in trace_qubits:
        sum_indices.append(q)  # Left index
        sum_indices.append(q + num_qubits)  # Right index

    # Contract over traced qubits
    result = np.trace(rho_reshaped, axis1=sum_indices[0], axis2=sum_indices[1])
    if len(sum_indices) > 2:
        for i in range(2, len(sum_indices), 2):
            result = np.trace(result, axis1=sum_indices[i], axis2=sum_indices[i + 1])

    # Reshape to matrix
    reduced_dim = 2 ** len(keep_qubits)
    return result.reshape(reduced_dim, reduced_dim)


def plot_bloch_sphere(
    state: QuantumState,
    qubit: int,
    title: Optional[str] = None,
    show_axes: bool = True,
) -> go.Figure:
    """
    Plot Bloch sphere for a single qubit.

    Args:
        state: Quantum state
        qubit: Qubit index
        title: Plot title
        show_axes: Whether to show coordinate axes

    Returns:
        Plotly figure
    """
    # Calculate Bloch vector
    vec = bloch_vector(state, qubit)

    # Create sphere
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    fig = go.Figure()

    # Add sphere surface
    fig.add_trace(
        go.Surface(
            x=x_sphere,
            y=y_sphere,
            z=z_sphere,
            opacity=0.3,
            colorscale="Blues",
            showscale=False,
        )
    )

    # Add Bloch vector
    fig.add_trace(
        go.Scatter3d(
            x=[0, vec[0]],
            y=[0, vec[1]],
            z=[0, vec[2]],
            mode="lines+markers",
            line=dict(color="red", width=5),
            marker=dict(size=5, color="red"),
            name="Bloch Vector",
        )
    )

    # Add axes if requested
    if show_axes:
        # X axis
        fig.add_trace(
            go.Scatter3d(
                x=[-1.2, 1.2],
                y=[0, 0],
                z=[0, 0],
                mode="lines",
                line=dict(color="gray", width=2, dash="dash"),
                showlegend=False,
            )
        )
        # Y axis
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[-1.2, 1.2],
                z=[0, 0],
                mode="lines",
                line=dict(color="gray", width=2, dash="dash"),
                showlegend=False,
            )
        )
        # Z axis
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, 0],
                z=[-1.2, 1.2],
                mode="lines",
                line=dict(color="gray", width=2, dash="dash"),
                showlegend=False,
            )
        )

        # Axis labels
        fig.add_trace(
            go.Scatter3d(
                x=[1.3, 0, 0],
                y=[0, 1.3, 0],
                z=[0, 0, 1.3],
                mode="text",
                text=["X", "Y", "Z"],
                textposition="middle center",
                showlegend=False,
            )
        )

    # Update layout
    fig.update_layout(
        title=title or f"Bloch Sphere - Qubit {qubit}",
        scene=dict(
            xaxis=dict(range=[-1.5, 1.5], title="X"),
            yaxis=dict(range=[-1.5, 1.5], title="Y"),
            zaxis=dict(range=[-1.5, 1.5], title="Z"),
            aspectmode="cube",
        ),
        width=600,
        height=600,
    )

    return fig


def plot_multiple_bloch_spheres(
    states: List[QuantumState],
    qubit: int,
    titles: Optional[List[str]] = None,
) -> go.Figure:
    """
    Plot multiple Bloch spheres side by side (for animation/evolution).

    Args:
        states: List of quantum states (evolution over time)
        qubit: Qubit index
        titles: Optional titles for each state

    Returns:
        Plotly figure with subplots
    """
    from plotly.subplots import make_subplots

    num_states = len(states)
    cols = min(4, num_states)
    rows = (num_states + cols - 1) // cols

    fig = make_subplots(
        rows=rows,
        cols=cols,
        specs=[[{"type": "scatter3d"} for _ in range(cols)] for _ in range(rows)],
        subplot_titles=titles or [f"Step {i}" for i in range(num_states)],
    )

    for i, state in enumerate(states):
        row = i // cols + 1
        col = i % cols + 1

        vec = bloch_vector(state, qubit)

        # Add Bloch vector
        fig.add_trace(
            go.Scatter3d(
                x=[0, vec[0]],
                y=[0, vec[1]],
                z=[0, vec[2]],
                mode="lines+markers",
                line=dict(color="red", width=5),
                marker=dict(size=5, color="red"),
                showlegend=(i == 0),
                name="Bloch Vector",
            ),
            row=row,
            col=col,
        )

        # Update subplot scene
        scene_name = f"scene{i+1}" if i > 0 else "scene"
        fig.update_layout(
            **{
                scene_name: dict(
                    xaxis=dict(range=[-1.5, 1.5]),
                    yaxis=dict(range=[-1.5, 1.5]),
                    zaxis=dict(range=[-1.5, 1.5]),
                    aspectmode="cube",
                )
            }
        )

    fig.update_layout(
        title=f"Bloch Sphere Evolution - Qubit {qubit}",
        height=200 * rows,
        width=200 * cols,
    )

    return fig


def animate_bloch_sphere(
    state_history: List[QuantumState],
    qubit: int,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Create animated Bloch sphere showing state evolution.

    Args:
        state_history: List of states over time
        qubit: Qubit index
        title: Plot title

    Returns:
        Plotly figure with animation
    """
    # Calculate Bloch vectors for all states
    vectors = [bloch_vector(state, qubit) for state in state_history]

    # Create sphere
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    fig = go.Figure()

    # Add sphere
    fig.add_trace(
        go.Surface(
            x=x_sphere,
            y=y_sphere,
            z=z_sphere,
            opacity=0.3,
            colorscale="Blues",
            showscale=False,
        )
    )

    # Add frames for animation
    frames = []
    for i, vec in enumerate(vectors):
        frames.append(
            go.Frame(
                data=[
                    go.Scatter3d(
                        x=[0, vec[0]],
                        y=[0, vec[1]],
                        z=[0, vec[2]],
                        mode="lines+markers",
                        line=dict(color="red", width=5),
                        marker=dict(size=5, color="red"),
                    )
                ],
                name=f"frame{i}",
            )
        )

    fig.frames = frames

    # Add initial vector
    if vectors:
        fig.add_trace(
            go.Scatter3d(
                x=[0, vectors[0][0]],
                y=[0, vectors[0][1]],
                z=[0, vectors[0][2]],
                mode="lines+markers",
                line=dict(color="red", width=5),
                marker=dict(size=5, color="red"),
                name="Bloch Vector",
            )
        )

    # Add animation buttons
    fig.update_layout(
        title=title or f"Bloch Sphere Animation - Qubit {qubit}",
        scene=dict(
            xaxis=dict(range=[-1.5, 1.5], title="X"),
            yaxis=dict(range=[-1.5, 1.5], title="Y"),
            zaxis=dict(range=[-1.5, 1.5], title="Z"),
            aspectmode="cube",
        ),
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 200, "redraw": True},
                                "fromcurrent": True,
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    },
                ],
            }
        ],
        width=600,
        height=600,
    )

    return fig


