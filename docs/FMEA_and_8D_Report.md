# FMEA & 8D Root Cause Analysis
## Case Study: SECOM 2008-07 Yield Excursion

> 本文以 SECOM 公開資料 (UCI 1,567 lots, 2008-07 ~ 2008-10) 為分析對象,
> 用**封裝可靠度工程師的標準文件框架 (FMEA + 8D)** 重現一次
> Yield Excursion 的根因分析流程。

---

## 0. Executive Summary

- **事件**:2008-07 SECOM 產線月度良率從基線 93.4% 陡降至 **85.96%**
- **影響**:單月失效批次數量 +138% (與 8/9 月平均比)
- **分析路徑**:Dashboard 定位 → Weibull 判斷失效機制 → Cpk 定位關鍵變數 → FMEA 排序改善優先度 → 8D 結構化行動
- **結論**:2008-07 excursion 屬 **Wear-out 型 (β=2.70)**,主要驅動來自 **5 個 Cpk < 1.0 的關鍵 sensor 參數失控**;建議依 RPN 排序執行 SPC 監控與參數再中心化 (re-centering)

> ⚠️ **資料透明度說明**:UCI SECOM 資料集的 sensor 意義已匿名化,
> 本 FMEA 表格中的物理失效機制為**基於統計分析結果的合理假設**,
> 用於展示分析框架,非真實 fab 內部診斷結論。

---

## 1. FMEA (Failure Mode and Effects Analysis)

### 1.1 評分基準 (依 AIAG FMEA 4th Edition)

| 分數 | Severity (嚴重度) | Occurrence (發生率) | Detection (偵測難度) |
|------|-------------------|--------------------|--------------------|
| 10   | 產品完全失效、危及安全 | > 1/2 批次      | 幾乎無法偵測       |
| 7-9  | 主要功能喪失、需 rework | 1/10 ~ 1/20     | 現有 SPC 難以捕捉   |
| 4-6  | 效能下降但可接受       | 1/100 ~ 1/500   | 抽樣可偵測         |
| 1-3  | 無感或美觀問題         | < 1/10,000      | 100% 檢測可捕捉    |

**RPN = Severity × Occurrence × Detection** (範圍 1 ~ 1000)

- RPN >= 200:高風險,必須立即處理
- RPN 100 ~ 200:中風險,列入改善計畫
- RPN < 100:低風險,持續監控

### 1.2 FMEA Worksheet — SECOM Top-5 Discriminating Sensors

| # | Sensor | Failure Mode (失效模式) | Effect on Product (對產品的影響) | Potential Cause (可能原因) | S | O | D | **RPN** | Recommended Action |
|---|--------|------------------------|------------------------------|--------------------------|---|---|---|--------|-------------------|
| 1 | S_431  | 參數分佈嚴重偏離 (Cpk=0.18) | Wafer lot final test fail | Chamber 溫度控制迴路失效 / 感測器校正漂移 | 9 | 8 | 7 | **504** | 立即停線校正,重建 SPC control chart,加裝冗餘 sensor |
| 2 | S_510  | 分佈拖尾,右側 outlier 密集 (Cpk=0.33) | Wafer lot final test fail | 氣體流量控制閥週期性失靈 | 9 | 7 | 6 | **378** | 更換流量控制閥,建立每日 first-piece 驗證 |
| 3 | S_348  | 參數中心飄移 (Cpk=0.37) | Yield loss | 製程配方 (recipe) 未依材料批號調整 | 8 | 7 | 5 | **280** | 建立材料批號 → recipe 對映表,自動化 setup |
| 4 | S_59   | 分佈過寬 (Cpk=0.51) | 隱性 yield loss | 設備週期性維護間隔過長 | 7 | 6 | 5 | **210** | 縮短 PM 週期由 720h → 500h |
| 5 | S_103  | 微幅偏移,但變異度大 (Cpk=0.61) | 邊緣批次 yield 敏感 | 環境溫濕度未在 cleanroom 規範內 | 6 | 5 | 6 | **180** | 加裝環境監控,連動 recipe 補償 |

