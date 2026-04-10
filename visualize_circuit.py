import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit

from bb import encode_qubits
from bb84_simulation import build_bb84_circuit_example


# ------------------ ALICE ------------------

def create_alice_encoding_circuits():
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle("Alice's Qubit Encoding in BB84", fontsize=16, fontweight='bold', y=0.98)

    configs = [
        (0, 0, "Bit=0, Z-basis → |0⟩"),
        (1, 0, "Bit=1, Z-basis → |1⟩"),
        (0, 1, "Bit=0, X-basis → |+⟩"),
        (1, 1, "Bit=1, X-basis → |−⟩"),
    ]

    for idx, (bit, basis, title) in enumerate(configs):
        qc = QuantumCircuit(1)

        if basis == 0:
            if bit == 1:
                qc.x(0)
        else:
            if bit == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)

        ax = axes[idx // 2][idx % 2]
        qc.draw('mpl', ax=ax)
        ax.set_title(title, fontsize=12, fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('circuit_alice_encoding.png', dpi=200, bbox_inches='tight')
    plt.close()

    print("  [OK] circuit_alice_encoding.png")


# ------------------ BOB ------------------

def create_bob_measurement_circuits():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Bob's Measurement in BB84", fontsize=16, fontweight='bold')

    # Matching basis
    qc1 = QuantumCircuit(1, 1)
    qc1.x(0)
    qc1.barrier(label='Channel')
    qc1.measure(0, 0)

    qc1.draw('mpl', ax=axes[0])
    axes[0].set_title("Z → Z (Correct)", fontsize=11, fontweight='bold')

    # Mismatch
    qc2 = QuantumCircuit(1, 1)
    qc2.x(0)
    qc2.barrier(label='Channel')
    qc2.h(0)
    qc2.measure(0, 0)

    qc2.draw('mpl', ax=axes[1])
    axes[1].set_title("Z → X (Random)", fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig('circuit_bob_measurement.png', dpi=200, bbox_inches='tight')
    plt.close()

    print("  [OK] circuit_bob_measurement.png")


# ------------------ EVE (UPGRADED 🔥) ------------------

def create_eve_interception_circuit():
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("BB84: Without vs With Eve (Interception Attack)",
                 fontsize=16, fontweight='bold')

    # -------- WITHOUT EVE --------
    qc1 = QuantumCircuit(1, 1)

    qc1.x(0)  # Alice sends |1⟩
    qc1.barrier(label='Quantum Channel')
    qc1.measure(0, 0)

    qc1.draw('mpl', ax=axes[0])
    axes[0].set_title("No Eve → Correct Transmission ✔", fontsize=11, fontweight='bold')

    # -------- WITH EVE --------
    qc2 = QuantumCircuit(1, 1)

    # Alice
    qc2.x(0)

    qc2.barrier(label='Eve Intercepts')

    # Eve measures in X basis
    qc2.h(0)
    qc2.measure(0, 0)

    qc2.barrier(label='Eve Resends')

    # Reset + resend wrong basis
    qc2.reset(0)
    qc2.h(0)

    qc2.barrier(label='To Bob')

    # Bob measures in Z
    qc2.measure(0, 0)

    qc2.draw('mpl', ax=axes[1])
    axes[1].set_title("Eve Attack → Disturbance ❌", fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig('circuit_eve_attack.png', dpi=200, bbox_inches='tight')
    plt.close()

    print("  [OK] circuit_eve_attack.png")


# ------------------ FULL PROTOCOL ------------------

def create_full_protocol_circuit():
    n = 4

    alice_bits =  [1, 0, 1, 0]
    alice_bases = [0, 1, 1, 0]
    bob_bases   = [0, 0, 1, 1]

    import bb
    old_n = bb.n
    bb.n = n

    qc = encode_qubits(alice_bits, alice_bases)

    bb.n = old_n

    qc.barrier(label='Quantum Channel (Eve may intercept)')

    for i in range(n):
        if bob_bases[i] == 1:
            qc.h(i)
        qc.measure(i, i)

    fig, ax = plt.subplots(figsize=(14, 6))
    qc.draw('mpl', ax=ax)

    title = "Full BB84 Protocol (4 Qubits)\n"
    title += "Alice bits: [1,0,1,0] | Bases: [Z,X,X,Z]\n"
    title += "Bob bases:  [Z,Z,X,X]\n"
    title += "Matching → q0, q2 → Final Key"

    ax.set_title(title, fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig('circuit_full_protocol.png', dpi=200, bbox_inches='tight')
    plt.close()

    print("  [OK] circuit_full_protocol.png")


# ------------------ RUN ALL ------------------

def run_all():
    print("\n[CIRCUITS] Generating Visualizations...\n")

    create_alice_encoding_circuits()
    create_bob_measurement_circuits()
    create_eve_interception_circuit()
    create_full_protocol_circuit()

    print("\n  DONE 🚀\n")


if __name__ == '__main__':
    run_all()
