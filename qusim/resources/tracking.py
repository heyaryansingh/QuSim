"""
Resource tracking for quantum circuits.

Tracks qubit count, gate count, depth, and simulation costs.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from qusim.core.circuit import Circuit
from qusim.backends.base import ExecutionResult
import time


class ResourceTracker:
    """Tracks resource usage for quantum circuits."""

    def __init__(self):
        """Initialize resource tracker."""
        pass

    def analyze_circuit_resources(self, circuit: Circuit) -> Dict[str, Any]:
        """
        Analyze circuit resources.

        Args:
            circuit: Circuit to analyze

        Returns:
            Resource metrics
        """
        gate_counts = circuit.gate_count()
        depth = circuit.depth()

        # Count entangling gates
        entangling_gates = {"CNOT", "CZ", "SWAP", "Toffoli"}
        entangling_count = sum(
            count for gate, count in gate_counts.items() if gate in entangling_gates
        )

        # Calculate entangling gate depth
        entangling_depth = self._calculate_entangling_depth(circuit)

        # Estimate simulation cost
        simulation_cost = self._estimate_simulation_cost(circuit)

        return {
            "num_qubits": circuit.num_qubits,
            "num_classical_bits": circuit.num_classical_bits,
            "total_gates": len(circuit.gates),
            "gate_counts": gate_counts,
            "circuit_depth": depth,
            "entangling_gate_count": entangling_count,
            "entangling_gate_depth": entangling_depth,
            "simulation_cost": simulation_cost,
        }

    def _calculate_entangling_depth(self, circuit: Circuit) -> int:
        """Calculate depth considering only entangling gates."""
        entangling_gates = {"CNOT", "CZ", "SWAP", "Toffoli"}

        if not circuit.gates:
            return 0

        layers: List[List[int]] = []
        qubit_layers = [-1] * circuit.num_qubits

        for i, (gate, qubits) in enumerate(circuit.gates):
            if gate.name not in entangling_gates:
                continue  # Skip non-entangling gates

            earliest_layer = max(qubit_layers[q] for q in qubits) + 1

            while len(layers) <= earliest_layer:
                layers.append([])

            layers[earliest_layer].append(i)

            for q in qubits:
                qubit_layers[q] = earliest_layer

        return len(layers)

    def _estimate_simulation_cost(self, circuit: Circuit) -> Dict[str, Any]:
        """
        Estimate classical simulation cost.

        Args:
            circuit: Circuit to analyze

        Returns:
            Cost estimates
        """
        num_qubits = circuit.num_qubits

        # Statevector cost: 2^n complex numbers
        statevector_memory = (2 ** num_qubits * 16) / (1024 ** 2)  # MB
        statevector_ops = len(circuit.gates) * (2 ** num_qubits)  # Rough estimate

        # Density matrix cost: 4^n complex numbers
        density_matrix_memory = (4 ** num_qubits * 16) / (1024 ** 2)  # MB
        density_matrix_ops = len(circuit.gates) * (4 ** num_qubits)  # Rough estimate

        # Stabilizer cost: O(n^2) for Clifford circuits
        stabilizer_memory = (num_qubits ** 2 * 8) / (1024 ** 2)  # MB
        stabilizer_ops = len(circuit.gates) * (num_qubits ** 2)

        return {
            "statevector": {
                "memory_mb": statevector_memory,
                "operations": statevector_ops,
            },
            "density_matrix": {
                "memory_mb": density_matrix_memory,
                "operations": density_matrix_ops,
            },
            "stabilizer": {
                "memory_mb": stabilizer_memory,
                "operations": stabilizer_ops,
            },
        }

    def track_execution_resources(
        self, circuit: Circuit, result: ExecutionResult
    ) -> Dict[str, Any]:
        """
        Track resources during execution.

        Args:
            circuit: Circuit that was executed
            result: Execution result

        Returns:
            Execution resource metrics
        """
        circuit_resources = self.analyze_circuit_resources(circuit)

        # Get execution metadata
        execution_time = result.metadata.get("execution_time", 0.0)
        memory_used = result.metadata.get("memory_mb", 0.0)

        return {
            **circuit_resources,
            "execution_time_seconds": execution_time,
            "memory_used_mb": memory_used,
            "backend": result.metadata.get("backend", "Unknown"),
        }

    def compare_resources(self, circuits: List[Circuit]) -> Dict[str, Any]:
        """
        Compare resources across multiple circuits.

        Args:
            circuits: List of circuits to compare

        Returns:
            Comparison results
        """
        comparisons = []

        for i, circuit in enumerate(circuits):
            resources = self.analyze_circuit_resources(circuit)
            resources["circuit_index"] = i
            comparisons.append(resources)

        # Aggregate statistics
        num_qubits_list = [r["num_qubits"] for r in comparisons]
        depths = [r["circuit_depth"] for r in comparisons]
        gate_counts = [r["total_gates"] for r in comparisons]

        return {
            "circuits": comparisons,
            "statistics": {
                "avg_qubits": np.mean(num_qubits_list),
                "max_qubits": np.max(num_qubits_list),
                "avg_depth": np.mean(depths),
                "max_depth": np.max(depths),
                "avg_gates": np.mean(gate_counts),
                "max_gates": np.max(gate_counts),
            },
        }

    def fault_tolerant_overhead(
        self, base_circuit: Circuit, qec_code_name: str = "BitFlip"
    ) -> Dict[str, Any]:
        """
        Calculate fault-tolerant overhead.

        Args:
            base_circuit: Base circuit
            qec_code_name: QEC code name

        Returns:
            Overhead metrics
        """
        from qusim.qec.codes import BitFlipCode, PhaseFlipCode, ShorCode

        code_map = {
            "BitFlip": BitFlipCode(),
            "PhaseFlip": PhaseFlipCode(),
            "Shor": ShorCode(),
        }

        if qec_code_name not in code_map:
            raise ValueError(f"Unknown QEC code: {qec_code_name}")

        code = code_map[qec_code_name]

        base_resources = self.analyze_circuit_resources(base_circuit)

        # Estimate protected circuit resources
        # Each logical qubit becomes num_physical_qubits physical qubits
        protected_qubits = base_circuit.num_qubits * code.num_physical_qubits

        # Gate count increases (encoding/decoding/syndrome extraction)
        # Rough estimate: 3x for encoding/decoding, plus syndrome overhead
        protected_gates = base_resources["total_gates"] * 3

        protected_resources = {
            "num_qubits": protected_qubits,
            "total_gates": protected_gates,
            "circuit_depth": base_resources["circuit_depth"] * 2,  # Rough estimate
        }

        overhead = {
            "qubit_overhead": protected_qubits / base_circuit.num_qubits,
            "gate_overhead": protected_gates / base_resources["total_gates"],
            "depth_overhead": protected_resources["circuit_depth"] / base_resources["circuit_depth"],
        }

        return {
            "base_resources": base_resources,
            "protected_resources": protected_resources,
            "overhead": overhead,
            "qec_code": qec_code_name,
        }


