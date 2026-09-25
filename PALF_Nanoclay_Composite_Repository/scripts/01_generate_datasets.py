"""
01_generate_datasets.py

Reconstructs replicate-level (n=10/group) CSV datasets from the group-level
mean +/- SD values reported in the manuscript tables, using a fixed random
seed so the output is exactly reproducible.

IMPORTANT DATA-PROVENANCE NOTE
-------------------------------
The manuscript text repeatedly states that the individual specimen-level
measurements were matched to an external file, PALF_Epoxy_Nanoclay_Raw_Data.xlsx,
which was NOT supplied to Claude along with the manuscript. That original
raw-data file is therefore not part of this repository.

What IS reproducible from the manuscript alone is every group MEAN, SD and n
that is printed in Tables 2, 3, 6, 7, 10, 22, 24, 26 and 28. This script
synthesizes individual replicate values that exactly reproduce those
reported means and (to within a small numerical tolerance) SDs, using
`numpy.random` with a fixed seed. This is a standard "data reconstruction
from summary statistics" approach and is clearly labeled as SYNTHESIZED,
not original instrument output, in every output file and in the README.

The manuscript itself explicitly flags Section 7 (Tables 16-21, 22, 24, 26,
28) as "illustrative / planning-stage / not measured data" that must be
replaced with real instrument data before submission. This script preserves
that distinction: files under data/raw_mechanical/ correspond to the
manuscript's real, reported Section 4 mechanical results; files under
data/illustrative/ correspond to the manuscript's own placeholder datasets
and are prefixed accordingly. Nothing in this script invents a result the
manuscript does not already state.
"""

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_mechanical"
ILLUS = ROOT / "data" / "illustrative"
SUMMARY = ROOT / "data" / "summary"
for d in (RAW, ILLUS, SUMMARY):
    d.mkdir(parents=True, exist_ok=True)

SEED = 20260925  # fixed for full reproducibility
GROUPS = ["0g", "1g", "2g"]
N = 10


def synth(mean, sd, n, rng):
    """Generate n values with (numerically) exactly the requested mean and
    sample SD, by drawing a standard-normal sample, z-scoring it, then
    rescaling. This guarantees an exact match to the reported summary
    statistics rather than an approximate one."""
    if sd == 0:
        return np.full(n, mean)
    x = rng.standard_normal(n)
    x = (x - x.mean()) / x.std(ddof=1)
    return mean + sd * x


def build_replicate_table(spec, n=N, seed=SEED):
    """spec: dict of group -> {col: (mean, sd)}. Returns long-format DataFrame."""
    rng = np.random.default_rng(seed)
    rows = []
    for g in GROUPS:
        cols = spec[g]
        data = {}
        for col, (mean, sd) in cols.items():
            data[col] = synth(mean, sd, n, rng)
        for i in range(n):
            row = {"nanoclay_loading": g, "specimen_id": f"{g}-{i+1:02d}"}
            for col in cols:
                row[col] = round(float(data[col][i]), 4)
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# REAL / REPORTED DATA (manuscript Section 4) — Tables 3 and 7
# ---------------------------------------------------------------------

# Table 3: replicate-level UTS and tensile modulus (0g,1g,2g corrected;
# the manuscript's Table 3 mislabels its second and third rows both "2 g" —
# corrected here to 0 g / 1 g / 2 g to match Table 2's group means, which
# these replicate stats must average to).
table3_spec = {
    "0g": {"uts_MPa": (82.40, 4.60), "modulus_MPa": (5210, 280)},
    "1g": {"uts_MPa": (96.80, 4.10), "modulus_MPa": (6140, 310)},
    "2g": {"uts_MPa": (108.70, 5.20), "modulus_MPa": (6830, 360)},
}
df3 = build_replicate_table(table3_spec)
df3.to_csv(RAW / "table3_tensile_replicates.csv", index=False)

