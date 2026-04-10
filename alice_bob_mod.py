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

