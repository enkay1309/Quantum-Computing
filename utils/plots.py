from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit.visualization import plot_histogram

from src.analysis import qber_vs_attack, key_length_vs_qubits


def save_qber_plot(output_dir: Path, n_qubits: int = 1000, trials: int = 20) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    attack_values = np.round(np.linspace(0.0, 1.0, 11), 2).tolist()
    frame = qber_vs_attack(n_qubits=n_qubits, attack_probabilities=attack_values, trials=trials)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(
        frame["attack_probability"],
        frame["qber_mean"],
        yerr=frame["qber_std"],
        fmt="o-",
        capsize=3,
        label="Simulation",
    )
    ax.plot(frame["attack_probability"], 0.25 * frame["attack_probability"], "--", label="Theory (0.25p)")
    ax.set_xlabel("Attack probability")
    ax.set_ylabel("QBER")
    ax.set_title("BB84 error rate under interception")
    ax.grid(alpha=0.3)
    ax.legend()

    path = output_dir / "qber_vs_attack.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_key_length_plot(output_dir: Path, trials: int = 20) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = key_length_vs_qubits(
        qubit_sizes=[128, 256, 512, 1024, 2048],
        trials=trials,
        attack_probability=0.5,
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(frame["n_qubits"], frame["key_length_mean"], yerr=frame["key_length_std"], fmt="o-")
    ax.plot(frame["n_qubits"], frame["n_qubits"] * 0.5, "--", label="Expected 50% sift")
    ax.set_xlabel("Qubits sent")
    ax.set_ylabel("Sifted key length")
    ax.set_title("BB84 key throughput")
    ax.grid(alpha=0.3)
    ax.legend()

    path = output_dir / "key_length.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_measurement_histogram(counts: dict[str, int], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig = plot_histogram(counts)
    path = output_dir / "measurement_histogram.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
