"""
SECOM Cpk 製程能力分析

方法:
1. 過濾 NaN < 10% 的 sensor
2. 挑「Pass vs Fail 分佈差距最大」的 Top 5 sensor (用 Cohen's d 概念)
3. 用 Pass 樣本的 P1/P99 作為隱含 spec limits (LSL/USL)
4. 計算 Cp / Cpk,並用業界標準判定製程能力

業界判定 (JEDEC / AIAG SPC):
  Cpk >= 1.67  Excellent (Six Sigma level)
  Cpk >= 1.33  Adequate (industry standard)
  Cpk >= 1.00  Marginal
  Cpk <  1.00  Not Capable — process improvement needed
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

DATA = Path("/Users/chiutzuhua/Desktop/專案/SECOM_半導體良率/dashboard/data/uci-secom.csv")
OUT = Path("/Users/chiutzuhua/Desktop/專案/SECOM_半導體良率/reliability/outputs")

# --- 1. 讀資料 ---
df = pd.read_csv(DATA)
sensor_cols = [c for c in df.columns if c not in ("Time", "Pass/Fail")]
labels = df["Pass/Fail"]  # -1 = Pass, +1 = Fail


# --- 2. 挑 Top 5 有區別力的 sensor (Cohen's d) ---
def discriminant(col: str) -> float:
    p = df.loc[labels == -1, col].dropna()
    f = df.loc[labels == 1, col].dropna()
    if p.std() == 0 or len(f) < 30:
        return 0.0
    pooled_var = ((p.var() * (len(p) - 1)) + (f.var() * (len(f) - 1))) / (len(p) + len(f) - 2)
    pooled_sd = np.sqrt(pooled_var)
    return abs(p.mean() - f.mean()) / pooled_sd if pooled_sd > 0 else 0.0


valid = [c for c in sensor_cols if df[c].isna().mean() < 0.10]
scores = sorted([(c, discriminant(c)) for c in valid], key=lambda x: x[1], reverse=True)
top5 = [c for c, _ in scores[:5]]


# --- 3. 計算 Cpk ---
def compute_cpk(col: str) -> dict | None:
    pass_data = df.loc[labels == -1, col].dropna()
    all_data = df[col].dropna()
    LSL, USL = np.percentile(pass_data, [1, 99])
    mu, sigma = all_data.mean(), all_data.std()
    if sigma == 0:
        return None
    cp = (USL - LSL) / (6 * sigma)
    cpk = min((USL - mu) / (3 * sigma), (mu - LSL) / (3 * sigma))
    return {"LSL": LSL, "USL": USL, "mean": mu, "std": sigma, "Cp": cp, "Cpk": cpk}


def judge(cpk_val: float) -> str:
    if cpk_val >= 1.67: return "Excellent (6-sigma)"
    if cpk_val >= 1.33: return "Adequate"
    if cpk_val >= 1.00: return "Marginal"
    return "Not Capable"


# --- 4. 印表格 ---
rows = []
for col in top5:
    r = compute_cpk(col)
    if r is None:
        continue
    r["Sensor"] = f"S_{col}"
    r["Judgment"] = judge(r["Cpk"])
    rows.append(r)

results = pd.DataFrame(rows)[["Sensor", "LSL", "USL", "mean", "std", "Cp", "Cpk", "Judgment"]]

print("=" * 82)
print("SECOM Top-5 Discriminating Sensors — Process Capability Analysis (Cpk)")
print("=" * 82)
print(results.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("=" * 82)
n_bad = (results["Cpk"] < 1.0).sum()
print(f"\n結論: {n_bad}/{len(results)} 個關鍵 sensor 落在 Not Capable 區間 → 這些製程參數需要改善")

# --- 5. 畫 Cpk 直方圖(6-in-1) ---
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for i, col in enumerate(top5):
    ax = axes[i]
    r = compute_cpk(col)
    if r is None:
        continue
    data = df[col].dropna()
    # 限制 x 範圍避免極端 outlier 撐爆圖
    lo, hi = np.percentile(data, [0.5, 99.5])
    ax.hist(data.clip(lo, hi), bins=40, alpha=0.65, edgecolor='black', color='steelblue')
    ax.axvline(r["LSL"], color='red', ls='--', lw=1.5, label=f'LSL={r["LSL"]:.2g}')
    ax.axvline(r["USL"], color='red', ls='--', lw=1.5, label=f'USL={r["USL"]:.2g}')
    ax.axvline(r["mean"], color='green', ls='-', lw=1.5, label=f'μ={r["mean"]:.2g}')
    ax.set_title(f'Sensor_{col}  |  Cpk={r["Cpk"]:.2f} — {judge(r["Cpk"])}',
                 fontsize=10)
    ax.set_xlabel('Reading')
    ax.set_ylabel('Count')
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(alpha=0.3)

axes[5].axis('off')
axes[5].text(0.1, 0.5,
             "Method:\n"
             "  Spec limits = Pass samples' P1/P99\n"
             "  Cpk = min[(USL-μ)/3σ, (μ-LSL)/3σ]\n\n"
             "Interpretation:\n"
             "  These are the 5 most discriminating sensors\n"
             "  (largest Pass-vs-Fail mean gap).\n"
             "  Low Cpk = process spread too wide for spec.",
             fontsize=10, family='monospace', verticalalignment='center')

plt.tight_layout()
out_path = OUT / "cpk_analysis.png"
plt.savefig(out_path, dpi=120, bbox_inches='tight')
print(f"\nChart saved: {out_path}")
