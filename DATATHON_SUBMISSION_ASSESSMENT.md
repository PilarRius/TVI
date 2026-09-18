# WOAH Datathon — Challenge 4 submission readiness

**Project:** Trade Vulnerability Index (TVI) for Animal-Health Shocks  
**Challenge:** [4 — Trade Vulnerability and Disease Risk Along Trade and Movement Networks](https://data-integration-department-woah.github.io/WOAH-Datathon/challenges.html)  
**Assessment criteria:** [Datathon Deliverable Assessment Criteria](https://data-integration-department-woah.github.io/WOAH-Datathon/criteria.html)  
**Submission rules:** [Final Submission Instructions](https://data-integration-department-woah.github.io/WOAH-Datathon/submission.html)  
**Deadline:** **31 October 2026** (repository frozen as of that date)  
**Purpose of this note:** Honest readiness check — strengths, weaknesses, gaps vs Challenge 4 and the four scoring axes. Same tone as the project README: practical, transparent, for team planning.

---

## Table of contents

1. [Challenge 4 fit (one paragraph)](#1-challenge-4-fit-one-paragraph)
2. [What judges are looking for](#2-what-judges-are-looking-for)
3. [Strengths](#3-strengths)
4. [Weaknesses](#4-weaknesses)
5. [What is missing (vs suggested data & deliverable)](#5-what-is-missing-vs-suggested-data--deliverable)
6. [Scorecard against assessment criteria](#6-scorecard-against-assessment-criteria)
7. [Submission package checklist](#7-submission-package-checklist)
8. [Priority actions before 31 Oct 2026](#8-priority-actions-before-31-oct-2026)
9. [Risks for the panel](#9-risks-for-the-panel)

---

## 1. Challenge 4 fit (one paragraph)

Challenge 4 asks how **animal-health events interact with trade and movement networks** to create vulnerability and disruption, and wants **indicators, analyses or dashboards** that identify **vulnerable trade links and pathways** under animal-health shocks ([challenges page](https://data-integration-department-woah.github.io/WOAH-Datathon/challenges.html)). Our prototype answers a closely related but broader policy question — *how vulnerable is Country X to the trade-related consequences of Disease X?* — via a three-pillar composite (disease exposure, economic sensitivity, legal preparedness) and a Shiny dashboard. That is a strong **policy framing** and a credible **dashboard deliverable**. It is only a **partial** match to the scientific emphasis on **network analysis** and **explicit trade-link / pathway vulnerability**. Closing that gap (bilateral trade/movement layers + pathway outputs) is the main analytic priority for a competitive submission.

---

## 2. What judges are looking for

| Axis | What “good” looks like for Challenge 4 |
|------|----------------------------------------|
| **Scientific / technical accuracy** | Clear methods; careful missing-data handling; reproducible raw→score workflow; some validation / sensitivity |
| **Innovation / creativity** | Not only a choropleth of one series — integrate disease + trade + movement (and ideally legal/resilience) in a novel, justified way |
| **Practical relevance / policy impact** | Interpretable for non-technical WOAH/Member audiences; actionable insights (where to invest, which levers) |
| **Reproducibility / documentation** | Private repo + pipeline + technical report + README; organisers can reproduce; `diad-woah` has access by the deadline |

Submission mechanics ([submission page](https://data-integration-department-woah.github.io/WOAH-Datathon/submission.html)):

1. Analytical pipeline  
2. Technical report (methods, results, interpretation)  
3. README (overview + reproduce steps)  
4. **Private** GitHub (or equivalent) with **`diad-woah`** as collaborator (read access) by **31 Oct 2026** — that *is* the submission; no separate form  

---

## 3. Strengths

### Challenge & policy alignment

- Direct response to Challenge 4’s **political** brief: trade resilience, proportional sanitary measures, risk-based decisions.
- Multidimensional framing (exposure × economics × legal preparedness) matches how Members and partners actually think about trade shocks — stronger than a single-risk map.
- Explicit **domestic outbreak vs partner outbreak** logic in the methodology narrative (export-side vs import-side).
- FMD focus is coherent for a datathon prototype (high trade relevance, EuFMD/RMT lineage available to the team).

### Product & decision-support design

- Working **dashboard** (Global / Country / Compare / Disease / Economic / Legal / Methodology) — matches the allowed deliverable form (“indicators, analyses, **or dashboards**”).
- Separates **“where?”** from **“why?”** (map + drivers + dimension tabs) — good for **practical relevance / interpretability**.
- Legal preparedness inverted into vulnerability (`100 − score`) is conceptually correct and configurable.
- Missing-data policy is submission-grade: **never impute to zero**; N/A is explicit — aligns with “correct handling of data” under technical accuracy.

### Architecture & reproducibility foundations

- Modular pipeline: replaceable modules, central `config/settings.py`, Parquet caches, `python -m scripts.build_data`.
- Public PVSIS PDF ingest path for legal indicators (~34 countries scored) — creative use of constrained public data.
- EuFMD **RMT formula** wired for disease (status, mitigation, pathway effectiveness) for ~20 neighbourhood countries — shows domain method, not only UI.
- In-app methodology + open questions for colleagues — transparent about provisional choices (weights, proxies).

### Innovation (relative)

- Combining **epidemiological entry-risk logic (RMT)** with **economic sensitivity** and **PVS legal CCs** in one index is unusual and on-brand for Challenge 4’s policy angle.
- Composite + dashboard + driver narrative is more than a notebook demo.

---

## 4. Weaknesses

### Scientific / network gap (most important)

- Challenge text foregrounds **network analysis** and **vulnerable trade links / pathways**. We still lack:
  - Bilateral **UN Comtrade** (or equivalent) connection matrices  
  - **WAHIS** outbreak/status layer at global scale  
  - Movement / transport proxies (OpenSky, AIS, road density, borders)  
  - Outputs that **rank source→target links or pathways**, not only a country-level index  
- Disease RMT uses **provisional mid-level connections** — scientifically weak if left as-is for judging.
- Economic dimension remains **fully mock** — high risk if judges probe the map narrative.

### Coverage & validation

- Disease scored for **~20** countries; legal for **~34**; economic mock for **191**. Partial TVI mixes real and synthetic signals — must be labelled ruthlessly in the report.
- No formal **validation** against national RMT exercises, historical trade disruptions, or known FMD free/infected contrasts.
- Equal **⅓ weights** are placeholders; OECD/JRC-style sensitivity testing is not yet implemented in the product.
- README is **out of date** relative to the live app (still describes disease/legal as fully mock/placeholder in places).

### Scope vs suggested Challenge 4 datasets

Suggested sources we barely or do not use yet: WAHIS, FAOSTAT/GLW livestock, WTO SPS, air/maritime/road networks, regional trade blocs. Legal/PVS is an asset but is **not** listed as a core Challenge 4 dataset — defend it as resilience/mitigation of trade disruption, not as a substitute for network data.

### Delivery polish for submission

- No dedicated **technical report** document yet (About tab ≠ formal report).
- Repo may not yet be configured as **private** + **`diad-woah`** collaborator.
- No pinned “demo freeze” of processed data / public shinyapps URL called out as the assessable artefact.
- Limited automated tests for TVI math and missing-data rules.

---

## 5. What is missing (vs suggested data & deliverable)

### Challenge 4 suggested data — coverage

| Suggested source | Status in TVI | Gap severity |
|------------------|---------------|--------------|
| International / regional trade (e.g. UN Comtrade) | Not wired; economic mock; RMT connections provisional | **Critical** |
| Animal movement / network proxies | Not wired | **Critical** for “links & pathways” story |
| WAHIS surveillance / outbreaks | Not ingested (status via EuFMD RMT extract only, limited countries) | **High** |
| Livestock population / density / production (FAOSTAT, GLW) | Not wired | **High** (economic + pathway host context) |
| Geographic / admin boundaries | Plotly built-in only | Medium |
| WTO SPS notifications | Not used | Medium (nice for trade-disruption narrative) |
| Air / maritime / road density | Not used | Medium (Phase 2 connections) |
| Regional trade stats (Mercosur, ASEAN, Eurostat) | Not used | Lower |

### Deliverable elements — coverage

| Expected element | Status |
|------------------|--------|
| Indicators of vulnerability | Partial (country TVI + sub-indicators) |
| Analysis of disease × trade/movement | Partial (RMT concept; weak network empirics) |
| Dashboard | **Strong** (working Shiny app) |
| Identification of **vulnerable trade links / pathways** | **Weak / missing** as a first-class output |

### Submission package elements — coverage

| Required item | Status |
|---------------|--------|
| Analytical pipeline | Present (`scripts/` + `src/pipeline/`) — needs polish + frozen build |
| Technical report | **Missing** as a standalone document |
| README | Present — **needs update** to match current modules |
| Private repo + `diad-woah` access | Confirm / do before deadline |

---

## 6. Scorecard against assessment criteria

Self-assessment **today** (0–5), assuming judges see the current prototype honestly documented. Target = competitive by deadline.

| Criterion | Today (est.) | If we close critical gaps | Comment |
|-----------|--------------|---------------------------|---------|
| Scientific / technical accuracy | **2.5–3** | **4–4.5** | Scaffolding + missing-data discipline strong; empirics thin; little validation |
| Innovation / creativity | **3.5–4** | **4–4.5** | Three-pillar + RMT + PVS + dashboard is distinctive; network integration would lock this |
| Practical relevance / policy impact | **4** | **4.5** | Already strong; keep language Member-facing; add 3–5 country “stories” |
| Reproducibility / documentation | **3** | **4.5–5** | Pipeline exists; README drift + no technical report + access ritual incomplete |

**Bottom line:** Policy product and architecture are ahead of the **network empirics** Challenge 4 emphasises. Without Comtrade/WAHIS (or a clearly justified proxy network) and a short validated technical report, scores on accuracy and “vulnerable links” will lag.

---

## 7. Submission package checklist

Use as the delivery gate (maps to [submission instructions](https://data-integration-department-woah.github.io/WOAH-Datathon/submission.html)).

### Repository & access

- [ ] Repository is **private**
- [ ] Organisation **`diad-woah`** added as collaborator (read access) **on or before 31 Oct 2026**
- [ ] No commits after the deadline (assessed state = deadline snapshot)
- [ ] If not on GitHub: email **diad@woah.org** with subject `WOAH Datathon Submission — <Team Name>` + URL + access notes

### Analytical pipeline

- [ ] Documented `build_data` / ingest scripts for every real source used
- [ ] Frozen `data/processed/` (or scripted rebuild from raw with versions pinned)
- [ ] `requirements.txt` pinned enough for another machine to run
- [ ] Clear statement of what is **real vs mock vs provisional**

### Technical report (to write)

- [ ] Problem statement ↔ Challenge 4 objective  
- [ ] Methods per dimension (formulas, weights, missing-data rules)  
- [ ] Data sources, coverage, limitations, licences  
- [ ] Results (global patterns, example countries, sensitivity if any)  
- [ ] Interpretation for trade / sanitary decision-makers  
- [ ] What we would do next with more time/data  

### README

- [ ] Align with live status (RMT disease, mock economic, public PVS legal)  
- [ ] One-command reproduce path  
- [ ] Link to technical report + how to run the app  

---

## 8. Priority actions before 31 Oct 2026

Ordered for scoring impact.

### Must-have (accuracy + Challenge 4 deliverable)

1. **Wire at least one bilateral connection layer** (UN Comtrade live animals / POAO) into RMT connections — even a coarse intensity score — and show **top source→target links** for a few demo countries.  
2. **WAHIS and/or WOAH official FMD status** for disease-status expansion beyond the EuFMD neighbourhood extract.  
3. **Replace or shrink economic mock**: at least FAOSTAT livestock importance and/or Comtrade export/import shares for FMD-susceptible products.  
4. Write the **technical report**; refresh **README**; freeze a demo build.

### Should-have (innovation + reproducibility)

5. Simple **weight sensitivity** (equal vs exposure-heavy) documented in the report (OECD/JRC-aligned).  
6. **Validate** 3–5 countries against expert/RMT intuition or known status.  
7. Deploy a stable **demo URL** (shinyapps.io) and cite it in the report (optional but helpful for policy impact).  
8. Confirm **PVSIS** access request status; expand legal coverage if possible — keep N/A honest.

### Nice-to-have

9. Proximity / transport proxies; SPS notification overlay; second disease stub with one real indicator.  
10. Automated tests for aggregation and missing-data rules.

---

## 9. Risks for the panel

| Risk | Why it hurts | Mitigation |
|------|--------------|------------|
| “This is a nice dashboard but not network analysis” | Challenge wording centres links & pathways | Add link/pathway views fed by Comtrade (even v1) |
| Mock economic / provisional connections over-read as results | Technical accuracy & trust | Label everywhere; restrict demo narrative to countries with real inputs |
| Legal/PVS seen as off-scope | Challenge data list omits PVS | Frame as **trade-disruption resilience**; keep network layers primary in the report |
| Incomplete submission ritual | Automatic fail on access | Add `diad-woah` early; don’t wait until 31 Oct |
| README/report contradiction | Reproducibility score | Sync docs in one pass before freeze |

---

## Quick reference — official links

- Challenges (incl. Challenge 4): https://data-integration-department-woah.github.io/WOAH-Datathon/challenges.html  
- Assessment criteria: https://data-integration-department-woah.github.io/WOAH-Datathon/criteria.html  
- Submission instructions: https://data-integration-department-woah.github.io/WOAH-Datathon/submission.html  

---

## One-line verdict

**Strong decision-support prototype and policy story; not yet a full Challenge 4 network-risk submission.** Closing Comtrade/WAHIS (or equivalent), demoting mocks, and shipping a technical report + `diad-woah` access will matter more than further UI polish.
