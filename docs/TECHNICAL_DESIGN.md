# WindWatch: Internal Technical Lead Design Review

**Author:** Software Engineering & Quantitative Development Team  
**Subject:** Software Architecture, Domain Design, & Production Implementation  
**Codebase:** Python 3.12 (FastAPI), React 18 (TypeScript, Vite, Tailwind CSS v4), Docker  

---

## 1. Architectural Philosophy & Layer Separation

WindWatch is built around **Clean Architecture / Hexagonal Design** principles. The core business rules and financial risk models have **zero dependencies** on external web frameworks, databases, or I/O libraries.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer (React 18)                 │
│      TypeScript, Vite, Tailwind CSS v4, Recharts, SVG Turbines  │
└─────────────────────────────────▲───────────────────────────────┘
                                  │ HTTP / JSON (Axios)
┌─────────────────────────────────▼───────────────────────────────┐
│                     API Layer (FastAPI v1)                      │
│     app/api/v1 (review.py, evolution.py, export.py, health.py)  │
│     Pydantic v2 Schemas, ProcessTimeMiddleware, Rate Limits     │
└─────────────────────────────────▲───────────────────────────────┘
                                  │ Dependency Injection
┌─────────────────────────────────▼───────────────────────────────┐
│                    Application / Service Layer                  │
│       DataService (stale-while-revalidate, single-flight lock)  │
│       ReviewService (LRU memoisation, precomputed aggregates)   │
└───────────────────▲─────────────────────────────▲───────────────┘
                    │                             │
┌───────────────────▼───────────┐    ┌────────────▼───────────────┐
│        Domain Model Core      │    │    Infrastructure & I/O    │
│  (Pure Python, zero deps)     │    │  ElexonClient (BMRS API)   │
│  - models.py: Store dataclass │    │  FUELHH & WINDFOR parsers  │
│  - vintage.py: bisect lookup  │    │  FileDataRepository        │
│  - metrics.py: MAE, RMSE, P90 │    │  Snapshot JSON persistence │
│  - evolution.py: run deltas   │    └────────────────────────────┘
│  - study.py: calendar & SPs   │
└───────────────────────────────┘
```

---

## 2. Domain Model & Mathematical Formulations

### 2.1 The `Store` Aggregate (`app/domain/models.py`)
Market time-series data is stored in memory as a frozen aggregate:
* `actuals: dict[datetime, float]`: Settlement-period wind generation in MW (keyed by UTC `startTime`).
* `forecasts: dict[datetime, dict[datetime, float]]`: Forecast curves keyed by UTC `publishTime`, mapping delivery UTC hour to forecasted MW.
* `_publish_times: list[datetime]`: Sorted list of publication timestamps.

### 2.2 $O(\log N)$ Decision-Time Vintage Lookup (`app/domain/vintage.py` & `models.py`)
To prevent look-ahead contamination, when a trader evaluates delivery day $D$ at gate clock $T_{\text{gate}}$ with minimum horizon buffer $H$:
$$\text{Cutoff} = T_{\text{gate}} - H$$
Instead of linear filtering ($O(N)$), the system uses `bisect.bisect_right` on the pre-sorted publication index:
```python
def latest_publication(self, cutoff: datetime) -> datetime | None:
    idx = bisect.bisect_right(self._publish_times, cutoff)
    return self._publish_times[idx - 1] if idx else None
