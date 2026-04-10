from __future__ import annotations

from dataclasses import dataclass, asdict
import random
from typing import List


@dataclass
class BB84Result:
    n_qubits: int
    attack_probability: float
    eve_present: bool
    alice_bits: List[int]
    alice_bases: List[int]
    bob_bases: List[int]
    eve_bases: List[int | None]
    eve_intercepted: List[bool]
    bob_results: List[int]
    sifted_alice: List[int]
    sifted_bob: List[int]
    sifted_length: int
    qber: float

    def to_dict(self) -> dict:
        return asdict(self)


def random_bits(size: int, rng: random.Random) -> List[int]:
    return [rng.randint(0, 1) for _ in range(size)]


def simulate_bb84(
    n_qubits: int,
    eve_present: bool = False,
    attack_probability: float = 1.0,
    seed: int | None = None,
) -> BB84Result:
    rng = random.Random(seed)

    alice_bits = random_bits(n_qubits, rng)
    alice_bases = random_bits(n_qubits, rng)  # 0=Z, 1=X
    bob_bases = random_bits(n_qubits, rng)

    eve_bases: List[int | None] = [None] * n_qubits
    eve_intercepted = [False] * n_qubits
    channel_bits = list(alice_bits)

    if eve_present:
        sampled_eve_bases = random_bits(n_qubits, rng)
        for idx in range(n_qubits):
            if rng.random() <= attack_probability:
                eve_intercepted[idx] = True
                eve_bases[idx] = sampled_eve_bases[idx]
                if sampled_eve_bases[idx] != alice_bases[idx]:
                    channel_bits[idx] = rng.randint(0, 1)

    bob_results: List[int] = []
    for idx in range(n_qubits):
        if bob_bases[idx] == alice_bases[idx]:
            bob_results.append(channel_bits[idx])
        else:
            bob_results.append(rng.randint(0, 1))

    sifted_alice = []
    sifted_bob = []
    for a_bit, b_bit, a_basis, b_basis in zip(alice_bits, bob_results, alice_bases, bob_bases):
        if a_basis == b_basis:
            sifted_alice.append(a_bit)
            sifted_bob.append(b_bit)

    sifted_length = len(sifted_alice)
    if sifted_length == 0:
        qber = 0.0
    else:
        errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
        qber = errors / sifted_length

    return BB84Result(
        n_qubits=n_qubits,
        attack_probability=attack_probability,
        eve_present=eve_present,
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        eve_bases=eve_bases,
        eve_intercepted=eve_intercepted,
        bob_results=bob_results,
        sifted_alice=sifted_alice,
        sifted_bob=sifted_bob,
        sifted_length=sifted_length,
        qber=qber,
    )
