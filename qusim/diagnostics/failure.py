"""
Failure detection and diagnostics for quantum circuits.

Detects noise dominance, entanglement bottlenecks, precision errors, etc.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from qusim.core.state import QuantumState
from qusim.metrics.fidelity import state_fidelity
from qusim.metrics.entanglement import von_neumann_entropy, mutual_information
from qusim.backends.base import ExecutionResult


class FailureDiagnostic:
    """Structured failure diagnostic report."""

    def __init__(
        self,
        failure_type: str,
        step: int,
        severity: str,
        description: str,
        suggested_mitigation: Optional[str] = None,
    ):
        """
        Initialize failure diagnostic.

        Args:
            failure_type: Type of failure (e.g., "noise_dominance", "precision_error")
            step: Circuit step where failure occurred
            severity: "low", "medium", "high", "critical"
            description: Human-readable description
            suggested_mitigation: Suggested fix
        """
        self.failure_type = failure_type
        self.step = step
        self.severity = severity
        self.description = description
        self.suggested_mitigation = suggested_mitigation

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "failure_type": self.failure_type,
            "step": self.step,
            "severity": self.severity,
            "description": self.description,
            "suggested_mitigation": self.suggested_mitigation,
        }


def detect_failures(
    ideal_result: ExecutionResult,
    noisy_result: Optional[ExecutionResult] = None,
    state_history: Optional[List[QuantumState]] = None,
    threshold_fidelity: float = 0.9,
    threshold_entropy: float = 0.1,
) -> List[FailureDiagnostic]:
    """
    Detect failures in circuit execution.

    Args:
        ideal_result: Result from ideal (noiseless) execution
        noisy_result: Result from noisy execution (if available)
        state_history: State history during execution
        threshold_fidelity: Fidelity threshold for noise dominance warning
        threshold_entropy: Entropy threshold for precision errors

    Returns:
        List of failure diagnostics
    """
    failures: List[FailureDiagnostic] = []

    # Check for noise dominance
    if noisy_result is not None:
        fidelity = state_fidelity(ideal_result.state, noisy_result.state)
        if fidelity < threshold_fidelity:
            failures.append(
                FailureDiagnostic(
                    failure_type="noise_dominance",
                    step=-1,  # Overall circuit
                    severity="high" if fidelity < 0.5 else "medium",
                    description=f"Noise significantly degrades state fidelity: {fidelity:.4f}",
                    suggested_mitigation="Reduce noise strength or use error correction",
                )
            )

        # Check noise accumulation over steps
        if (
            ideal_result.state_history is not None
            and noisy_result.state_history is not None
            and len(ideal_result.state_history) == len(noisy_result.state_history)
        ):
            for step, (ideal_state, noisy_state) in enumerate(
                zip(ideal_result.state_history, noisy_result.state_history)
            ):
                step_fidelity = state_fidelity(ideal_state, noisy_state)
                if step_fidelity < threshold_fidelity:
                    failures.append(
                        FailureDiagnostic(
                            failure_type="noise_accumulation",
                            step=step,
                            severity="medium",
                            description=f"Fidelity drops to {step_fidelity:.4f} at step {step}",
                            suggested_mitigation="Consider error correction or noise reduction",
                        )
                    )

    # Check for precision errors
    if state_history:
        for step, state in enumerate(state_history):
            # Check if state is properly normalized
            if state.is_density_matrix:
                trace = np.real(np.trace(state.state))
                if not np.isclose(trace, 1.0, atol=1e-6):
                    failures.append(
                        FailureDiagnostic(
                            failure_type="precision_error",
                            step=step,
                            severity="medium",
                            description=f"Density matrix trace = {trace:.6f} (should be 1.0)",
                            suggested_mitigation="Renormalize state or use higher precision",
                        )
                    )

                # Check for negative eigenvalues
                eigenvals = np.linalg.eigvalsh(state.state)
                if np.any(eigenvals < -1e-10):
                    failures.append(
                        FailureDiagnostic(
                            failure_type="precision_error",
                            step=step,
                            severity="high",
                            description=f"Negative eigenvalues detected: min = {np.min(eigenvals):.6f}",
                            suggested_mitigation="Use higher numerical precision or different backend",
                        )
                    )

    # Check for entanglement bottlenecks
    if state_history:
        entropies = []
        for state in state_history:
            # Calculate average entropy per qubit
            num_qubits = state.num_qubits
            total_entropy = von_neumann_entropy(state)
            avg_entropy = total_entropy / num_qubits if num_qubits > 0 else 0
            entropies.append(avg_entropy)

        # Check if entropy grows too quickly (potential bottleneck)
        if len(entropies) > 1:
            entropy_growth = np.diff(entropies)
            max_growth_idx = np.argmax(entropy_growth)
            if entropy_growth[max_growth_idx] > 2.0:  # Large entropy jump
                failures.append(
                    FailureDiagnostic(
                        failure_type="entanglement_bottleneck",
                        step=max_growth_idx,
                        severity="low",
                        description=f"Large entropy increase at step {max_growth_idx}: {entropy_growth[max_growth_idx]:.4f}",
                        suggested_mitigation="Consider circuit optimization or different entanglement structure",
                    )
                )

    return failures


def detect_backend_limitations(
    circuit: Circuit, backend_name: str, execution_result: ExecutionResult
) -> List[FailureDiagnostic]:
    """
    Detect backend-specific limitations.

    Args:
        circuit: Circuit that was executed
        backend_name: Name of backend used
        execution_result: Execution result

    Returns:
        List of failure diagnostics
    """
    failures: List[FailureDiagnostic] = []

    # Check memory limitations
    dim = 2 ** circuit.num_qubits
    memory_gb = (dim * dim * 16) / (1024 ** 3)  # For density matrix

    if memory_gb > 1.0:  # > 1GB
        failures.append(
            FailureDiagnostic(
                failure_type="memory_limitation",
                step=-1,
                severity="medium",
                description=f"Circuit requires ~{memory_gb:.2f}GB memory for {circuit.num_qubits} qubits",
                suggested_mitigation=f"Consider using Stabilizer backend (if Clifford) or tensor network backend",
            )
        )

    # Check for non-Clifford gates in stabilizer backend
    if backend_name == "StabilizerBackend":
        from qusim.backends.stabilizer import detect_clifford_circuit

        is_clifford, reason = detect_clifford_circuit(circuit)
        if not is_clifford:
            failures.append(
                FailureDiagnostic(
                    failure_type="backend_limitation",
                    step=-1,
                    severity="high",
                    description=f"Stabilizer backend cannot execute non-Clifford circuit: {reason}",
                    suggested_mitigation="Use StatevectorBackend or DensityMatrixBackend",
                )
            )

    return failures


def generate_diagnostic_report(
    failures: List[FailureDiagnostic],
) -> Dict[str, Any]:
    """
    Generate structured diagnostic report.

    Args:
        failures: List of failure diagnostics

    Returns:
        Structured report dictionary
    """
    # Group by severity
    by_severity: Dict[str, List[FailureDiagnostic]] = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
    }

    for failure in failures:
        by_severity[failure.severity].append(failure)

    # Group by type
    by_type: Dict[str, List[FailureDiagnostic]] = {}
    for failure in failures:
        if failure.failure_type not in by_type:
            by_type[failure.failure_type] = []
        by_type[failure.failure_type].append(failure)

    # Find dominant error source
    dominant_error = None
    if failures:
        error_counts = {}
        for failure in failures:
            error_counts[failure.failure_type] = error_counts.get(failure.failure_type, 0) + 1
        dominant_error = max(error_counts.items(), key=lambda x: x[1])[0]

    report = {
        "total_failures": len(failures),
        "by_severity": {k: [f.to_dict() for f in v] for k, v in by_severity.items()},
        "by_type": {k: [f.to_dict() for f in v] for k, v in by_type.items()},
        "dominant_error_source": dominant_error,
        "summary": _generate_summary(failures),
    }

    return report


def _generate_summary(failures: List[FailureDiagnostic]) -> str:
    """Generate human-readable summary."""
    if not failures:
        return "No failures detected. Circuit executed successfully."

    critical = [f for f in failures if f.severity == "critical"]
    high = [f for f in failures if f.severity == "high"]

    summary_parts = []
    if critical:
        summary_parts.append(f"{len(critical)} critical issue(s) detected")
    if high:
        summary_parts.append(f"{len(high)} high-severity issue(s) detected")

    if summary_parts:
        return ". ".join(summary_parts) + "."
    else:
        return f"{len(failures)} minor issue(s) detected."


