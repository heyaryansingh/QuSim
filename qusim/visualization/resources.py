"""
Resource visualization utilities.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any
from qusim.resources.tracking import ResourceTracker


def plot_resource_comparison(circuits: List[Dict[str, Any]], title: Optional[str] = None) -> go.Figure:
    """
    Plot resource comparison across circuits.

    Args:
        circuits: List of circuit resource dictionaries
        title: Plot title

    Returns:
        Plotly figure
    """
    tracker = ResourceTracker()
    comparison = tracker.compare_resources([c["circuit"] for c in circuits])

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=["Qubits", "Depth", "Gate Count", "Simulation Cost"],
    )

    circuit_names = [c.get("name", f"Circuit {i}") for i, c in enumerate(circuits)]

    # Qubits
    qubits = [r["num_qubits"] for r in comparison["circuits"]]
    fig.add_trace(go.Bar(x=circuit_names, y=qubits, name="Qubits"), row=1, col=1)

    # Depth
    depths = [r["circuit_depth"] for r in comparison["circuits"]]
    fig.add_trace(go.Bar(x=circuit_names, y=depths, name="Depth"), row=1, col=2)

    # Gate count
    gates = [r["total_gates"] for r in comparison["circuits"]]
    fig.add_trace(go.Bar(x=circuit_names, y=gates, name="Gates"), row=2, col=1)

    # Simulation cost (statevector memory)
    costs = [
        r["simulation_cost"]["statevector"]["memory_mb"] for r in comparison["circuits"]
    ]
    fig.add_trace(go.Bar(x=circuit_names, y=costs, name="Memory (MB)"), row=2, col=2)

    fig.update_layout(
        title=title or "Resource Comparison",
        height=600,
        showlegend=False,
    )

    return fig


def plot_resource_evolution(
    resource_history: List[Dict[str, Any]], title: Optional[str] = None
) -> go.Figure:
    """
    Plot resource evolution over time.

    Args:
        resource_history: List of resource dictionaries over time
        title: Plot title

    Returns:
        Plotly figure
    """
    steps = list(range(len(resource_history)))

    fig = go.Figure()

    # Plot multiple metrics
    if resource_history:
        keys = ["num_qubits", "circuit_depth", "total_gates"]
        for key in keys:
            if key in resource_history[0]:
                values = [r.get(key, 0) for r in resource_history]
                fig.add_trace(go.Scatter(x=steps, y=values, mode="lines+markers", name=key))

    fig.update_layout(
        title=title or "Resource Evolution",
        xaxis_title="Step",
        yaxis_title="Resource Count",
    )

    return fig


