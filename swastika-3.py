# ===============================
# BB84 STATISTICAL TESTING
# ===============================

from bb import alice_bit_generator
from bb import alice_bases_generator
from bb import encode_qubits

from evemod import eve_attack

from qiskit import transpile
from qiskit_aer import AerSimulator


# -------------------------------
# PARAMETERS
# -------------------------------
n = 8                 # number of qubits
runs = 200            # number of simulations
shots = 1             # one transmission per run
attack_prob = 0.5     # Eve attack probability


# -------------------------------
# BACKEND
# -------------------------------
backend = AerSimulator()


# -------------------------------
# STORE RESULTS
# -------------------------------
qber_list = []


# ===============================
# REPEATED SIMULATIONS
# ===============================
for _ in range(runs):

    # ---------------------------
    # ALICE
    # ---------------------------
    alice_bits = alice_bit_generator(n)
    alice_bases = alice_bases_generator(n)

    qc = encode_qubits(alice_bits, alice_bases)


    # ---------------------------
    # EVE ATTACK
    # ---------------------------
    qc, eve_bases = eve_attack(qc, n, attack_prob)


    # ---------------------------
    # BOB MEASUREMENT
    # ---------------------------
    bob_basis = alice_bases_generator(n)

    for i in range(n):
        if bob_basis[i] == 1:
            qc.h(i)
        qc.measure(i, i)


    # ---------------------------
    # RUN SIMULATION
    # ---------------------------
    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)

    res = job.result().get_counts()


    # ---------------------------
    # EXTRACT MEASURED BITS
    # ---------------------------
    bitstring = list(res.keys())[0]
    bitstring = bitstring[::-1]

    measured_bits = [int(b) for b in bitstring]


    # ---------------------------
    # KEY SIFTING
    # ---------------------------
    sifted_alice = []
    sifted_bob = []

    for i in range(n):
        if alice_bases[i] == bob_basis[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(measured_bits[i])


    # ---------------------------
    # QBER CALCULATION
    # ---------------------------
    if len(sifted_alice) == 0:
        qber_list.append(0)

    else:
        errors = 0

        for i in range(len(sifted_alice)):
            if sifted_alice[i] != sifted_bob[i]:
                errors += 1

        qber = errors / len(sifted_alice)

        qber_list.append(qber)


# ===============================
# FINAL RESULTS
# ===============================
avg_qber = sum(qber_list) / len(qber_list)
avg_error_percent = avg_qber * 100

print("\n===============================")
print("Average QBER over", runs, "runs:", avg_qber)
print("Average Error Percentage:", avg_error_percent, "%")
print("===============================")