```
This guarantees sub-microsecond vintage resolution even with hundreds of historical NWP model runs.

### 2.3 Metric Calculations (`app/domain/metrics.py`)
* **Signed Error ($e_t$):**
  $$e_t = \text{Forecast}_t - \text{Actual}_t$$
  A positive error indicates over-forecasting (buying deficit risk in the Balancing Mechanism).
* **Mean Absolute Error (MAE):** $\frac{1}{N} \sum |e_t|$
* **Root Mean Square Error (RMSE):** $\sqrt{\frac{1}{N} \sum e_t^2}$ (penalizes tail deviations quadratically).
* **Empirical P90 Planning Margin:**
  $$\text{Margin}_{P90} = \max\left(0, \text{Percentile}_{90}(\{e_t\})\right)$$
  Computed via linear rank interpolation between closest samples.
* **Conservative P90 Planning Baseline:**
  $$\text{Baseline}_t = \max\left(0, \text{Forecast}_t - \text{Margin}_{P90}\right)$$
* **Normalized MAE (nMAE):** Error relative to peak observed Elexon wind actuals ($\max(P_{\text{actual}})$ from `FUELHH`), strictly adhering to the constraint of relying on Elexon data alone without external capacity databases.
* **MAPE Floor:** Actuals below 100 MW are excluded from the MAPE denominator to avoid extreme division instability during low-wind calms.

---

## 3. Data Ingestion & Upstream Resilience

### 3.1 Live Elexon BMRS Stream Client (`app/integrations/elexon/`)
* **Actuals (`FUELHH`):** Streams half-hourly actuals filtering for `fuelType == "WIND"`. Chunked in 7-day windows using `ThreadPoolExecutor(max_workers=6)`.
* **Forecasts (`WINDFOR`):** Streams hourly forecast publications from 3 days prior to delivery to capture early day-ahead model runs. Chunked in 5-day publication windows using `ThreadPoolExecutor(max_workers=7)`.
* **Retries & Backoff:** `ElexonClient` intercepts HTTP 429 and transient 5xx errors, respecting `Retry-After` response headers with exponential backoff.

### 3.2 Thread-Safe Cache & Concurrency Patterns (`app/services/data_service.py`)
* **Stale-While-Revalidate:** Incoming web requests are served directly from memory in $<15\text{ms}$. When the TTL (default 15 minutes) expires, a background daemon thread asynchronously triggers upstream synchronization.
* **Single-Flight Synchronization (`_refresh_lock`):** Prevents cache stampedes. If multiple concurrent requests trigger a cache miss or refresh, only one thread executes the upstream Elexon fetch while others wait or serve the existing snapshot.
* **Retry Storm Protection:** If an upstream fetch fails, the timestamp is refreshed to avoid continuously thrashing Elexon on subsequent requests.
* **Instant Cold Starts (`FileDataRepository`):** On startup, `DataService` immediately warms itself from `backend/data/elexon_snapshot.json`. If Elexon BMRS is unreachable, the application starts cleanly in read-only mode without blocking health checks.

### 3.3 LRU Memoisation (`app/services/review_service.py`)
* Pre-computes hourly mean actuals and lead-time horizon tables once per dataset version.
* Memoises per-request reviews with an `OrderedDict` bounded at 512 entries, guaranteeing instantaneous response times across slider adjustments.

---

## 4. Frontend Architecture & Design System

* **Stack:** React 18, TypeScript 5.7, Vite, Tailwind CSS v4.
* **Parallel Data Fetching:** `App.tsx` dispatches `fetchReview` and `fetchEvolution` concurrently via `Promise.all` to minimize time-to-interactive.
* **Dynamic Time-Series Visualization (Recharts):**
  * Settlement Periods 1–48 x-axis with hour-tick markers.
  * Area bands for MAE uncertainty envelope (`bandLow`, `bandHigh`).
  * Dedicated dashed amber curve for the **Conservative P90 Planning Baseline**.
  * Directional bar charts for run-to-run forecast revision deltas (emerald for upgrades, rose for downgrades).
* **Fault-Tolerant Error Handling:** User-friendly inline error alerts with interactive "Retry" actions that preserve existing controls.

---

## 5. Quality Assurance & Verification

* **Python Linting & Formatting:** 100% compliant with `ruff` (`line-length = 120`). Zero errors across `app` and `tests`.
* **Static Typing:**
  * Backend: 100% strict `mypy` passing across all 39 source modules.
  * Frontend: Strict `tsc --noEmit` passing across all components, API clients, and types.
* **Automated Test Suite:**
  * 50 unit and integration tests executing in $<0.25\text{s}$ under `pytest`.
  * Contract testing across `/api/v1/review`, `/api/v1/forecasts/evolution`, `/api/v1/export/review.csv`, and `/api/v1/health`.
* **Continuous Integration (`.github/workflows/deploy.yml`):**
  * Automated frontend build (`npm run build`).
  * Automated backend lint (`ruff check`), format validation (`ruff format --check`), type checking (`mypy`), and test suite execution (`pytest`).
