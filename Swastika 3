# ===============================
# 1.3 STATISTICAL TESTING
# ===============================

from qiskit import transpile

# Extract most probable bitstring
bitstring = max(res, key=res.get)
bitstring = bitstring[::-1]   # reverse due to Qiskit ordering
measured_bits = [int(b) for b in bitstring]

print("Measured bits:", measured_bits)

# -------------------------------
# KEY SIFTING
# -------------------------------
sifted_alice = []
sifted_bob = []

for i in range(n):
    if alice_bases[i] == bob_basis[i]:
        sifted_alice.append(alice_bits[i])
        sifted_bob.append(measured_bits[i])

print("Sifted Alice key:", sifted_alice)
print("Sifted Bob key:", sifted_bob)

# -------------------------------
# ERROR COMPARISON
# -------------------------------
errors = 0

for i in range(len(sifted_alice)):
    if sifted_alice[i] != sifted_bob[i]:
        errors += 1

print("Total errors:", errors)

# -------------------------------
# QBER + ERROR PERCENTAGE
# -------------------------------
if len(sifted_alice) == 0:
    qber = 0
    error_percent = 0
else:
    qber = errors / len(sifted_alice)
    error_percent = qber * 100

print("QBER:", qber)
print("Error Percentage:", error_percent, "%")


# ===============================
# REPEATED SIMULATIONS
# ===============================
runs = 20
shots = 5000   # within required range

qber_list = []

backend = Aer.get_backend('aer_simulator')

for _ in range(runs):

    # Alice
    alice_bits = alice_bit_generator(n)
    alice_bases = alice_bases_generator(n)
    qc = encode_qubits(alice_bits, alice_bases)

    # Eve (from 1.2)
    eve_bases = eve_bases_generator(n)
    qc = eve_attack(qc, eve_bases, attack_prob)

    # Bob
    bob_basis = alice_bases_generator(n)

    for i in range(n):
        if bob_basis[i] == 1:
            qc.h(i)
        qc.measure(i, i)

    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots)
    res = job.result().get_counts()

    bitstring = max(res, key=res.get)[::-1]
    measured_bits = [int(b) for b in bitstring]

    # Sifting
    sifted_alice = []
    sifted_bob = []

    for i in range(n):
        if alice_bases[i] == bob_basis[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(measured_bits[i])

    # QBER calculation
    if len(sifted_alice) == 0:
        qber_list.append(0)
    else:
        errors = sum(1 for i in range(len(sifted_alice)) if sifted_alice[i] != sifted_bob[i])
        qber_value = errors / len(sifted_alice)
        qber_list.append(qber_value)

# -------------------------------
# FINAL AVERAGE RESULTS
# -------------------------------
avg_qber = sum(qber_list) / len(qber_list)
avg_error_percent = avg_qber * 100

print("Average QBER over", runs, "runs:", avg_qber)
print("Average Error Percentage:", avg_error_percent, "%")
