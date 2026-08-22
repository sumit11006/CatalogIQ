# CatalogIQ

> **AI-Powered Product Intelligence & Catalog Enrichment Platform**
>
> Turn messy, incomplete catalog rows into complete, standardized, commerce-ready product records — with full traceability, quality scoring, and human-in-the-loop validation.

**Built for UniHack** · FastAPI + React + Google Gemini

---

## 🏆 What This Platform Solves

Industrial distributors receive product catalogs that look like this:

| Raw Input | The Problem |
|---|---|
| `DCB518ASTS06G` / `"DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc"` | Cryptic part number + abbreviated description |
| `E1_Brand: -- Unbranded --` | Brand fields are placeholders, not data |
| `Part_Manuf: Freud Inc (2435)` | Inconsistent manufacturer naming |

A human content team would manually research each row and write: title, invoice description (≤40 chars, ALL CAPS), mobile description (60–80 chars), long description, marketing copy, extract 5–50 attributes with normalized units, classify it into a taxonomy… **for every single row.**

CatalogIQ automates this entire pipeline. One click turns 1,000 raw rows into delivery-ready records across the **full 252-column output schema**, with every generated field scored for quality and traceable to its source.

### Mapped to the UniHack Expected Outcomes

| Challenge Outcome | How CatalogIQ Delivers |
|---|---|
| **Generate structured intelligence from limited inputs** | Batched Gemini AI calls transform 6 sparse columns into classification, brand resolution, 7 description fields, up to 20 features, and 50 attribute triplets per row |
| **Improve data quality & consistency** | Deterministic rules engine enforces house style: char limits, approved unit abbreviations (`24 in`, never `24in`), decimal→fraction conversion (`50.25 in` → `50-1/4 in`), placeholder stripping, abbreviation expansion (`SS` → Stainless Steel) |
| **Validate & enrich with traceable outputs** | Every field stores provenance — source (`input`/`rule`/`AI`/`human`), method, confidence score, and the AI's reasoning. 11 compliance checks produce a 0–100 quality score per record |
| **Scale efficiently** | Bounded-concurrency async pipeline (8 rows/AI-call × 3 parallel calls ≈ 24 rows in flight), live progress tracking, cost-controlling row limits |
| **Human-in-the-loop** | Low-confidence or failed-check fields land in a validation queue; one-click approve writes back to the live record |

---

## ⚙️ How It Works

```
                        ┌──────────────────────────────┐
   CSV Upload ────────► │  Parse & Clean               │
   (or demo button)     │  placeholders stripped,      │
                        │  manufacturer codes parsed   │
                        └──────────────┬───────────────┘
                                       ▼
                        ┌──────────────────────────────┐
                        │  AI Enrichment (Gemini)      │
                        │  batches of 8 rows × 3       │
                        │  concurrent calls            │
                        └──┬──────────┬──────────┬────┘
                           ▼          ▼          ▼
                    Classification  Description  Attribute
                    Dept/Class/     Builder      Extractor
                    Fine/Classpath  5 formats +  label·value·UOM
                    UNSPSC          marketing    triplets
                           └──────────┬──────────┘
                                      ▼
                        ┌──────────────────────────────┐
                        │  Rules Engine (post-process) │
                        │  char limits enforced, UOM   │
                        │  normalized, decimals→fractions│
                        └──────────────┬───────────────┘
                                       ▼
                          ┌────────────────────────┐
                          │  Quality Engine        │
                          │  11 checks → 0-100     │
                          └───────┬─────────┬──────┘
                                  │         │
                     passes ──────┘         └────── fails/low-confidence
                         ▼                              ▼
              ┌──────────────────┐         ┌──────────────────────────┐
              │  Ready to Export │         │  Human Validation Queue  │
              │                  │         │  approve → write-back +  │
              │  252-column CSV  │◄────────  provenance = "human"    │
              └──────────────────┘         └──────────────────────────┘
```

### The Two-Layer Design

**Layer 1 — AI (creative, fuzzy):** Gemini handles what requires understanding — detecting that `"Diablo"` is the brand hidden inside a description, classifying a sanding belt into the right taxonomy branch, writing persuasive marketing copy.

**Layer 2 — Rules Engine (deterministic, exact):** Post-processing enforces what must be precise — hard character limits, approved unit abbreviations, fraction conversions. The AI drafts; the rules engine guarantees format compliance. If the API key is missing or blocked, Layer 1 falls back to rules-only mode so the platform never breaks.

### Traceability Model

Every enriched field carries a provenance record:

```json
{
  "invoice_desc": {
    "source": "rule",
    "method": "AI draft + house char-limit/caps enforcement",
    "confidence": 0.95,
    "reasoning": "Extracted item type and dimensions from abbreviated description..."
  }
}
```

Approve a field through the validation queue and its provenance re-stamps as `"human"` — a complete audit trail from raw input to published value.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/) — optional; the platform runs without it)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements-light.txt google-genai

