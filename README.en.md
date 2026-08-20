[繁體中文](README.md) | **English**

---

# SECOM Yield Analytics — End-to-End Portfolio

> A **4-layer semiconductor yield analysis framework** built on UCI SECOM
> (1,567 wafer lots × 590 sensors, 2008-07 ~ 2008-10).
> This repo is the **landing page** — it hosts the reliability layer (this repo)
> and links to the dashboard and prediction layers (sister repos).

---

## The 4-Layer Framework

A single yield incident (**2008-07 excursion: yield dropped 93.4% → 85.96%**) analyzed
through four progressively deeper lenses, in the order a real fab reliability engineer
would use them:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Layer 1         │───▶│  Layer 2         │───▶│  Layer 3         │───▶│  Layer 4         │
│  DASHBOARD       │    │  WEIBULL         │    │  Cpk             │    │  FMEA + 8D       │
│                  │    │                  │    │                  │    │                  │
│  WHERE is the    │    │  HOW does it     │    │  WHAT is         │    │  WHY & how to    │
│  problem?        │    │  fail?           │    │  driving it?     │    │  FIX?            │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
        │                        │                        │                        │
        ▼                        ▼                        ▼                        ▼
  Monthly yield          β = 2.70                 5 critical sensors      RPN-prioritized
  trend chart            Wear-out failure         Cpk 0.18 ~ 0.61         corrective actions
  surfaces 2008-07       (not random)             ALL Not Capable         + 5-Why + Fishbone
  excursion
```

Each layer stands alone — but the **compound narrative** (statistical evidence chains
across four independent analyses converging on the same root cause) is what shows
end-to-end engineering thinking.

---

## Layer-by-Layer

### Layer 1 · Dashboard — Yield Trend & Sensor Health

**Repo**: [semicon-yield-dashboard](https://github.com/tzuhua0308/semicon-yield-dashboard)

PostgreSQL 16 + Streamlit + Plotly. 3-tab dashboard on 92 万 sensor readings:
monthly yield trend, sensor health (NULL analysis), lot-level drill-down.

**Key finding**: 2008-07 yield dropped to **85.96%** (baseline 93.4%) — the anchor
event this whole portfolio investigates.

**Tech**: PostgreSQL, psycopg2, pandas ETL, Streamlit, Plotly, Tableau Public

---

### Layer 2 · Prediction — Imbalanced Classification

**Repo**: [semicon-yield-prediction](https://github.com/tzuhua0308/semicon-yield-prediction)

XGBoost baseline → improved classifier on 93.4% imbalanced data.
Demonstrates the "majority class trap" (baseline F1 = 0.00) and the tuning path
to a working model (**5-fold OOF F1 = 0.26**).

**Techniques**: VarianceThreshold, Mutual Information Top-50 selection,
scale_pos_weight, OOF threshold tuning (0.5 → 0.12)

**Tech**: XGBoost, scikit-learn, cross-validation

---

### Layer 3 · Reliability — Weibull + Cpk (this repo)

Full reliability engineering treatment of the 2008-07 failures.

#### Weibull Distribution Fitting

```
β (shape)  =  2.702   → Wear-out failure mode (not random)
η (scale)  = 5175.8 hr → Characteristic life
B10 life   = 2250.2 hr → 10% failure time
MTTF       = 4602.8 hr → Mean time to failure
```

![Weibull Analysis](outputs/weibull_analysis.png)

The Weibull probability plot (right panel) shows failures fall on a straight line
— supporting the Weibull assumption. β = 2.70 mathematically confirms the failures
are **accumulating over time**, not random events.

#### Cpk Process Capability

Top-5 discriminating sensors selected via **Cohen's d** between Pass and Fail groups,
then evaluated against implicit spec limits (Pass samples' P1/P99):

| Sensor | Cpk  | Judgment       |
|--------|------|----------------|
| S_431  | 0.18 | Not Capable    |
| S_510  | 0.33 | Not Capable    |
| S_348  | 0.37 | Not Capable    |
| S_59   | 0.51 | Not Capable    |
| S_103  | 0.61 | Not Capable    |

![Cpk Analysis](outputs/cpk_analysis.png)

**Interpretation**: All 5 critical sensors fall below the industry threshold of
Cpk ≥ 1.33 — quantifying **which process parameters** need improvement.

---

### Layer 4 · FMEA + 8D — Structured RCA

Full report: **[`docs/FMEA_and_8D_Report.md`](docs/FMEA_and_8D_Report.md)**

- **FMEA worksheet** scored per AIAG 4th Ed. (S × O × D = RPN)
- **8D Report** (D1 Team → D8 Recognition)
- **5-Why analysis** on the highest-RPN failure mode
- **Fishbone (Ishikawa) diagram** in ASCII
- **Corrective actions** with owner / deadline / success metric
- **Verification plan** (Cpk targets, Weibull β convergence, monthly yield ≥ 93.4%)

---

## Project Structure

```
secom-yield-analytics/  (this repo — reliability code + landing page)
├── README.md                    ← you are here
├── weibull_analysis.py          ← Layer 3a
├── cpk_analysis.py              ← Layer 3b
├── docs/
│   └── FMEA_and_8D_Report.md    ← Layer 4
└── outputs/
    ├── weibull_analysis.png
    └── cpk_analysis.png