**RPN 排序結論**:全部落在中高風險,S_431 是**必須立即處理的第一優先**。

---

## 2. 8D Report

### D1 — Team (跨功能團隊組成)

| Role | Responsibility |
|------|---------------|
| Package Reliability Engineer | 資料分析、Weibull/Cpk 統計驗證、報告主筆 |
| Process Engineer (Etch/Depo) | S_431、S_510 對應機台調校 |
| Equipment Engineer | Chamber 校正、流量控制閥更換 |
| Quality Engineer | SPC control chart 重建、線上監控 |
| Materials Engineer | 材料批號與 recipe 對映表建立 |

### D2 — Problem Description (問題描述)

**Is / Is-Not 分析**:

| 面向 | Is | Is-Not |
|-----|-----|--------|
| **What** | Wafer lot final test fail rate ↑ | 特定產品線異常 |
| **When** | 2008-07 (peak),8-9 月回穩 | 全年持續問題 |
| **Where** | 全產線良率均受影響 | 特定機台獨有 |
| **How Much** | 良率 93.4% → 85.96% (-7.44pp) | 完全停線等級 |

**量化資料**:
- 基線良率:93.4% (2008-08、09 平均)
- 峰值失效月:2008-07,良率 85.96%
- 失效批次數:104 lots (across 3 個月)
- 統計分析:β=2.70 → wear-out 型失效 (非隨機)

### D3 — Interim Containment (臨時圍堵措施)

1. **停止影響最大的 sensor 對應機台生產**,轉移至備用機台
2. **對已完成但未出貨的批次執行 100% retest**,防止不良品流出
3. **暫時將 sampling 頻率從每 4 hr 提升至每 1 hr**,增加偵測機會

### D4 — Root Cause Analysis (根因分析)

#### 4.1 5-Why Analysis (以 S_431 為例)

```
Why 1: 為什麼 lot 會 fail?
       → 因為 S_431 讀值超出 Pass 樣本的 P1/P99 範圍
Why 2: 為什麼 S_431 讀值會超出範圍?
       → 因為 Cpk = 0.18,製程本身變異度遠大於規格容忍
Why 3: 為什麼變異度會這麼大?
       → 因為對應機台的溫度控制迴路 (PID) 未經校正
Why 4: 為什麼 PID 沒有校正?
       → 因為現有 PM 排程只包含物理清潔,不含控制迴路重整
Why 5: 為什麼 PM 排程不含控制迴路?
       → 因為 SOP 撰寫時未納入控制系統老化 (wear-out) 假設
```

**Root Cause**:PM SOP 設計時未考量控制系統長時間漂移,與 Weibull 分析結果 (β=2.70, wear-out 主導) 完全吻合。

#### 4.2 Fishbone (Ishikawa) Diagram

```
                                                          Yield Excursion
                                                          (85.96% in 2008-07)
                                                                  ▲
     ┌─────Man─────┐         ┌──────Machine──────┐              │
     │             │         │                    │              │
     │ Operator    │         │ Chamber temp drift ├──────────────┤
     │ training    │         │ (S_431, Cpk=0.18)  │              │
     │ gap         │         │                    │              │
     │             │         │ Flow valve fatigue │              │
     └─────────────┘         │ (S_510, Cpk=0.33)  │              │
                             └────────────────────┘              │
                                                                  │
     ┌─────Method────┐        ┌──────Material─────┐              │
     │               │        │                   │              │
     │ Recipe not    │        │ Batch-to-batch    ├──────────────┤
     │ adapted per   ├────────┤ variation not     │              │
     │ batch (S_348) │        │ compensated       │              │
     │               │        │                   │              │
     │ PM interval   │        │                   │              │
     │ too long      │        └───────────────────┘              │
     │ (S_59)        │                                            │
     └───────────────┘        ┌──Measurement──┐                  │
                              │                │                  │
                              │ SPC sampling   ├──────────────────┘
                              │ rate too low   │
                              │ (Detection=7)  │
                              └────────────────┘
```

