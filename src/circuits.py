from __future__ import annotations

from qiskit import QuantumCircuit


BASIS_LABELS = {0: "Z", 1: "X"}


def build_single_bb84_circuit(
    alice_bit: int,
    alice_basis: int,
    bob_basis: int,
    eve_present: bool = False,
    eve_basis: int | None = None,
) -> QuantumCircuit:
    """Build a compact, visual BB84 circuit for one transmitted qubit."""
    clbits = 2 if eve_present else 1
    circuit = QuantumCircuit(1, clbits)

    if alice_basis == 0 and alice_bit == 1:
        circuit.x(0)
    elif alice_basis == 1 and alice_bit == 0:
        circuit.h(0)
    elif alice_basis == 1 and alice_bit == 1:
        circuit.x(0)
        circuit.h(0)

    if eve_present and eve_basis is not None:
        circuit.barrier(label="Eve")
        if eve_basis == 1:
            circuit.h(0)
        circuit.measure(0, 0)
        circuit.reset(0)
        if eve_basis == 1:
            circuit.h(0)

    circuit.barrier(label="To Bob")
    if bob_basis == 1:
        circuit.h(0)
    circuit.measure(0, 1 if eve_present else 0)

    circuit.name = (
        f"A({alice_bit},{BASIS_LABELS[alice_basis]}) "
        f"B({BASIS_LABELS[bob_basis]})"
    )
    return circuit