Sister repos:
├── semicon-yield-dashboard      ← Layer 1
└── semicon-yield-prediction     ← Layer 2
```

---

## How to Run (Reliability Layer)

Requires the SECOM dataset from the sister Dashboard project (`../dashboard/data/uci-secom.csv`).

```bash
# Activate shared venv
source ../dashboard/.venv/bin/activate

# Weibull analysis
python weibull_analysis.py

# Cpk analysis
python cpk_analysis.py
```

---

## Design Decisions Worth Explaining

| Decision | Rationale |
|----------|-----------|
| **2-parameter Weibull (`floc=0`)** | Industry standard; 3-parameter version overfits on small failure samples (n=104). |
| **Time-to-failure = hours since first observation** | SECOM is a discrete-time production log, not a life test. This framing bridges to standard Weibull renewal analysis. |
| **Median rank via Bernard's approximation `(i - 0.3) / (n + 0.4)`** | Standard for small-sample plotting; less biased than `i / (n+1)` for n < 50. |
| **Cohen's d for sensor selection** | Effect-size ranking is robust to the 14:1 class imbalance in SECOM. |
| **Implicit spec = Pass samples' P1 / P99** | SECOM has no engineered spec limits. Using the empirical Pass distribution as tolerance is a defensible proxy. |
| **AIAG 4th Ed. FMEA scoring** | Widely used in automotive + semiconductor supply chains; more portable than fab-specific rubrics. |

---

## Limitations & Honesty

- **Sensor meanings are anonymized** in UCI SECOM. The FMEA document uses sensor IDs
  as proxies for physical process parameters, with **hypothesized failure mechanisms
  clearly labeled as assumptions** rather than diagnosed root causes.
- **Small failure sample** (n = 104) — 90% CI on Weibull β would span roughly ±0.4.
- This is a **portfolio demonstration of the analytical framework**, not a
  production incident report.

---

## Skills Demonstrated (Portfolio-Wide)

**Data Engineering**: PostgreSQL 16 (long-format schema, views, indexes), pandas ETL, SQL

**Machine Learning**: XGBoost, imbalanced classification, cross-validation, threshold tuning, feature selection (VarianceThreshold, Mutual Information)

**Statistics & Reliability**: Weibull distribution fitting, Cp/Cpk process capability, Cohen's d effect size, Median Rank plotting, probability plots

**Reliability Engineering Frameworks**: FMEA (AIAG 4th Ed.), 8D Report, 5-Why, Fishbone/Ishikawa, RPN, DMAIC, SPC

**Visualization**: Streamlit + Plotly interactive dashboards, matplotlib static plots, Tableau Public

**Industry Standards Referenced**: AIAG SPC, AIAG FMEA 4th Ed., JEDEC JESD22

---

## Related Projects

- **[semicon-defect-cnn](https://github.com/tzuhua0308/semicon-defect-cnn)** — PyTorch CNN for WM-811K wafer map defect classification. Computer vision sister track (image data / deep learning), complementary to this tabular / statistics-heavy SECOM portfolio.
