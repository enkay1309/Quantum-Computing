from __future__ import annotations

import numpy as np
import pandas as pd

from src.simulation import simulate_bb84


def qber_vs_attack(
    n_qubits: int,
    attack_probabilities: list[float],
    trials: int,
) -> pd.DataFrame:
    rows = []
    for probability in attack_probabilities:
        qbers = [
            simulate_bb84(
                n_qubits=n_qubits,
                eve_present=probability > 0,
                attack_probability=probability,
            ).qber
            for _ in range(trials)
        ]
        rows.append(
            {
                "attack_probability": probability,
                "qber_mean": float(np.mean(qbers)),
                "qber_std": float(np.std(qbers)),
            }
        )
    return pd.DataFrame(rows)


def key_length_vs_qubits(
    qubit_sizes: list[int],
    trials: int,
    attack_probability: float,
) -> pd.DataFrame:
    rows = []
    for qubit_count in qubit_sizes:
        lengths = [
            simulate_bb84(
                n_qubits=qubit_count,
                eve_present=attack_probability > 0,
                attack_probability=attack_probability,
            ).sifted_length
            for _ in range(trials)
        ]
        rows.append(
            {
                "n_qubits": qubit_count,
                "key_length_mean": float(np.mean(lengths)),
                "key_length_std": float(np.std(lengths)),
                "efficiency": float(np.mean(lengths) / qubit_count),
            }
        )
    return pd.DataFrame(rows)