copy .env.example .env           # then add your key:
# GEMINI_API_KEY=your_key_here
# GEMINI_MODEL=gemini-flash-lite-latest

uvicorn app.main:app --port 8000 --reload
```

The SQLite database auto-creates at `backend/data/product_intelligence.db` on first start.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

> Prefer ONE URL? Run `npm run build` in `frontend/`, then just start the backend —
> FastAPI automatically serves the built app at **http://localhost:8000** (SPA fallback included).

### 60-Second Demo

1. Open the dashboard — check the **Gemini Engine** chip says *Live* (green) or *Fallback* (amber)
2. Go to **Pipeline Runs** → click **"Sample 12 rows"**
3. Watch progress fill in real time (~15–40s depending on AI mode)
4. Click **"Open catalog"** on the completed run
5. Click any row → explore the detail drawer: descriptions tab, attributes tab, **traceability tab** (field-level provenance), quality tab
6. Visit **Validation Queue** → approve/reject low-confidence proposals
7. Go to **Export** → preview completion % → download the 252-column CSV

---

## 📖 Using the Platform

### Pipeline Runs Page

| Control | What It Does |
|---|---|
| Drop zone | Upload your catalog CSV (expects `Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf`) |
| Row limit | Cap how many rows process — controls API cost on large files |
| Sample buttons | Run bundled UniHack dataset rows without uploading anything |
| Progress bar | Live polling shows rows processed as the AI works through batches |

### Catalog Page

- **Search** across part numbers, brands, titles, raw descriptions
- **Filter tabs**: all / enriched / needs review / pending / failed
- Click any row for the detail drawer with four tabs:
  - **Record** — all description formats side by side with live char counts
  - **Attributes** — extracted triplets with approved-unit badges
  - **Traceability** — per-field provenance cards showing source pill (AI/Rule/Input/Human), confidence bar, method, and the AI's reasoning
  - **Quality** — pass/fail against all 11 content-standard checks plus raw-input comparison

### Validation Queue (HITL)

Items appear here when AI confidence < 65%, when critical quality checks fail, or when the AI itself flags uncertainty. Each card shows current vs. proposed values, confidence, and expandable AI rationale. **Approve** writes the value into the live record and stamps provenance as human-verified; **Reject** dismisses it.

### Export Page

- Select a run (or export everything)
- Preview per-row completion percentage against all 252 columns
- Download the CSV in **exact UniHack delivery schema** — column-for-column identical header order, ready for scoring

---

## 📡 API Reference

Base URL: `http://localhost:8000/api/v1` · Interactive docs at `/docs`

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/runs/upload?limit=N` | Upload catalog CSV, starts enrichment run |
| `POST` | `/runs/sample?limit=N` | Demo run from bundled dataset |
| `GET` | `/runs` · `/runs/{id}` | Run list / live progress detail |
| `GET` | `/items?run_id&q&status&page` | Search/filter enriched catalog |
| `GET` | `/items/{id}` | Full record + provenance + quality checks |
| `PATCH` | `/items/{id}` | Manual field override (provenance = human) |
| `GET` | `/validation/queue?status=` | HITL queue (lowest confidence first) |
| `POST` | `/validation/{id}/action` | `{action: "approve"\|"reject"}` |
| `GET` | `/export/csv?run_id=` | Download 252-column delivery CSV |
| `GET` | `/export/preview?run_id=` | Per-row completion percentages |
| `GET` | `/analytics` | Dashboard KPIs |

### Example: End-to-End via API

```bash
# Start a run
curl -X POST "http://localhost:8000/api/v1/runs/sample?limit=12"

# Check progress
curl "http://localhost:8000/api/v1/runs/{run_id}"

# Download results
curl -OJ "http://localhost:8000/api/v1/export/csv?run_id={run_id}"
```

---

## 🧱 Architecture

```
frontend/           React 18 · TypeScript · Tailwind · TanStack Query
                    Recharts · Framer Motion · Lucide
    │
    ▼  REST (axios)
backend/app/
    ├── main.py                 FastAPI app, CORS, gzip, lifespan
    ├── routers/
    │   ├── runs.py             upload · sample · progress · items CRUD
    │   ├── validation.py       HITL queue + approve/reject actions
    │   ├── export.py           252-column CSV writer + previews
    │   └── analytics.py        dashboard aggregation
    ├── services/
    │   ├── enrichment_ai.py    batched Gemini calls + offline fallback
    │   ├── rules_engine.py     abbreviations · UOM standards · fractions
    │   ├── quality_engine.py   11 compliance checks · HITL escalation
    │   ├── pipeline.py         async orchestrator + provenance capture
    │   └── exporter.py         exact-schema delivery writer
    ├── models/catalog.py       PipelineRun · CatalogItem · ValidationItem
    └── assets/                 delivery template + sample dataset
    │
    ▼
