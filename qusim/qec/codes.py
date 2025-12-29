"""
Quantum error correction code implementations.

Includes bit-flip, phase-flip, and Shor codes.
"""

from typing import List, Tuple, Optional
from qusim.core.circuit import Circuit
from qusim.core.gates import X, Z, CNOT, H


class QECCode:
    """Base class for quantum error correction codes."""

    def __init__(self, name: str, num_logical_qubits: int, num_physical_qubits: int):
        """
        Initialize QEC code.

        Args:
            name: Code name
            num_logical_qubits: Number of logical qubits
            num_physical_qubits: Number of physical qubits
        """
        self.name = name
        self.num_logical_qubits = num_logical_qubits
        self.num_physical_qubits = num_physical_qubits

    def encode(self, logical_qubit: int = 0) -> Circuit:
        """
        Create encoding circuit.

        Args:
            logical_qubit: Logical qubit index to encode

        Returns:
            Encoding circuit
        """
        raise NotImplementedError

    def syndrome_extraction(self) -> Circuit:
        """
        Create syndrome extraction circuit.

        Returns:
            Syndrome extraction circuit
        """
        raise NotImplementedError

    def decode(self, logical_qubit: int = 0) -> Circuit:
        """
        Create decoding circuit.

        Args:
            logical_qubit: Logical qubit index to decode

        Returns:
            Decoding circuit
        """
        raise NotImplementedError


class BitFlipCode(QECCode):
    """
    3-qubit bit-flip code.

    Encodes 1 logical qubit into 3 physical qubits.
    Protects against X errors.
    """

    def __init__(self):
        super().__init__("BitFlip", 1, 3)

    def encode(self, logical_qubit: int = 0) -> Circuit:
        """Create encoding circuit for bit-flip code."""
        circuit = Circuit(self.num_physical_qubits)

        # |ψ⟩ -> |ψ⟩|0⟩|0⟩
        # Apply CNOTs to create |ψ⟩|ψ⟩|ψ⟩
        circuit.cnot(logical_qubit, 1)
        circuit.cnot(logical_qubit, 2)

        return circuit

    def syndrome_extraction(self) -> Circuit:
        """Create syndrome extraction circuit."""
        circuit = Circuit(self.num_physical_qubits, num_classical_bits=2)

        # Ancilla qubits for syndrome (use qubits 3, 4 if available, otherwise use classical bits)
        # For simplicity, we'll use classical bits to store syndrome
        # Syndrome qubits: check parity between qubits 0-1 and qubits 1-2
        circuit.cnot(0, 1)  # This would need ancilla, simplified here
        circuit.measure(0, 0)
        circuit.measure(1, 1)

        return circuit

    def decode(self, logical_qubit: int = 0) -> Circuit:
        """Create decoding circuit."""
        circuit = Circuit(self.num_physical_qubits)

        # Reverse encoding
        circuit.cnot(logical_qubit, 2)
        circuit.cnot(logical_qubit, 1)

        return circuit


class PhaseFlipCode(QECCode):
    """
    3-qubit phase-flip code.

    Encodes 1 logical qubit into 3 physical qubits.
    Protects against Z errors.
    Uses Hadamard basis.
    """

    def __init__(self):
        super().__init__("PhaseFlip", 1, 3)

    def encode(self, logical_qubit: int = 0) -> Circuit:
        """Create encoding circuit for phase-flip code."""
        circuit = Circuit(self.num_physical_qubits)

        # Convert to Hadamard basis
        circuit.h(logical_qubit)
        circuit.h(1)
        circuit.h(2)

        # Apply bit-flip encoding in Hadamard basis
        circuit.cnot(logical_qubit, 1)
        circuit.cnot(logical_qubit, 2)

        return circuit

    def syndrome_extraction(self) -> Circuit:
        """Create syndrome extraction circuit."""
        circuit = Circuit(self.num_physical_qubits, num_classical_bits=2)

        # Convert back to computational basis for measurement
        circuit.h(0)
        circuit.h(1)
        circuit.h(2)

        circuit.measure(0, 0)
        circuit.measure(1, 1)

        return circuit

    def decode(self, logical_qubit: int = 0) -> Circuit:
        """Create decoding circuit."""
        circuit = Circuit(self.num_physical_qubits)

        # Reverse encoding
        circuit.cnot(logical_qubit, 2)
        circuit.cnot(logical_qubit, 1)

        # Convert back to computational basis
        circuit.h(logical_qubit)
        circuit.h(1)
        circuit.h(2)

        return circuit


