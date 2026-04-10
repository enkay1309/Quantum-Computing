# Quantum Computing BB84 Suite

A refactored, portfolio-ready BB84 quantum key distribution project with:
- modular simulation code,
- CLI execution,
- interactive dashboard,
- visualization outputs for circuits, histograms, key transmission, and QBER trends.

## Project Structure

```text
.
├── dashboard/
│   └── app.py
├── outputs/
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── circuits.py
│   └── simulation.py
├── utils/
│   ├── __init__.py
│   ├── logging_config.py
│   └── plots.py
├── main.py
├── requirements.txt
└── README.md
```

## Features

- **BB84 simulation** with/without eavesdropping (intercept-resend model).
- **Quantum circuit rendering** for protocol flow.
- **Measurement histogram plotting** from Aer simulation.
- **QBER trend analysis** across attack probabilities.
- **Sifted key throughput analysis**.
- **CLI support** for scriptable runs.
- **Streamlit dashboard** for interactive exploration.
- **Structured logging** for reproducible experiment output.

## Quick Start

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run CLI simulation

```bash
python main.py --n-qubits 1000 --attack 0.5 --seed 42
```

Artifacts are saved into `outputs/` by default.

### 3) Run dashboard

```bash
streamlit run dashboard/app.py
```

## CLI Options

```bash
python main.py --help
```

Key options:
- `--n-qubits`: number of transmitted qubits
- `--attack`: Eve attack probability in `[0, 1]`
- `--seed`: random seed
- `--output-dir`: output folder for generated files

## Sample Simulation Scenarios

- **No attack:** `python main.py --n-qubits 1000 --attack 0.0`
- **Partial attack:** `python main.py --n-qubits 1000 --attack 0.5`
- **Full attack:** `python main.py --n-qubits 1000 --attack 1.0`

Expected behavior:
- attack `0.0` => QBER near `0`
- attack `1.0` => QBER near `0.25`

## Screenshots

_Replace with dashboard screenshots._

- `docs/screenshots/dashboard-main.png` (placeholder)

