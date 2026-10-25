# WindWatch

**GB Day-Ahead Wind Forecast Monitor & Risk Optimization Platform**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS-v4.3-38bdf8.svg)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/tests-50%20passed-success.svg)](backend/tests)
[![CI](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg)](.github/workflows/deploy.yml)

WindWatch is an operational decision platform tailored for UK wholesale power trading and dispatch desks. It evaluates national wind generation actuals and forecasts from Elexon BMRS to de-risk day-ahead power procurement and optimize thermal plant commitments.

> **Project Presentations & Specifications:**
> * 📊 [**Client Pitch & Presentation (Power Trading Desk)**](docs/CLIENT_PITCH.md)
> * ⚙️ [**Internal Technical Design Review (Tech Lead)**](docs/TECHNICAL_DESIGN.md)

---

## Executive Summary & Trading Context

In the UK electricity wholesale market, licensed suppliers must balance expected customer demand against contracted power generation before day-ahead auction gates close (e.g. EPEX SPOT GB day-ahead auction at 09:20 London time). 

$$\text{Procurement Target} = \text{Consumer Demand} - \text{Expected Wind Generation}$$

Because renewable wind generation is intermittent, buyers face asymmetric financial risks:
* **Over-forecasting Wind:** Leads to under-procurement in the wholesale day-ahead auction, forcing the utility to buy deficit volume in the **Balancing Mechanism (BM)** at high System Buy Prices (Cashout Prices), which can surge above £1,000–£4,000/MWh.
* **Under-forecasting Wind:** Results in over-procuring expensive thermal generation and spilling excess power into depressed markets.

WindWatch resolves this dilemma by delivering **look-ahead-free forecast intelligence**, **run-to-run forecast revision tracking**, and a **statistically conservative P90 planning baseline**.

---

## Core Platform Capabilities

1. **Gate-Closure Decision Fidelity**
   - Reconstructs the exact market information state at any chosen gate time (e.g. 09:00 London time, 20 minutes prior to the EPEX SPOT auction).
   - Enforces configurable forecast horizon lead times (e.g., $\ge 4\text{ hours}$ before gate) using binary-search index lookup ($O(\log N)$) to eliminate look-ahead bias.

2. **Forecast Evolution & Revision Tracking (`/forecasts/evolution`)**
   - Compares consecutive Elexon forecast publications leading up to the auction deadline.
   - Computes period-by-period delta ($\Delta = \text{Latest} - \text{Previous}$ in GW) to show whether atmospheric models are upgrading or downgrading wind yield.

3. **Settlement Period Granularity (SP 1–48)**
   - Maps half-hourly actuals and forecasts directly to official GB 30-minute Settlement Periods (SP 1 through SP 48), matching standard trading and National Grid ESO dispatch terminology.

4. **Quantitative Accuracy Suite**
   - Evaluates forecast deviations across historical delivery days and lead-time horizon buckets (0–6h, 6–12h, 12–24h, 24–48h).
   - Generates an empirical **P90 Planning Margin** ensuring 90% statistical confidence that actual wind output will exceed the committed baseline.

5. **Trading Desk Data Export (`/export/review.csv`)**
   - One-click CSV export delivering full 48-period intraday timeseries for downstream quantitative models, dispatch algorithms, and trading spreadsheets.

---

## Data Architecture & Upstream Ingestion

WindWatch streams data directly from the live Elexon BMRS API:
* **Actual Generation (`FUELHH`)**: [FUELHH Stream](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream) filtered for `fuelType == "WIND"` at 30-minute settlement period resolution.
* **Forecasted Generation (`WINDFOR`)**: [WINDFOR Stream](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream) indexed by target delivery hour (`startTime`) and publication timestamp (`publishTime`).

### Resilience & Performance Architecture
* **Stale-While-Revalidate Caching:** Sub-millisecond response latency (<15ms) via an in-memory `Store` cache. Background threads handle upstream synchronization asynchronously when TTL expires (default 15 minutes).
* **Single-Flight Synchronization:** Multi-threaded mutex locking (`_refresh_lock`) prevents cache stampedes against Elexon during concurrent request spikes.
* **Cold-Start Disk Snapshot Fallback:** Automatically serializes market state to `elexon_snapshot.json` so container instances boot instantly without cold-start blocking.

---

## Metric Formulations

