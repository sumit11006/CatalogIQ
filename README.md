<div align="center">

# 💎 CatalogIQ

### **Autonomous Industrial Product Intelligence & Catalog Enrichment Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4.5-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Challenge](https://img.shields.io/badge/Built%20for-UniHack%20Challenge-FF6F61.svg)](#-what-catalogiq-solves)

*Transform cryptic, abbreviated industrial catalog rows into standardized, delivery-ready product records across a 252-column schema — featuring deterministic rules, automated quality scoring, field-level provenance, and human-in-the-loop review.*

[Key Features](#-key-features) • [Architecture](#-system-architecture) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Deployment](#-deployment-options) • [Content Standards](#-content-standard--rules-engine)

---

</div>

## 🏆 What CatalogIQ Solves

Industrial distributors receive millions of messy, unstructured product records from manufacturers that are unsearchable and commerce-unready:

```
Raw Input: "DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc", E1_Brand: "-- Unbranded --", Part_Manuf: "Freud Inc (2435)"
```

### The Problem
- **Cryptic Part Numbers & Abbreviations**: Missing titles, cryptic trade jargon (`CPLG`, `BRS`, `SS`), and missing units.
- **Placeholder Leakage**: Brand columns filled with empty placeholders (`-- Unbranded --`, `-- No DIB Brand --`, `None`).
- **Inconsistent Manufacturer Naming**: Legal suffixes, codes, and capitalization are scrambled (`Freud Inc (2435)` vs `FREUD`).
- **Multi-Channel Description Demands**: Distributors need specific formats for till invoices (≤40 chars ALL CAPS), mobile apps (60–80 chars), ecommerce PDP titles (≤120 chars), and long marketing copy.
- **Manual Overhead**: Content teams spend weeks researching spec sheets and hand-formatting 50+ attributes and 252 columns per item.

### The CatalogIQ Solution
CatalogIQ automates this entire pipeline. In one click, **raw supplier records are converted into complete, verified product records** adhering strictly to Unilog content standards and mapped directly into the **252-column delivery schema**.

---

## 📊 Before vs. After: End-to-End Transformation

| Dimension | Raw Input | CatalogIQ Enriched Record | Compliance Standard |
|---|---|---|---|
| **Product Title** | `DCB518ASTS06G` / `Part_Desc` | **Diablo DCB518ASTS06G 1/2 in x 18 in Sanding Belt 6-Pack** | ≤120 chars, Brand + MPN + Type + Spec |
| **Invoice Desc** | `""` | `SANDING BELT 1/2X18 6PK` | ≤40 chars, ALL CAPS, word-boundary trim |
| **Mobile Desc** | `""` | `Diablo 1/2 in x 18 in Sanding Belt, Cubitron II, 6/Pack` | 60–80 chars concise mobile PDP view |
| **Long Description** | `""` | Full sentence description with normalized dimensions, fractions, and key features | Grammatical sentence with fractions & approved units |
| **Brand Resolution** | `-- Unbranded --` | **Diablo** *(extracted from text & manufacturer hierarchy)* | Canonical brand name, symbol-aware |
| **Manufacturer** | `Freud Inc (2435)` | **Freud Inc.** *(Code: `2435` preserved in provenance)* | Legal suffix normalization (Inc, LLC, Ltd) |
| **Taxonomy** | `None` | `Tools > Power Tool Accessories > Sanding Belts` *(UNSPSC: `31191500`)* | Exact 3-level depth classpath |
| **Dimensions & UOM** | `1/2"x18"` | `Width: 1/2 in`, `Length: 18 in`, `Quantity: 6 pk` | Approved unit abbreviation + number spacing |
| **Quality Score** | `0 / 100` | **95.2 / 100** | 11 automated compliance checks |
| **Traceability** | Untracked | `AI draft + house rule enforcement (Confidence: 96%)` | Field-by-field audit provenance |

---

## ⚙️ System Architecture

CatalogIQ uses a robust **Two-Layer Architecture**: combining creative generative AI for fuzzy understanding with a deterministic rules engine for hard mathematical constraints.

```
                    ┌──────────────────────────────────────────────┐
                    │            CSV Upload / Demo Run             │
                    │   (Mfg_Part_Num, Part_Desc, Brands, Manuf)   │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │      Cleansing & Normalization Engine        │
                    │  • Strips placeholder strings (-- Unbranded) │
                    │  • Extracts manufacturer legal entity & code │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │       Layer 1: AI Enrichment (Gemini)        │
                    │  • Batched async execution (8 rows/call)     │
                    │  • Taxonomy classification (3 levels deep)   │
                    │  • Brand resolution from cryptic context     │
                    │  • 5-variant description drafting            │
                    │  • Multi-attribute triplet extraction        │
                    │  • Offline deterministic fallback engine     │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │      Layer 2: Deterministic Rules Engine     │
                    │  • Invoice char limit (≤40) & CAPS guarantee │
                    │  • Mobile desc length window (60–80 chars)   │
                    │  • Approved UOM enforcement (in, ft, mm, K)  │
                    │  • Decimal-to-fraction converter (50.25→50¼) │
                    │  • Trade abbreviation expansion (SS→Steel)   │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Quality & Compliance Engine         │
                    │  • 11 rigorous content-standard validations  │
                    │  • Computes 0–100 quality score per record   │
                    │  • Full provenance tracking (AI/Rule/Human)  │
                    └──────────────────────┬───────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        │                                     │
           [Score ≥ 80% & High Confidence]       [Score < 80% or Low Confidence]
                        │                                     │
                        ▼                                     ▼
             ┌─────────────────────┐              ┌────────────────────────┐
             │   Export Ready      │              │ Human-in-the-Loop Queue│
             │ Exact 252-Col CSV   │◄─────────────┤ Analyst review/approve │
             └─────────────────────┘              └────────────────────────┘
```

---

## ✨ Key Features

### 1. Multi-Format Description Builder
Generates 5 distinct description formats required by distributor ERP and eCommerce platforms from a single raw line:
- **Product Title**: Concise, searchable PDP title (`<Brand> <MPN> <Item Type> <Differentiators>`, ≤120 chars).
- **Invoice Description**: Telegraphic, uppercase, word-boundary truncated (≤40 chars, ALL CAPS).
- **Mobile Description**: Streamlined for smartphone viewport (60–80 chars).
- **Short Description**: Feature-led summary (≤160 chars).
- **Long Description**: Comprehensive prose containing dimensions, materials, and quantities.
- **PDP Marketing Copy**: Persuasive copy designed for product detail pages.

### 2. Strict Content Standard & Unit Normalization
- **Approved UOM Standards**: Standardizes 27+ measurement families (`in`, `ft`, `mm`, `cm`, `m`, `V`, `A`, `W`, `kW`, `dBA`, `lb`, `kg`, `oz`, `ga`, `qt`, `psi`, `rpm`, `hp`, `°F`, `°C`, `pc`, `pk`, `pr`, `cfm`, `lm`, `K`). Enforces strict spacing (`24 in`, never `24in`).
- **Decimal-to-Fraction Engine**: Automatically translates decimal manufacturer dimensions to industry-standard fractional inches (`50.25 in` → `50-1/4 in`, `8.5 in` → `8-1/2 in`).
- **Abbreviation Expansion**: Expands trade shorthand while protecting part model numbers (`SS` → Stainless Steel, `WH` → White, `GALV` → Galvanized, `CPLG` → Coupling).

### 3. Traceability & Field-Level Provenance Audit
Every single enriched attribute stores an immutable provenance record:
```json
{
  "product_name": {
    "source": "ai",
    "method": "Gemini 2.0 Flash generation",
    "confidence": 0.94,
    "reasoning": "Detected Diablo brand, extracted dimensions 1/2 in x 18 in and 6-pack packaging from part description."
  },
  "invoice_desc": {
    "source": "rule",
    "method": "AI draft + house char-limit/caps enforcement",
    "confidence": 0.95
  }
}
```
When an analyst overrides or approves a field in the HITL queue, provenance updates to `"human"` with reviewer timestamp and notes.

### 4. 11 Automated Quality & Compliance Checks
Every record is validated against 11 strict content standards:
1. `TITLE`: Product title present and non-empty.
2. `TITLE_LEN`: Product title length within ≤120 chars.
3. `INVOICE`: Invoice description present.
4. `INV_LIMIT`: Invoice description within ≤40 chars.
5. `INV_CAPS`: Invoice description strictly uppercase.
6. `MOBILE_RANGE`: Mobile description within target window (60–80 chars ± 10 chars tolerance).
7. `LONG`: Long description present and substantive.
8. `ATTR_COUNT`: At least 3 structured attributes extracted.
9. `UOM`: 100% of units match the approved abbreviation set.
10. `CLASSPATH`: Classification hierarchy strictly 3 levels deep (`Dept > Class > Fine`).
11. `NO_PLACEHOLDER`: Zero placeholder leakage into enriched copy.

### 5. Human-in-the-Loop (HITL) Validation Queue
Proposals with AI confidence < 65% or failed critical quality checks are routed to the interactive Validation Queue. Analysts can review side-by-side diffs, view the AI's reasoning, and approve or reject proposals with a single click.

### 6. Exact 252-Column Delivery CSV Export
Exports data conforming column-for-column to the Unilog UniHack delivery format specification (headers, passthrough columns, 20 item feature slots, and 50 attribute triplets).

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **Google Gemini API Key** (optional — offline deterministic fallback operates automatically if key is absent)

### 1. Clone the Repository
```bash
git clone https://github.com/sumit11006/CatalogIQ.git
cd CatalogIQ
```

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux

# Set your Gemini API key in .env (Optional):
# GEMINI_API_KEY=your_gemini_api_key_here

# Start FastAPI server
uvicorn app.main:app --port 8000 --reload
```
*The SQLite database is automatically initialized at `backend/data/product_intelligence.db` on startup.*

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open **http://localhost:5173** in your browser.

> **Single-Port Production Mode**: Run `npm run build` inside `frontend/`. FastAPI will automatically serve both the API and the React SPA from **http://localhost:8000**!

---

## ⚡ 60-Second Demo Walkthrough

1. **Dashboard**: Check the **Gemini Engine** status chip (*Live* in green or *Fallback* in amber).
2. **Pipeline Runs**: Click **"Sample 12 rows"** or drop an industrial catalog CSV file.
3. **Live Progress**: Watch batches process in real time with the live polling progress bar.
4. **Catalog Detail Drawer**: Click any enriched row to explore:
   - **Record Tab**: All 5 description variants with real-time character counters.
   - **Attributes Tab**: Extracted triplets with approved UOM badges.
   - **Traceability Tab**: Field-level provenance cards showing source, confidence, and reasoning.
   - **Quality Tab**: Pass/fail breakdown across all 11 compliance checks.
5. **Validation Queue**: Review low-confidence items, inspect the AI rationale, and approve or reject.
6. **Export**: Preview row completeness percentages and download the **252-column delivery CSV**.

---

## 📡 API Reference

Interactive OpenAPI documentation is available at **http://localhost:8000/docs**.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status and version |
| `GET` | `/api/v1/analytics` | Dashboard KPIs, category distribution, and engine mode |
| `POST` | `/api/v1/runs/upload?limit=N` | Upload catalog CSV and start enrichment pipeline |
| `POST` | `/api/v1/runs/sample?limit=N` | Execute demo run from bundled dataset |
| `GET` | `/api/v1/runs` | List all pipeline runs with summary statistics |
| `GET` | `/api/v1/runs/{run_id}` | Detailed progress, counts, and status of a run |
| `GET` | `/api/v1/items?run_id=&q=&status=&page=` | Search, filter, and paginate enriched catalog items |
| `GET` | `/api/v1/items/{item_id}` | Full product intelligence record with provenance |
| `PATCH`| `/api/v1/items/{item_id}` | Manual field override (stamps provenance as human) |
| `POST` | `/api/v1/items/{item_id}/accept` | Accept record as-is and resolve queue items |
| `GET` | `/api/v1/validation/queue?status=` | Fetch HITL validation queue |
| `POST` | `/api/v1/validation/{id}/action` | Approve or reject proposed field value |
| `GET` | `/api/v1/export/template` | Retrieve delivery header schema definition |
| `GET` | `/api/v1/export/preview?run_id=` | Completion percentage preview against 252 columns |
| `GET` | `/api/v1/export/csv?run_id=` | Download full 252-column delivery CSV |

---

## 🧪 Testing

CatalogIQ includes a comprehensive test suite verifying API routes, rules engine operations, and export integrity:

```bash
cd backend
pytest -v
```

---

## 🚢 Deployment Options

### Option A: Render (Single Service — Recommended)
FastAPI serves the REST API and the built React frontend from a single container:
1. Push repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com), click **New → Blueprint** and select your repository.
3. Add `GEMINI_API_KEY` under Environment Variables.
4. Click **Deploy**. Your demo is live at `https://catalogiq-xxxx.onrender.com`.

### Option B: Docker Container
```bash
cd backend
docker build -t catalogiq-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key catalogiq-backend
```

---

## 📁 Repository Structure

```
CatalogIQ/
├── backend/
│   ├── app/
│   │   ├── assets/                 # Delivery template CSV & sample dataset
│   │   ├── models/catalog.py       # SQLAlchemy ORM models (PipelineRun, CatalogItem, ValidationItem)
│   │   ├── routers/                # REST API routes (runs, items, validation, export, analytics)
│   │   ├── services/
│   │   │   ├── enrichment_ai.py    # Batched Gemini AI service & offline fallback
│   │   │   ├── rules_engine.py     # Deterministic UOM, abbreviation & fraction engine
│   │   │   ├── quality_engine.py   # 11 compliance checks & HITL routing
│   │   │   ├── pipeline.py         # Async batch orchestrator & provenance capture
│   │   │   └── exporter.py         # 252-column delivery CSV writer
│   │   ├── utils/                  # Structured logger & image utilities
│   │   ├── config.py               # Pydantic environment configuration
│   │   ├── database.py             # Async SQLite engine & session management
│   │   └── main.py                 # FastAPI application & SPA static router
│   ├── alembic/                    # Database migration scripts
│   ├── tests/                      # Automated test suite (pytest + httpx)
│   ├── requirements.txt            # Python dependencies
│   └── Dockerfile                  # Lightweight backend container configuration
├── frontend/
│   ├── src/
│   │   ├── api/client.ts           # Axios client with request tracing
│   │   ├── components/             # Reusable UI primitives, cards, and motion helpers
│   │   ├── hooks/useCatalog.ts     # TanStack Query hooks with live polling
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx   # KPI cards, charts, and system status
│   │   │   ├── RunsPage.tsx        # CSV drag-and-drop & pipeline progress
│   │   │   ├── CatalogPage.tsx     # Filterable catalog table & detail drawer
│   │   │   ├── ValidationPage.tsx  # HITL review queue with diff viewer
│   │   │   └── ExportPage.tsx      # Schema preview & 252-col CSV download
│   │   ├── types/catalog.ts        # TypeScript data definitions
│   │   └── styles/index.css        # Rose gold & onyx design system
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── Resources/                      # UniHack specification guide & ground-truth data
├── render.yaml                     # Render.com blueprint deployment configuration
└── README.md
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<div align="center">
Built for <b>UniHack</b> • Powered by <b>FastAPI</b>, <b>React</b> & <b>Google Gemini</b>
</div>
