"""
Additional API routes for QuSim.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import numpy as np

router = APIRouter()


class VisualizationRequest(BaseModel):
    """Request for visualization data."""

    circuit_dsl: str
    visualization_type: str  # "bloch", "density", "histogram", etc.
    qubit: Optional[int] = None


@router.post("/visualize")
async def get_visualization_data(request: VisualizationRequest):
    """Get visualization data for a circuit."""
    try:
        from qusim.dsl.parser import parse
        from qusim.backends.selector import BackendSelector

        # Parse and execute circuit
        circuit = parse(request.circuit_dsl)
        selector = BackendSelector()
        backend, _ = selector.select_backend(circuit)

        result = backend.execute(circuit, return_state_history=True)

        # Generate visualization data based on type
        if request.visualization_type == "bloch":
            from qusim.visualization.bloch import bloch_vector

            qubit = request.qubit or 0
            vec = bloch_vector(result.state, qubit)
            return {
                "type": "bloch",
                "qubit": qubit,
                "vector": vec.tolist(),
            }

        elif request.visualization_type == "density":
            from qusim.visualization.density import plot_density_matrix

            # Return density matrix data
            if result.state.is_density_matrix:
                rho = result.state.state
                return {
                    "type": "density_matrix",
                    "real": np.real(rho).tolist(),
                    "imaginary": np.imag(rho).tolist(),
                }
            else:
                rho = result.state.to_density_matrix().state
                return {
                    "type": "density_matrix",
                    "real": np.real(rho).tolist(),
                    "imaginary": np.imag(rho).tolist(),
                }

        elif request.visualization_type == "histogram":
            return {
                "type": "histogram",
                "counts": result.get_counts(),
                "probabilities": result.get_probabilities().tolist(),
            }

        else:
            raise ValueError(f"Unknown visualization type: {request.visualization_type}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/entanglement")
async def get_entanglement_metrics(circuit_dsl: str):
    """Get entanglement metrics for a circuit."""
    try:
        from qusim.dsl.parser import parse
        from qusim.backends.selector import BackendSelector
        from qusim.metrics.entanglement import (
            von_neumann_entropy,
            mutual_information,
            all_pairwise_mutual_information,
        )

        circuit = parse(circuit_dsl)
        selector = BackendSelector()
        backend, _ = selector.select_backend(circuit)

        result = backend.execute(circuit)

        # Calculate metrics
        total_entropy = von_neumann_entropy(result.state)
        mi_matrix = all_pairwise_mutual_information(result.state)

        return {
            "total_entropy": total_entropy,
            "pairwise_mutual_information": mi_matrix.tolist(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

