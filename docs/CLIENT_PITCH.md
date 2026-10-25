# WindWatch: Client Pitch & Product Presentation

**Target Audience:** UK Wholesale Power Trading Desk & Day-Ahead Dispatch Team  
**Product:** WindWatch – GB Day-Ahead Wind Forecast Monitor & Risk Optimization Platform  
**Target Market:** UK Electricity Wholesale Market (Day-Ahead Auctions & Balancing Mechanism)  

---

## 1. Executive Summary & Market Problem

As a licensed electricity supplier in Great Britain, your core obligation is to ensure that the power you procure in wholesale markets matches your retail consumers' demand profile for every 30-minute settlement period across the delivery day.

Before day-ahead auction gates close (e.g. EPEX SPOT GB Day-Ahead auction at **09:20 London time**), your trading desk faces a fundamental calculation:

$$\text{Procurement Target} = \text{Consumer Demand} - \text{Expected Wind Generation}$$

Because wind generation is weather-dependent and intermittent, your procurement strategy hinges directly on the quality and conservatism of the wind forecasts available when you submit your bids.

### The Asymmetric Cost of Forecast Error
In power trading, forecast errors do not carry symmetric costs:
* **Over-forecasting Wind Generation (The Critical Danger):**  
  If your desk expects 14 GW of wind generation but only 10 GW materializes, you will have under-procured 4 GW in the day-ahead auction. To balance your position, you are forced into the **Balancing Mechanism (BM)** at **System Buy Prices (Cashout Prices)**. During tight winter supply margins (e.g. January cold snaps with low wind), Cashout Prices routinely surge to **£1,000 – £4,000+ / MWh**. A 500 MW deficit over just a few peak evening settlement periods can cost your utility millions of pounds in imbalance penalties.
* **Under-forecasting Wind Generation:**  
  If your desk underestimates wind yield, you over-commit expensive thermal generation (CCGT/peaker contracts) at high spark spreads and must spill or dump surplus power into depressed within-day markets.

---

## 2. Introducing WindWatch

**WindWatch** is an operational intelligence and decision-support platform designed specifically for the day-ahead trading and power procurement workflow. It ingests national wind actuals (`FUELHH`) and forecast runs (`WINDFOR`) from Elexon BMRS to give your desk complete clarity on latest available forecasts, run-to-run forecast momentum, and quantified statistical error distributions.

---

## 3. Core Capabilities Tailored for Your Trading Desk

### 1. Decision-Fidelity & Gate Closure Control
* **Reconstruct Real Information States:** Select your exact decision time (e.g. **09:00 London time**, 20 minutes prior to EPEX SPOT auction gate closure). 
* **Zero Look-Ahead Bias:** WindWatch uses high-performance binary search to select only the latest forecast vintage published *before* your decision deadline. Forecasts published after your gate are strictly excluded from your decision baseline.
* **Configurable Horizon Buffer:** Enforce a lead-time buffer (e.g., $\ge 4\text{ hours}$ before gate) to ensure atmospheric weather models have fully digested European meteorological assimilation data.

### 2. Run-to-Run Forecast Evolution & Momentum (`/forecasts/evolution`)
* Atmospheric numerical weather prediction (NWP) models update throughout the morning. 
* WindWatch tracks consecutive Elexon forecast runs and highlights period-by-period revisions ($\Delta = \text{Latest} - \text{Previous}$ in GW):
  * **Emerald Highlight ($\Delta > 0$):** Model runs are upgrading wind yield.
  * **Rose Highlight ($\Delta < 0$):** Model runs are downgrading wind yield (warning of potential deficit).
* Allows your traders to observe whether weather forecasts are converging or drifting before locking orders.

### 3. Settlement Period Granularity (SP 1–48)
* All data is mapped directly to standard GB half-hourly **Settlement Periods (SP 1 through SP 48)**, matching your trade capture systems, Elexon settlement reports, and National Grid ESO dispatch instructions.

### 4. Quantified Accuracy Suite & Horizon Breakdown
* **Comprehensive Metrics:** Real-time visibility into Mean Absolute Error (MAE), Root Mean Square Error (RMSE), Directional Bias, and Capacity-Normalized Error (nMAE).
* **Lead-Time Horizon Buckets:** Forecast accuracy naturally degrades with lead time. WindWatch segments historical performance into actionable operational buckets:
  * **0–6 hours** (Intraday gate closure)
  * **6–12 hours** (Same-day positioning)
  * **12–24 hours** (Day-ahead auction decision window)
  * **24–48 hours** (Preliminary scheduling & thermal unit commitment)

### 5. Empirical P90 Planning Margin (Conservative Thermal Sizing)
* To protect your balance sheet against extreme cashout price spikes, relying on median or mean forecast output is insufficient.
* WindWatch calculates an empirical **P90 Planning Margin** based on the 90th percentile of historical forecast over-prediction.
* **P90 Planning Baseline:**
  $$\text{Baseline}_t = \max(0, \text{Forecast}_t - \text{Margin}_{P90})$$
* By committing thermal baseload contracts up to this P90 baseline, your desk has **90% statistical confidence** that physical wind generation will not fall below your procured position.

### 6. One-Click Desk Export (`/export/review.csv`)
* One-click download of the complete 48-period settlement schedule, including actuals, latest forecasts, error bands, and P90 baselines, ready for immediate ingestion into your proprietary trade valuation spreadsheets and dispatch algorithms.

---

## 4. Operational Workflow: A Morning at the Day-Ahead Desk

1. **08:30 London Time:** Trader opens WindWatch. The system defaults to delivery for tomorrow with an 09:00 gate time.
2. **08:35 London Time:** Trader reviews the **Forecast Evolution** tab. The latest 07:30 run revised wind generation downward by 450 MW for evening peak (SP 34–38) compared to the 06:00 run.
3. **08:45 London Time:** Desk inspects the **Horizon Table**; 12–24h forecast error shows an MAE of 1.2 GW with an average over-forecast bias.
4. **08:50 London Time:** Trader references the **P90 Planning Baseline** (2.1 GW margin). To eliminate cashout penalty exposure during peak demand hours, the trader secures thermal baseload matching the P90 baseline.
5. **09:10 London Time:** Trader exports the 48-period schedule CSV into the trading execution system and submits orders to EPEX SPOT well before 09:20 gate closure.

---

## 5. Summary Value Proposition

| Client Risk | Traditional Approach | WindWatch Advantage |
|---|---|---|
| **Balancing Mechanism Penalties** | Unhedged forecast errors trigger £1,000+/MWh cashout exposure. | **P90 Planning Margin** caps exposure with 90% statistical confidence. |
| **Look-Ahead Contamination** | Backtests and tools accidentally use forecasts published post-gate. | **Strict Gate-Closure Time-Lock** guarantees realistic operational fidelity. |
| **Sudden Model Shift** | Traders unaware of morning weather model downgrades. | **Run-to-Run Delta Tracking** provides immediate momentum alert. |
| **Decision Latency** | Manual spreadsheets and delayed downloads from BMRS. | **Sub-15ms In-Memory Engine** with live Elexon streaming and instant CSV export. |
