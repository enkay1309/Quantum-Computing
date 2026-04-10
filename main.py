from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from qiskit_aer import AerSimulator

from src.circuits import build_single_bb84_circuit
from src.simulation import simulate_bb84
from utils.logging_config import configure_logging
from utils.plots import save_key_length_plot, save_measurement_histogram, save_qber_plot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BB84 quantum key distribution simulations.")
    parser.add_argument("--n-qubits", type=int, default=1000, help="Number of transmitted qubits.")
    parser.add_argument("--attack", type=float, default=0.0, help="Eve interception probability [0,1].")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic runs.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Directory for plots and artifacts.")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level.")
    return parser.parse_args()


def run_cli() -> None:
    args = parse_args()
    configure_logging(args.log_level)
    logger = logging.getLogger("bb84")

    logger.info("Running BB84 simulation: n_qubits=%s, attack=%s", args.n_qubits, args.attack)
    result = simulate_bb84(
        n_qubits=args.n_qubits,
        eve_present=args.attack > 0,
        attack_probability=args.attack,
        seed=args.seed,
    )
    logger.info("Sifted length=%s | QBER=%.4f", result.sifted_length, result.qber)

    preview_circuit = build_single_bb84_circuit(1, 1, 0, eve_present=args.attack > 0, eve_basis=1)
    backend = AerSimulator()
    counts = backend.run(preview_circuit, shots=512).result().get_counts()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    qber_plot = save_qber_plot(args.output_dir)
    key_plot = save_key_length_plot(args.output_dir)
    hist_plot = save_measurement_histogram(counts, args.output_dir)

    summary_path = args.output_dir / "simulation_summary.json"
    summary_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    logger.info("Saved: %s", qber_plot)
    logger.info("Saved: %s", key_plot)
    logger.info("Saved: %s", hist_plot)
    logger.info("Saved: %s", summary_path)


if __name__ == "__main__":
    run_cli()
