"""
Sensitivity analysis for quantum circuits.

Analyzes how circuit output changes with parameter perturbations.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable
from qusim.core.circuit import Circuit
from qusim.backends.base import Backend, ExecutionResult
from qusim.metrics.fidelity import state_fidelity
from qusim.metrics.entanglement import von_neumann_entropy


class SensitivityAnalysis:
    """Performs sensitivity analysis on quantum circuits."""

    def __init__(self, base_backend: Backend):
        """
        Initialize sensitivity analysis.

        Args:
            base_backend: Base backend to use for execution
        """
        self.base_backend = base_backend

    def analyze_noise_sensitivity(
        self,
        circuit: Circuit,
        noise_param: str,
        param_values: List[float],
        noise_channel_factory: Callable[[float], Any],
        qubit: int = 0,
    ) -> Dict[str, Any]:
        """
        Analyze sensitivity to noise parameter.

        Args:
            circuit: Circuit to analyze
            noise_param: Name of noise parameter
            param_values: List of parameter values to test
            noise_channel_factory: Function that creates noise channel from parameter
            qubit: Qubit to apply noise to

        Returns:
            Dictionary with sensitivity results
        """
        from qusim.backends.noisy_backend import NoisyBackend
        from qusim.backends.statevector import StatevectorBackend

        # Get ideal result
        ideal_backend = StatevectorBackend()
        ideal_result = ideal_backend.execute(circuit, return_state_history=True)

        # Test each parameter value
        results = []
        fidelities = []
        entropies = []

        for param_val in param_values:
            # Create noisy backend
            noise_channel = noise_channel_factory(param_val)
            noise_model = {qubit: [noise_channel]}
            noisy_backend = NoisyBackend(
                base_backend=self.base_backend, noise_model=noise_model
            )

            # Execute
            noisy_result = noisy_backend.execute(circuit, return_state_history=True)

            # Calculate metrics
            fidelity = state_fidelity(ideal_result.state, noisy_result.state)
            entropy = von_neumann_entropy(noisy_result.state)

            results.append(
                {
                    "param_value": param_val,
                    "fidelity": fidelity,
                    "entropy": entropy,
                    "result": noisy_result,
                }
            )
            fidelities.append(fidelity)
            entropies.append(entropy)

        # Calculate sensitivity (derivative)
        if len(param_values) > 1:
            sensitivity = np.gradient(fidelities, param_values)
        else:
            sensitivity = [0.0]

        return {
            "noise_param": noise_param,
            "param_values": param_values,
            "fidelities": fidelities,
            "entropies": entropies,
            "sensitivity": sensitivity.tolist(),
            "results": results,
            "ideal_result": ideal_result,
        }

    def compare_backends(
        self,
        circuit: Circuit,
        backends: List[Backend],
        backend_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare execution across multiple backends.

        Args:
            circuit: Circuit to execute
            backends: List of backends to compare
            backend_names: Optional names for backends

        Returns:
            Comparison results
        """
        if backend_names is None:
            backend_names = [backend.get_name() for backend in backends]

        results = {}
        execution_times = []
        memory_usage = []

        import time

        for backend, name in zip(backends, backend_names):
            start_time = time.time()
            result = backend.execute(circuit)
            execution_time = time.time() - start_time

            # Estimate memory (simplified)
            dim = 2 ** circuit.num_qubits
            if "DensityMatrix" in name:
                memory = (dim * dim * 16) / (1024 ** 2)  # MB
            else:
                memory = (dim * 16) / (1024 ** 2)  # MB

            results[name] = {
                "result": result,
                "execution_time": execution_time,
                "memory_mb": memory,
            }
            execution_times.append(execution_time)
            memory_usage.append(memory)

        return {
            "backend_names": backend_names,
            "results": results,
            "execution_times": execution_times,
            "memory_usage": memory_usage,
        }

    def parameter_sweep(
        self,
        circuit_factory: Callable[[float], Circuit],
        param_name: str,
        param_values: List[float],
        metric: Callable[[ExecutionResult], float],
    ) -> Dict[str, Any]:
        """
        Perform parameter sweep and calculate metric.

        Args:
            circuit_factory: Function that creates circuit from parameter
            param_name: Name of parameter
            param_values: Parameter values to test
            metric: Function that calculates metric from execution result

        Returns:
            Sweep results
        """
        metric_values = []

        for param_val in param_values:
            circuit = circuit_factory(param_val)
            result = self.base_backend.execute(circuit)
            metric_val = metric(result)
            metric_values.append(metric_val)

        return {
            "param_name": param_name,
            "param_values": param_values,
            "metric_values": metric_values,
        }


