"""
SECOM Weibull Analysis
把 SECOM 資料的 Fail 事件當作「失效時間」,fit Weibull 分佈,
產出封裝可靠度工程師常看的三個關鍵指標:
  - β (shape)  : 判斷失效機制 (嬰兒期 / 隨機 / 老化)
  - η (scale)  : 特徵壽命,63.2% 產品失效的時間
  - B10 life   : 10% 產品失效的時間 (常用保固基準)
"""

import numpy as np
import pandas as pd
from scipy.stats import weibull_min
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path("/Users/chiutzuhua/Desktop/專案/SECOM_半導體良率/dashboard/data/uci-secom.csv")
OUT = Path("/Users/chiutzuhua/Desktop/專案/SECOM_半導體良率/reliability/outputs")

# --- 1. 讀資料 + 算失效時間 (小時) ---
df = pd.read_csv(DATA, parse_dates=["Time"]).sort_values("Time").reset_index(drop=True)
t0 = df["Time"].min()
fail_hr = ((df.loc[df["Pass/Fail"] == 1, "Time"] - t0).dt.total_seconds() / 3600).values

# --- 2. Fit Weibull (強制 loc=0,標準做法) ---
shape, _, scale = weibull_min.fit(fail_hr, floc=0)
b10 = weibull_min.ppf(0.10, shape, loc=0, scale=scale)
mttf = weibull_min.mean(shape, loc=0, scale=scale)

# --- 3. 輸出結果 ---
if shape < 0.9:
    mechanism = "早期失效 (Infant Mortality) — 通常是製程 bug 或材料瑕疵"
elif shape < 1.1:
    mechanism = "隨機失效 (Random) — 外部因素主導"
else:
    mechanism = "磨耗失效 (Wear-out) — 老化 / 疲勞主導"

print("=" * 55)
print(f"SECOM Weibull 分析結果 (N={len(fail_hr)} 失效事件)")
print("=" * 55)
print(f"β (shape)  = {shape:6.3f}   → {mechanism}")
print(f"η (scale)  = {scale:6.1f} hr → 特徵壽命 (63.2% 失效)")
print(f"B10 life   = {b10:6.1f} hr → 10% 失效時間")
print(f"MTTF       = {mttf:6.1f} hr → 平均失效時間")
print("=" * 55)

# --- 4. 畫兩張圖 (英文標籤,portfolio 用) ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# (a) Histogram + fitted Weibull PDF
axes[0].hist(fail_hr, bins=20, density=True, alpha=0.6, edgecolor='black', label='SECOM failures')
x = np.linspace(0.1, fail_hr.max(), 300)
axes[0].plot(x, weibull_min.pdf(x, shape, loc=0, scale=scale), 'r-', lw=2,
             label=f'Weibull fit (β={shape:.2f}, η={scale:.0f}h)')
axes[0].set_xlabel('Time to Failure (hours)')
axes[0].set_ylabel('Density')
axes[0].set_title('Failure Time Distribution + Weibull Fit')
axes[0].legend()
axes[0].grid(alpha=0.3)

# (b) Weibull probability plot (linearized)
sorted_t = np.sort(fail_hr)
n = len(sorted_t)
median_rank = (np.arange(1, n + 1) - 0.3) / (n + 0.4)  # Bernard's approximation
xp = np.log(sorted_t)
yp = np.log(-np.log(1 - median_rank))
axes[1].scatter(xp, yp, s=25, alpha=0.7, label='Data points')
x_line = np.linspace(xp.min(), xp.max(), 100)
axes[1].plot(x_line, shape * (x_line - np.log(scale)), 'r-', lw=2,
             label=f'Fit line (slope=β={shape:.2f})')
axes[1].set_xlabel('ln(Time to Failure)')
axes[1].set_ylabel('ln(-ln(1-F))')
axes[1].set_title('Weibull Probability Plot')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
out_path = OUT / "weibull_analysis.png"
plt.savefig(out_path, dpi=120, bbox_inches='tight')
print(f"\nChart saved: {out_path}")