SQLite (async, aiosqlite)      zero-config persistence
```

### Quality Checks (per record)

Product title present & ≤120 chars · Invoice desc ≤40 chars CAPS · Mobile desc within 60–80 chars · Long description present · ≥3 attributes extracted · All UOMs from approved set · Classpath exactly 3 levels deep · No placeholder leakage

### Graceful Degradation

| Scenario | Behavior |
|---|---|
| No API key configured | Rules-based enrichment (abbreviation expansion, template assembly) — lower quality scores but fully functional |
| API key rate-limited mid-run | Automatic model cascade retry, then per-batch fallback |
| Key blocked (leaked/reported) | Same as no key — platform stays usable, dashboard shows *Fallback* status |

---

## 🚢 Free Deployment (for demos)

The whole platform deploys as **one free web service** on [Render](https://render.com) — FastAPI serves both the API and the built React app from a single URL. No CORS setup, no separate frontend hosting.

### Option A — Render (recommended, 1 service)

1. Push this repo to GitHub
2. Render Dashboard → **New → Blueprint** → select the repo (auto-reads `render.yaml`)
3. In the service's **Environment** tab, add `GEMINI_API_KEY`
4. Deploy → your demo lives at `https://catalogiq-xxxx.onrender.com`

`render.yaml` handles everything: installs Python deps, builds the frontend, starts uvicorn on `$PORT`, health check at `/health`.

**Free-tier caveats:**
- Cold start: first request after ~15 min idle takes ~30–60 s to wake
- Ephemeral disk: uploaded data resets on redeploys (fine for a live demo — re-upload your CSV or hit "Sample run")

### Option B — Vercel (instant frontend) + Render (backend) + keep-alive

Best of both: **zero UI cold starts** via Vercel, and a free GitHub Action that pings the Render API every 10 minutes so it never sleeps — even mid-demo.

> **Why not the whole app on Vercel?** Vercel serverless functions time out at 10–60s (the enrichment pipeline runs longer batches) and their filesystem is ephemeral, so SQLite can't persist. The frontend is perfect for Vercel; the backend needs a real always-on process.

| Piece | Host | Setting |
|---|---|---|
| Frontend | Vercel (free) | root dir `frontend/`, framework: Vite (auto). Edit `frontend/vercel.json` → replace `YOUR-RENDER-APP` with your Render app name — this proxies `/api/*` and `/health` to Render, so no CORS or URL config needed |
| Backend | Render web service (free) | Blueprint (`render.yaml`) or manual: root dir `backend/`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, env: `GEMINI_API_KEY` |
| Keep-alive | GitHub Actions (free, included) | `.github/workflows/keep-alive.yml` already in repo — after your first deploy, add repo secret `BACKEND_URL = https://<your-render-app>.onrender.com`. It pings `/health` every 10 min |

**Setup order:** deploy backend on Render first → copy its URL → set it in `frontend/vercel.json` → push → import frontend on Vercel → add `BACKEND_URL` secret on GitHub → done. Demo loads instantly from Vercel's CDN; the API stays warm around the clock.

> ⚠️ Never put your Gemini key in the repo — set it in the host's environment variables.

---

## 📱 Mobile & Tablets

The UI is fully responsive:
- **< 1024px**: hamburger menu with animated slide-in sidebar, sticky top bar
- Tables scroll horizontally; stat cards reflow (5 → 3 → 2 columns)
- Item drawer and validation cards go full-width
- Works on any modern phone browser — open the deployed URL on your phone during the demo

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query v5, Recharts, Framer Motion, Lucide icons |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2 (async), aiosqlite, structlog |
| AI | Google Gemini (`google-genai` SDK) with multi-model cascade fallback |
| Storage | SQLite (zero-config, file-based) |

---

## 📁 Project Layout

```
catalog-iq/
├── backend/
│   ├── app/
│   │   ├── models/catalog.py       # data models
│   │   ├── routers/                # REST endpoints
│   │   ├── services/               # AI, rules, quality, pipeline, export
│   │   ├── assets/                 # delivery schema template + sample CSV
│   │   └── config.py               # env-driven settings
│   ├── data/                       # auto-created SQLite DB
│   └── .env                        # GEMINI_API_KEY (never commit)
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Dashboard · Runs · Catalog · Validation · Export
│   │   ├── components/             # Layout, UI primitives, motion helpers
│   │   ├── hooks/useCatalog.ts     # React Query hooks w/ live polling
│   │   └── types/catalog.ts
│   └── package.json
├── Resources/                      # UniHack challenge pack
└── README.md
```

## 🔐 Security Notes

- `backend/.env` is gitignored — never commit API keys
- Google auto-disables keys found in public repos ("reported as leaked"); if you see `403 PERMISSION_DENIED`, generate a fresh key
- All CORS origins are open for local development only — restrict before deploying

---

Built with ☕ and rose gold for **UniHack**.
