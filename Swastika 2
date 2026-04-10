#Statistical testing
#----------------
from bb import alice_bit_generator
from bb import alice_bases_generator
from evemod import eve_bases_generator
from evemod import eve-attack

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
