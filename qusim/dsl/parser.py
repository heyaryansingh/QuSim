"""
Text-based DSL parser for quantum circuit definition.

Supports Python-like syntax for defining circuits.
Example:
    circuit = parse(""'
        qreg q[2]
        h(0)
        cnot(0, 1)
        measure(0, 0)
    """)
"""

import re
from typing import List, Optional
from qusim.core.circuit import Circuit
from qusim.core.gates import (
    X,
    Y,
    Z,
    H,
    S,
    T,
    RX,
    RY,
    RZ,
    CNOT,
    CZ,
    SWAP,
    Toffoli,
    CustomGate,
)
import numpy as np


def parse(dsl_code: str) -> Circuit:
    """
    Parse DSL code and return a Circuit object.

    Args:
        dsl_code: DSL code string

    Returns:
        Circuit object
    """
    parser = DSLParser()
    return parser.parse(dsl_code)


class DSLParser:
    """Parser for quantum circuit DSL."""

    def __init__(self):
        self.circuit: Optional[Circuit] = None
        self.num_qubits = 0
        self.num_classical_bits = 0

    def parse(self, code: str) -> Circuit:
        """Parse DSL code."""
        # Remove comments
        code = self._remove_comments(code)

        # Split into lines
        lines = [line.strip() for line in code.split("\n") if line.strip()]

        # First pass: find register declarations
        for line in lines:
            if line.startswith("qreg"):
                match = re.match(r"qreg\s+(\w+)\[(\d+)\]", line)
                if match:
                    self.num_qubits = int(match.group(2))
            elif line.startswith("creg"):
                match = re.match(r"creg\s+(\w+)\[(\d+)\]", line)
                if match:
                    self.num_classical_bits = int(match.group(2))

        # Default to 1 qubit if not specified
        if self.num_qubits == 0:
            # Try to infer from gate calls
            max_qubit = self._find_max_qubit(lines)
            self.num_qubits = max(1, max_qubit + 1)

        # Create circuit
        self.circuit = Circuit(self.num_qubits, self.num_classical_bits)

        # Second pass: parse gates and measurements
        for line in lines:
            self._parse_line(line)

        return self.circuit

    def _remove_comments(self, code: str) -> str:
        """Remove comments from code."""
        lines = []
        for line in code.split("\n"):
            # Remove inline comments
            if "#" in line:
                line = line[: line.index("#")]
            lines.append(line)
        return "\n".join(lines)

    def _find_max_qubit(self, lines: List[str]) -> int:
        """Find maximum qubit index used in gate calls."""
        max_qubit = -1
        for line in lines:
            # Match function calls with arguments
            matches = re.findall(r"\((\d+(?:\s*,\s*\d+)*)\)", line)
            for match in matches:
                qubits = [int(q.strip()) for q in match.split(",")]
                max_qubit = max(max_qubit, max(qubits) if qubits else -1)
        return max_qubit

    def _parse_line(self, line: str):
        """Parse a single line of DSL code."""
        # Skip register declarations (already processed)
        if line.startswith("qreg") or line.startswith("creg"):
            return

        # Match gate calls: gate_name(arg1, arg2, ...)
        match = re.match(r"(\w+)\s*\((.*?)\)", line)
        if not match:
            return

        gate_name = match.group(1).lower()
        args_str = match.group(2)

        # Parse arguments
        args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
        args_int = [int(arg) for arg in args]

        # Map gate names to gate constructors
        gate_map = {
            "x": lambda q: self.circuit.x(q),
            "y": lambda q: self.circuit.y(q),
            "z": lambda q: self.circuit.z(q),
            "h": lambda q: self.circuit.h(q),
            "s": lambda q: self.circuit.s(q),
            "t": lambda q: self.circuit.t(q),
            "rx": lambda q, theta: self.circuit.rx(q, theta),
            "ry": lambda q, theta: self.circuit.ry(q, theta),
            "rz": lambda q, theta: self.circuit.rz(q, theta),
            "cnot": lambda c, t: self.circuit.cnot(c, t),
            "cx": lambda c, t: self.circuit.cnot(c, t),
            "cz": lambda c, t: self.circuit.cz(c, t),
            "swap": lambda q1, q2: self.circuit.swap(q1, q2),
            "toffoli": lambda c1, c2, t: self.circuit.toffoli(c1, c2, t),
            "ccx": lambda c1, c2, t: self.circuit.toffoli(c1, c2, t),
            "measure": lambda q, c=None: self.circuit.measure(q, c),
        }

        if gate_name in gate_map:
            try:
                if gate_name in ["rx", "ry", "rz"]:
                    # Rotation gates: first arg is qubit, second is angle
                    if len(args_int) >= 2:
                        qubit = args_int[0]
                        # Try to parse angle (could be number or expression)
                        angle_str = args[1]
                        try:
                            angle = float(angle_str)
                        except ValueError:
                            # Try to evaluate as expression (e.g., "pi/2")
                            angle = self._evaluate_expression(angle_str)
                        gate_map[gate_name](qubit, angle)
                    else:
                        raise ValueError(f"{gate_name} requires qubit and angle")
                elif gate_name == "measure":
                    if len(args_int) >= 1:
                        qubit = args_int[0]
                        classical_bit = args_int[1] if len(args_int) > 1 else None
                        self.circuit.measure(qubit, classical_bit)
                    else:
                        raise ValueError("measure requires at least qubit index")
                else:
                    gate_map[gate_name](*args_int)
            except Exception as e:
                raise ValueError(f"Error parsing line '{line}': {e}")
        else:
            raise ValueError(f"Unknown gate: {gate_name}")

    def _evaluate_expression(self, expr: str) -> float:
        """Evaluate a mathematical expression (e.g., 'pi/2', '3.14')."""
        # Replace common constants
        expr = expr.replace("pi", str(np.pi))
        expr = expr.replace("π", str(np.pi))
        expr = expr.replace("e", str(np.e))

        # Evaluate safely
        try:
            return float(eval(expr, {"__builtins__": {}}, {}))
        except Exception:
            raise ValueError(f"Could not evaluate expression: {expr}")


# Convenience function for easy import
def parse_circuit(dsl_code: str) -> Circuit:
    """Parse DSL code into a Circuit."""
    return parse(dsl_code)


