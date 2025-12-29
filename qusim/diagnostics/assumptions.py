"""
Assumption tracking for quantum circuit simulation.

Tracks idealizations and warns when assumptions are violated.
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class AssumptionType(Enum):
    """Types of assumptions."""

    PERFECT_GATES = "perfect_gates"
    NO_DECOHERENCE = "no_decoherence"
    INFINITE_PRECISION = "infinite_precision"
    IDEAL_MEASUREMENT = "ideal_measurement"
    NO_CROSSTALK = "no_crosstalk"
    PERFECT_INITIALIZATION = "perfect_initialization"


class Assumption:
    """Represents a simulation assumption."""

    def __init__(
        self,
        assumption_type: AssumptionType,
        description: str,
        is_violated: bool = False,
        violation_reason: Optional[str] = None,
    ):
        """
        Initialize assumption.

        Args:
            assumption_type: Type of assumption
            description: Human-readable description
            is_violated: Whether assumption is violated
            violation_reason: Reason for violation (if violated)
        """
        self.assumption_type = assumption_type
        self.description = description
        self.is_violated = is_violated
        self.violation_reason = violation_reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.assumption_type.value,
            "description": self.description,
            "is_violated": self.is_violated,
            "violation_reason": self.violation_reason,
        }


class AssumptionTracker:
    """Tracks assumptions during circuit execution."""

    def __init__(self):
        """Initialize assumption tracker."""
        self.assumptions: List[Assumption] = []
        self._initialize_default_assumptions()

    def _initialize_default_assumptions(self):
        """Initialize default assumptions for ideal simulation."""
        self.assumptions = [
            Assumption(
                AssumptionType.PERFECT_GATES,
                "All gates are applied perfectly without errors",
            ),
            Assumption(
                AssumptionType.NO_DECOHERENCE,
                "No decoherence or environmental noise",
            ),
            Assumption(
                AssumptionType.INFINITE_PRECISION,
                "Infinite numerical precision (no rounding errors)",
            ),
            Assumption(
                AssumptionType.IDEAL_MEASUREMENT,
                "Measurements are ideal (no measurement errors)",
            ),
            Assumption(
                AssumptionType.NO_CROSSTALK,
                "No crosstalk between qubits",
            ),
            Assumption(
                AssumptionType.PERFECT_INITIALIZATION,
                "Perfect initial state preparation",
            ),
        ]

    def mark_violated(
        self, assumption_type: AssumptionType, reason: str
    ):
        """Mark an assumption as violated."""
        for assumption in self.assumptions:
            if assumption.assumption_type == assumption_type:
                assumption.is_violated = True
                assumption.violation_reason = reason
                break

    def get_violated_assumptions(self) -> List[Assumption]:
        """Get list of violated assumptions."""
        return [a for a in self.assumptions if a.is_violated]

    def get_assumption_report(self) -> Dict[str, Any]:
        """Generate assumption report."""
        violated = self.get_violated_assumptions()
        return {
            "total_assumptions": len(self.assumptions),
            "violated_count": len(violated),
            "assumptions": [a.to_dict() for a in self.assumptions],
            "violated": [a.to_dict() for a in violated],
        }

