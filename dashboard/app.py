from __future__ import annotations

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer

from src.analysis import qber_vs_attack
from src.circuits import build_single_bb84_circuit
from src.simulation import simulate_bb84

st.set_page_config(page_title="BB84 Dashboard", layout="wide")

st.title("🔐 BB84 Quantum Key Distribution Dashboard")
st.caption("Interactive simulation for circuit flow, measurement distributions, and eavesdropping impact.")

with st.sidebar:
    st.header("Input Parameters")
    n_qubits = st.slider("Qubits sent", min_value=64, max_value=4096, value=512, step=64)
    attack_probability = st.slider("Eve attack probability", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
    random_seed = st.number_input("Random seed", min_value=0, max_value=1_000_000, value=42)
    run = st.button("Run simulation", type="primary")

if run:
    result = simulate_bb84(
        n_qubits=n_qubits,
        eve_present=attack_probability > 0,
        attack_probability=attack_probability,
        seed=int(random_seed),
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Sifted key length", result.sifted_length)
    col2.metric("QBER", f"{result.qber:.4f}")
    col3.metric("Eve interceptions", int(np.sum(result.eve_intercepted)))

    st.subheader("Quantum Circuit")
    example_circuit = build_single_bb84_circuit(1, 1, 0, eve_present=attack_probability > 0, eve_basis=1)
    circuit_figure = circuit_drawer(example_circuit, output="mpl")
    st.pyplot(circuit_figure)

    st.subheader("Measurement Histogram")
    counts = AerSimulator().run(example_circuit, shots=1024).result().get_counts()
    histogram_frame = pd.DataFrame({"state": list(counts.keys()), "count": list(counts.values())})
    st.plotly_chart(px.bar(histogram_frame, x="state", y="count", color="state", title="Outcome counts"), use_container_width=True)

    st.subheader("Bit Transmission Preview (first 64 bits)")
    preview_n = min(64, n_qubits)
    transmission = pd.DataFrame(
        {
            "index": np.arange(preview_n),
            "alice": result.alice_bits[:preview_n],
            "bob": result.bob_results[:preview_n],
            "basis_match": [int(a == b) for a, b in zip(result.alice_bases[:preview_n], result.bob_bases[:preview_n])],
        }
    )
    st.dataframe(transmission, use_container_width=True)

    st.subheader("Error Rate vs Attack Probability")
    attack_grid = np.round(np.linspace(0, 1, 11), 2).tolist()
    qber_frame = qber_vs_attack(n_qubits=max(256, n_qubits // 2), attack_probabilities=attack_grid, trials=8)
    st.plotly_chart(
        px.line(qber_frame, x="attack_probability", y="qber_mean", error_y="qber_std", markers=True, title="QBER curve"),
        use_container_width=True,
    )
else:
    st.info("Set parameters in the sidebar and click **Run simulation**.")
