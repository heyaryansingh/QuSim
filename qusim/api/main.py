"""
FastAPI application for QuSim web interface.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import numpy as np
from qusim.api import routes

app = FastAPI(title="QuSim API", version="0.1.0")

# Include additional routes
app.include_router(routes.router, prefix="/api", tags=["visualization", "metrics"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CircuitRequest(BaseModel):
    """Circuit execution request."""

    dsl_code: Optional[str] = None
    gates: Optional[List[Dict[str, Any]]] = None
    num_qubits: int
    backend: Optional[str] = None
    shots: int = 1
    return_state_history: bool = False
    noise_model: Optional[Dict[str, Any]] = None


class CircuitResponse(BaseModel):
    """Circuit execution response."""

    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "QuSim API", "version": "0.1.0"}


@app.post("/execute", response_model=CircuitResponse)
async def execute_circuit(request: CircuitRequest):
    """Execute a quantum circuit."""
    try:
        from qusim.dsl.parser import parse
        from qusim.backends.selector import BackendSelector
        from qusim.backends.noisy_backend import NoisyBackend
        from qusim.noise.channels import (
            DepolarizingChannel,
            AmplitudeDampingChannel,
            PhaseDampingChannel,
            BitFlipChannel,
            PhaseFlipChannel,
        )

        # Parse circuit
        if request.dsl_code:
            circuit = parse(request.dsl_code)
        else:
            # Build circuit from gates (simplified)
            from qusim.core.circuit import Circuit

            circuit = Circuit(request.num_qubits)
            # Would need to parse gates here
            raise NotImplementedError("Gate-based circuit construction not yet implemented")

        # Select backend
        selector = BackendSelector()
        noise_model = None

        if request.noise_model:
            # Build noise model
            noise_model = {}
            for qubit_str, channels in request.noise_model.items():
                qubit = int(qubit_str)
                noise_model[qubit] = []
                for channel_spec in channels:
                    channel_type = channel_spec["type"]
                    params = channel_spec.get("params", {})

                    if channel_type == "depolarizing":
                        noise_model[qubit].append(DepolarizingChannel(params.get("p", 0.01)))
                    elif channel_type == "amplitude_damping":
                        noise_model[qubit].append(AmplitudeDampingChannel(params.get("gamma", 0.01)))
                    elif channel_type == "phase_damping":
                        noise_model[qubit].append(PhaseDampingChannel(params.get("gamma", 0.01)))
                    elif channel_type == "bit_flip":
                        noise_model[qubit].append(BitFlipChannel(params.get("p", 0.01)))
                    elif channel_type == "phase_flip":
                        noise_model[qubit].append(PhaseFlipChannel(params.get("p", 0.01)))

        backend, explanation = selector.select_backend(
            circuit,
            use_noise=request.noise_model is not None,
            noise_model=noise_model,
            preferred_backend=request.backend,
        )

        # Execute
        result = backend.execute(
            circuit,
            shots=request.shots,
            return_state_history=request.return_state_history,
        )

        # Convert result to JSON-serializable format
        result_dict = {
            "measurements": result.measurements,
            "counts": result.get_counts(),
            "probabilities": result.get_probabilities().tolist(),
            "metadata": result.metadata,
        }

        # Add state information (simplified)
        if result.state.is_density_matrix:
            # For density matrix, return key information
            dim = result.state.state.shape[0]
            result_dict["state_type"] = "density_matrix"
            result_dict["state_dim"] = dim
            # Return diagonal (probabilities)
            result_dict["diagonal"] = np.real(np.diag(result.state.state)).tolist()
        else:
            # For statevector, return amplitudes
            result_dict["state_type"] = "statevector"
            result_dict["amplitudes"] = result.state.state.tolist()

        if result.state_history:
            result_dict["state_history_length"] = len(result.state_history)

        return CircuitResponse(success=True, result=result_dict)

    except Exception as e:
        return CircuitResponse(success=False, error=str(e))


@app.get("/backends")
async def list_backends():
    """List available backends."""
    from qusim.backends.selector import BackendSelector

    selector = BackendSelector()
    backends = {}

    for name in selector.available_backends.keys():
        info = selector.get_backend_info(name)
        backends[name] = info

    return {"backends": backends}


@app.post("/analyze")
async def analyze_circuit(request: CircuitRequest):
    """Analyze circuit (resources, diagnostics, etc.)."""
    try:
        from qusim.dsl.parser import parse
        from qusim.resources.tracking import ResourceTracker
        from qusim.diagnostics.failure import detect_failures, generate_diagnostic_report

        # Parse circuit
        if request.dsl_code:
            circuit = parse(request.dsl_code)
        else:
            raise NotImplementedError("Gate-based circuit construction not yet implemented")

        # Resource analysis
        tracker = ResourceTracker()
        resources = tracker.analyze_circuit_resources(circuit)

        # Execute for diagnostics
        from qusim.backends.selector import BackendSelector
        from qusim.backends.statevector import StatevectorBackend

        selector = BackendSelector()
        backend, _ = selector.select_backend(circuit)

        ideal_result = backend.execute(circuit, return_state_history=True)

        # Run with noise if specified
        noisy_result = None
        if request.noise_model:
            from qusim.backends.noisy_backend import NoisyBackend

            # Build noise model (simplified)
            noisy_backend = NoisyBackend(base_backend=backend)
            noisy_result = noisy_backend.execute(circuit, return_state_history=True)

        # Failure diagnostics
        failures = detect_failures(ideal_result, noisy_result, ideal_result.state_history)
        diagnostic_report = generate_diagnostic_report(failures)

        return {
            "success": True,
            "resources": resources,
            "diagnostics": diagnostic_report,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

