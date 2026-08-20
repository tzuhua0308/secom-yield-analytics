# SECOM Reliability Analysis Toolkit

> **Semiconductor package reliability analysis on UCI SECOM (1,567 wafer lots × 590 sensors).**
> Weibull distribution fitting, process capability (Cpk) analysis, and a full FMEA + 8D report
> demonstrating the standard reliability engineering workflow used in fab and OSAT operations.

## TL;DR

This project takes the UCI SECOM dataset (Pass/Fail labels + 590 anonymized sensor readings)
and applies **four layers of reliability analysis** in the same sequence a package reliability
engineer would use in real fab operations:

```
Dashboard   →   Weibull       →   Cpk             →   FMEA + 8D
(WHERE)         (HOW failing)     (WHAT drivers)      (WHY & FIX)
```

Sister project of an existing SECOM Dashboard (Streamlit + PostgreSQL) that first surfaced
a **2008-07 yield excursion (yield dropped 93.4% → 85.96%)**. This toolkit provides the
statistical evidence and structured RCA for that finding.

---

## Key Results

### 1. Weibull Analysis — Failure Mechanism

```
β (shape)  =  2.702   → Wear-out failure mode (aging / fatigue driven)
η (scale)  = 5175.8 hr → Characteristic life (63.2% failure point)
B10 life   = 2250.2 hr → 10% failure time (warranty threshold)
MTTF       = 4602.8 hr → Mean time to failure
```

![Weibull Analysis](outputs/weibull_analysis.png)

**Interpretation**: β > 1 with a well-linearized probability plot → failures are **not random**,
they accumulate over time. This mathematically supports the yield excursion pattern observed
in the sister Dashboard project.

### 2. Cpk Process Capability — Critical Sensor Diagnosis

Top-5 most discriminating sensors (selected by Cohen's d between Pass and Fail groups):

| Sensor | Cpk  | Judgment       |
|--------|------|----------------|
| S_431  | 0.18 | Not Capable    |
| S_510  | 0.33 | Not Capable    |
| S_348  | 0.37 | Not Capable    |
| S_59   | 0.51 | Not Capable    |
| S_103  | 0.61 | Not Capable    |

![Cpk Analysis](outputs/cpk_analysis.png)

**Interpretation**: All 5 critical sensors fall below the industry threshold of Cpk ≥ 1.33.
This quantifies **which specific process parameters** are driving the yield loss.

### 3. FMEA + 8D Report — Structured RCA

Full report: [`docs/FMEA_and_8D_Report.md`](docs/FMEA_and_8D_Report.md)

Includes:
- **FMEA worksheet** scored per AIAG 4th Ed. (Severity × Occurrence × Detection = RPN)
- **8D Report** (D1 Team → D8 Recognition)
- **5-Why analysis** and **Fishbone (Ishikawa) diagram**
- Corrective actions with owner / deadline / success metric
- Verification plan (Cpk targets, Weibull β convergence)

---

## Project Structure

```
reliability/
├── weibull_analysis.py         # Module 1 — Weibull fit + probability plot
├── cpk_analysis.py             # Module 2 — Cpk on Top-5 discriminating sensors
├── docs/
│   └── FMEA_and_8D_Report.md   # Module 3 — Structured RCA document
├── outputs/
│   ├── weibull_analysis.png
│   └── cpk_analysis.png
└── README.md
```

---

## How to Run

Requires the SECOM dataset from the sister Dashboard project
(`../dashboard/data/uci-secom.csv`) and the same virtual environment
(Python 3.13, scipy, pandas, matplotlib).

```bash
# Activate shared venv
source ../dashboard/.venv/bin/activate

# Weibull analysis
python weibull_analysis.py

# Cpk analysis
python cpk_analysis.py
```

Both scripts print numeric results to stdout and save PNG figures to `outputs/`.

---

## Design Decisions

Non-trivial choices worth explaining in an interview:

| Decision | Rationale |
|----------|-----------|
| **Fit Weibull with `floc=0`** | Standard reliability engineering practice (2-parameter Weibull); the 3-parameter version with free location often overfits on small failure samples. |
| **Time-to-failure = hours since first observation** | SECOM is a discrete-time production log, not a life test. Framing failures as a renewal process is the standard bridge to Weibull. |
| **Median rank via Bernard's approximation `(i - 0.3) / (n + 0.4)`** | Industry-standard for small sample plotting; less biased than `i / (n+1)` for n < 50. |
| **Cohen's d for sensor selection** | Effect-size ranking is more robust than raw t-statistic when sample sizes are imbalanced (1,463 Pass vs 104 Fail). |
| **Spec limits = Pass samples' P1 / P99** | SECOM has no engineered spec limits. Using the empirical Pass distribution as implicit tolerance is a defensible proxy that lets Cpk be computed at all. |
| **AIAG 4th Ed. scoring for FMEA** | Widely used in automotive and semiconductor supply chains; more portable than fab-specific rubrics. |

---

## Limitations & Honesty

- **Sensor meanings are anonymized** in the UCI SECOM dataset. The FMEA document uses
  sensor IDs as proxies for physical process parameters, with **hypothesized failure
  mechanisms** clearly labeled as assumptions rather than diagnosed root causes.
- **Small failure sample** (n = 104) limits the precision of Weibull parameters;
  90% confidence intervals on β would span roughly ±0.4 for this sample size.
- **Not a substitute for real fab telemetry**. This is a portfolio demonstration of
  the analytical framework, not a production-ready incident report.

---

## Skills Demonstrated

**Statistical Methods**: Weibull distribution fitting, Process Capability (Cp / Cpk),
Cohen's d effect size, Median Rank / Bernard's approximation, Empirical CDF, Probability plots

**Reliability Engineering Frameworks**: FMEA (AIAG 4th Ed.), 8D Report, 5-Why,
Fishbone / Ishikawa, RPN prioritization, DMAIC, SPC (Statistical Process Control)

**Industry Standards Referenced**: AIAG SPC, AIAG FMEA 4th Ed., JEDEC JESD22 (reliability testing)

**Python Stack**: `pandas`, `numpy`, `scipy.stats.weibull_min`, `matplotlib`

---

## Related Projects

- **[SECOM Dashboard](https://github.com/tzuhua0308/)** — PostgreSQL + Streamlit yield dashboard (upstream project that surfaced the 2008-07 excursion)
- **[semicon-defect-cnn](https://github.com/tzuhua0308/semicon-defect-cnn)** — PyTorch CNN for WM-811K wafer map defect classification (CV / DL sister project)
