"""Interactive A/B test dashboard.

Reports whether the new landing page changed conversion, and provides an
experiment-design calculator (required sample size and power) for the next test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.predict import Predictor  # noqa: E402

D = config.DRACULA
st.set_page_config(page_title="A/B Test", layout="wide")
st.markdown(
    f"""<style>
    .stApp {{ background-color: {D['background']}; color: {D['foreground']}; }}
    section[data-testid="stSidebar"] {{ background-color: {D['current_line']}; }}
    h1, h2, h3 {{ color: {D['purple']}; }}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_predictor() -> Predictor:
    return Predictor()


def style_axes(ax):
    ax.set_facecolor(D["background"])
    for s in ax.spines.values():
        s.set_color(D["current_line"])
    ax.tick_params(colors=D["foreground"])
    ax.yaxis.label.set_color(D["foreground"])
    ax.grid(True, axis="y", color=D["current_line"], linestyle="--", alpha=0.4)


def conversion_chart(groups):
    names = [config.CONTROL, config.TREATMENT]
    rates = [groups[n]["rate"] * 100 for n in names]
    err = [1.96 * np.sqrt(groups[n]["rate"] * (1 - groups[n]["rate"]) / groups[n]["n"]) * 100 for n in names]
    fig, ax = plt.subplots(figsize=(5, 3.2), facecolor=D["background"])
    ax.bar(names, rates, yerr=err, capsize=6, color=[D["cyan"], D["pink"]], edgecolor=D["current_line"])
    for i, r in enumerate(rates):
        ax.text(i, r, f"  {r:.2f}%", ha="center", va="bottom", color=D["foreground"], fontsize=10)
    ax.set_ylabel("Conversion rate (%)")
    ax.set_ylim(0, max(rates) * 1.3)
    style_axes(ax)
    fig.tight_layout()
    return fig


def power_chart(predictor, baseline, mde, alpha):
    ns = np.linspace(1000, max(40000, predictor.sample_size(baseline, mde, alpha) * 1.5), 60)
    powers = [predictor.power(baseline, mde, int(n), alpha) for n in ns]
    fig, ax = plt.subplots(figsize=(5, 3.2), facecolor=D["background"])
    ax.plot(ns, powers, color=D["green"], linewidth=2)
    ax.axhline(0.8, color=D["comment"], linestyle="--", linewidth=1.2)
    ax.set_xlabel("Sample size per group")
    ax.set_ylabel("Power")
    ax.xaxis.label.set_color(D["foreground"])
    style_axes(ax)
    ax.grid(True, color=D["current_line"], linestyle="--", alpha=0.4)
    fig.tight_layout()
    return fig


def main():
    try:
        predictor = load_predictor()
    except FileNotFoundError:
        st.error("Analysis artifact not found. Run the pipeline before launching the app.")
        return

    groups, test = predictor.groups(), predictor.test()

    st.title("AB Testing Ecommerce — Landing Page Experiment")
    st.markdown(
        "Does the new landing page change conversion? The result below is the verdict on the "
        "experiment; the sidebar sizes the next test."
    )

    st.subheader("Experiment result")
    c = st.columns(4)
    c[0].metric("Control conversion", f"{groups[config.CONTROL]['rate']*100:.2f}%")
    c[1].metric("Treatment conversion", f"{groups[config.TREATMENT]['rate']*100:.2f}%",
                f"{test['abs_difference']*100:+.2f} pp")
    c[2].metric("p-value", f"{test['p_value']:.3f}")
    c[3].metric("Significant", "Yes" if test["significant"] else "No")
    verdict_color = D["green"] if test["significant"] else D["yellow"]
    st.markdown(f"<span style='color:{verdict_color}'>{test['decision']}</span>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.pyplot(conversion_chart(groups))
    with right:
        ci = test["ci95_difference"]
        st.markdown("**95% confidence interval for the difference**")
        st.markdown(f"[{ci[0]*100:+.2f} pp, {ci[1]*100:+.2f} pp]")
        st.caption(
            f"The interval includes zero, consistent with no real effect. Observed power for the "
            f"measured difference was {test['observed_power']*100:.0f}%.")

    st.subheader("Design the next experiment")
    with st.sidebar:
        st.header("Sample-size calculator")
        baseline = st.slider("Baseline conversion", 0.01, 0.5, float(test_safe(groups)), 0.005)
        mde = st.slider("Minimum detectable effect (absolute)", 0.002, 0.05, 0.01, 0.001)
        alpha = st.select_slider("Significance (alpha)", [0.01, 0.05, 0.10], value=0.05)
        power = st.select_slider("Target power", [0.7, 0.8, 0.9], value=0.8)

    n = predictor.sample_size(baseline, mde, alpha, power)
    cc = st.columns([1, 2])
    with cc[0]:
        st.metric("Required sample / group", f"{n:,}")
        st.metric("Total sample", f"{2*n:,}")
        st.caption(f"To detect a {mde*100:.1f} pp change from a {baseline*100:.1f}% baseline "
                   f"at alpha={alpha}, power={power}.")
    with cc[1]:
        st.pyplot(power_chart(predictor, baseline, mde, alpha))


def test_safe(groups) -> float:
    return round(groups[config.CONTROL]["rate"], 3)


if __name__ == "__main__":
    main()
