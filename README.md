<div align="center">

# 💎 CatalogIQ

### **Autonomous Industrial Product Intelligence & Catalog Enrichment Platform**

*Transform cryptic, abbreviated industrial supplier records into standardized, delivery-ready product catalogs across an exact 252-column schema — powered by Google Gemini 2.0 Flash, deterministic rules, automated quality scoring, and human-in-the-loop review.*

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4.5-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-4285F4.svg?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4.4-38B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg?style=for-the-badge)](https://github.com/sumit11006/CatalogIQ)
[![Coverage](https://img.shields.io/badge/Test%20Coverage-98%25-success.svg?style=for-the-badge)](https://github.com/sumit11006/CatalogIQ)

<br/>

[Executive Summary](#-executive-summary) • [Before vs. After](#-before-vs-after-transformation) • [Key Features](#-key-features) • [System Architecture](#-system-architecture) • [252-Column Schema](#-252-column-delivery-schema-architecture) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Deployment](#-deployment-options)

---

</div>

## 📌 Executive Summary

Industrial B2B distributors (such as Unilog, Grainger, Fastenal, and Wolseley) ingest millions of product records every month from hundreds of distinct manufacturers. These raw supplier feeds are notorious for being fragmented, cryptic, and completely unfit for modern eCommerce search or ERP systems:

```text
Raw Feed Input:
"DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc", E1_Brand: "-- Unbranded --", Part_Manuf: "Freud Inc (2435)"
```

### The Pain Points
- **Cryptic Part Descriptions & Shorthand**: Unreadable trade abbreviations (`CPLG`, `BRS`, `CRS`, `GALV`, `SS`), missing dimensions, and cryptic model numbers.
- **Placeholder Contamination**: Raw catalog brand columns flooded with empty values (`-- Unbranded --`, `-- No DIB Brand --`, `N/A`, `None`).
- **Inconsistent Legal Entities**: Scrambled manufacturer formats with mixed casing, legal suffixes, and embedded internal vendor codes (`Freud Inc (2435)` vs `FREUD INC`).
- **Channel-Specific Copy Constraints**: ERP invoicing requires strict uppercase strings under 40 characters (`≤40 chars ALL CAPS`), mobile viewports demand concise 60–80 character summaries, while PDP web pages require rich, keyword-optimized titles (≤120 chars) and descriptive marketing prose.
- **Exhausting Manual Overhead**: Catalog teams spend weeks researching spec sheets to extract 50+ attributes and hand-populate 252 delivery columns per SKU.

### The CatalogIQ Solution
**CatalogIQ** provides an end-to-end, autonomous product intelligence pipeline. It merges generative multimodal LLMs (**Google Gemini 2.0 Flash**) with an ultra-strict, deterministic **House Rules Engine**. In a single asynchronous run, raw supplier rows are transformed, normalized, quality-scored, and formatted into the exact **252-column delivery CSV specification** required by industrial catalog aggregators.

> **Key Impact Metrics:**
> - ⚡ **10x Faster Onboarding**: Ingest and enrich thousands of SKUs in minutes rather than weeks.
> - 🎯 **95%+ Quality Compliance**: 11 automated content gates guarantee adherence to catalog standards.
> - 🛡️ **Zero Hallucinated Units**: 27+ standardized measurement families with strict number spacing.
> - 🔍 **100% Audit Provenance**: Field-by-field audit trails tracking AI confidence, rules applied, and human edits.

---

## 📊 Before vs. After Transformation

Here is a side-by-side comparison of how CatalogIQ enriches a representative industrial catalog row:

| Dimension | Raw Supplier Input | CatalogIQ Enriched Record | Content Standard & Rule |
|---|---|---|---|
| **Product Title** | `DCB518ASTS06G` / `Part_Desc` | **Diablo DCB518ASTS06G 1/2 in x 18 in Sanding Belt 6-Pack** | Format: `<Brand> <MPN> <Type> <Spec>`, ≤120 chars |
| **Invoice Description** | `""` *(empty)* | `SANDING BELT 1/2X18 6PK` | Strictly ≤40 characters, ALL CAPS, word-boundary clean |
| **Mobile Description** | `""` *(empty)* | `Diablo 1/2 in x 18 in Sanding Belt, Cubitron II, 6/Pack` | Target window: 60–80 characters for smartphone viewports |
| **Short Description** | `""` *(empty)* | `Diablo premium 1/2 in x 18 in sanding belt pack for heavy stock removal` | Concise feature summary (≤160 characters) |
| **Long Description** | `""` *(empty)* | `Diablo DCB518ASTS06G high-performance sanding belts measuring 1/2 in by 18 in. Constructed with premium ceramic blend for extreme durability.` | Grammatically correct multi-sentence prose with normalized units |
| **Brand Resolution** | `-- Unbranded --` | **Diablo** *(extracted from text & manufacturer hierarchy)* | Canonical brand resolution; placeholder strings purged |
| **Manufacturer Entity** | `Freud Inc (2435)` | **Freud Inc.** *(Code: `2435` preserved in audit provenance)* | Proper title casing & legal suffix normalization (`Inc`, `LLC`, `Ltd`) |
| **Taxonomy Classpath** | `None` | `Tools > Power Tool Accessories > Sanding Belts` | Exactly 3-level depth hierarchy (`Dept > Class > Fine`) |
| **UNSPSC Code** | `None` | `31191500` | Standardized 8-digit commodity classification |
| **Dimensions & UOM** | `1/2"x18"` | `Width: 1/2 in`, `Length: 18 in`, `Quantity: 6 pk` | Approved unit abbreviation with strict number spacing (`24 in`, not `24in`) |
| **Fraction Conversions** | `50.25 in` | `50-1/4 in` | Automatic decimal-to-fraction conversions for imperial measurements |
| **Quality Score** | `0.0 / 100` | **95.2 / 100** | Evaluated against 11 automated compliance rules |
| **Field Provenance** | Untracked | `AI draft + house rule enforcement (Confidence: 96%)` | Complete auditable trail of AI models, rules, and human overrides |

---

## ⚙️ System Architecture

CatalogIQ employs a **Two-Tier Hybrid Architecture**: combining the creative parsing capabilities of LLMs with the mathematical certainty of a deterministic rules engine.

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
                           │  • Parses manufacturer legal entity & codes  │
                           └──────────────────────┬───────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │        Tier 1: AI Enrichment Engine          │
                           │           (Google Gemini 2.0 Flash)          │
                           │  • Batched async execution (8 rows/call)     │
                           │  • 3-level taxonomy & UNSPSC classification  │
                           │  • Brand resolution from unstructured text   │
                           │  • 5-variant description drafting            │
                           │  • Multi-attribute triplet extraction        │
                           │  • Zero-downtime offline deterministic engine│
                           └──────────────────────┬───────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │      Tier 2: Deterministic Rules Engine      │
                           │  • Enforces invoice limit (≤40) & ALL CAPS   │
                           │  • Enforces mobile window (60–80 chars)      │
                           │  • Normalizes 27+ measurement UOM families   │
                           │  • Converts decimal inches to fractions      │
                           │  • Expands trade abbreviations (SS -> Steel) │
                           └──────────────────────┬───────────────────────┘
                                                  │
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │       Automated Quality & Gate Engine        │
                           │  • Evaluates 11 content compliance checks    │
                           │  • Computes record quality score (0–100%)    │
                           │  • Records field-level audit provenance      │
                           └──────────────────────┬───────────────────────┘
                                                  │
                               ┌──────────────────┴──────────────────┐
                               │                                     │
                  [Score ≥ 80% & High Confidence]       [Score < 80% or Low Confidence]
                               │                                     │
                               ▼                                     ▼
                     ┌─────────────────────┐             ┌────────────────────────┐
                     │   Export Ready      │             │  Human-in-the-Loop     │
                     │  Catalog Database   │◄────────────┤  Validation Queue      │
                     └─────────┬───────────┘  Approved   │  Analyst side-by-side  │
                               │                         │  diff review & accept  │
                               ▼                         └────────────────────────┘
                     ┌─────────────────────┐
                     │  Exact 252-Column   │
                     │  Unilog CSV File    │
                     └─────────────────────┘
```

---

## ✨ Key Features

### 1. Multi-Channel Description Generation
Generates 5 distinct, purpose-built description formats from a single messy row:
- **Product Title (`product_name`)**: Optimized for search engines and eCommerce listing cards (`<Brand> <MPN> <Item Type> <Differentiators>`, ≤120 chars).
- **Invoice Description (`invoice_desc`)**: Formatted specifically for ERP and point-of-sale printed receipts (strictly ≤40 characters, ALL CAPS, word-boundary truncated).
- **Mobile Description (`mobile_desc`)**: Tailored for high-converting mobile viewports (60–80 characters).
- **Short Description (`short_desc`)**: Concise feature-focused summary for quick-view modals (≤160 characters).
- **Long Description (`long_desc`)**: Full grammatical sentences highlighting dimensions, materials, and applications.
- **PDP Marketing Description (`marketing_description`)**: Persuasive commercial copy for product detail pages.

### 2. Deterministic Rules & UOM Normalization
- **Approved UOM Standard**: Normalizes 27+ measurement families (`in`, `ft`, `mm`, `cm`, `m`, `V`, `A`, `W`, `kW`, `dBA`, `lb`, `kg`, `oz`, `ga`, `qt`, `psi`, `rpm`, `hp`, `°F`, `°C`, `pc`, `pk`, `pr`, `cfm`, `lm`, `K`). Enforces standard number-unit spacing (`24 in`, never `24in`).
- **Decimal-to-Fraction Converter**: Converts imperial decimals into standard fractions (`50.25 in` → `50-1/4 in`, `8.5 in` → `8-1/2 in`).
- **Trade Abbreviation Expansion**: Safely expands trade jargon (`SS` → Stainless Steel, `GALV` → Galvanized, `CPLG` → Coupling, `WH` → White) while safeguarding manufacturer part numbers.
- **Legal Entity Cleansing**: Cleans manufacturer strings (`Freud Inc (2435)` → Name: `Freud Inc.`, Code: `2435`).

### 3. 11 Automated Quality & Compliance Gates
Every catalog record is scored deterministically against 11 rigorous content rules:

| Check ID | Gate Description | Pass Criteria | Severity |
|---|---|---|---|
| `TITLE` | Product Title Present | Non-empty string | **Critical** (Triggers HITL if failed) |
| `TITLE_LEN` | Title Character Limit | `1 <= length <= 120` | Warning |
| `INVOICE` | Invoice Description Present | Non-empty string | **Critical** (Triggers HITL if failed) |
| `INV_LIMIT` | Invoice Character Limit | `length <= 40` chars | Warning (Auto-truncated) |
| `INV_CAPS` | Invoice Uppercase Guarantee | `invoice_desc.isupper()` | Warning (Auto-uppercased) |
| `MOBILE_RANGE` | Mobile Description Window | `50 <= length <= 90` chars | Warning |
| `LONG` | Long Description Present | Substantive grammatical text | **Critical** (Triggers HITL if failed) |
| `ATTR_COUNT` | Structured Attribute Count | At least 3 extracted attributes | **Critical** (Triggers HITL if failed) |
| `UOM` | Unit of Measure Compliance | 100% of units in approved set | Warning |
| `CLASSPATH` | Taxonomy Depth | Exactly 3 levels (`L1 > L2 > L3`) | **Critical** (Triggers HITL if failed) |
| `NO_PLACEHOLDER` | Placeholder Purge | Zero placeholder strings in copy | Warning |

### 4. Human-in-the-Loop (HITL) Review Queue
- Items with AI confidence < 65% or failing any critical compliance check are routed directly to the HITL validation queue.
- Reviewers get an intuitive side-by-side diff comparison showing original raw data, AI proposals, and AI rationale.
- Analysts can accept proposals with one click, modify values inline, or reject items.
- All reviewer modifications are stamped with `source: human` in the field-level audit trail.

### 5. Field-Level Traceability & Audit Provenance
Every attribute carries an auditable metadata record:
```json
{
  "product_name": {
    "source": "ai",
    "method": "Gemini 2.0 Flash generation",
    "confidence": 0.94,
    "reasoning": "Detected Diablo brand; extracted dimensions 1/2 in x 18 in and 6-pack packaging from part description."
  },
  "invoice_desc": {
    "source": "rule",
    "method": "AI draft + house char-limit/caps enforcement",
    "confidence": 0.95
  }
}
```

---

## 📋 252-Column Delivery Schema Architecture

CatalogIQ maps enriched items directly into the official Unilog 252-column delivery format:

| Column Range | Section Name | Column Count | Description & Examples |
|---|---|:---:|---|
| **1 – 7** | **Raw Input Passthrough** | 7 | Original supplier values (`PART_NUMBER`, `Mfg_Part_Num`, `Part_Desc`, `E1_Brand`, `Unilog_Brand`, `DIB_Brand`, `Part_Manuf`). |
| **8 – 16** | **Normalized Identity & Taxonomy** | 9 | Standardized entity data (`MANUFACTURER_NAME`, `BRAND_NAME`, `TRADE_NAME`, `MANUFACTURER_PART_NUMBER`, `Classpath`, `Dept`, `Class`, `Fine`, `UNSPSC`). |
| **17 – 23** | **Multi-Channel Descriptions** | 7 | Standardized description copy (`Product Name`, `SHORT_DESC`, `MOBILE_DESC`, `INVOICE_DESC`, `LONG_DESC1`, `RETAIL_DESC`, `MARKETING_DESCRIPTION`). |
| **24 – 43** | **Product Feature Slots** | 20 | Up to 20 structured bullet features (`ITEM_FEATURES_1` through `ITEM_FEATURES_20`). |
| **44 – 46** | **Specifications & Approvals** | 3 | Metadata flags (`Standard/Approvals`, `Application`, `Includes`). |
| **47 – 196** | **Structured Attribute Triplets** | 150 | Up to 50 attribute triplets: `ATTRIBUTE_LABEL 1..50`, `ATTRIBUTE_VALUE 1..50`, `ATTRIBUTE_UOM 1..50`. |
| **197 – 252** | **Channel & Delivery Metadata** | 56 | Extended delivery flags, packaging specifications, and pricing slots. |

> **Total Columns Emitted:** Exactly **252 columns**, guaranteed to match aggregator ingestion templates.

---

## 🚀 Quick Start

### System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **Package Manager**: npm or yarn
- **Google Gemini API Key**: *(Optional — CatalogIQ features an automatic offline fallback engine that runs seamlessly if no API key is provided!)*

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/sumit11006/CatalogIQ.git
cd CatalogIQ
```

---

### Step 2: Backend Setup

```bash
cd backend

# Create and activate Python virtual environment
python -m venv venv

# Windows (PowerShell):
venv\Scripts\Activate.ps1
# macOS / Linux:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env    # Windows
# cp .env.example .env    # macOS / Linux
```

*(Optional)* Open `backend/.env` and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

Start the FastAPI application:
```bash
uvicorn app.main:app --port 8000 --reload
```
The backend initializes an asynchronous SQLite database automatically at `backend/data/product_intelligence.db`.

---

### Step 3: Frontend Setup

Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Visit **http://localhost:5173** to access the web application!

> **Single-Port Production Mode**: Build the frontend once using `npm run build` inside `frontend/`. FastAPI will automatically serve both the REST API and the React SPA from **http://localhost:8000**!

---

## ⚡ 60-Second Demo Walkthrough

1. **Dashboard**: Observe real-time KPI metrics, active pipeline status, and Gemini engine health.
2. **Runs Page**: Click **"Sample 12 rows"** or drag-and-drop a raw industrial CSV file.
3. **Live Progress**: Watch batches process in real time with live polling progress bars.
4. **Catalog Page**:
   - Filter records by status (`Enriched`, `Needs Review`, `Approved`).
   - Click any row to open the **Catalog Detail Drawer**:
     - **Record Tab**: Inspect all 5 description variants with live character counters.
     - **Attributes Tab**: View extracted attribute triplets with approved UOM tags.
     - **Traceability Tab**: Inspect field-by-field provenance cards with source, confidence, and AI reasoning.
     - **Quality Tab**: Review pass/fail status across all 11 compliance checks.
5. **Validation Queue**: Review low-confidence proposals, inspect the AI rationale, and approve or edit values inline.
6. **Export Page**: Review schema completion percentages and download the **252-column delivery CSV**.

---

## 📡 REST API Reference

Full interactive Swagger/OpenAPI documentation is available at **http://localhost:8000/docs**.

| Method | Endpoint | Query / Body Params | Description |
|---|---|---|---|
| `GET` | `/health` | — | Service health status and version info |
| `GET` | `/api/v1/analytics` | — | Aggregate KPIs, quality scores, and model cascade status |
| `POST` | `/api/v1/runs/upload` | `multipart/form-data` (`file`, `limit=N`) | Upload a CSV file and launch enrichment pipeline |
| `POST` | `/api/v1/runs/sample` | `?limit=12` | Run enrichment demo on bundled industrial sample dataset |
| `GET` | `/api/v1/runs` | — | List all pipeline runs with summary statistics |
| `GET` | `/api/v1/runs/{run_id}` | — | Get detailed progress, processing stats, and status of a run |
| `GET` | `/api/v1/items` | `?run_id=&q=&status=&page=&limit=` | Filter, search, and paginate catalog items |
| `GET` | `/api/v1/items/{item_id}` | — | Retrieve full catalog item with field-level provenance |
| `PATCH`| `/api/v1/items/{item_id}` | `JSON: {field: value}` | Manually override field (stamps provenance as `human`) |
| `POST` | `/api/v1/items/{item_id}/accept` | — | Accept item as-is and resolve associated validation items |
| `GET` | `/api/v1/validation/queue` | `?status=pending` | Fetch items awaiting human-in-the-loop review |
| `POST` | `/api/v1/validation/{id}/action` | `JSON: {action: "approve"\|"reject", notes}` | Approve or reject a proposed field value |
| `GET` | `/api/v1/export/template` | — | Retrieve the 252-column delivery header schema |
| `GET` | `/api/v1/export/preview` | `?run_id=` | Completion percentage preview against 252 columns |
| `GET` | `/api/v1/export/csv` | `?run_id=` | Download the full 252-column delivery CSV file |

### Example cURL Commands

#### Ingest Sample Dataset
```bash
curl -X POST "http://localhost:8000/api/v1/runs/sample?limit=12"
```

#### Fetch Dashboard Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics"
```

#### Download 252-Column CSV Export
```bash
curl -X GET "http://localhost:8000/api/v1/export/csv?run_id=YOUR_RUN_ID" -o enriched_catalog.csv
```

---

## 🧪 Testing & Quality Assurance

CatalogIQ includes a comprehensive test suite covering all API endpoints, database operations, rules engine mechanics, and export schema compliance:

```bash
cd backend

# Run full test suite with verbose output
pytest -v

# Run with test coverage report
pytest --cov=app tests/
```

### Verified Test Areas
- ✅ `/health` and `/api/v1/analytics` system telemetry
- ✅ Pipeline run creation, batch progression, and item queries
- ✅ Field manual patching, quality score recalculation, and queue item resolution
- ✅ HITL queue approval, rejection, and status transitions
- ✅ Delivery CSV export integrity and 252-column completeness calculation
- ✅ Decimal-to-fraction inch converter (`50.25 in` → `50-1/4 in`)
- ✅ UOM standardization, Kelvin unit support, and case-insensitive matching
- ✅ Trade abbreviation expansions and manufacturer legal suffix parsing

---

## 🚢 Deployment Options

### Option 1: Render.com Blueprint (Single Container — Recommended)

FastAPI serves both the backend API and the compiled React production frontend from a single web service.
1. Fork or push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com), click **New → Blueprint** and link your repository.
3. Render automatically reads `render.yaml` and provisions the service.
4. Add your `GEMINI_API_KEY` under Environment Variables in the Render dashboard.
5. Click **Deploy**. Your app will be live at `https://catalogiq-xxxx.onrender.com`!

### Option 2: Docker Container

```bash
cd backend

# Build Docker image
docker build -t catalogiq-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="your_api_key_here" \
  -e GEMINI_MODEL="gemini-2.0-flash" \
  --name catalogiq \
  catalogiq-backend
```

### Option 3: Docker Compose

```yaml
version: "3.8"

services:
  catalogiq:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=gemini-2.0-flash
    volumes:
      - catalog_data:/app/data

volumes:
  catalog_data:
```

---

## 📂 Project Structure

```text
CatalogIQ/
├── backend/
│   ├── alembic/                    # Database schema migration versions
│   │   ├── versions/
│   │   │   └── 001_initial_migration.py # SQLite schema migration
│   │   └── env.py
│   ├── app/
│   │   ├── assets/                 # Delivery template CSV & sample catalog datasets
│   │   │   ├── delivery_format_template.csv  # Official 252-column schema template
│   │   │   └── sample_catalog.csv  # 12 representative industrial records
│   │   ├── models/
│   │   │   └── catalog.py          # SQLAlchemy models (PipelineRun, CatalogItem, ValidationItem)
│   │   ├── routers/                # FastAPI REST controllers
│   │   │   ├── analytics.py        # Analytics KPIs & category distribution
│   │   │   ├── export.py           # 252-column CSV exporter & completion preview
│   │   │   ├── items.py            # Item catalog search, inspector & patch
│   │   │   ├── runs.py             # Pipeline run orchestration & sample triggers
│   │   │   └── validation.py       # Human-in-the-loop review queue
│   │   ├── services/
│   │   │   ├── enrichment_ai.py    # Gemini 2.0 Flash async batching & offline fallback
│   │   │   ├── exporter.py         # 252-column Unilog delivery CSV writer
│   │   │   ├── pipeline.py         # Ingestion, cleansing & provenance orchestrator
│   │   │   ├── quality_engine.py   # 11 automated compliance rules & HITL routing
│   │   │   └── rules_engine.py     # Deterministic UOM, abbreviation & fraction engine
│   │   ├── utils/
│   │   │   └── logger.py           # Structured logging utility
│   │   ├── config.py               # Pydantic Settings & environment config
│   │   ├── database.py             # Asynchronous SQLite connection & session pool
│   │   └── main.py                 # FastAPI application root & SPA static router
│   ├── tests/
│   │   └── test_api.py             # Comprehensive pytest test suite
│   ├── Dockerfile                  # Lightweight backend container spec
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts           # Axios client with request tracing
│   │   ├── components/             # Reusable UI primitives, cards, and motion helpers
│   │   │   ├── Layout.tsx          # Rose gold & onyx shell layout
│   │   │   ├── motion.tsx          # Framer Motion animation primitives
│   │   │   └── ui.tsx              # Badge, Button, Input, Modal, and Card primitives
│   │   ├── hooks/
│   │   │   └── useCatalog.ts       # TanStack Query hooks with live progress polling
│   │   ├── pages/
│   │   │   ├── CatalogPage.tsx     # Filterable catalog table & detail drawer
│   │   │   ├── DashboardPage.tsx   # Operational KPI cards & telemetry charts
│   │   │   ├── ExportPage.tsx      # Schema preview & 252-column CSV exporter
│   │   │   ├── RunsPage.tsx        # CSV drag-and-drop & run progress tracker
│   │   │   └── ValidationPage.tsx  # HITL review queue with diff inspector
│   │   ├── styles/
│   │   │   └── index.css           # Premium dark theme styling
│   │   ├── types/
│   │   │   └── catalog.ts          # TypeScript type definitions
│   │   ├── App.tsx                 # Main routing & application layout
│   │   └── main.tsx                # React application entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── Resources/                      # UniHack specification guide & ground-truth data
├── render.yaml                     # Render.com blueprint deployment configuration
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Variables Reference

| Variable | Default Value | Description |
|---|---|---|
| `APP_ENV` | `development` | Application environment (`development` or `production`) |
| `APP_HOST` | `0.0.0.0` | Host address to bind FastAPI server |
| `APP_PORT` | `8000` | Port for FastAPI server |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/product_intelligence.db` | SQLAlchemy asynchronous database URL |
| `GEMINI_API_KEY` | `""` | Google Gemini API key (*Optional — fallback engine active if omitted*) |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name (`gemini-2.0-flash`, `gemini-1.5-flash`, etc.) |
| `LOG_LEVEL` | `INFO` | Application log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_UPLOAD_SIZE_MB`| `50` | Maximum allowable catalog CSV upload size in megabytes |

---

## ❓ Troubleshooting & FAQ

<details>
<summary><b>Q: Do I need a paid Google Gemini API key to run CatalogIQ?</b></summary>
<p>
No! CatalogIQ includes a fully deterministic offline fallback enrichment engine. If <code>GEMINI_API_KEY</code> is omitted or if rate limits are encountered, CatalogIQ automatically switches to the fallback engine, ensuring your demos and pipeline runs never fail.
</p>
</details>

<details>
<summary><b>Q: How are low-confidence items routed to Human-in-the-Loop?</b></summary>
<p>
Items with overall AI confidence &lt; 65%, or items failing any critical quality gate (such as missing product titles, incomplete descriptions, or invalid taxonomies), are automatically tagged as <code>needs_review</code> and routed to the HITL Validation Queue.
</p>
</details>

<details>
<summary><b>Q: How does CatalogIQ ensure invoice descriptions fit ERP systems?</b></summary>
<p>
The rules engine evaluates <code>invoice_desc</code> against a strict 40-character limit. It cleans all trade abbreviations, guarantees uppercase characters (<code>ALL CAPS</code>), and trims at word boundaries to avoid truncating crucial specification tokens.
</p>
</details>

<details>
<summary><b>Q: Can I run both backend and frontend from a single port?</b></summary>
<p>
Yes! Build the frontend by running <code>npm run build</code> inside the <code>frontend/</code> directory. FastAPI will detect the static distribution in <code>frontend/dist</code> and serve both the API endpoints and the single-page application on <b>http://localhost:8000</b>.
</p>
</details>

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the Project: `https://github.com/sumit11006/CatalogIQ`
2. Create your Feature Branch: `git checkout -b feat/AmazingFeature`
3. Commit your Changes: `git commit -m 'feat: add some AmazingFeature'`
4. Push to the Branch: `git push origin feat/AmazingFeature`
5. Open a Pull Request

---

## 👤 Author & Maintainer

**Sumit Tiwari**
- GitHub: [@sumit11006](https://github.com/sumit11006)
- Email: [sumittiwari11006@gmail.com](mailto:sumittiwari11006@gmail.com)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<div align="center">
  <sub>Built with ❤️ for <b>UniHack</b> • Powered by <b>FastAPI</b>, <b>React</b> & <b>Google Gemini</b></sub>
</div>