| Metric | Formula | Operational Interpretation |
|---|---|---|
| **Signed Error ($e_t$)** | $e_t = \text{Forecast}_t - \text{Actual}_t$ | Positive = Over-forecast, Negative = Under-forecast. |
| **Mean Absolute Error (MAE)** | $\frac{1}{N} \sum \|e_t\|$ | Average absolute deviation in GW. |
| **Root Mean Square Error (RMSE)** | $\sqrt{\frac{1}{N} \sum e_t^2}$ | Penalizes large deviations quadratically, reflecting non-linear balancing costs. |
| **Mean Signed Bias** | $\frac{1}{N} \sum e_t$ | Directional bias indicating persistent over- or under-forecasting. |
| **Normalized MAE (nMAE)** | $(\text{MAE} / \text{Capacity}_{\text{Elexon}}) \times 100\%$ | Error percentage relative to peak observed Elexon wind actuals (no external data). |
| **MAPE** | $\frac{1}{N} \sum_{\text{Act} \ge 100\text{MW}} \frac{\|e_t\|}{\text{Actual}_t}$ | Percentage error floored at 100 MW to avoid low-wind division volatility. |
| **P90 Planning Margin** | $\text{Percentile}_{90}(\{e_t\})$ | Over-forecast volume exceeded in only 1 hour in 10. |
| **P90 Planning Baseline** | $\max(0, \text{Forecast}_t - \text{Margin}_{P90})$ | Conservative wind figure to size thermal baseload procurement. |

---

## Files and Architecture

```text
wind-forecast-monitor/
├── Dockerfile                      # Multi-stage build: compiles Vite app, runs FastAPI
├── pytest.ini                      # Root pytest config routing cache_dir to backend/.pytest_cache
├── README.md                       # Project documentation and architecture guide
├── .dockerignore                   # Build context exclusions
├── .github/
│   └── workflows/
│       └── deploy.yml              # Production CI/CD for Google Cloud Run
│
├── backend/
│   ├── pyproject.toml              # Python dependencies, metadata, and pytest options
│   ├── data/
│   │   └── elexon_snapshot.json    # Cold-start snapshot fallback from Elexon BMRS
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory, middleware, router mounts, static hosting
│   │   ├── api/
│   │   │   ├── deps.py             # Dependency injection (Store, ReviewService)
│   │   │   └── v1/
│   │   │       ├── router.py       # API v1 router composition
│   │   │       ├── health.py       # Liveness (/health) and readiness (/ready) probes
│   │   │       ├── meta.py         # Study window metadata & Elexon source details (/meta)
│   │   │       ├── review.py       # Day-ahead forecast and accuracy evaluation (/review)
│   │   │       ├── evolution.py    # Run-to-run forecast revision tracking (/forecasts/evolution)
│   │   │       └── export.py       # 48-period CSV timeseries download (/export/review.csv)
│   │   ├── core/
│   │   │   ├── config.py           # Environment settings (Elexon URLs, TTL, timeouts)
│   │   │   ├── errors.py           # Custom exception hierarchy and HTTP handlers
│   │   │   ├── logging.py          # Structured process logging
│   │   │   └── middleware.py       # Request latency timing (x-process-time header)
│   │   ├── domain/                 # Pure domain business logic (zero framework dependencies)
│   │   │   ├── models.py           # Store dataclass and in-memory time-series indices
│   │   │   ├── metrics.py          # MAE, RMSE, P90 planning margin, nMAE, bias, and MAPE
│   │   │   ├── review.py           # Day-ahead review synthesis and lead-time horizon tables
│   │   │   ├── evolution.py        # Vintage delta tracking (latest vs previous model run)
│   │   │   ├── study.py            # UK timezone, settlement periods, and study calendar
│   │   │   └── vintage.py          # Binary-search latest eligible forecast publication
│   │   ├── integrations/
│   │   │   └── elexon/             # Elexon BMRS Live Streaming client
│   │   │       ├── client.py       # HTTP client with retries, exponential backoff, ISO date parser
│   │   │       ├── fuelhh.py       # Actuals stream parser (fuelType == "WIND")
│   │   │       └── windfor.py      # Forecast stream parser (startTime, publishTime, generation)
│   │   ├── repositories/
│   │   │   ├── base.py             # Abstract DataRepository interface
│   │   │   └── file_repo.py        # JSON snapshot file serialization & disk I/O
│   │   ├── schemas/                # Strict Pydantic v2 response schemas
│   │   │   ├── health.py           # HealthResponse schema
│   │   │   ├── meta.py             # MetaResponse schema
│   │   │   ├── review.py           # ReviewResponse, KPIs, Planning, and SeriesPoint schemas
│   │   │   └── evolution.py        # EvolutionResponse and VintageSummary schemas
│   │   └── services/
│   │       ├── data_service.py     # Thread-safe cache with stale-while-revalidate & single-flight
│   │       └── review_service.py   # Dataset-level aggregates and LRU review memoisation
│   └── tests/
│       ├── conftest.py             # Deterministic test fixtures and mock market data store
│       ├── api/
│       │   └── test_api.py         # HTTP contract tests for all /api/v1 and /api routes
│       └── unit/
│           ├── domain/             # Unit tests for metrics, review, evolution, vintage
│           ├── integrations/       # Elexon HTTP client, FUELHH and WINDFOR parser tests
│           └── services/           # Cache, snapshot fallback, and concurrency tests
│
└── frontend/
    ├── package.json                # React 18, Vite, Tailwind CSS v4, Recharts
    ├── vite.config.ts              # Proxy configuration forwarding /api to port 8000
    ├── index.html                  # HTML entry point with modern typography
    └── src/
        ├── main.tsx                # React DOM mount point
        ├── App.tsx                 # Dashboard layout, state orchestration, parallel data fetching
        ├── types.ts                # TypeScript interfaces (Review, Evolution, Meta, KPIs)
        ├── format.ts               # GW/MW formatters, date/time and timezone helpers
        ├── styles.css              # Custom styling tokens and design system utilities
        ├── api/
        │   ├── client.ts           # Axios HTTP client instance
        │   ├── endpoints.ts        # fetchMeta, fetchReview, fetchEvolution, getExportReviewCsvUrl
        │   └── index.ts            # Public API exports
        └── components/
            ├── Header.tsx          # Navigation bar with live streaming status indicator
            ├── Controls.tsx        # Delivery date, decision gate, horizon selectors & CSV export
            ├── Kpis.tsx            # Peak, average, MAE, RMSE, nMAE, and bias KPI metric cards
            ├── ForecastChart.tsx   # Intraday delivery chart with settlement periods (SP 1–48)
            ├── ForecastEvolution.tsx # Run-to-run forecast revision delta (emerald/rose bars & runs)
            ├── HorizonTable.tsx    # Accuracy breakdown by lead-time horizon (0–6h, 6–12h, 12–24h, 24–48h)
            ├── DailyChart.tsx      # Daily historical MAE distribution bar chart
            └── PlanningPanel.tsx   # Conservative P90 wind baseline for thermal sizing
```