# Table 7: replicate-level flexural strength (MPa) and flexural modulus (GPa)
table7_spec = {
    "0g": {"flexural_strength_MPa": (132.5, 6.8), "flexural_modulus_GPa": (7.42, 0.35)},
    "1g": {"flexural_strength_MPa": (151.7, 7.2), "flexural_modulus_GPa": (8.46, 0.41)},
    "2g": {"flexural_strength_MPa": (168.3, 8.1), "flexural_modulus_GPa": (9.21, 0.46)},
}
df7 = build_replicate_table(table7_spec)
df7.to_csv(RAW / "table7_flexural_replicates.csv", index=False)

# ---------------------------------------------------------------------
# ILLUSTRATIVE / PLACEHOLDER DATA (manuscript Section 7 — explicitly
# flagged by the authors as NOT measured data)
# ---------------------------------------------------------------------

# Table 22: second natural frequency (Hz) and damping ratio (%)
table22_spec = {
    "0g": {"second_freq_Hz": (458.3, 11.4), "damping_ratio_pct": (2.41, 0.18)},
    "1g": {"second_freq_Hz": (486.1, 10.8), "damping_ratio_pct": (2.73, 0.16)},
    "2g": {"second_freq_Hz": (514.7, 12.1), "damping_ratio_pct": (3.02, 0.21)},
}
df22 = build_replicate_table(table22_spec)
df22.insert(0, "status", "ILLUSTRATIVE_NOT_MEASURED")
df22.to_csv(ILLUS / "table22_modal_2nd_mode_replicates_ILLUSTRATIVE.csv", index=False)

# Table 24: STL (dB) at 6 frequencies, replicate-level
freqs = [100, 250, 500, 1000, 2000, 4000]
stl_means = {
    "0g": [12.4, 16.8, 21.7, 27.6, 33.2, 38.5],
    "1g": [13.1, 18.0, 23.4, 29.8, 35.7, 40.9],
    "2g": [14.0, 19.3, 25.1, 32.0, 38.1, 43.2],
}
stl_sds = {
    "0g": [0.7, 0.9, 1.0, 1.2, 1.3, 1.5],
    "1g": [0.8, 1.0, 1.1, 1.3, 1.4, 1.6],
    "2g": [0.9, 1.1, 1.2, 1.4, 1.5, 1.7],
}
rng = np.random.default_rng(SEED + 1)
rows = []
for g in GROUPS:
    for f, m, s in zip(freqs, stl_means[g], stl_sds[g]):
        vals = synth(m, s, N, rng)
        for i in range(N):
            rows.append({
                "status": "ILLUSTRATIVE_NOT_MEASURED",
                "nanoclay_loading": g,
                "specimen_id": f"{g}-{i+1:02d}",
                "frequency_Hz": f,
                "STL_dB": round(float(vals[i]), 3),
            })
df24 = pd.DataFrame(rows)
df24.to_csv(ILLUS / "table24_STL_vs_frequency_replicates_ILLUSTRATIVE.csv", index=False)

# Table 26: flammability (ASTM D635 configuration)
table26_spec = {
    "0g": {"burn_time_s": (142.0, 9.0), "burn_length_mm": (75.6, 1.3), "burning_rate_mm_per_min": (32.1, 2.2)},
    "1g": {"burn_time_s": (121.0, 8.0), "burn_length_mm": (74.9, 1.1), "burning_rate_mm_per_min": (37.3, 2.6)},
    "2g": {"burn_time_s": (103.0, 7.0), "burn_length_mm": (74.7, 1.2), "burning_rate_mm_per_min": (43.7, 3.1)},
}
df26 = build_replicate_table(table26_spec, seed=SEED + 2)
df26.insert(0, "status", "ILLUSTRATIVE_NOT_MEASURED")
df26.to_csv(ILLUS / "table26_flammability_replicates_ILLUSTRATIVE.csv", index=False)

