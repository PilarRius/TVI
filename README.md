# Trade Vulnerability Index (TVI)

**WOAH Datathon — Challenge 4**  
**Trade Vulnerability and Disease Risk Along Trade and Movement Networks**

Interactive decision-support prototype that answers:

1. **Where is vulnerability highest?** (global map & rankings)
2. **Why is this country vulnerable?** (dimensions, drivers, legal detail)

**Working title:** Trade Vulnerability Index for Animal-Health Shocks  
**Initial disease focus:** Foot-and-Mouth Disease (FMD)  
**Stack:** Python · Shiny for Python · Pandas · Plotly · Parquet · custom CSS  
**Status:** End-to-end prototype running locally (UI + mock/placeholder analytics)

---

## Table of contents

1. [What this project is](#1-what-this-project-is)
2. [What we have so far](#2-what-we-have-so-far)
3. [What is still mock / placeholder](#3-what-is-still-mock--placeholder)
4. [Conceptual model](#4-conceptual-model)
5. [Project structure](#5-project-structure)
6. [How to run](#6-how-to-run)
7. [Data pipeline](#7-data-pipeline)
8. [Configuration (weights & rules)](#8-configuration-weights--rules)
9. [Application experience (tabs)](#9-application-experience-tabs)
10. [PVS / legal data strategy](#10-pvs--legal-data-strategy)
11. [Decisions already made](#11-decisions-already-made)
12. [Known limitations](#12-known-limitations)
13. [What next — backlog](#13-what-next--backlog)
14. [How colleagues can plug in real data](#14-how-colleagues-can-plug-in-real-data)
15. [Deploy to shinyapps.io](#15-deploy-to-shinyappsio)
16. [Team notes & contacts for inputs](#16-team-notes--contacts-for-inputs)
17. [Disclaimer](#17-disclaimer)

---

## 1. What this project is

The **Trade Vulnerability Index (TVI)** is a country-level composite score (0–100) that summarises vulnerability to the **trade-related consequences** of an animal-health shock.

It combines three dimensions:

| Dimension | Role | Current implementation |
|-----------|------|------------------------|
| **Disease Exposure** | Risk / exposure → raises TVI | **MOCK** module (replaceable) |
| **Economic Sensitivity** | Risk / exposure → raises TVI | **MOCK** module (replaceable) |
| **Legal Preparedness** | Resilience / protection → **lowers** TVI | **PLACEHOLDER** methodology + synthetic PVS-style scores |

Design principle for this datathon prototype:

- **Do not over-engineer** (single Shiny app, local Parquet/CSV, no React/FastAPI/auth/DB).
- Keep the **analytical model separate from the UI** so Disease Exposure and Economic Sensitivity can be swapped without rewriting the dashboard.
- Be transparent with scientific/policy users about mock data and methodology limits.

---

## 2. What we have so far

### Working product

- Single-page **Shiny for Python** app with institutional visual design (navy/teal palette, IBM Plex Sans, restrained colour).
- **191 countries** precomputed with TVI and all three dimensions.
- **WOAH regional** grouping (Africa, Americas, Asia and the Pacific, Europe, Middle East).
- Precomputed **Parquet caches** so the UI stays fast.
- Full documentation of methodology inside the app (**About / Methodology** tab).

### Analytical layer (complete scaffolding)

| Piece | Done? | Notes |
|-------|-------|-------|
| Central config (`config/settings.py`) | Yes | Weights, thresholds, legal invert, missing-data rules |
| WOAH region + country master | Yes | ISO3 → name / region |
| Disease Exposure module API | Yes | Mock values + 3 sub-indicators |
| Economic Sensitivity module API | Yes | Mock values + 4 sub-indicators |
| Legal Preparedness module | Yes | Placeholder PVS 1–5 → 0–100; Domestic + Trade-Continuity components |
| Legal data schema | Yes | country, ISO3, year, indicator codes, score, source, missing flag, … |
| File ingestion for real PVS data | Yes | CSV / Excel / JSON via `data/raw/pvs_indicators.*` |
| TVI aggregation | Yes | Configurable weights; legal inverted via `100 − preparedness` |
| Qualitative classes | Yes | Very Low → Very High (configurable thresholds) |
| Driver analysis (“Why?”) | Yes | Generated from indicator data, not hand-written per country |
| Benchmarks | Yes | Global, regional, peer averages |
| Build pipeline | Yes | `python -m scripts.build_data` |

### UI features (complete for prototype)

| Tab | What it does |
|-----|----------------|
| **Global view** | Disease selector (FMD live; others “coming soon”), WOAH region filter, choropleth map by TVI, hover (country + 3 dimensions + data availability), summary stats, top-vulnerability table, country selector |
| **Country profile** | Header with TVI + class; three dimension scorecards (preparedness clearly labelled as protective); weighted contribution chart; “What is driving vulnerability?” (risk vs protective factors) |
| **Compare** | Focal country vs global average vs regional average vs optional peers |
| **Legal preparedness** | Domestic Legal Readiness, Trade-Continuity Preparedness, overall score; IV-1A/1B/4/6/7 table with year/source/interpretation; **Data unavailable** (never zero); coverage indicator |
| **About / Methodology** | Conceptual flow, weights, legal construction, PVS source note, limitations, how to replace modules |

### Current build metadata

From last `build_data` run (`data/processed/build_meta.json`):

- Countries in master list: **191**
- Countries with complete TVI: see latest build output (legal gaps reduce coverage when public extracts are incomplete)
- Disease module: **MOCK**
- Economic module: **MOCK**
- Legal module: **mixed** — public PVSIS report extracts where parsed + placeholders elsewhere
- Refresh public legal extracts: `python -m scripts.ingest_public_pvs`

---

## 3. What is still mock / placeholder

**Important for demos and for colleagues.**

### Disease Exposure — MOCK

- File: `src/modules/disease_exposure.py`
- Label in code: `MOCK — REPLACE WITH REAL DISEASE EXPOSURE MODEL`
- Scale: 0–100
- Mock sub-indicators: domestic exposure, network exposure, trade/movement exposure
- Values are seeded random with regional baselines (reproducible, not real epidemiology)

### Economic Sensitivity — MOCK

- File: `src/modules/economic_sensitivity.py`
- Label: `MOCK — REPLACE WITH REAL ECONOMIC SENSITIVITY MODEL`
- Scale: 0–100
- Mock sub-indicators: livestock importance, export exposure, import dependence, trade concentration

### Legal Preparedness — PLACEHOLDER

- File: `src/modules/legal_preparedness.py`
- Label: `PLACEHOLDER — REPLACE WITH REAL LEGAL PREPAREDNESS METHODOLOGY`
- Generates synthetic PVS-like scores (1–5) for IV-1A, IV-1B, IV-4, IV-6, IV-7
- ~22% of country–indicator cells intentionally missing to demonstrate missing-data handling
- Aggregation logic (component weights, normalisation) is real scaffolding; **input scores are not real PVS assessments**

The UI does **not** shout “MOCK” on every chart (for demo polish), but the **Methodology tab** and this README state it explicitly.

---

## 4. Conceptual model

```
┌─────────────────────┐   ┌──────────────────────┐   ┌─────────────────────────┐
│  Disease Exposure   │   │ Economic Sensitivity │   │  Legal Preparedness     │
│  (risk / exposure)  │   │  (risk / exposure)   │   │  (resilience)           │
└──────────┬──────────┘   └──────────┬───────────┘   └────────────┬────────────┘
           │                         │                             │
           │                         │              vulnerability = 100 − score
           │                         │                             │
           └────────────┬────────────┴─────────────────────────────┘
                        │
                        ▼
              Trade Vulnerability Index
              (weighted average, default ⅓ each)
```

### Legal preparedness ≠ high vulnerability

Example:

- Legal Preparedness **78 / 100** → “Strong preparedness”
- Vulnerability contribution ≈ **22** (before weight), not 78

This transform is explicit and configurable: `LEGAL_VULN_TRANSFORM = "invert_100"` in `config/settings.py`.

### Legal components

| Component | Indicators | Default weight |
|-----------|------------|----------------|
| Domestic Legal Readiness | IV-1A, IV-1B | 50% |
| Trade-Continuity Preparedness | IV-4, IV-6, IV-7 | 50% |

PVS Critical Competency levels (1–5) are normalised to 0–100 before weighting.

---

## 5. Project structure

```
TVI/
├── app.py                          # Shiny application (UI + server)
├── requirements.txt
├── README.md                       # This file
├── .gitignore
│
├── config/
│   ├── settings.py                 # Weights, thresholds, brand, paths
│   └── woah_regions.py             # ISO3 → WOAH region + country names
│
├── assets/
│   └── styles.css                  # Institutional visual system
│
├── data/
│   ├── raw/                        # Drop real PVS files here
│   │   ├── pvs_indicators.SCHEMA.csv
│   │   └── pvs_indicators_placeholder.*  (auto-generated if no real file)
│   ├── clean/                      # Cleaned PVS parquet
│   └── processed/                  # disease / economic / legal / tvi caches
│
├── scripts/
│   └── build_data.py               # CLI: python -m scripts.build_data
│
└── src/
    ├── modules/                    # REPLACEABLE analytical modules
    │   ├── disease_exposure.py
    │   ├── economic_sensitivity.py
    │   └── legal_preparedness.py
    ├── calculations/               # Shared scoring logic
    │   ├── tvi.py
    │   ├── drivers.py
    │   ├── benchmarks.py
    │   └── classification.py
    ├── pipeline/
    │   └── build_dataset.py        # RAW → … → TVI
    └── ui/
        └── charts.py               # Plotly builders (no Shiny dependency)
```

**Rule:** the UI must not calculate raw PVS transforms. All scoring happens in modules/pipeline; the app only visualises processed outputs.

---

## 6. How to run

### Prerequisites

- Python 3.10+ (developed with 3.12)
- Packages in `requirements.txt`

### First-time setup

```bash
cd TVI
pip install -r requirements.txt
python -m scripts.build_data
shiny run app.py
```

Open the URL printed in the terminal (e.g. `http://127.0.0.1:8000`).

### After changing config or modules

Always rebuild caches, then restart Shiny:

```bash
python -m scripts.build_data
shiny run app.py
```

### Key dependencies

- `shiny`, `shinywidgets`
- `pandas`, `pyarrow`, `numpy`
- `plotly`
- `openpyxl` (Excel ingestion)
- `rsconnect-python` (deployment)

---

## 7. Data pipeline

```
raw_pvs (CSV/Excel/JSON or placeholder generator)
        ↓
clean_pvs
        ↓
legal_indicators (standardised 0–100; missing stay null)
        ↓
legal_component_scores → legal_preparedness
        ↓
+ disease_exposure (mock module)
+ economic_sensitivity (mock module)
        ↓
tvi.parquet / tvi.csv
        ↓
Shiny visualisation
```

Processed artefacts written to `data/processed/`:

| File | Content |
|------|---------|
| `disease_exposure.parquet` | Country disease index + sub-indicators |
| `economic_sensitivity.parquet` | Country economic index + sub-indicators |
| `legal_preparedness.parquet` | Domestic, trade-continuity, overall legal |
| `legal_indicators.parquet` | Indicator-level legal scores + metadata |
| `tvi.parquet` / `tvi.csv` | Full country TVI table for the app |
| `build_meta.json` | Build provenance (mock vs real flags) |

Missing data policy (enforced in config):

- **Never** silently replace missing with zero
- UI shows **“Data unavailable”**
- Component/overall scores use only available indicators; if nothing is available, score is null

---

## 8. Configuration (weights & rules)

Edit **`config/settings.py`** — do not hard-code weights in the UI.

| Setting | Current default | Purpose |
|---------|-----------------|---------|
| `DIMENSION_WEIGHTS` | ⅓ / ⅓ / ⅓ | Disease, Economic, Legal |
| `LEGAL_VULN_TRANSFORM` | `invert_100` | Preparedness → vulnerability contribution |
| `LEGAL_COMPONENT_WEIGHTS` | 50% / 50% | Domestic vs Trade-Continuity |
| `LEGAL_INDICATOR_WEIGHTS` | Equal within component | IV-1A/1B and IV-4/6/7 |
| `CLASSIFICATION_THRESHOLDS` | 0–20–40–60–80–100 | Very Low → Very High |
| `MISSING_DATA` | no zero-imputation | Explicit missing handling |
| `ACTIVE_DISEASE` | `FMD` | Only FMD fully wired |

Alternative weighting scenarios for sensitivity testing can call `compute_tvi(..., weights={...})` without changing the UI.

---

## 9. Application experience (tabs)

### Global view

- Answers: *Where is vulnerability highest?*
- World choropleth coloured by TVI
- Hover: country, TVI, Disease, Economic, Legal, data availability
- Region filter (WOAH)
- Summary strip + ranked table
- Disease selector: FMD active; PPR / ASF / HPAI labelled coming soon

### Country profile

- Answers: *Why is this country vulnerable?*
- TVI score + qualitative class
- Three scorecards with contribution notes
- Legal card distinguishes **preparedness score** vs **vulnerability contribution**
- Data-driven driver lists (high contribution vs protective factors)
- Horizontal contribution bars

### Compare

- Country vs global vs regional (± peers)

### Legal preparedness

- Component scorecards
- Full indicator table (score, year, source, interpretation)
- Coverage: country indicators available + global PVS-style coverage count

### About / Methodology

- Transparency for WOAH / FAO / government audiences

---

## 10. PVS / legal data strategy

### What we researched

- WOAH **PVS Pathway** and **PVS Information System (PVSIS)** are the authoritative homes for assessment reports and digitised Critical Competency (CC) Levels of Advancement.
- Identifiable CC tables for all Members are **not** publicly bulk-exportable: each Member sees their own data; public dashboards are mostly anonymous cohorts ([WOAH note on PVSIS confidentiality](https://www.woah.org/en/members-experience-the-pvs-information-system-for-the-first-time/)).
- There is **no documented public API** that returns a full country × CC score matrix for IV-1A / IV-1B / IV-4 / IV-6 / IV-7.

### Interim approach — public reports (implemented)

While access to the digitised PVSIS tables is requested, the prototype uses **public** Evaluation / Follow-Up reports:

1. Catalog: `GET https://pvs.woah.org/pvs-is-be/api/document-management/public`
2. PDF download: `GET https://pvs.woah.org/pvs-is-be/api/document-management/download-public/{id}`
3. Parse Levels of Advancement for the five legal indicators from the PDF text

```bash
python -m scripts.ingest_public_pvs   # writes data/raw/pvs_indicators.csv
python -m scripts.build_data
```

**Current coverage (last ingest):** ~**34 countries** with at least one parsed public CC score (~103 scored indicator cells). Countries without a usable public extract still use **placeholders** (clearly labelled). Failed/partial PDF parses stay **Data unavailable** (never zero).

### Longer-term (preferred)

Obtain an **approved extract** or Member/partner PVSIS access for the target CCs, then replace `data/raw/pvs_indicators.csv` and rebuild.

### Manual file schema

Prefer a local file: `data/raw/pvs_indicators.csv` (or `.xlsx` / `.json`).  
Schema documented in `data/raw/pvs_indicators.SCHEMA.csv`.

### Required columns for real data

| Column | Required | Notes |
|--------|----------|-------|
| `iso3` | Yes | ISO 3166-1 alpha-3 |
| `indicator_code` | Yes | `IV-1A`, `IV-1B`, `IV-4`, `IV-6`, `IV-7` |
| `score` | Yes | PVS 1–5 (blank/NA if missing) |
| `assessment_year` | Recommended | |
| `source` | Recommended | e.g. PVS Evaluation Report |
| `source_url` | Optional | |
| `missing_data_flag` | Optional | Auto-derived from null scores if omitted |
| `country` | Optional | Filled from master list if missing |

Authoritative sources to prioritise later (no random web scraping):

1. WOAH PVS Pathway assessment data / reports  
2. Publicly available WOAH PVS documentation  
3. Official national veterinary legislation information where appropriate  
4. Other authoritative WOAH sources if structured extracts become available  

---

## 11. Decisions already made

| Topic | Decision |
|-------|----------|
| Scope | Full world coverage where possible (~191 ISO3 in master list) |
| Disease | FMD now; other diseases stubbed as coming soon |
| Regions | WOAH regional commissions |
| Navigation | Tabbed views |
| Language | English |
| Branding | Invented institutional palette (not official WOAH branding) |
| Legal scores | Placeholder until methodology + real data arrive |
| Disease & economic | Mock until colleagues specify datasets/models |
| Deployment target | shinyapps.io |
| Legal in TVI | Higher preparedness **reduces** vulnerability (`100 − score`) |
| Missing data | Never impute to zero |
| Architecture | Single Shiny app; modules replaceable; no microservices |

---

## 12. Known limitations

1. **Not official WOAH** — datathon prototype only; not for operational use.
2. **Mock disease & economic** dimensions — map patterns are illustrative.
3. **Placeholder legal scores** — do not cite as real PVS results.
4. **Equal weights** — starting point only; need expert/sensitivity review.
5. **WOAH membership list** — approximate ISO3→region mapping for demo; verify against official Member lists.
6. **Map interaction** — country selection is via dropdowns (synced across tabs); map is hover/visual (click-to-select can be improved).
7. **No live API** — by design for reliability; refresh is offline file + rebuild.
8. **Mobile** — secondary; desktop/laptop is the primary demo surface.
9. **Geometries** — Plotly choropleth built-in countries; tiny territories may be limited.
10. **Sensitivity UI** — weights are config-file based; no in-app weight slider yet.

---

## 13. What next — backlog

Prioritised for the datathon team. Check items off as they land.

### A. Blocked on colleagues / domain experts (highest priority)

- [ ] **Confirm Disease Exposure data & method** — which datasets (outbreaks, trade networks, WAHIS, livestock density, etc.) and formula
- [ ] **Confirm Economic Sensitivity data & method** — trade values, livestock GDP share, partner concentration, etc.
- [ ] **Confirm Legal Preparedness methodology** — exact indicator definitions, normalisation, weights, treatment of old assessments
- [ ] **Obtain real PVS scores** (or approved extract) for IV-1A, IV-1B, IV-4, IV-6, IV-7 for as many countries as possible
- [ ] **Validate WOAH region membership** against official lists
- [ ] **Agree classification thresholds** and dimension weights for the demo narrative
- [ ] **Agree disclaimer / branding** (use of WOAH name, logos, colours)

### B. Data engineering (once sources are known)

- [ ] Drop real legal file → `data/raw/pvs_indicators.csv` → rebuild
- [ ] Replace `generate_disease_exposure()` with real calculation module
- [ ] Replace `generate_economic_sensitivity()` with real calculation module
- [ ] Add data dictionaries and source licences for each input dataset
- [ ] Document assessment year currency and “latest available” rules
- [ ] Optional: scripted download from approved repositories (still cache locally)

### C. Product / UX polish

- [ ] Map **click → select country** and auto-switch to Country profile tab
- [ ] In-app **weight scenario** toggle (e.g. equal vs exposure-heavy) for sensitivity story
- [ ] Export country brief (PDF/PNG) for judges
- [ ] Short “demo script” (2–3 minute walkthrough)
- [ ] Loading / empty states polish; accessibility pass
- [ ] Optional light dark-section for methodology diagrams only if it stays institutional

### D. Analytical enhancements

- [ ] Peer-group presets (e.g. same region + similar livestock trade intensity)
- [ ] Time dimension if multi-year PVS exists
- [ ] Uncertainty / data-quality score more prominent on map
- [ ] Additional PVS indicators without breaking schema (architecture already allows new codes)
- [ ] Scenario analysis: “what if zoning improves by X”

### E. Deployment & delivery

- [ ] Create shinyapps.io account / tokens
- [ ] Deploy and share public URL with team
- [ ] Pin dependency versions that work on shinyapps.io
- [ ] Freeze a “demo build” of `data/processed/` for the judging day
- [ ] Prepare 1-pager methodology PDF from the About tab content

### F. Stretch (only if core real data is in)

- [ ] Second disease (PPR / ASF) behind the existing selector
- [ ] Simple API-less “compare two countries” side-by-side layout
- [ ] Automated tests for TVI math and missing-data rules

---

## 14. How colleagues can plug in real data

### Legal / PVS (ready now)

1. Export indicators to CSV with columns `iso3`, `indicator_code`, `score`, …
2. Save as `data/raw/pvs_indicators.csv`
3. Run `python -m scripts.build_data`
4. Restart `shiny run app.py`
5. Check Methodology / Legal tab — source fields should reflect your file

### Disease Exposure (when ready)

1. Implement real logic in `src/modules/disease_exposure.py`
2. Keep the same output columns the pipeline expects (`iso3`, `disease_exposure`, plus optional sub-indicators)
3. Update `MODULE_STATUS` string
4. Rebuild

### Economic Sensitivity (when ready)

1. Same pattern in `src/modules/economic_sensitivity.py`
2. Keep `economic_sensitivity` column + optional drivers
3. Rebuild

### Changing weights without touching UI

Edit `config/settings.py` → rebuild → restart.

---

## 15. Deploy to shinyapps.io

```bash
pip install rsconnect-python

# one-time: add account credentials from shinyapps.io dashboard
rsconnect add --account <ACCOUNT> --name <NAME> --token <TOKEN> --secret <SECRET>

# from project root (after build_data)
python -m scripts.build_data
rsconnect deploy shiny . --name tvi-woah-datathon --title "Trade Vulnerability Index"
```

**Deploy checklist**

- [ ] `data/processed/*.parquet` present (app loads caches at startup)
- [ ] `requirements.txt` complete
- [ ] No dependency on live WOAH API
- [ ] Smoke-test all five tabs on the public URL
- [ ] Confirm disclaimer visible in footer / Methodology

---

## 16. Team notes & inputs needed

Use this as a handoff checklist for the next working session.

| Input needed from | Question |
|-------------------|----------|
| Epidemiology colleagues | Which Disease Exposure indicators and formula for FMD? |
| Economics / trade colleagues | Which Economic Sensitivity indicators and data sources? |
| Legal / PVS colleagues | Final scoring rules + access path to PVS CC scores |
| All | Preferred dimension weights for the official demo narrative |
| All | Countries to feature in the live demo (3–5 “story” countries) |
| Comms / leads | Branding constraints and public URL naming |

**Suggested near-term sequence**

1. Lock methodology sketches on paper (even if rough)  
2. Drop first real PVS extract into `data/raw/`  
3. Wire one real disease or economic indicator as a pilot  
4. Deploy to shinyapps.io for shared review  
5. Iterate weights and demo script before judging  

---

## 17. Disclaimer

This repository is a **WOAH Datathon prototype**. It is **not** an official WOAH, FAO, or EuFMD product. Mock and placeholder data must not be used for operational animal-health, trade, or investment decisions. Replace analytical modules and validate all inputs before any policy use.

---

## Quick reference

```bash
# install
pip install -r requirements.txt

# rebuild all scores
python -m scripts.build_data

# run locally
shiny run app.py

# after adding real PVS file
# → save to data/raw/pvs_indicators.csv
python -m scripts.build_data
shiny run app.py
```

**Replaceable modules:** `src/modules/*.py`  
**Tunable methodology:** `config/settings.py`  
**UI entrypoint:** `app.py`