class ShorCode(QECCode):
    """
    9-qubit Shor code.

    Encodes 1 logical qubit into 9 physical qubits.
    Protects against both bit-flip and phase-flip errors.
    """

    def __init__(self):
        super().__init__("Shor", 1, 9)

    def encode(self, logical_qubit: int = 0) -> Circuit:
        """Create encoding circuit for Shor code."""
        circuit = Circuit(self.num_physical_qubits)

        # First encode in 3-qubit phase-flip code
        circuit.h(logical_qubit)
        circuit.h(3)
        circuit.h(6)

        circuit.cnot(logical_qubit, 3)
        circuit.cnot(logical_qubit, 6)

        # Then encode each of the 3 qubits in bit-flip code
        # Block 1: qubits 0, 1, 2
        circuit.cnot(0, 1)
        circuit.cnot(0, 2)

        # Block 2: qubits 3, 4, 5
        circuit.cnot(3, 4)
        circuit.cnot(3, 5)

        # Block 3: qubits 6, 7, 8
        circuit.cnot(6, 7)
        circuit.cnot(6, 8)

        return circuit

    def syndrome_extraction(self) -> Circuit:
        """Create syndrome extraction circuit."""
        circuit = Circuit(self.num_physical_qubits, num_classical_bits=6)

        # Extract bit-flip syndromes for each block
        # Block 1
        circuit.measure(0, 0)
        circuit.measure(1, 1)

        # Block 2
        circuit.measure(3, 2)
        circuit.measure(4, 3)

        # Block 3
        circuit.measure(6, 4)
        circuit.measure(7, 5)

        return circuit

    def decode(self, logical_qubit: int = 0) -> Circuit:
        """Create decoding circuit."""
        circuit = Circuit(self.num_physical_qubits)

        # Reverse bit-flip encoding
        circuit.cnot(6, 8)
        circuit.cnot(6, 7)
        circuit.cnot(3, 5)
        circuit.cnot(3, 4)
        circuit.cnot(0, 2)
        circuit.cnot(0, 1)

        # Reverse phase-flip encoding
        circuit.cnot(logical_qubit, 6)
        circuit.cnot(logical_qubit, 3)

        circuit.h(6)
        circuit.h(3)
        circuit.h(logical_qubit)

        return circuit


def create_qec_circuit(
    code: QECCode,
    data_circuit: Optional[Circuit] = None,
    apply_errors: Optional[List[Tuple[str, int]]] = None,
) -> Circuit:
    """
    Create full QEC circuit with encoding, data operations, and decoding.

    Args:
        code: QEC code to use
        data_circuit: Circuit to apply to logical qubit (after encoding)
        apply_errors: List of (error_type, qubit) to apply (for testing)

    Returns:
        Full QEC circuit
    """
    full_circuit = Circuit(code.num_physical_qubits, num_classical_bits=code.num_physical_qubits)

    # Encode
    encode_circuit = code.encode(0)
    for gate, qubits in encode_circuit.gates:
        full_circuit.add_gate(gate, qubits)

    # Apply errors if specified
    if apply_errors:
        for error_type, qubit in apply_errors:
            if error_type == "X":
                full_circuit.x(qubit)
            elif error_type == "Z":
                full_circuit.z(qubit)
            elif error_type == "Y":
                full_circuit.y(qubit)

    # Apply data circuit (if provided)
    if data_circuit:
        # Map logical qubit operations to physical qubits
        # For simplicity, apply to first physical qubit
        for gate, qubits in data_circuit.gates:
            # Map qubit indices
            mapped_qubits = [q if q != 0 else 0 for q in qubits]
            full_circuit.add_gate(gate, mapped_qubits)

    # Syndrome extraction
    syndrome_circuit = code.syndrome_extraction()
    for gate, qubits in syndrome_circuit.gates:
        full_circuit.add_gate(gate, qubits)
    for qubit, classical_bit in syndrome_circuit.measurements:
        full_circuit.measure(qubit, classical_bit)

    # Decode
    decode_circuit = code.decode(0)
    for gate, qubits in decode_circuit.gates:
        full_circuit.add_gate(gate, qubits)

    return full_circuit


