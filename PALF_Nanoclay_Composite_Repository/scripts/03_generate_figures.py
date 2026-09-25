"""
03_generate_figures.py

Regenerates the manuscript's data figures from the CSV files in data/,
using matplotlib only (no manuscript images are reused). Output PNGs are
written to figures/.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_mechanical"
ILLUS = ROOT / "data" / "illustrative"
SUMMARY = ROOT / "data" / "summary"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

GROUPS = ["0g", "1g", "2g"]
COLORS = {"0g": "#8c8c8c", "1g": "#4C72B0", "2g": "#C44E52"}
plt.rcParams.update({"figure.dpi": 150, "font.size": 10})


def bar_with_replicates(df, value_col, ylabel, title, fname, sig_letters=None):
    fig, ax = plt.subplots(figsize=(4.2, 3.4))
    means = [df.loc[df.nanoclay_loading == g, value_col].mean() for g in GROUPS]
    sds = [df.loc[df.nanoclay_loading == g, value_col].std(ddof=1) for g in GROUPS]
    x = np.arange(len(GROUPS))
    ax.bar(x, means, yerr=sds, capsize=4, color=[COLORS[g] for g in GROUPS],
           edgecolor="black", linewidth=0.6, zorder=2)
    for g, xi in zip(GROUPS, x):
        vals = df.loc[df.nanoclay_loading == g, value_col].values
        jitter = (np.random.default_rng(0).random(len(vals)) - 0.5) * 0.25
        ax.scatter(np.full(len(vals), xi) + jitter, vals, facecolors="none",
                   edgecolors="black", s=18, linewidth=0.6, zorder=3)
    if sig_letters:
        for xi, m, s, letter in zip(x, means, sds, sig_letters):
            ax.text(xi, m + s + 0.03 * max(means), letter, ha="center", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS)
    ax.set_xlabel("Nanoclay loading")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / fname)
    plt.close(fig)


# ---------- Fig. 3 / 4 : tensile ----------
df3 = pd.read_csv(RAW / "table3_tensile_replicates.csv")
bar_with_replicates(df3, "uts_MPa", "Ultimate tensile strength (MPa)",
                     "Fig 3. Ultimate tensile strength vs nanoclay loading",
                     "fig03_tensile_strength.png", sig_letters=["a", "b", "c"])
bar_with_replicates(df3, "modulus_MPa", "Tensile modulus (MPa)",
                     "Fig 4. Tensile modulus vs nanoclay loading",
                     "fig04_tensile_modulus.png", sig_letters=["a", "b", "c"])

# ---------- Fig. 6 / 7 : flexural ----------
df7 = pd.read_csv(RAW / "table7_flexural_replicates.csv")
bar_with_replicates(df7, "flexural_strength_MPa", "Flexural strength (MPa)",
                     "Fig 6. Flexural strength vs nanoclay loading",
                     "fig06_flexural_strength.png", sig_letters=["a", "b", "c"])
bar_with_replicates(df7, "flexural_modulus_GPa", "Flexural modulus (GPa)",
                     "Fig 7. Flexural modulus vs nanoclay loading",
                     "fig07_flexural_modulus.png", sig_letters=["a", "b", "c"])

# ---------- Fig. 8 : percent change vs control ----------
t10 = pd.read_csv(SUMMARY / "table10_percent_change_vs_control.csv")
fig, ax = plt.subplots(figsize=(6, 3.6))
props = ["UTS_change_pct", "Tensile_modulus_change_pct",
         "Flexural_strength_change_pct", "Flexural_modulus_change_pct",
         "Total_elongation_change_pct"]
labels = ["UTS", "Tensile\nmodulus", "Flexural\nstrength", "Flexural\nmodulus", "Elongation"]
x = np.arange(len(props))
width = 0.35
for i, g in enumerate(["1g", "2g"]):
    vals = t10.loc[t10.nanoclay == g, props].values.flatten()
    ax.bar(x + (i - 0.5) * width, vals, width, label=g, color=COLORS[g], edgecolor="black", linewidth=0.6)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("% change vs 0 g control")
ax.set_title("Fig 8. Relative change in mechanical properties vs control")
ax.legend(title="Nanoclay")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "fig08_percent_change.png")
plt.close(fig)

# ---------- Fig. 12 : normalized grouped-bar comparison ----------
t2 = pd.read_csv(SUMMARY / "table2_tensile_group_means.csv").set_index("property")
t6 = pd.read_csv(SUMMARY / "table6_flexural_group_means.csv").set_index("property")
props12 = {
    "UTS": t2.loc["Ultimate_Stress_MPa"],
    "Tensile modulus": t2.loc["Tensile_Modulus_MPa"],
    "Flexural strength": t6.loc["Flexural_Strength_MPa"],
    "Flexural modulus": t6.loc["Flexural_Modulus_N_mm2"],
    "Elongation": t2.loc["Total_Elongation_pct"],
}
fig, ax = plt.subplots(figsize=(6.2, 4))
x = np.arange(len(props12))
width = 0.25
for i, g in enumerate(GROUPS):
    norm_vals = [float(props12[p][g]) / max(float(v) for v in props12[p][GROUPS]) for p in props12]
    bars = ax.bar(x + (i - 1) * width, norm_vals, width, label=g, color=COLORS[g], edgecolor="black", linewidth=0.6)
    ax.bar_label(bars, fmt="%.2f", fontsize=7, padding=1)
ax.set_xticks(x)
ax.set_xticklabels(list(props12.keys()), rotation=15)
ax.set_ylabel("Normalized value (fraction of group max)")
ax.set_ylim(0, 1.25)
ax.set_title("Fig 12. Normalized property comparison across nanoclay loadings")
ax.legend(title="Nanoclay")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "fig12_normalized_comparison.png")
plt.close(fig)

# ---------- Fig. 13 : desirability optimization ----------
t14 = pd.read_csv(SUMMARY / "table14_surrogate_model_coefficients.csv").set_index("response")
x_range = np.linspace(0, 2, 100)


def surrogate(resp, x):
    a, b, c = t14.loc[resp, ["a", "b", "c"]]
    return a * x**2 + b * x + c


responses = ["UTS_MPa", "Tensile_modulus_MPa", "Flexural_strength_MPa", "Damping_acoustic_proxy_0to1"]
resp_labels = ["UTS", "Tensile modulus", "Flexural strength", "Damping/acoustic proxy"]

fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
weights = {
    "Tensile-priority": [0.50, 0.20, 0.10, 0.20],
    "Balanced": [0.25, 0.25, 0.25, 0.25],
    "Acoustic-priority": [0.10, 0.20, 0.30, 0.40],
}
for name, w in weights.items():
    d_curves = []
    for resp, wi in zip(responses, w):
        y = surrogate(resp, x_range)
        d = (y - y.min()) / (y.max() - y.min())
        d_curves.append(d ** wi)
    D = np.prod(d_curves, axis=0) ** (1 / sum(w))
    axes[0].plot(x_range, D, label=name, linewidth=2)
    axes[0].scatter([x_range[np.argmax(D)]], [D.max()], zorder=5)
axes[0].set_xlabel("Nanoclay loading (g)")
axes[0].set_ylabel("Composite desirability D(x)")
axes[0].set_title("(a) Desirability by application scenario")
axes[0].legend(fontsize=7)
axes[0].spines[["top", "right"]].set_visible(False)

for resp, label in zip(responses, resp_labels):
    y = surrogate(resp, x_range)
    d = (y - y.min()) / (y.max() - y.min())
    axes[1].plot(x_range, d, label=label, linewidth=2)
    y0 = surrogate(resp, np.array([0, 1, 2]))
    d0 = (y0 - y.min()) / (y.max() - y.min())
    axes[1].scatter([0, 1, 2], d0, s=15, zorder=5)
axes[1].set_xlabel("Nanoclay loading (g)")
axes[1].set_ylabel("Normalized desirability, d(x)")
axes[1].set_title("(b) Individual normalized surrogate curves")
axes[1].legend(fontsize=7)
axes[1].spines[["top", "right"]].set_visible(False)
fig.suptitle("Fig 13. AI-assisted multi-objective optimization of nanoclay loading")
fig.tight_layout()
fig.savefig(FIG / "fig13_desirability_optimization.png")
plt.close(fig)

# ---------- Fig. 16 : modal 2nd mode (illustrative) ----------
df22 = pd.read_csv(ILLUS / "table22_modal_2nd_mode_replicates_ILLUSTRATIVE.csv")
fig, axes = plt.subplots(1, 2, figsize=(8, 3.4))
for ax, col, ylabel, letters in [
    (axes[0], "second_freq_Hz", "Second natural frequency (Hz)", ["a", "b", "c"]),
    (axes[1], "damping_ratio_pct", "Damping ratio (%)", ["a", "b", "c"]),
]:
    means = [df22.loc[df22.nanoclay_loading == g, col].mean() for g in GROUPS]
    sds = [df22.loc[df22.nanoclay_loading == g, col].std(ddof=1) for g in GROUPS]
    x = np.arange(len(GROUPS))
    ax.bar(x, means, yerr=sds, capsize=4, color=[COLORS[g] for g in GROUPS], edgecolor="black", linewidth=0.6)
    for g, xi in zip(GROUPS, x):
        vals = df22.loc[df22.nanoclay_loading == g, col].values
        jitter = (np.random.default_rng(1).random(len(vals)) - 0.5) * 0.25
        ax.scatter(np.full(len(vals), xi) + jitter, vals, facecolors="none", edgecolors="black", s=16, linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Fig 16. Second natural frequency & damping ratio (ILLUSTRATIVE — not measured data)")
fig.tight_layout()
fig.savefig(FIG / "fig16_modal_2ndmode_ILLUSTRATIVE.png")
plt.close(fig)

# ---------- Fig. 17 : STL vs frequency (illustrative) ----------
stl = pd.read_csv(ILLUS / "table24_STL_vs_frequency_replicates_ILLUSTRATIVE.csv")
fig, ax = plt.subplots(figsize=(5.2, 3.6))
for g in GROUPS:
    sub = stl[stl.nanoclay_loading == g]
    agg = sub.groupby("frequency_Hz")["STL_dB"].agg(["mean", "std"]).reset_index()
    ax.errorbar(agg.frequency_Hz, agg["mean"], yerr=agg["std"], marker="o", capsize=3,
                label=g, color=COLORS[g])
ax.set_xscale("log")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Sound transmission loss (dB)")
ax.set_title("Fig 17. STL vs frequency\n(ILLUSTRATIVE — not measured data)", fontsize=9)
ax.legend(title="Nanoclay")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG / "fig17_STL_vs_frequency_ILLUSTRATIVE.png")
plt.close(fig)

# ---------- Fig. 18 : flammability (illustrative) ----------
df26 = pd.read_csv(ILLUS / "table26_flammability_replicates_ILLUSTRATIVE.csv")
fig, axes = plt.subplots(1, 2, figsize=(8, 3.4))
for ax, col, ylabel in [(axes[0], "burn_time_s", "Burn time (s)"),
                         (axes[1], "burning_rate_mm_per_min", "Linear burning rate (mm/min)")]:
    means = [df26.loc[df26.nanoclay_loading == g, col].mean() for g in GROUPS]
    sds = [df26.loc[df26.nanoclay_loading == g, col].std(ddof=1) for g in GROUPS]
    x = np.arange(len(GROUPS))
    ax.bar(x, means, yerr=sds, capsize=4, color=[COLORS[g] for g in GROUPS], edgecolor="black", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Fig 18. Flammability screening, ASTM D635 configuration (ILLUSTRATIVE)")
fig.tight_layout()
fig.savefig(FIG / "fig18_flammability_ILLUSTRATIVE.png")
plt.close(fig)

# ---------- Fig. 19 : screening properties (illustrative) ----------
df28 = pd.read_csv(ILLUS / "table28_screening_properties_replicates_ILLUSTRATIVE.csv")
fig, axes = plt.subplots(1, 5, figsize=(14, 3))
panels = [("water_abs_168h_pct", "168h water\nabsorption (%)"),
          ("impact_strength_kJ_m2", "Impact strength\n(kJ/m²)"),
          ("density_g_cm3", "Density (g/cm³)"),
          ("hardness_shoreD", "Hardness"),
          ("oxygen_index_pct", "Oxygen index (%)")]
for ax, (col, ylabel) in zip(axes, panels):
    means = [df28.loc[df28.nanoclay_loading == g, col].mean() for g in GROUPS]
    sds = [df28.loc[df28.nanoclay_loading == g, col].std(ddof=1) for g in GROUPS]
    x = np.arange(len(GROUPS))
    ax.bar(x, means, yerr=sds, capsize=4, color=[COLORS[g] for g in GROUPS], edgecolor="black", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Fig 19. Screening properties by nanoclay loading (ILLUSTRATIVE — not measured data)")
fig.tight_layout()
fig.savefig(FIG / "fig19_screening_properties_ILLUSTRATIVE.png")
plt.close(fig)

print("Figures written to", FIG)
for f in sorted(FIG.glob("*.png")):
    print(" -", f.name)