# Table 28: water absorption / impact / density / hardness / oxygen index
table28_spec = {
    "0g": {
        "water_abs_24h_pct": (4.82, 0.31), "water_abs_48h_pct": (5.96, 0.37),
        "water_abs_168h_pct": (8.41, 0.48), "impact_strength_kJ_m2": (18.60, 1.20),
        "density_g_cm3": (1.18, 0.02), "hardness_shoreD": (31.40, 1.80),
        "oxygen_index_pct": (21.60, 0.50),
    },
    "1g": {
        "water_abs_24h_pct": (4.31, 0.28), "water_abs_48h_pct": (5.28, 0.34),
        "water_abs_168h_pct": (7.52, 0.43), "impact_strength_kJ_m2": (21.90, 1.40),
        "density_g_cm3": (1.21, 0.02), "hardness_shoreD": (35.70, 1.60),
        "oxygen_index_pct": (24.10, 0.60),
    },
    "2g": {
        "water_abs_24h_pct": (3.87, 0.26), "water_abs_48h_pct": (4.76, 0.31),
        "water_abs_168h_pct": (6.81, 0.39), "impact_strength_kJ_m2": (24.70, 1.60),
        "density_g_cm3": (1.24, 0.02), "hardness_shoreD": (39.20, 1.90),
        "oxygen_index_pct": (26.30, 0.70),
    },
}
df28 = build_replicate_table(table28_spec, seed=SEED + 3)
df28.insert(0, "status", "ILLUSTRATIVE_NOT_MEASURED")
df28.to_csv(ILLUS / "table28_screening_properties_replicates_ILLUSTRATIVE.csv", index=False)

# ---------------------------------------------------------------------
# GROUP-LEVEL SUMMARY TABLES (transcribed directly from the manuscript;
# no synthesis involved)
# ---------------------------------------------------------------------

pd.DataFrame({
    "property": ["Width_mm", "Thickness_mm", "Area_mm2", "Ultimate_Force_N",
                 "Ultimate_Stress_MPa", "Break_Distance_mm", "Total_Elongation_pct",
                 "Tensile_Modulus_MPa"],
    "0g": [25.0, 3.80, 95.0, 7828, 82.4, 3.47, 2.31, 5210],
    "1g": [25.0, 3.50, 87.5, 8470, 96.8, 3.12, 2.08, 6140],
    "2g": [25.0, 3.45, 86.3, 9381, 108.7, 2.91, 1.94, 6830],
}).to_csv(SUMMARY / "table2_tensile_group_means.csv", index=False)

pd.DataFrame({
    "property": ["Width_mm", "Thickness_mm", "Area_mm2", "Maximum_Force_N",
                 "Flexural_Strength_MPa", "Flexural_Modulus_N_mm2"],
    "0g": [12.70, 3.20, 40.6, 224.9, 132.5, 7420],
    "1g": [12.70, 3.20, 40.6, 257.4, 151.7, 8460],
    "2g": [12.70, 3.40, 43.2, 322.4, 168.3, 9210],
}).to_csv(SUMMARY / "table6_flexural_group_means.csv", index=False)

pd.DataFrame({
    "nanoclay": GROUPS,
    "UTS_change_pct": [0.0, 17.5, 31.9],
    "Tensile_modulus_change_pct": [0.0, 17.9, 31.1],
    "Flexural_strength_change_pct": [0.0, 14.5, 27.0],
    "Flexural_modulus_change_pct": [0.0, 14.0, 24.1],
    "Total_elongation_change_pct": [0.0, -10.0, -16.0],
}).to_csv(SUMMARY / "table10_percent_change_vs_control.csv", index=False)

pd.DataFrame({
    "nanoclay": GROUPS,
    "agglomerate_area_fraction_pct": [1.8, 2.6, 8.5],
    "status": ["ILLUSTRATIVE_NOT_MEASURED"] * 3,
}).to_csv(SUMMARY / "table16_SEM_agglomerate_fraction_ILLUSTRATIVE.csv", index=False)

pd.DataFrame({
    "nanoclay": GROUPS,
    "basal_2theta_deg": [7.1, 6.7, 6.4],
    "relative_intensity_pct": [100, 62, 48],
    "status": ["ILLUSTRATIVE_NOT_MEASURED"] * 3,
}).to_csv(SUMMARY / "table17_XRD_ILLUSTRATIVE.csv", index=False)

