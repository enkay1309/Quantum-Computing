import random
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer


# ===============================
# CONFIG
# ===============================
n = 8
shots = 1000
runs = 10
attack_prob = 0.3


# ===============================
# BB84 HELPERS
# ===============================
def alice_bit_generator(n):
    return [random.randint(0, 1) for _ in range(n)]


def alice_bases_generator(n):
    return [random.randint(0, 1) for _ in range(n)]


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
    return [random.randint(0, 1) for _ in range(n)]


def eve_attack(qc, eve_bases, attack_prob):
    backend = Aer.get_backend('aer_simulator')

    for i in range(n):
        if random.random() < attack_prob:

            if eve_bases[i] == 1:
                qc.h(i)

            qc.measure(i, i)

            compiled = transpile(qc, backend)
            job = backend.run(compiled, shots=1)

            res = list(job.result().get_counts().keys())[0]
            bit = int(res[n - 1 - i])

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


# ===============================
# SINGLE SIMULATION
# ===============================
def run_single_bb84(attack_prob):

    backend = Aer.get_backend('aer_simulator')

    alice_bits = alice_bit_generator(n)
    alice_bases = alice_bases_generator(n)

    qc = encode_qubits(alice_bits, alice_bases)

    eve_bases = eve_bases_generator(n)
    qc = eve_attack(qc, eve_bases, attack_prob)

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

    sifted_alice = []
    sifted_bob = []

    for i in range(n):
        if alice_bases[i] == bob_basis[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(measured_bits[i])

    if len(sifted_alice) == 0:
        qber = 0
        errors = 0
    else:
        errors = sum(
            1 for i in range(len(sifted_alice))
            if sifted_alice[i] != sifted_bob[i]
        )
        qber = errors / len(sifted_alice)

    return {
        "qber": qber,
        "errors": errors,
        "error_percentage": qber * 100,
        "sifted_length": len(sifted_alice),
        "sifted_alice": sifted_alice,
        "sifted_bob": sifted_bob
    }


# ===============================
# MAIN
# ===============================
print("=" * 60)
print("BB84 Statistical Testing with Qiskit")
print("=" * 60)

print("\nRunning single simulation...")
single_result = run_single_bb84(attack_prob)

print(f"QBER: {single_result['qber']:.4f}")
print(f"Error Percentage: {single_result['error_percentage']:.2f}%")
print(f"Errors: {single_result['errors']}")
print(f"Sifted Key Length: {single_result['sifted_length']}")
print(f"Sifted Alice Key: {single_result['sifted_alice']}")
print(f"Sifted Bob Key: {single_result['sifted_bob']}")


# ===============================
# REPEATED STATISTICAL RUNS
# ===============================
print(f"\nRunning {runs} repeated simulations...")

qber_list = []
key_length_list = []

for i in range(runs):
    result = run_single_bb84(attack_prob)

    qber_list.append(result["qber"])
    key_length_list.append(result["sifted_length"])

    print(
        f"Run {i+1:2d}: "
        f"QBER = {result['qber']:.4f}, "
        f"Errors = {result['errors']}, "
        f"Key Length = {result['sifted_length']}"
    )

avg_qber = np.mean(qber_list)
std_qber = np.std(qber_list)

print("\nAverage QBER:", avg_qber)
print("Average Error Percentage:", avg_qber * 100, "%")


# ===============================
# PLOT 1: QBER repeated runs
# ===============================
plt.figure(figsize=(12, 6))

runs_x = np.arange(1, runs + 1)

plt.plot(
    runs_x,
    qber_list,
    'o-',
    linewidth=2,
    markersize=7,
    color='blue',
    label='QBER per run'
)

plt.axhline(
    avg_qber,
    color='red',
    linestyle='--',
    linewidth=2,
    label=f'Average QBER = {avg_qber:.4f}'
)

plt.fill_between(
    runs_x,
    avg_qber - std_qber,
    avg_qber + std_qber,
    alpha=0.2,
    color='skyblue',
    label='±1 Std Dev'
)

plt.xlabel("Run Number")
plt.ylabel("QBER")
plt.title("BB84 Statistical Testing - QBER Across Runs")
plt.grid(True, alpha=0.3)
plt.legend()

plt.savefig("statistical_testing_qber.png", dpi=200, bbox_inches='tight')
print("[OK] Saved statistical_testing_qber.png")

plt.close()


# ===============================
# PLOT 2: Surface + Heatmap
# ===============================
print("\nGenerating statistical surface / heatmap...")

attack_probs = np.arange(0.0, 1.05, 0.2)
run_values = np.arange(1, runs + 1)

X, Y = np.meshgrid(attack_probs, run_values)
Z = np.zeros_like(X)

for i in range(len(run_values)):
    for j in range(len(attack_probs)):
        result = run_single_bb84(attack_probs[j])
        Z[i, j] = result["qber"]


# 3D Surface
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(
    X,
    Y,
    Z,
    cmap='coolwarm',
    edgecolor='none',
    alpha=0.85
)

fig.colorbar(surf, shrink=0.5, aspect=10)

ax.set_xlabel("Attack Probability")
ax.set_ylabel("Run Number")
ax.set_zlabel("QBER")
ax.set_title("BB84 QBER Surface (Qiskit Statistical Testing)")

plt.tight_layout()
plt.savefig("statistical_qber_surface_3d.png", dpi=200, bbox_inches='tight')
print("[OK] Saved statistical_qber_surface_3d.png")

plt.close()


# Heatmap
plt.figure(figsize=(10, 6))

plt.imshow(
    Z,
    aspect='auto',
    origin='lower',
    cmap='coolwarm',
    extent=[
        attack_probs[0],
        attack_probs[-1],
        run_values[0],
        run_values[-1]
    ]
)

plt.colorbar(label="QBER")

plt.xlabel("Attack Probability")
plt.ylabel("Run Number")
plt.title("BB84 QBER Heatmap (Qiskit Statistical Testing)")

plt.tight_layout()
plt.savefig("statistical_qber_heatmap.png", dpi=200, bbox_inches='tight')
print("[OK] Saved statistical_qber_heatmap.png")

plt.close()

print("\nDone.")