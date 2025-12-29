"""
QEC tracking and analysis.

Tracks logical vs physical errors, syndromes, and thresholds.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from qusim.core.circuit import Circuit
from qusim.backends.base import ExecutionResult
from qusim.metrics.fidelity import state_fidelity
from qusim.qec.codes import QECCode


class QECTracker:
    """Tracks QEC performance metrics."""

    def __init__(self, code: QECCode):
        """
        Initialize QEC tracker.

        Args:
            code: QEC code being used
        """
        self.code = code

    def analyze_qec_performance(
        self,
        ideal_result: ExecutionResult,
        noisy_result: ExecutionResult,
        syndrome_measurements: Optional[List[Dict[str, int]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze QEC performance.

        Args:
            ideal_result: Result from ideal (noiseless) execution
            noisy_result: Result from noisy execution
            syndrome_measurements: Syndrome measurement results

        Returns:
            Performance metrics
        """
        # Calculate logical fidelity
        logical_fidelity = state_fidelity(ideal_result.state, noisy_result.state)

        # Analyze syndromes
        syndrome_analysis = self._analyze_syndromes(syndrome_measurements)

        # Calculate error rates
        physical_error_rate = self._estimate_physical_error_rate(noisy_result)
        logical_error_rate = 1.0 - logical_fidelity

        return {
            "logical_fidelity": logical_fidelity,
            "logical_error_rate": logical_error_rate,
            "physical_error_rate": physical_error_rate,
            "syndrome_analysis": syndrome_analysis,
            "error_reduction": physical_error_rate / logical_error_rate if logical_error_rate > 0 else float("inf"),
        }

    def _analyze_syndromes(
        self, syndrome_measurements: Optional[List[Dict[str, int]]]
    ) -> Dict[str, Any]:
        """Analyze syndrome measurements."""
        if not syndrome_measurements:
            return {"syndrome_detected": False}

        # Count syndrome patterns
        syndrome_counts: Dict[str, int] = {}
        for measurement in syndrome_measurements:
            # Convert to syndrome string
            syndrome_bits = []
            for i in sorted(measurement.keys(), key=int):
                syndrome_bits.append(str(measurement[i]))
            syndrome_str = "".join(syndrome_bits)
            syndrome_counts[syndrome_str] = syndrome_counts.get(syndrome_str, 0) + 1

        # Check if any non-zero syndromes detected
        non_zero_syndromes = {k: v for k, v in syndrome_counts.items() if k != "0" * len(syndrome_counts)}

        return {
            "syndrome_detected": len(non_zero_syndromes) > 0,
            "syndrome_counts": syndrome_counts,
            "non_zero_syndromes": non_zero_syndromes,
        }

    def _estimate_physical_error_rate(self, result: ExecutionResult) -> float:
        """Estimate physical error rate from result."""
        # Simplified: use state fidelity as proxy
        # In practice, would analyze error syndromes
        if result.state.is_density_matrix:
            purity = np.real(np.trace(result.state.state @ result.state.state))
            error_rate = 1.0 - purity
        else:
            # Pure state
            error_rate = 0.0

        return error_rate

    def threshold_simulation(
        self,
        noise_strengths: List[float],
        noise_channel_factory,
        test_circuit: Optional[Circuit] = None,
    ) -> Dict[str, Any]:
        """
        Simulate QEC threshold under noise.

        Args:
            noise_strengths: List of noise parameter values
            noise_channel_factory: Function that creates noise channel from parameter
            test_circuit: Test circuit (if None, uses simple identity)

        Returns:
            Threshold analysis results
        """
        from qusim.backends.statevector import StatevectorBackend
        from qusim.backends.noisy_backend import NoisyBackend
        from qusim.qec.codes import create_qec_circuit, BitFlipCode

        if test_circuit is None:
            # Simple test: identity operation
            test_circuit = Circuit(1)

        logical_fidelities = []
        physical_error_rates = []

        ideal_backend = StatevectorBackend()

        for noise_strength in noise_strengths:
            # Create QEC circuit with noise
            code = BitFlipCode()
            noise_channel = noise_channel_factory(noise_strength)

            # Create noisy backend
            noise_model = {i: [noise_channel] for i in range(code.num_physical_qubits)}
            noisy_backend = NoisyBackend(
                base_backend=StatevectorBackend(), noise_model=noise_model
            )

            # Execute QEC circuit
            qec_circuit = create_qec_circuit(code, test_circuit)
            noisy_result = noisy_backend.execute(qec_circuit)

            # Execute ideal circuit
            ideal_result = ideal_backend.execute(test_circuit)

            # Calculate metrics
            logical_fidelity = state_fidelity(ideal_result.state, noisy_result.state)
            physical_error_rate = noise_strength

            logical_fidelities.append(logical_fidelity)
            physical_error_rates.append(physical_error_rate)

        # Find threshold (where logical error rate < physical error rate)
        threshold = None
        for i, (phys_rate, log_fid) in enumerate(zip(physical_error_rates, logical_fidelities)):
            log_rate = 1.0 - log_fid
            if log_rate < phys_rate:
                threshold = noise_strengths[i]
                break

        return {
            "noise_strengths": noise_strengths,
            "logical_fidelities": logical_fidelities,
            "physical_error_rates": physical_error_rates,
            "threshold": threshold,
        }


