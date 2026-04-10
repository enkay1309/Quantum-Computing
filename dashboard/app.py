from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from qiskit.visualization import circuit_drawer
from qiskit_aer import AerSimulator

from src.analysis import qber_vs_attack
from src.circuits import build_single_bb84_circuit
from src.simulation import simulate_bb84


ACCENT = "#7c8cff"  # soft purple


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: #0b0f1a;
            --text: #f5f7ff;
            --muted: #8e96ab;
            --accent: {ACCENT};
            --card-bg: rgba(255,255,255,0.03);
            --card-border: rgba(255,255,255,0.08);
        }}

        .stApp {{
            background: var(--bg);
            color: var(--text);
        }}

        .main .block-container {{
            max-width: 1160px;
            padding-top: 2.4rem;
            padding-bottom: 2.4rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }}

        header[data-testid="stHeader"], footer {{
            display: none !important;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        .title {{
            font-size: 2rem;
            font-weight: 650;
            letter-spacing: 0.1px;
            margin-bottom: 0.35rem;
        }}

        .subtitle {{
            color: var(--muted);
            font-size: 0.98rem;
            margin-bottom: 1.35rem;
        }}

        .glass-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 1.1rem 1.1rem;
            margin-bottom: 1.1rem;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        }}

        .glass-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(124,140,255,0.28);
            box-shadow: 0 8px 28px rgba(124,140,255,0.10);
        }}

        .section-title {{
            color: var(--text);
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.7rem;
        }}

        .section-note {{
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: -0.2rem;
            margin-bottom: 0.75rem;
        }}

        .metrics-row {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
        }}

        .metric-card {{
            background: rgba(255,255,255,0.015);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 0.8rem;
        }}

        .metric-label {{
            color: var(--muted);
            font-size: 0.78rem;
            margin-bottom: 0.3rem;
        }}

        .metric-value {{
            color: var(--text);
            font-size: 1.35rem;
            font-weight: 650;
            line-height: 1.2;
            text-shadow: 0 0 18px rgba(124,140,255,0.2);
        }}

        .stButton > button {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(124,140,255,0.14);
            color: var(--text);
            font-weight: 600;
            transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }}

        .stButton > button:hover {{
            border-color: rgba(124,140,255,0.45);
            box-shadow: 0 0 16px rgba(124,140,255,0.23);
            transform: translateY(-1px);
        }}

        div[data-baseweb="slider"] > div {{
            color: var(--accent) !important;
        }}

        div[data-baseweb="slider"] div[role="slider"] {{
            box-shadow: 0 0 0 3px rgba(124,140,255,0.2);
        }}

        div[data-testid="stNumberInput"] input {{
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(255,255,255,0.02);
            color: var(--text);
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_plotly(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.01)",
        font=dict(color="#f5f7ff"),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
        margin=dict(l=20, r=20, t=48, b=20),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    return fig


def render_metrics(result) -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">Key Metrics</div>
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-label">Sifted Key Length</div>
                    <div class="metric-value">{result.sifted_length}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">QBER</div>
                    <div class="metric-value">{result.qber:.4f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Eve Interceptions</div>
                    <div class="metric-value">{int(np.sum(result.eve_intercepted))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="BB84 Dashboard", layout="wide")
    inject_css()

    st.markdown("<div class='title'>BB84 Quantum Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>A minimal, premium control surface for BB84 simulation and protocol diagnostics.</div>",
        unsafe_allow_html=True,
    )

    controls_col, results_col = st.columns([0.9, 2.1], gap="large")

    with controls_col:
        st.markdown("<div class='glass-card'><div class='section-title'>Simulation Controls</div>", unsafe_allow_html=True)
        n_qubits = st.slider("Qubits", min_value=64, max_value=4096, value=512, step=64)
        attack_probability = st.slider("Eve attack probability", min_value=0.0, max_value=1.0, value=0.30, step=0.05)
        random_seed = st.number_input("Seed", min_value=0, max_value=1_000_000, value=42)
        run = st.button("Run Simulation")
        st.markdown("</div>", unsafe_allow_html=True)

    with results_col:
        st.markdown(
            "<div class='glass-card'><div class='section-title'>Results</div>"
            "<div class='section-note'>Run a simulation to update circuit, histogram, and QBER trend analysis.</div></div>",
            unsafe_allow_html=True,
        )

    if not run:
        st.info("Run the simulation to view updated outputs.")
        return

    with st.spinner("Computing simulation..."):
        result = simulate_bb84(
            n_qubits=n_qubits,
            eve_present=attack_probability > 0,
            attack_probability=attack_probability,
            seed=int(random_seed),
        )

        render_metrics(result)

        upper_left, upper_right = st.columns([1.1, 1.15], gap="large")

        with upper_left:
            st.markdown("<div class='glass-card'><div class='section-title'>Circuit</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-note'>Single-qubit BB84 flow with optional interception.</div>", unsafe_allow_html=True)
            preview_circuit = build_single_bb84_circuit(
                alice_bit=1,
                alice_basis=1,
                bob_basis=0,
                eve_present=attack_probability > 0,
                eve_basis=1,
            )
            st.pyplot(circuit_drawer(preview_circuit, output="mpl"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with upper_right:
            st.markdown("<div class='glass-card'><div class='section-title'>Measurement Histogram</div>", unsafe_allow_html=True)
            counts = AerSimulator().run(preview_circuit, shots=1024).result().get_counts()
            histogram_frame = pd.DataFrame({"state": list(counts.keys()), "count": list(counts.values())})
            hist_fig = px.bar(
                histogram_frame,
                x="state",
                y="count",
                color="state",
                text="count",
                color_discrete_sequence=[ACCENT],
                title="Outcome distribution",
            )
            hist_fig.update_traces(textposition="outside")
            st.plotly_chart(style_plotly(hist_fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        lower_left, lower_right = st.columns([1.2, 1.0], gap="large")

        with lower_left:
            st.markdown("<div class='glass-card'><div class='section-title'>QBER vs Attack Probability</div>", unsafe_allow_html=True)
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
                title="Protocol error trend",
            )
            qber_fig.update_traces(line=dict(width=3, color=ACCENT), marker=dict(size=7, color=ACCENT))
            qber_fig.update_layout(showlegend=False, xaxis_title="Attack probability", yaxis_title="QBER")
            st.plotly_chart(style_plotly(qber_fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with lower_right:
            st.markdown("<div class='glass-card'><div class='section-title'>Bit Transmission Preview</div>", unsafe_allow_html=True)
            preview_n = min(64, n_qubits)
            transmission = pd.DataFrame(
                {
                    "index": np.arange(preview_n),
                    "alice": result.alice_bits[:preview_n],
                    "bob": result.bob_results[:preview_n],
                    "basis_match": [
                        int(a == b)
                        for a, b in zip(result.alice_bases[:preview_n], result.bob_bases[:preview_n])
                    ],
                }
            )
            st.dataframe(transmission, use_container_width=True, height=360)
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