---

## Local Development & Setup

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```
* **API Server:** http://localhost:8000
* **Interactive OpenAPI Docs:** http://localhost:8000/api/docs

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```
* **Web Application:** http://localhost:5173 (automatically proxies `/api` calls to port 8000)

### 3. Running the Test Suite

```bash
cd backend
pytest
```
*Alternatively, from the project root:*
```bash
pytest
```

---

## Containerization & Deployment

### Production Docker Container

```bash
docker build -t windwatch .
docker run --rm -p 8000:8000 windwatch
```
Open **http://localhost:8000** in your browser.

### CI/CD Pipeline (Docker Hub & GCP VM Deployment)

The repository includes an automated GitHub Actions workflow (`.github/workflows/deploy.yml`):
1. **Tests:** Executes frontend build (`npm run build`) and backend tests (`pytest`).
2. **Build & Push:** Builds multi-stage production Docker image and pushes to **Docker Hub**.
3. **Automated VM Deployment:** Connects via SSH to the GCP VM (`34.131.148.108`), pulls the updated container, and relaunches the service on port 8000.

#### Required GitHub Secrets
Configure the following in GitHub (**Settings > Secrets and variables > Actions > Secrets**):
* `DOCKERHUB_USERNAME`: Your Docker Hub username.
* `DOCKERHUB_TOKEN`: Docker Hub Personal Access Token (or password).
* `VM_HOST`: `34.131.148.108` (VM Public IP).
* `VM_USER`: `tanw9`.
* `VM_SSH_KEY`: Content of your private SSH key (`id_ed25519`).

---

## Development & Engineering

Developed with the assistance of Google Antigravity. All code, domain models, decision logic, and test suites were reviewed and tested by Tanwir.
