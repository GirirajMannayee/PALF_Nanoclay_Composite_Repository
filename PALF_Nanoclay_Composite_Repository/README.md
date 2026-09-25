# PALF–Epoxy–Nanoclay Composite: Data & Analysis Repository

This repository packages the data, analysis code, and figures that
accompany the manuscript:

> **Effect of Nanoclay Loading on the Mechanical, Free-Vibration, and Sound
> Transmission Loss Behavior of Pineapple Leaf Fiber–Epoxy Composites**
> (`manuscript/19_Nanoclay_PALF_Composite.docx`)

The study characterizes PALF-epoxy composites at three nanoclay loadings
(0 g, 1 g, 2 g control/filler content) across tensile testing (ASTM
D3039), flexural testing (ASTM D790), free-vibration (modal) analysis,
sound transmission loss (ASTM E2611-17), and SEM fracture-surface
imaging, plus an AI-assisted multi-objective optimization of nanoclay
loading.


This is the single most important thing in this repository. The source
manuscript is explicit that:

1. **Tables 2–10 (Section 4)** report **real, measured mechanical
   results** (tensile and flexural properties)
  
2. **Section 7 (Tables 16–29)** — SEM quantitative dispersion, XRD,
   FTIR, DMA, quantitative modal parameters, impedance-tube STL,
   flammability, water absorption, impact, density, hardness, and
   oxygen index — is explicitly labeled by the manuscript's own authors
   as 


## Repository structure

```
.
├── README.md                  <- this file
├── requirements.txt            <- Python dependencies
├── LICENSE                     <- code license (MIT)
├── DATA_LICENSE.txt            <- data license (CC BY 4.0)
├── CITATION.cff                <- citation metadata
├── manuscript/
│   └── 19_Nanoclay_PALF_Composite.docx   <- source manuscript, as supplied
├── data/
│   ├── raw_mechanical/         <- reconstructed replicate data, REAL reported means (Tables 3, 7)
│   ├── illustrative/           <- reconstructed replicate data, PLACEHOLDER values (Tables 22, 24, 26, 28)
│   └── summary/                <- group-level tables transcribed as-is (Tables 2, 6, 10, 14–21)
├── scripts/
│   ├── 01_generate_datasets.py <- builds every CSV in data/ from manuscript-reported statistics
│   ├── 02_run_statistics.py    <- one-way ANOVA + Tukey HSD, reproduces Tables 4/5/8/9/23/25/27/29
│   └── 03_generate_figures.py  <- regenerates Figs. 3,4,6,7,8,12,13,16,17,18,19 as PNGs
├── results/                    <- ANOVA / Tukey HSD output tables (CSV), from script 02
└── figures/                    <- regenerated figures (PNG), from script 03
```

## Reproducing everything

```bash
pip install -r requirements.txt
python scripts/01_generate_datasets.py   # writes data/
python scripts/02_run_statistics.py      # writes results/
python scripts/03_generate_figures.py    # writes figures/
```

Because `01_generate_datasets.py` uses a fixed random seed, running the
pipeline is fully reproducible: the same CSVs, statistics, and figures
are produced every time.

### How closely do the recomputed statistics match the manuscript?

Very closely, because the synthesis method forces the synthesized
replicates to reproduce the manuscript's own reported mean/SD/n exactly.
For example, the recomputed tensile ANOVA gives **F = 80.04, p =
4.48 × 10⁻¹²** for ultimate tensile strength against the manuscript's
reported **F = 80.04, p = 4.479 × 10⁻¹²** (Table 4) — matching because
both numbers derive from the same three group means/SDs/n. This
agreement demonstrates that the reconstruction is internally consistent
with the manuscript, not that it recovers the authors' individual
specimen measurements.

## Key reported findings (Section 4, real data)

All four mechanical properties increased **monotonically** with
nanoclay loading from 0 → 2 g, while ductility fell:

| Property | 0 g | 1 g | 2 g | Δ (0→2 g) |
|---|---|---|---|---|
| Ultimate tensile strength (MPa) | 82.4 | 96.8 | 108.7 | +31.9% |
| Tensile modulus (MPa) | 5210 | 6140 | 6830 | +31.1% |
| Flexural strength (MPa) | 132.5 | 151.7 | 168.3 | +27.0% |
| Flexural modulus (N/mm²) | 7420 | 8460 | 9210 | +24.1% |
| Total elongation (%) | 2.31 | 2.08 | 1.94 | −16.0% |

All one-way ANOVAs are significant (p < 0.001); Tukey HSD confirms every
pairwise group difference is significant at α = 0.05 (see
`results/tensile_TukeyHSD.csv` and `results/flexural_TukeyHSD.csv`).

Because every measured property was still improving at the highest
tested loading (2 g), the manuscript concludes the true property optimum
may lie **beyond** the tested range (Sections 4.8, 5.2, 9) and
recommends testing additional loadings (e.g., 2.5 g, 3 g) as future
work.



## Licensing

- Code (`scripts/`): MIT License — see `LICENSE`.
- Data (`data/`, `results/`, `figures/`): CC BY 4.0 — see `DATA_LICENSE.txt`.
- The manuscript file itself is included only as reference material
  supplied by the user; its rights remain with its authors.

## Citation

See `CITATION.cff`. Please cite the manuscript itself for the reported
Section 4 mechanical findings, and this repository for the reproducible
data/analysis pipeline.