### D5 — Corrective Actions (根本對策)

| # | Action | Owner | Deadline | Success Metric |
|---|--------|-------|----------|---------------|
| 1 | 重寫 PM SOP,納入 chamber PID 迴路校正 | Equipment Eng. | Week 2 | SOP v2.0 發布 |
| 2 | S_431 對應機台立即執行控制迴路重整 | Process Eng. | Week 1 | Cpk 由 0.18 → ≥ 1.33 |
| 3 | 更換 S_510 對應流量閥,建立 first-piece SPC | Process Eng. | Week 3 | Cpk ≥ 1.00 且 stable 4 週 |
| 4 | 建立材料批號與 recipe 對映表 | Materials Eng. | Week 4 | 100% 批次自動對映 |
| 5 | PM 週期由 720h 縮短為 500h | Equipment Eng. | Week 2 | 排程更新完成 |

### D6 — Verify Effectiveness (效果驗證)

**驗證方法**:對策實施後,連續 8 週追蹤以下指標:

| 指標 | 對策前 | 目標 | 驗證方法 |
|------|-------|------|---------|
| 月度良率 | 85.96% (peak fail) | ≥ 93.4% 且穩定 | 月度 Yield 報表 |
| Top-5 Sensor Cpk | 0.18 ~ 0.61 | 全部 ≥ 1.33 | 每週 Cpk 報表 |
| Weibull β | 2.70 (wear-out) | 接近 1.0 (random) | 月度重跑 Weibull |
| 失效批次數/月 | 34 (peak) | < 15 | 週報統計 |

### D7 — Prevent Recurrence (預防再發)

1. **標準化**:將 PM SOP v2.0 推廣至同型號所有機台 (共 12 台)
2. **系統化監控**:建立 real-time SPC dashboard,Cpk < 1.33 自動 email 告警
3. **知識管理**:將本次分析納入新人 training 教材 (case study format)
4. **定期審視**:每季重跑 Weibull + Cpk 分析,監控 β 是否再次偏移到 wear-out 區間

### D8 — Team Recognition

跨功能團隊在 8 週內完成從問題定位到系統性改善的完整循環,建立**「Dashboard → Weibull → Cpk → FMEA → 8D」的標準分析框架**,可套用於未來所有 yield excursion 事件。

---

## 3. 分析框架總結

本案例展示**四層分析工具的串接使用**:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Dashboard       │───▶│  Weibull         │───▶│  Cpk             │───▶│  FMEA + 8D       │
│  (定位現象)      │    │  (判斷失效機制)  │    │  (定位關鍵變數)  │    │  (排序 + 行動)   │
│                  │    │                  │    │                  │    │                  │
│  月度趨勢圖顯示  │    │  β=2.70          │    │  5 個 Cpk<1.0    │    │  RPN 排序        │
│  2008-07 陡降    │    │  → wear-out      │    │  的關鍵 sensor   │    │  行動計畫        │
└──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘
       WHERE                    HOW                     WHAT                     WHY & FIX
```

**方法論價值**:單一工具只能回答單一問題,四層工具串接才能完成從「發現異常」到「執行改善」的完整閉環。

---

## Appendix: Keywords / Tools Referenced

**Statistical Methods**: Weibull distribution, Cohen's d, Process Capability (Cp/Cpk), Median Rank, Bernard's Approximation

**Reliability Frameworks**: FMEA (AIAG 4th Ed.), 8D Report, 5-Why, Fishbone/Ishikawa, DMAIC (Define-Measure-Analyze-Improve-Control)

**Industry Standards Referenced**: JEDEC JESD22 (reliability test), AIAG SPC (statistical process control)

**Python Stack**: pandas, numpy, scipy.stats.weibull_min, matplotlib
