"""Methodology content for Legal Preparedness — concept + data-source options."""

from __future__ import annotations

from htmltools import HTML, TagList, tags

from config.settings import LEGAL_COMPONENT_WEIGHTS, LEGAL_INDICATOR_WEIGHTS, LEGAL_INDICATORS
from src.ui.methodology_common import model_questions_block, source_card


def _decision_callout():
    return tags.div(
        {"class": "tvi-callout"},
        HTML(
            "<strong>Team decision needed:</strong> which enhancement sources (if any) "
            "should enter the numeric Legal Preparedness score versus remaining as "
            "context in this Methodology tab and the Legal detail view. "
            "Until then, the live Index scores legal preparedness from <strong>PVS only</strong>; "
            "countries without usable PVS extracts show <strong>N/A</strong>. "
            "WAHIS and WOAH official disease status are documented under "
            "<strong>Disease Exposure</strong>."
        ),
    )


def legal_methodology_section() -> TagList:
    """Colleague concept note + candidate data sources for team decision."""
    return TagList(
        tags.h3("Legal Preparedness — methodology concept"),
        tags.p(
            "The legal preparedness dimension assesses the extent to which a country has "
            "the legal and regulatory foundations needed to respond to an animal-health shock "
            "and to maintain, restore or adapt trade following such an event."
        ),
        tags.p(
            "For the prototype, the legal preparedness dimension relies primarily on information "
            "generated through the WOAH Performance of Veterinary Services (PVS) Pathway. The PVS "
            "provides structured assessments of countries’ Veterinary Services across a common set "
            "of Critical Competencies, including aspects of veterinary legislation, implementation, "
            "sanitary agreements, zoning and compartmentalisation. This makes it particularly "
            "valuable for the Index because it offers an existing, internationally recognised and "
            "relatively standardised source from which comparable proxies for legal preparedness "
            "can be derived, avoiding the need for a new country-by-country legal assessment."
        ),
        tags.p(
            "The PVS data nevertheless have important limitations. Assessments are not publicly "
            "available for all countries, reports have been conducted in different years and under "
            "different versions of the PVS methodology, and PVS scores assess the broader capacity "
            "and performance of Veterinary Services rather than legal preparedness for trade "
            "disruption specifically. The indicators used in the Index should therefore be "
            "understood as proxies for the legal preparedness dimension. Their suitability and "
            "comparability will be tested during the development of the prototype, and the "
            "methodology may be refined as more specialised legal and regulatory data become available."
        ),
        tags.h4("1. Domestic legal readiness"),
        tags.p(
            "This component assesses whether the country has an adequate legal and regulatory "
            "basis for its Veterinary Services to act effectively when an animal-health shock occurs. "
            "For the prototype, the main PVS indicators to be explored are:"
        ),
        tags.ul(
            tags.li(
                tags.strong("IV-1A — Veterinary legislation: legal quality and coverage")
            ),
            tags.li(
                tags.strong(
                    "IV-1B — Veterinary legislation: implementation and compliance"
                )
            ),
        ),
        tags.p(
            "Together, these indicators provide a proxy for whether the country has a sufficiently "
            "robust and operational veterinary legal framework to support timely disease-control measures."
        ),
        tags.h4("2. Trade-continuity preparedness"),
        tags.p(
            "This component assesses whether arrangements are in place that may help a country "
            "maintain, redirect or restore trade following an animal-health shock, including where "
            "the shock occurs domestically or in a key trading partner. The main PVS indicators "
            "to be explored are:"
        ),
        tags.ul(
            tags.li(
                tags.strong("IV-4 — Equivalence and other types of sanitary agreements")
            ),
            tags.li(tags.strong("IV-6 — Zoning")),
            tags.li(tags.strong("IV-7 — Compartmentalisation")),
        ),
        tags.p(
            "These indicators are relevant because sanitary agreements, zoning and "
            "compartmentalisation can help prevent an outbreak from resulting in a complete "
            "interruption of trade and can support the continuation or restoration of trade from "
            "unaffected areas or populations."
        ),
        tags.p(
            f"Prototype weights — Domestic Legal Readiness "
            f"{LEGAL_COMPONENT_WEIGHTS['domestic_legal_readiness']:.0%}; "
            f"Trade-Continuity Preparedness "
            f"{LEGAL_COMPONENT_WEIGHTS['trade_continuity_preparedness']:.0%}. "
            "Indicator weights within components: "
            + ", ".join(
                f"{code} ({LEGAL_INDICATOR_WEIGHTS[code]:.0%})"
                for code in LEGAL_INDICATORS
            )
            + ". Configurable in config/settings.py."
        ),
        _decision_callout(),
        tags.h3("Legal data sources — options for team decision"),
        tags.p(
            "PVS remains the main scoring source. The sources below are documented so colleagues "
            "can decide whether to keep them as context only, add them as enhancement indicators, "
            "or leave them out of v1. None replace the five PVS Critical Competencies above. "
            "Disease status / WAHIS are listed under Disease Exposure."
        ),
        tags.div(
            {"class": "tvi-source-grid"},
            source_card(
                "WOAH PVS Pathway / PVSIS",
                "MAIN SOURCE — implemented",
                "Digitised Critical Competency Levels of Advancement exist in PVSIS for many "
                "Members that have undertaken Evaluation/Follow-Up missions (>140 countries engaged "
                "historically). Public PDF reports cover only a subset; identifiable CC tables for "
                "all Members are not fully public. Coverage in this prototype currently reflects "
                "parsed public reports (others shown as N/A).",
                "No public bulk API for the full country × CC matrix. Public report catalog + PDF "
                "download endpoints exist on pvs.woah.org. Full CC extract requires Delegate/Focal "
                "Point / approved partner access or an authorised CSV from Capacity Building. "
                "Prototype: python -m scripts.ingest_public_pvs.",
                "Primary input for Legal Preparedness. IV-1A/IV-1B → Domestic Legal Readiness; "
                "IV-4/IV-6/IV-7 → Trade-Continuity Preparedness; normalised 1–5 → 0–100; missing = N/A.",
                "Keep as the sole scorer for the legal dimension in v1. Prioritise an approved "
                "PVSIS extract to reduce N/A. Record assessment year and PVS Tool edition for "
                "transparency and sensitivity checks.",
                primary=True,
            ),
            source_card(
                "FAOLEX (FAO)",
                "Enhancement candidate — Domestic legal readiness",
                "Very large open repository of national laws/regulations/policies on food, "
                "agriculture and natural resources (200k+ records). Global coverage uneven by "
                "theme and update lag; presence of texts ≠ quality or enforcement.",
                "Open data CSV downloads (no live dependency required). Searchable by country "
                "(ISO3), keywords (e.g. animal health), type of text. Full texts linked as PDF/TXT. "
                "See fao.org/faolex/opendata.",
                "Cannot replace IV-1A/IV-1B (no Level of Advancement). Useful as a proxy for "
                "whether a veterinary / animal-health legal corpus is documented and current.",
                "Optional enhancement: build a Domestic Legal Corpus Coverage score "
                "(e.g. count/recency of in-force animal-health & veterinary legislation records) "
                "shown beside PVS IV-1A/B, or used only when PVS is N/A as a weak interim signal — "
                "team to decide whether it enters the composite or stays contextual.",
            ),
            source_card(
                "WOAH Observatory",
                "Enhancement / triangulation candidate",
                "Periodic monitoring reports and dashboards on uptake of WOAH standards "
                "(trade & sanitary measures, workforce, etc.). Country-level detail varies; "
                "some underlying series reuse PVS or WTO data.",
                "Public report PDFs, indicator matrix and data catalogue (XLSX). Interactive "
                "Power BI dashboards — typically manual/semi-manual extraction, not a clean "
                "CC API for IV-1A–IV-7.",
                "Useful to triangulate trade-related standard implementation and document "
                "limitations; not a substitute for PVS Critical Competency scores.",
                "Optional: cite Observatory indicators as external benchmarks in the Country "
                "profile / Methodology, or map selected Observatory trade indicators as "
                "non-weighted context next to Trade-Continuity — do not double-count PVS "
                "if Observatory already embeds PVS.",
            ),
            source_card(
                "WTO ePing / SPS notifications",
                "Enhancement candidate — Trade-continuity / transparency",
                "Near-global WTO Membership coverage of SPS (and TBT) notifications since 1995; "
                "updated frequently. Volume of notifications ≠ legal preparedness quality; "
                "reflects transparency and regulatory activity under the SPS Agreement.",
                "ePing platform + WTO Data Portal dataset (HTML/XLSX/API). Filterable by Member, "
                "product, objective (animal health). Can be cached locally for the app.",
                "Proxy for SPS regulatory transparency and engagement with trade partners — "
                "relevant to adapting trade rules after a shock, but not zoning or compartmentalisation capacity.",
                "Optional enhancement: SPS Animal-Health Notification Activity index "
                "(normalised count / recent activity) as a secondary Trade-Continuity signal "
                "or data-quality flag. Recommend keeping outside the core PVS composite unless "
                "colleagues agree a small weight (e.g. ≤10% of trade-continuity).",
            ),
            source_card(
                "WOAH VLSP (Veterinary Legislation Support Programme)",
                "Qualitative enhancement — Domestic legal readiness",
                "Mission reports and legislation reviews for countries that requested VLSP "
                "support — valuable depth, limited and non-systematic geographic coverage.",
                "Public/selected reports via WOAH channels; manual review. Not a scored "
                "global panel comparable to PVS CCs.",
                "Narrative evidence on legislative gaps relative to Terrestrial Code Ch. 3.4 "
                "(veterinary legislation) — useful for country briefs, not a global index input.",
                "Optional: expert-coded flags (VLSP completed / major gap identified) only "
                "for demo countries, shown in Legal detail as qualitative notes — exclude "
                "from the numeric TVI unless a transparent coding protocol is agreed.",
            ),
            source_card(
                "National veterinary legislation portals / Official Gazettes",
                "Last-resort / deep-dive only",
                "Potentially complete for a given country; highly heterogeneous formats, "
                "languages and update practices; not comparable across 190+ countries.",
                "Manual collection; no single API. High cost for a datathon prototype.",
                "Gold-standard legal interpretation for case studies — not scalable for the Index.",
                "Use only for 3–5 featured demo countries to validate whether PVS IV-1A/B "
                "align with a lawyer’s reading of the statute book — quality assurance, "
                "not production scoring.",
            ),
        ),
        model_questions_block(
            "Questions for colleagues — Legal Preparedness mathematical model",
            "Please answer these so we can lock the PVS-based composite (and any enhancements) "
            "into code: weights, normalisation, missingness and invert-to-vulnerability rules.",
            [
                "Confirm Domestic Legal Readiness = f(IV-1A, IV-1B) and Trade-Continuity = "
                "f(IV-4, IV-6, IV-7). Are equal weights within each component acceptable for v1, "
                "or do you want specified weights?",
                "Confirm component weights (currently 50% / 50%). Any disease-specific override "
                "for FMD (e.g. higher weight on zoning/compartmentalisation)?",
                "PVS Levels of Advancement are 1–5: confirm linear map to 0–100 "
                "((score−1)/4×100), or a different transform (e.g. treat 1–2 as critical band)?",
                "When only some indicators in a component are available, do we renormalise "
                "weights among available indicators (current behaviour) or require a minimum "
                "set before the component is non-missing?",
                "If Domestic is available but Trade-Continuity is N/A (or vice versa), is overall "
                "Legal Preparedness = the available component, weighted partial, or N/A?",
                "Assessment vintage: if the latest public/PVSIS assessment is older than N years, "
                "do we still use it, down-weight it, or set Legal = N/A?",
                "Different PVS Tool editions renumber CCs (e.g. older IV-7 Zoning vs newer IV-6). "
                "Who validates the crosswalk we use, and is a single global crosswalk enough?",
                "Legal → TVI: confirm vulnerability contribution = 100 − Legal Preparedness "
                "(current), or another resilience transform?",
                "Enhancements (FAOLEX, WTO SPS activity): contextual only, side scores, or "
                "enter the composite? If composite, exact formulas and max weight share?",
                "Should IV-6/IV-7 (capacity) remain strictly separate from WOAH official FMD "
                "status (outcome), which is scored under Disease Exposure?",
                "For countries with no PVS extract, is N/A final for v1, or is a weak FAOLEX-only "
                "interim score allowed for demos?",
                "What sensitivity tests must we show judges (e.g. alternate weights ±10%, "
                "drop IV-7, invert transform on/off)?",
            ],
        ),
        tags.h3("Suggested decision path for Legal Preparedness"),
        tags.ol(
            tags.li(
                TagList(
                    tags.strong("Confirm PVS as sole core scorer"),
                    " for Legal Preparedness (IV-1A, IV-1B, IV-4, IV-6, IV-7).",
                )
            ),
            tags.li(
                TagList(
                    tags.strong("Secure PVSIS access or an approved extract"),
                    " to reduce N/A coverage beyond public PDFs.",
                )
            ),
            tags.li(
                TagList(
                    "Choose zero or more ",
                    tags.strong("enhancements"),
                    ": FAOLEX corpus coverage; WTO SPS activity.",
                )
            ),
            tags.li(
                TagList(
                    "Decide whether enhancements are ",
                    tags.strong("contextual only"),
                    ", ",
                    tags.strong("displayed beside"),
                    " component scores, or ",
                    tags.strong("enter the weighted composite"),
                    " (with explicit weights).",
                )
            ),
            tags.li(
                "Treat VLSP/gazettes as qualitative QA only; keep disease status under Disease Exposure."
            ),
        ),
    )
