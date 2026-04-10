import random
from qiskit import QuantumCircuit

from alice_bob_mod import alice_bit_generator
from alice_bob_mod import alice_bases_generator
from alice_bob_mod import encode_qubits
from evemod import eve_attack


def eve_bases_generator(n):
    return [random.randint(0, 1) for _ in range(n)]


def simulate_bb84(n_qubits, eve_present=False, eve_attack_prob=1.0):
    """
    Simulate the BB84 QKD protocol using functions from alice_bob_mod and evemod.

    Uses a fast probabilistic model that matches the quantum physics
    (no circuit execution needed for large-scale statistics).

    Parameters:
        n_qubits: Number of qubits Alice sends
        eve_present: Whether Eve intercepts
        eve_attack_prob: Probability Eve intercepts each qubit (0.0 to 1.0)

    Returns:
        Dictionary with simulation results including sifted keys and QBER
    """
    # --- Alice (from alice_bob_mod) ---
    alice_bits = alice_bit_generator(n_qubits)
    alice_bases = alice_bases_generator(n_qubits)

    # --- Bob basis selection (same generator) ---
    bob_bases = alice_bases_generator(n_qubits)

    # --- Eve interception tracking ---
    eve_intercepted = [False] * n_qubits
    eve_bases = [None] * n_qubits
    eve_results = [None] * n_qubits

    actual_bits = list(alice_bits)

    # --- Eve attack (probabilistic model matching evemod logic) ---
    if eve_present:
        eve_bases_list = eve_bases_generator(n_qubits)
        for i in range(n_qubits):
            if random.random() < eve_attack_prob:
                eve_intercepted[i] = True
                eve_bases[i] = eve_bases_list[i]

                # Eve measures: same basis -> gets correct bit
                #               different basis -> random result
                if eve_bases[i] == alice_bases[i]:
                    eve_results[i] = alice_bits[i]
                else:
                    eve_results[i] = random.randint(0, 1)

                # Eve resends what she measured
                actual_bits[i] = eve_results[i]

    # --- Bob measurement ---
    bob_results = []
    for i in range(n_qubits):
        if bob_bases[i] == alice_bases[i]:
            bob_results.append(actual_bits[i])
        else:
            bob_results.append(random.randint(0, 1))

    # --- Key sifting (matching bases only) ---
    sifted_alice = []
    sifted_bob = []
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])

    # --- QBER calculation ---
    sifted_length = len(sifted_alice)
    if sifted_length > 0:
        errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
        qber = errors / sifted_length
    else:
        qber = 0.0

    return {
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_results': bob_results,
        'sifted_alice': sifted_alice,
        'sifted_bob': sifted_bob,
        'sifted_length': sifted_length,
        'qber': qber,
        'eve_intercepted': eve_intercepted,
    }


def build_bb84_circuit_example(alice_bit, alice_basis, bob_basis,
                                eve_present=False, eve_basis=None):
    """
    Build a demonstration Qiskit circuit for a single qubit BB84 exchange.

    Uses the same encoding logic as alice_bob_mod.encode_qubits and
    the same Eve attack structure as evemod.eve_attack.
    """
    if eve_present:
        qc = QuantumCircuit(1, 2)
        qc.name = f"BB84 | Alice({alice_bit},{['Z','X'][alice_basis]}) " \
                   f"Eve({['Z','X'][eve_basis]}) Bob({['Z','X'][bob_basis]})"
    else:
        qc = QuantumCircuit(1, 1)
        qc.name = f"BB84 | Alice({alice_bit},{['Z','X'][alice_basis]}) " \
                   f"Bob({['Z','X'][bob_basis]})"

    # Alice encoding (same logic as alice_bob_mod.encode_qubits)
    if alice_basis == 0:
        if alice_bit == 1:
            qc.x(0)
    else:
        if alice_bit == 0:
            qc.h(0)
        else:
            qc.x(0)
            qc.h(0)

    qc.barrier(label='Send')

    # Eve interception (same logic as evemod.eve_attack)
    if eve_present and eve_basis is not None:
        if eve_basis == 1:
            qc.h(0)
        qc.measure(0, 0)
        qc.barrier(label='Eve')

        qc.reset(0)
        qc.x(0)
        if eve_basis == 1:
            qc.h(0)
        qc.barrier(label='Resend')

    # Bob measurement
    if bob_basis == 1:
        qc.h(0)

    if eve_present:
        qc.measure(0, 1)
    else:
        qc.measure(0, 0)

    return qc


if __name__ == '__main__':
    result = simulate_bb84(1000, eve_present=False)
    print(f"No Eve  -> Sifted key length: {result['sifted_length']}, QBER: {result['qber']:.4f}")

    result = simulate_bb84(1000, eve_present=True, eve_attack_prob=1.0)
    print(f"Eve 100% -> Sifted key length: {result['sifted_length']}, QBER: {result['qber']:.4f}")

    result = simulate_bb84(1000, eve_present=True, eve_attack_prob=0.5)
    print(f"Eve 50%  -> Sifted key length: {result['sifted_length']}, QBER: {result['qber']:.4f}")
