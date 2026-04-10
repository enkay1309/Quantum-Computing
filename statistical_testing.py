import random
from qiskit import QuantumCircuit
from qiskit_aer import Aer


n=8

#alice bit generator--

def alice_bit_generator(n):
    bits= []
    for i in range(n):    #n= number of bits to be generated
        bits.append(random.randint(0,1))
    return bits

def alice_bases_generator(n):
    bases= []    #Z-> 0, X-> 1
    for i in range(n):
        bases.append(random.randint(0,1))
    return bases

def encode_qubits(bits, bases):

    qc = QuantumCircuit(n, n)

    for i in range(len(bits)):

        if bases[i] == 0:
            if bits[i] == 1:
                qc.x(i)

        else:
            if bits[i] == 0:
                qc.h(i)
            else:
                qc.x(i)
                qc.h(i)

    return qc

alice_bits = alice_bit_generator(n)
alice_bases = alice_bases_generator(n)

print("Alice bits:", alice_bits)
print("Alice bases:", alice_bases)

# Encode qubits
qc = encode_qubits(alice_bits, alice_bases)


# Bob basis
bob_basis = alice_bases_generator(n)

print("Bob bases:", bob_basis)


# Bob measures the qubits
for i in range(n):
    
    if bob_basis[i] == 1:
        qc.h(i)

    qc.measure(i, i)

backend = Aer.get_backend("aer_simulator")

job = backend.run(qc, shots=5000)

result = job.result()

counts = result.get_counts()

print("Measurement result:", counts)









import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

n = 8
shots = 5000   # as required (1000–10000)

def alice_bit_generator(n):
    return [random.randint(0,1) for _ in range(n)]

def alice_bases_generator(n):
    return [random.randint(0,1) for _ in range(n)]

def encode_qubits(bits, bases):
    qc = QuantumCircuit(n, n)
    for i in range(n):
        if bases[i] == 0:
            if bits[i] == 1:
                qc.x(i)
        else:
            if bits[i] == 0:
                qc.h(i)
            else:
                qc.x(i)
                qc.h(i)
    return qc


def eve_bases_generator(n):
    return [random.randint(0,1) for _ in range(n)]

def eve_attack(qc, eve_bases, attack_prob):
    backend = Aer.get_backend('aer_simulator')

    for i in range(n):
        if random.random() < attack_prob:

            # Measure in Eve basis
            if eve_bases[i] == 1:
                qc.h(i)

            qc.measure(i, i)

            compiled = transpile(qc, backend)
            job = backend.run(compiled, shots=1)
            res = list(job.result().get_counts().keys())[0]
            bit = int(res[n-1-i])

            # Reset + resend
            qc.reset(i)

            if eve_bases[i] == 0:
                if bit == 1:
                    qc.x(i)
            else:
                if bit == 0:
                    qc.h(i)
                else:
                    qc.x(i)
                    qc.h(i)

    return qc


# -------------------------------
# MAIN PROGRAM
# -------------------------------

alice_bits = alice_bit_generator(n)
alice_bases = alice_bases_generator(n)

print("Alice bits:", alice_bits)
print("Alice bases:", alice_bases)

qc = encode_qubits(alice_bits, alice_bases)

eve_bases = eve_bases_generator(n)
attack_prob = 0.5   

qc = eve_attack(qc, eve_bases, attack_prob)

print("Eve bases:", eve_bases)
print("Attack probability:", attack_prob)


bob_basis = alice_bases_generator(n)
print("Bob bases:", bob_basis)

for i in range(n):
    if bob_basis[i] == 1:
        qc.h(i)
    qc.measure(i, i)

backend = Aer.get_backend('aer_simulator')

compiled = transpile(qc, backend)
job = backend.run(compiled, shots=shots)

res = job.result().get_counts()

print("Measurement:", res)





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