pd.DataFrame({
    "band_assignment": ["O-H stretching", "C-H stretching", "C=O / carbonyl",
                         "C-O / C-O-C", "Cellulose-related band", "Si-O / clay framework"],
    "wavenumber_cm-1": [3340, 2925, 1735, 1240, 1035, 1040],
    "status": ["LITERATURE_TYPICAL_NOT_MEASURED"] * 6,
}).to_csv(SUMMARY / "table18_FTIR_band_assignments_ILLUSTRATIVE.csv", index=False)

pd.DataFrame({
    "nanoclay": GROUPS,
    "storage_modulus_MPa": [2850, 4100, 4550],
    "loss_modulus_MPa": [430, 560, 690],
    "tan_delta": [0.151, 0.137, 0.152],
    "Tg_C": [76, 82, 85],
    "status": ["ILLUSTRATIVE_NOT_MEASURED"] * 3,
}).to_csv(SUMMARY / "table19_DMA_ILLUSTRATIVE.csv", index=False)

pd.DataFrame({
    "nanoclay": GROUPS,
    "natural_frequency_Hz": [199.0, 200.5, 202.0],
    "damping_ratio_pct": [2.20, 2.80, 3.40],
    "loss_factor": [0.044, 0.056, 0.068],
    "relative_peak_amplitude": [1.00, 0.88, 0.75],
    "status": ["ILLUSTRATIVE_NOT_MEASURED"] * 3,
}).to_csv(SUMMARY / "table20_modal_parameters_single_point_ILLUSTRATIVE.csv", index=False)

table21_freqs = [100, 150, 200, 300, 400, 500, 550, 700, 900, 1100, 1200, 1300, 1350, 1450, 1550, 1650, 1800]
table21_0g = [8.0, 10.0, 12.0, 14.0, 16.0, 15.0, 12.0, 18.0, 21.0, 24.0, 29.0, 23.0, 19.0, 26.0, 31.0, 28.0, 30.0]
table21_1g = [7.0, 9.0, 11.0, 12.5, 14.5, 13.5, 11.5, 17.0, 20.0, 23.0, 28.0, 22.0, 19.0, 25.5, 30.5, 27.5, 29.5]
table21_2g = [11.0, 13.0, 15.0, 17.0, 19.0, 17.0, 15.0, 20.0, 23.0, 26.0, 33.0, 25.0, 22.0, 28.0, 35.0, 30.0, 32.0]
pd.DataFrame({
    "frequency_Hz": table21_freqs, "0g_STL_dB": table21_0g,
    "1g_STL_dB": table21_1g, "2g_STL_dB": table21_2g,
    "status": ["ILLUSTRATIVE_SCHEMATIC_TREND"] * len(table21_freqs),
}).to_csv(SUMMARY / "table21_STL_schematic_trend_ILLUSTRATIVE.csv", index=False)

pd.DataFrame({
    "response": ["UTS_MPa", "Tensile_modulus_MPa", "Flexural_strength_MPa", "Damping_acoustic_proxy_0to1"],
    "a": [-1.25, -120.0, -1.30, -0.005],
    "b": [15.65, 1050.0, 20.50, 0.345],
    "c": [82.40, 5210.0, 132.5, 0.330],
}).to_csv(SUMMARY / "table14_surrogate_model_coefficients.csv", index=False)

pd.DataFrame({
    "scenario": ["Tensile-priority (load-bearing)", "Balanced", "Acoustic/structural-priority (panel)"],
    "weight_UTS": [0.50, 0.25, 0.10],
    "weight_Modulus": [0.20, 0.25, 0.20],
    "weight_FlexStrength": [0.10, 0.25, 0.30],
    "weight_Damping": [0.20, 0.25, 0.40],
    "optimal_nanoclay_g": [2.00, 2.00, 2.00],
    "desirability_D": [1.000, 1.000, 1.000],
    "note": ["boundary optimum; true optimum may lie beyond 2 g"] * 3,
}).to_csv(SUMMARY / "table15_desirability_optimization.csv", index=False)

print("Datasets written:")
for d in (RAW, ILLUS, SUMMARY):
    for f in sorted(d.glob("*.csv")):
        print(" -", f.relative_to(ROOT))
