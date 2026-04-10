from __future__ import annotations

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from qiskit.visualization import circuit_drawer
from qiskit_aer import AerSimulator

from src.analysis import qber_vs_attack
from src.circuits import build_single_bb84_circuit
from src.simulation import simulate_bb84


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --accent-cyan: #00e5ff;
            --accent-purple: #a855f7;
            --text-main: #e5e7eb;
            --text-muted: #9ca3af;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.10);
        }

        .stApp {
            background: radial-gradient(circle at 20% 20%, #1f1147 0%, #0b1023 40%, #04050a 100%);
            color: var(--text-main);
        }

        .main .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            color: #f3f4f6 !important;
            letter-spacing: 0.2px;
        }

        .subtitle {
            color: var(--text-muted);
            margin-top: -0.5rem;
            margin-bottom: 1.2rem;
        }

        .glass-card {
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
            padding: 1rem 1.1rem;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            margin-bottom: 1rem;
        }

        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(168, 85, 247, 0.35);
            box-shadow: 0 12px 36px rgba(0, 229, 255, 0.12);
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 0.6rem;
        }

        .metric-item {
            background: rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 0.8rem;
        }

        .metric-label {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }

        .metric-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: #f8fafc;
            text-shadow: 0 0 18px rgba(0, 229, 255, 0.18);
        }

        .section-title {
            font-size: 1.05rem;
            margin-bottom: 0.55rem;
            color: #f9fafb;
        }

        .accent {
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        .stButton > button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            background: linear-gradient(90deg, rgba(0,229,255,0.2), rgba(168,85,247,0.22));
            color: #f3f4f6;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            border-color: rgba(0,229,255,0.45);
            box-shadow: 0 0 20px rgba(0,229,255,0.22);
        }

        div[data-baseweb="slider"] > div {
            color: var(--accent-cyan) !important;
        }

        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input {
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.04);
            color: #f9fafb;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def plotly_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,12,24,0.55)",
        font=dict(color="#e5e7eb"),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
        margin=dict(l=24, r=24, t=50, b=24),
    )
    return fig


def render_metric_cards(sifted_length: int, qber: float, interceptions: int) -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">Simulation Results</div>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-label">Sifted Key Length</div>
                    <div class="metric-value">{sifted_length}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">QBER</div>
                    <div class="metric-value">{qber:.4f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Eve Interceptions</div>
                    <div class="metric-value">{interceptions}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="BB84 Premium Dashboard", layout="wide")
    inject_css()

    st.markdown("<h1>🔐 <span class='accent'>BB84 Quantum Dashboard</span></h1>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Modern glassmorphism interface for quantum key distribution simulation.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([0.95, 2.1], gap="large")

    with left:
        st.markdown("<div class='glass-card'><div class='section-title'>Input Controls</div>", unsafe_allow_html=True)
        n_qubits = st.slider("Qubits sent", min_value=64, max_value=4096, value=512, step=64)
        attack_probability = st.slider("Eve attack probability", min_value=0.0, max_value=1.0, value=0.35, step=0.05)
        random_seed = st.number_input("Random seed", min_value=0, max_value=1_000_000, value=42)
        run = st.button("Run Simulation ⚡", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            "<div class='glass-card'><div class='section-title'>Overview</div>"
            "Adjust parameters and run to see circuit behavior, output distribution, and attack-driven error trends."
            "</div>",
            unsafe_allow_html=True,
        )

    if not run:
        st.info("Click **Run Simulation ⚡** to generate results.")
        return

    with st.spinner("Running quantum simulation..."):
        result = simulate_bb84(
            n_qubits=n_qubits,
            eve_present=attack_probability > 0,
            attack_probability=attack_probability,
            seed=int(random_seed),
        )

        render_metric_cards(
            sifted_length=result.sifted_length,
            qber=result.qber,
            interceptions=int(np.sum(result.eve_intercepted)),
        )

        col_a, col_b = st.columns([1.05, 1.2], gap="large")

        with col_a:
            st.markdown("<div class='glass-card'><div class='section-title'>Circuit Visualization</div>", unsafe_allow_html=True)
            st.caption("Single-qubit BB84 transmission path with optional Eve interception.")
            example_circuit = build_single_bb84_circuit(1, 1, 0, eve_present=attack_probability > 0, eve_basis=1)
            st.pyplot(circuit_drawer(example_circuit, output="mpl"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("<div class='glass-card'><div class='section-title'>Measurement Distribution</div>", unsafe_allow_html=True)
            counts = AerSimulator().run(example_circuit, shots=1024).result().get_counts()
            histogram_frame = pd.DataFrame({"state": list(counts.keys()), "count": list(counts.values())})
            hist_fig = px.bar(
                histogram_frame,
                x="state",
                y="count",
                color="state",
                text="count",
                title="Outcome histogram",
                color_discrete_sequence=px.colors.sequential.Plasma,
            )
            hist_fig = plotly_theme(hist_fig)
            hist_fig.update_traces(textposition="outside")
            st.plotly_chart(hist_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'><div class='section-title'>Bit Transmission Preview</div>", unsafe_allow_html=True)
        preview_n = min(64, n_qubits)
        transmission = pd.DataFrame(
            {
                "index": np.arange(preview_n),
                "alice": result.alice_bits[:preview_n],
                "bob": result.bob_results[:preview_n],
                "basis_match": [int(a == b) for a, b in zip(result.alice_bases[:preview_n], result.bob_bases[:preview_n])],
            }
        )
        st.dataframe(transmission, use_container_width=True, height=260)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'><div class='section-title'>Error Rate vs Attack Probability</div>", unsafe_allow_html=True)
        attack_grid = np.round(np.linspace(0.0, 1.0, 11), 2).tolist()
        qber_frame = qber_vs_attack(
            n_qubits=max(256, n_qubits // 2),
            attack_probabilities=attack_grid,
            trials=8,
        )
        qber_fig = px.line(
            qber_frame,
            x="attack_probability",
            y="qber_mean",
            error_y="qber_std",
            markers=True,
            title="QBER trend under increasing interception",
        )
        qber_fig.update_traces(line=dict(width=3, color="#00e5ff"), marker=dict(size=8, color="#a855f7"))
        qber_fig = plotly_theme(qber_fig)
        qber_fig.update_layout(xaxis_title="Attack probability", yaxis_title="QBER")
        st.plotly_chart(qber_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
