"""
Trade Vulnerability Index — Shiny for Python application.

Run locally:
    shiny run app.py

Deploy:
    rsconnect deploy shiny . --name tvi-woah-datathon
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path when launched via shiny run
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from htmltools import HTML, TagList, tags
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

from config.settings import (
    ACTIVE_DISEASE,
    APP_SUBTITLE,
    APP_TITLE,
    ASSETS_DIR,
    DIMENSION_WEIGHTS,
    DISEASE_LABELS,
    LEGAL_COMPONENT_WEIGHTS,
    LEGAL_INDICATOR_WEIGHTS,
    LEGAL_INDICATORS,
    LEGAL_VULN_TRANSFORM,
    MISSING_DATA,
)
from config.woah_regions import WOAH_REGIONS
from src.calculations.benchmarks import comparison_frame
from src.calculations.classification import classify_css_class, classify_score
from src.calculations.drivers import country_drivers
from src.pipeline.build_dataset import load_processed
from src.ui.charts import (
    choropleth_tvi,
    comparison_grouped_bars,
    dimension_contribution_bars,
    legal_indicator_bars,
    ranking_table_data,
)

# ---------------------------------------------------------------------------
# Pre-load processed data (fast UI; rebuild via scripts.build_data)
# ---------------------------------------------------------------------------
DATA = load_processed()
TVI = DATA["tvi"]
DISEASE = DATA["disease"].set_index("iso3")
ECONOMIC = DATA["economic"].set_index("iso3")
LEGAL = DATA["legal"].set_index("iso3")
LEGAL_IND = DATA["legal_indicators"]

COUNTRY_CHOICES = {
    "": "— Select a country —",
    **{
        r.iso3: r.country
        for r in TVI.sort_values("country").itertuples()
    },
}

DISEASE_CHOICES = {
    "FMD": DISEASE_LABELS["FMD"],
    "PPR": DISEASE_LABELS["PPR"],
    "ASF": DISEASE_LABELS["ASF"],
    "HPAI": DISEASE_LABELS["HPAI"],
}


def _fmt(val, digits=0) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return MISSING_DATA["missing_label"]
    return f"{val:.{digits}f}"


def _score_html(score, out_of=100) -> str:
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return MISSING_DATA["missing_label"]
    return f"{score:.0f} <span>/ {out_of}</span>"


def scorecard(title: str, css: str, score, classification: str, explain: str, contrib: str):
    cls = classify_css_class(None if score is None or pd.isna(score) else float(score))
    return ui.div(
        {"class": f"tvi-scorecard {css}"},
        tags.p({"class": "tvi-scorecard-label"}, title),
        tags.p({"class": "tvi-scorecard-score"}, HTML(_score_html(score))),
        tags.span({"class": f"tvi-scorecard-class {cls}"}, classification),
        tags.p({"class": "tvi-scorecard-explain"}, explain),
        tags.p({"class": "tvi-scorecard-contrib"}, contrib),
    )


css_path = ASSETS_DIR / "styles.css"
app_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
app_ui = ui.page_fluid(
    ui.tags.style(app_css),
    ui.div(
        {"class": "tvi-shell"},
        ui.div(
            {"class": "tvi-header"},
            ui.div(
                {"class": "tvi-header-inner"},
                ui.div(
                    tags.p({"class": "tvi-brand"}, "WOAH Datathon · Challenge 4"),
                    tags.h1({"class": "tvi-title"}, APP_TITLE),
                    tags.p({"class": "tvi-subtitle"}, APP_SUBTITLE),
                ),
                ui.div(
                    {"class": "tvi-header-meta"},
                    tags.div("Decision-support prototype"),
                    tags.div("Focus: Foot-and-Mouth Disease"),
                ),
            ),
        ),
        ui.div(
            {"class": "tvi-main"},
            ui.navset_tab(
                # ========== GLOBAL ==========
                ui.nav_panel(
                    "Global view",
                    ui.div(
                        {"class": "tvi-controls"},
                        ui.input_select(
                            "disease",
                            "Disease",
                            choices=DISEASE_CHOICES,
                            selected=ACTIVE_DISEASE,
                        ),
                        ui.input_select(
                            "region_filter",
                            "WOAH region filter",
                            choices={"All": "All regions", **{r: r for r in WOAH_REGIONS}},
                            selected="All",
                        ),
                        ui.input_select(
                            "country",
                            "Select country",
                            choices=COUNTRY_CHOICES,
                            selected="",
                        ),
                    ),
                    ui.output_ui("disease_notice"),
                    ui.output_ui("global_stats"),
                    ui.div(
                        {"class": "tvi-grid-2"},
                        ui.div(
                            {"class": "tvi-panel"},
                            tags.h2("Where is vulnerability highest?"),
                            tags.p(
                                {"class": "tvi-panel-intro"},
                                "Countries coloured by Trade Vulnerability Index (0–100). "
                                "Hover for dimension scores; select a country above or in the Country profile tab.",
                            ),
                            output_widget("world_map", height="520px"),
                            ui.div(
                                {"class": "tvi-legend"},
                                tags.span("Lower TVI"),
                                tags.div({"class": "tvi-legend-bar"}),
                                tags.span("Higher TVI"),
                            ),
                        ),
                        ui.div(
                            {"class": "tvi-panel"},
                            tags.h2("Highest vulnerability"),
                            tags.p(
                                {"class": "tvi-panel-intro"},
                                "Top countries by TVI in the current filter.",
                            ),
                            ui.output_ui("ranking_table"),
                        ),
                    ),
                ),
                # ========== COUNTRY ==========
                ui.nav_panel(
                    "Country profile",
                    ui.div(
                        {"class": "tvi-controls"},
                        ui.input_select(
                            "country_profile",
                            "Country",
                            choices=COUNTRY_CHOICES,
                            selected="",
                        ),
                    ),
                    ui.output_ui("country_body"),
                ),
                # ========== COMPARE ==========
                ui.nav_panel(
                    "Compare",
                    ui.div(
                        {"class": "tvi-controls"},
                        ui.input_select(
                            "compare_country",
                            "Focal country",
                            choices=COUNTRY_CHOICES,
                            selected="",
                        ),
                        ui.input_selectize(
                            "peer_countries",
                            "Peer countries",
                            choices={k: v for k, v in COUNTRY_CHOICES.items() if k},
                            multiple=True,
                        ),
                    ),
                    ui.output_ui("compare_intro"),
                    ui.div(
                        {"class": "tvi-panel"},
                        tags.h2("Country vs global vs regional benchmarks"),
                        output_widget("compare_chart", height="400px"),
                    ),
                ),
                # ========== LEGAL DETAIL ==========
                ui.nav_panel(
                    "Legal preparedness",
                    ui.div(
                        {"class": "tvi-controls"},
                        ui.input_select(
                            "legal_country",
                            "Country",
                            choices=COUNTRY_CHOICES,
                            selected="",
                        ),
                    ),
                    ui.output_ui("legal_body"),
                ),
                # ========== METHODOLOGY ==========
                ui.nav_panel(
                    "About / Methodology",
                    ui.div(
                        {"class": "tvi-panel tvi-prose"},
                        tags.h2("About the Trade Vulnerability Index"),
                        tags.p(
                            "The Trade Vulnerability Index (TVI) is a decision-support metric that "
                            "summarises how vulnerable a country is to the trade-related consequences "
                            "of an animal-health shock. This prototype focuses on Foot-and-Mouth Disease (FMD)."
                        ),
                        tags.h3("Conceptual model"),
                        tags.p(
                            "TVI combines three dimensions. Disease Exposure and Economic Sensitivity "
                            "increase vulnerability. Legal Preparedness is a resilience score: higher "
                            "preparedness reduces vulnerability."
                        ),
                        ui.div(
                            {"class": "tvi-flow"},
                            ui.div(
                                {"class": "tvi-flow-node risk"},
                                tags.strong("Disease Exposure"),
                                tags.span("Risk / exposure"),
                            ),
                            tags.div({"class": "tvi-flow-plus"}, "+"),
                            ui.div(
                                {"class": "tvi-flow-node econ"},
                                tags.strong("Economic Sensitivity"),
                                tags.span("Risk / exposure"),
                            ),
                            tags.div({"class": "tvi-flow-plus"}, "+"),
                            ui.div(
                                {"class": "tvi-flow-node prep"},
                                tags.strong("Legal Preparedness"),
                                tags.span("Resilience (inverted)"),
                            ),
                            tags.div({"class": "tvi-flow-plus"}, "→"),
                            ui.div(
                                {"class": "tvi-flow-node tvi"},
                                tags.strong("Trade Vulnerability Index"),
                                tags.span("Weighted composite"),
                            ),
                        ),
                        ui.div(
                            {"class": "tvi-callout"},
                            HTML(
                                "<strong>Current data status:</strong> Disease Exposure and Economic "
                                "Sensitivity are <strong>mock modules</strong> (replaceable). Legal "
                                "Preparedness uses a <strong>placeholder methodology</strong> with "
                                "synthetic PVS-style scores until real assessment data and scoring "
                                "rules are supplied. No values are silently imputed to zero."
                            ),
                        ),
                        tags.h3("Weights (configurable)"),
                        tags.ul(
                            tags.li(
                                f"Disease Exposure: {DIMENSION_WEIGHTS['disease_exposure']:.3f}"
                            ),
                            tags.li(
                                f"Economic Sensitivity: {DIMENSION_WEIGHTS['economic_sensitivity']:.3f}"
                            ),
                            tags.li(
                                f"Legal Preparedness: {DIMENSION_WEIGHTS['legal_preparedness']:.3f}"
                            ),
                        ),
                        tags.p(
                            f"Legal vulnerability transform: {LEGAL_VULN_TRANSFORM} "
                            "(preparedness → 100 − preparedness before aggregation)."
                        ),
                        tags.h3("Legal Preparedness construction"),
                        tags.p("Two components, with configurable weights:"),
                        tags.ul(
                            tags.li(
                                f"Domestic Legal Readiness "
                                f"({LEGAL_COMPONENT_WEIGHTS['domestic_legal_readiness']:.0%}): "
                                "IV-1A, IV-1B"
                            ),
                            tags.li(
                                f"Trade-Continuity Preparedness "
                                f"({LEGAL_COMPONENT_WEIGHTS['trade_continuity_preparedness']:.0%}): "
                                "IV-4, IV-6, IV-7"
                            ),
                        ),
                        tags.p("Indicator weights:"),
                        tags.ul(
                            *[
                                tags.li(f"{code}: {LEGAL_INDICATORS[code]['name']} — {w:.2f}")
                                for code, w in LEGAL_INDICATOR_WEIGHTS.items()
                            ]
                        ),
                        tags.h3("PVS data sources"),
                        tags.p(
                            "Authoritative sources for future population of legal indicators include "
                            "WOAH PVS Pathway assessment reports and the PVS Information System (PVSIS). "
                            "There is currently no public bulk API for Critical Competency scores; "
                            "this application ingests local CSV/Excel/JSON files placed in data/raw/ "
                            "and does not depend on a live network call."
                        ),
                        tags.h3("Missing data"),
                        tags.p(
                            "Missing observations are flagged explicitly and displayed as "
                            f"“{MISSING_DATA['missing_label']}”. They are never replaced with zero."
                        ),
                        tags.h3("Limitations"),
                        tags.ul(
                            tags.li("Prototype for the WOAH Datathon — not an official WOAH product."),
                            tags.li("Mock epidemiological and economic dimensions."),
                            tags.li("Placeholder legal scores pending real methodology and data."),
                            tags.li("Equal dimension weights are a starting point for sensitivity testing."),
                            tags.li("WOAH region membership is approximate for demonstration."),
                        ),
                        tags.h3("Replacing modules"),
                        tags.p(
                            "Replace src/modules/disease_exposure.py, economic_sensitivity.py, "
                            "and the scoring logic in legal_preparedness.py independently. "
                            "Re-run python -m scripts.build_data, then restart the app. "
                            "Weights and thresholds live in config/settings.py."
                        ),
                    ),
                ),
                id="main_tabs",
            ),
        ),
        ui.div(
            {"class": "tvi-footer"},
            "Trade Vulnerability Index · WOAH Datathon prototype · "
            "Analytical modules are separable from this interface · Not for operational use",
        ),
    ),
)


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
def server(input, output, session):
    # Keep country selectors in sync
    @reactive.effect
    def _sync_from_global():
        c = input.country()
        if c:
            ui.update_select("country_profile", selected=c)
            ui.update_select("compare_country", selected=c)
            ui.update_select("legal_country", selected=c)

    @reactive.effect
    def _sync_from_profile():
        c = input.country_profile()
        if c:
            ui.update_select("country", selected=c)
            ui.update_select("compare_country", selected=c)
            ui.update_select("legal_country", selected=c)

    @reactive.calc
    def filtered_tvi() -> pd.DataFrame:
        df = TVI.copy()
        region = input.region_filter()
        if region and region != "All":
            df = df[df["region"] == region]
        return df

    @reactive.calc
    def active_iso3() -> str | None:
        for key in (input.country_profile, input.country, input.compare_country, input.legal_country):
            v = key()
            if v:
                return v
        return None

    @render.ui
    def disease_notice():
        d = input.disease()
        if d != "FMD":
            return ui.div(
                {"class": "tvi-callout"},
                f"{DISEASE_LABELS.get(d, d)} is not yet available. Showing FMD results.",
            )
        return ui.div()

    @render.ui
    def global_stats():
        df = filtered_tvi()
        valid = df.dropna(subset=["tvi"])
        if valid.empty:
            avg = high = n = "—"
            top = "—"
        else:
            avg = f"{valid['tvi'].mean():.1f}"
            high = f"{valid['tvi'].max():.1f}"
            n = f"{len(valid)}"
            top = valid.iloc[0]["country"]
        coverage = (
            f"{int(LEGAL['legal_preparedness'].notna().sum())} / {len(LEGAL)}"
        )
        return ui.div(
            {"class": "tvi-stats"},
            ui.div(
                {"class": "tvi-stat"},
                tags.p({"class": "tvi-stat-label"}, "Countries scored"),
                tags.p({"class": "tvi-stat-value"}, n),
                tags.p({"class": "tvi-stat-note"}, "with complete TVI"),
            ),
            ui.div(
                {"class": "tvi-stat"},
                tags.p({"class": "tvi-stat-label"}, "Mean TVI"),
                tags.p({"class": "tvi-stat-value"}, avg),
                tags.p({"class": "tvi-stat-note"}, "in current filter"),
            ),
            ui.div(
                {"class": "tvi-stat"},
                tags.p({"class": "tvi-stat-label"}, "Highest TVI"),
                tags.p({"class": "tvi-stat-value"}, high),
                tags.p({"class": "tvi-stat-note"}, top),
            ),
            ui.div(
                {"class": "tvi-stat"},
                tags.p({"class": "tvi-stat-label"}, "Legal coverage"),
                tags.p({"class": "tvi-stat-value"}, coverage.split("/")[0].strip()),
                tags.p({"class": "tvi-stat-note"}, f"of {coverage.split('/')[-1].strip()} countries"),
            ),
        )

    @render_widget
    def world_map():
        df = filtered_tvi()
        return choropleth_tvi(df, selected_iso3=input.country() or None)

    @render.ui
    def ranking_table():
        df = ranking_table_data(filtered_tvi(), n=12)
        if df.empty:
            return tags.p({"class": "tvi-empty"}, "No countries in this filter.")
        header = tags.tr(*[tags.th(c) for c in df.columns if c != "ISO3"])
        rows = []
        for r in df.itertuples(index=False):
            rows.append(
                tags.tr(
                    tags.td(r[0]),  # Country
                    tags.td(r[2]),  # Region
                    tags.td(f"{r[3]:.1f}" if pd.notna(r[3]) else "—"),
                    tags.td(f"{r[4]:.0f}" if pd.notna(r[4]) else "—"),
                    tags.td(f"{r[5]:.0f}" if pd.notna(r[5]) else "—"),
                    tags.td(f"{r[6]:.0f}" if pd.notna(r[6]) else "—"),
                )
            )
        return tags.table(
            {"class": "tvi-rank-table"},
            tags.thead(header),
            tags.tbody(*rows),
        )

    @render.ui
    def country_body():
        iso3 = input.country_profile()
        if not iso3:
            return ui.div(
                {"class": "tvi-panel"},
                tags.p(
                    {"class": "tvi-panel-intro"},
                    "Select a country to inspect why it is vulnerable: dimension scores, "
                    "contributions, and data-driven drivers.",
                ),
            )
        row = TVI[TVI["iso3"] == iso3]
        if row.empty:
            return tags.p("Country not found.")
        r = row.iloc[0]
        drow = DISEASE.loc[iso3] if iso3 in DISEASE.index else None
        erow = ECONOMIC.loc[iso3] if iso3 in ECONOMIC.index else None

        drivers = country_drivers(
            iso3,
            r,
            drow if drow is not None else pd.Series(dtype=float),
            erow if erow is not None else pd.Series(dtype=float),
            LEGAL_IND,
        )

        risk_items = (
            [tags.li(t) for t in drivers["high_contribution"]]
            or [tags.li({"class": "tvi-empty"}, "No strong risk drivers identified.")]
        )
        prot_items = (
            [tags.li(t) for t in drivers["protective_factors"]]
            or [tags.li({"class": "tvi-empty"}, "No strong protective factors identified.")]
        )

        w = DIMENSION_WEIGHTS
        return TagList(
            ui.div(
                {"class": "tvi-panel"},
                ui.div(
                    {"class": "tvi-country-header"},
                    ui.div(
                        tags.h2({"class": "tvi-country-name"}, r["country"]),
                        tags.p(
                            {"class": "tvi-country-disease"},
                            f"{DISEASE_LABELS['FMD']} · {r['region']}",
                        ),
                    ),
                    ui.div(
                        {"class": "tvi-tvi-block"},
                        tags.p({"class": "tvi-tvi-label"}, "Trade Vulnerability Index"),
                        tags.p(
                            {"class": "tvi-tvi-score"},
                            HTML(_score_html(r["tvi"])),
                        ),
                        tags.span(
                            {
                                "class": f"tvi-scorecard-class {classify_css_class(r['tvi'] if pd.notna(r['tvi']) else None)}"
                            },
                            r["tvi_class"] if pd.notna(r["tvi"]) else MISSING_DATA["missing_label"],
                        ),
                    ),
                ),
                ui.div(
                    {"class": "tvi-grid-3"},
                    scorecard(
                        "Disease Exposure",
                        "exposure",
                        r["disease_exposure"],
                        r["disease_class"],
                        "Pressure from domestic status, network links, and trade/movement exposure. "
                        "(Mock module — replaceable.)",
                        f"Contribution to TVI: {_fmt(r['contrib_disease'], 1)} "
                        f"(weight {w['disease_exposure']:.0%})",
                    ),
                    scorecard(
                        "Economic Sensitivity",
                        "economic",
                        r["economic_sensitivity"],
                        r["economic_class"],
                        "Sensitivity of livestock economy and trade structure to an animal-health shock. "
                        "(Mock module — replaceable.)",
                        f"Contribution to TVI: {_fmt(r['contrib_economic'], 1)} "
                        f"(weight {w['economic_sensitivity']:.0%})",
                    ),
                    scorecard(
                        "Legal Preparedness",
                        "preparedness",
                        r["legal_preparedness"],
                        r["legal_class"],
                        "Domestic legal readiness and trade-continuity preparedness. "
                        "Higher score = stronger protection (reduces TVI).",
                        f"Vulnerability contribution: {_fmt(r['legal_vulnerability'], 1)} "
                        f"(= 100 − preparedness × weight {w['legal_preparedness']:.0%})",
                    ),
                ),
            ),
            ui.div(
                {"class": "tvi-grid-2"},
                ui.div(
                    {"class": "tvi-panel"},
                    tags.h2("What is driving vulnerability?"),
                    tags.p(
                        {"class": "tvi-panel-intro"},
                        "Drivers are generated from indicator values, not hand-written narratives.",
                    ),
                    ui.div(
                        {"class": "tvi-drivers"},
                        ui.div(
                            {"class": "tvi-driver-col risk"},
                            tags.h4("High contribution to vulnerability"),
                            tags.ul({"class": "tvi-driver-list"}, *risk_items),
                        ),
                        ui.div(
                            {"class": "tvi-driver-col protect"},
                            tags.h4("Protective factors"),
                            tags.ul({"class": "tvi-driver-list"}, *prot_items),
                        ),
                    ),
                ),
                ui.div(
                    {"class": "tvi-panel"},
                    tags.h2("Weighted contributions"),
                    tags.p(
                        {"class": "tvi-panel-intro"},
                        "How each dimension feeds the overall TVI after weighting. "
                        "Legal bar shows vulnerability contribution (inverted preparedness).",
                    ),
                    output_widget("contrib_chart", height="240px"),
                ),
            ),
        )

    @render_widget
    def contrib_chart():
        iso3 = input.country_profile()
        if not iso3:
            import plotly.graph_objects as go

            return go.Figure()
        r = TVI[TVI["iso3"] == iso3].iloc[0]
        return dimension_contribution_bars(r)

    @render.ui
    def compare_intro():
        iso3 = input.compare_country()
        if not iso3:
            return ui.div(
                {"class": "tvi-panel"},
                tags.p(
                    {"class": "tvi-panel-intro"},
                    "Compare a focal country against the global average, its WOAH regional average, "
                    "and optional peer countries.",
                ),
            )
        r = TVI[TVI["iso3"] == iso3].iloc[0]
        return ui.div(
            {"class": "tvi-callout"},
            HTML(
                f"<strong>{r['country']}</strong> · Region: {r['region']} · "
                f"TVI {_fmt(r['tvi'], 1)} ({r['tvi_class']})"
            ),
        )

    @render_widget
    def compare_chart():
        iso3 = input.compare_country()
        import plotly.graph_objects as go

        if not iso3:
            return go.Figure()
        row = TVI[TVI["iso3"] == iso3].iloc[0]
        peers = list(input.peer_countries() or [])
        peers = [p for p in peers if p and p != iso3]
        comp = comparison_frame(row, TVI, peers if peers else None)
        return comparison_grouped_bars(comp)

    @render.ui
    def legal_body():
        iso3 = input.legal_country()
        if not iso3:
            return ui.div(
                {"class": "tvi-panel"},
                tags.p(
                    {"class": "tvi-panel-intro"},
                    "Inspect Domestic Legal Readiness and Trade-Continuity Preparedness indicators "
                    "(IV-1A, IV-1B, IV-4, IV-6, IV-7).",
                ),
            )
        if iso3 not in LEGAL.index:
            return tags.p("No legal data for this country.")
        lr = LEGAL.loc[iso3]
        ind = LEGAL_IND[LEGAL_IND["iso3"] == iso3].copy()

        n_avail = int(lr["legal_indicators_available"])
        n_tot = int(lr["legal_indicators_total"])
        # Global coverage for this indicator set
        countries_with_any = int(
            LEGAL_IND.loc[~LEGAL_IND["missing_data_flag"], "iso3"].nunique()
        )
        n_countries = int(LEGAL_IND["iso3"].nunique())

        def ind_rows(codes):
            rows = []
            for code in codes:
                sub = ind[ind["indicator_code"] == code]
                if sub.empty:
                    continue
                r = sub.iloc[0]
                missing = bool(r["missing_data_flag"]) or pd.isna(r.get("score_100"))
                score_cell = (
                    tags.td({"class": "tvi-missing"}, MISSING_DATA["missing_label"])
                    if missing
                    else tags.td(f"{r['score_100']:.0f} / 100 (raw {r['score']} / 5)")
                )
                year = "—" if missing or pd.isna(r.get("assessment_year")) else str(int(r["assessment_year"]))
                interp = LEGAL_INDICATORS.get(code, {}).get("description", "")
                if not missing and pd.notna(r.get("score_100")):
                    interp = (
                        f"{classify_score(float(r['score_100']), preparedness=True)} preparedness. "
                        + interp
                    )
                rows.append(
                    tags.tr(
                        tags.td(tags.strong(code)),
                        tags.td(r.get("indicator_name", "")),
                        score_cell,
                        tags.td(year),
                        tags.td(r.get("source", "—")),
                        tags.td(interp),
                    )
                )
            return rows

        domestic_codes = ["IV-1A", "IV-1B"]
        trade_codes = ["IV-4", "IV-6", "IV-7"]

        return TagList(
            ui.div(
                {"class": "tvi-panel"},
                tags.h2(f"Legal preparedness — {lr['country']}"),
                ui.div(
                    {"class": "tvi-coverage"},
                    tags.span(f"Country indicator coverage: {n_avail} / {n_tot}"),
                    tags.span("·"),
                    tags.span(f"PVS coverage (any indicator): {countries_with_any} / {n_countries} countries"),
                ),
                ui.div(
                    {"class": "tvi-grid-3"},
                    scorecard(
                        "Domestic Legal Readiness",
                        "preparedness",
                        lr["domestic_legal_readiness"],
                        classify_score(
                            None
                            if pd.isna(lr["domestic_legal_readiness"])
                            else float(lr["domestic_legal_readiness"]),
                            preparedness=True,
                        ),
                        "IV-1A and IV-1B composite.",
                        f"Component weight {LEGAL_COMPONENT_WEIGHTS['domestic_legal_readiness']:.0%}",
                    ),
                    scorecard(
                        "Trade-Continuity Preparedness",
                        "preparedness",
                        lr["trade_continuity_preparedness"],
                        classify_score(
                            None
                            if pd.isna(lr["trade_continuity_preparedness"])
                            else float(lr["trade_continuity_preparedness"]),
                            preparedness=True,
                        ),
                        "IV-4, IV-6 and IV-7 composite.",
                        f"Component weight {LEGAL_COMPONENT_WEIGHTS['trade_continuity_preparedness']:.0%}",
                    ),
                    scorecard(
                        "Legal Preparedness (overall)",
                        "preparedness",
                        lr["legal_preparedness"],
                        classify_score(
                            None
                            if pd.isna(lr["legal_preparedness"])
                            else float(lr["legal_preparedness"]),
                            preparedness=True,
                        ),
                        "Weighted combination of the two components. Higher = more prepared.",
                        "Inverted when entering TVI (100 − score).",
                    ),
                ),
            ),
            ui.div(
                {"class": "tvi-panel"},
                tags.h2("Indicator detail"),
                output_widget("legal_chart", height="300px"),
                tags.h3("Domestic Legal Readiness"),
                tags.table(
                    {"class": "tvi-legal-table"},
                    tags.thead(
                        tags.tr(
                            tags.th("Code"),
                            tags.th("Indicator"),
                            tags.th("Score"),
                            tags.th("Year"),
                            tags.th("Source"),
                            tags.th("Interpretation"),
                        )
                    ),
                    tags.tbody(*ind_rows(domestic_codes)),
                ),
                tags.h3("Trade-Continuity Preparedness"),
                tags.table(
                    {"class": "tvi-legal-table"},
                    tags.thead(
                        tags.tr(
                            tags.th("Code"),
                            tags.th("Indicator"),
                            tags.th("Score"),
                            tags.th("Year"),
                            tags.th("Source"),
                            tags.th("Interpretation"),
                        )
                    ),
                    tags.tbody(*ind_rows(trade_codes)),
                ),
            ),
        )

    @render_widget
    def legal_chart():
        iso3 = input.legal_country()
        import plotly.graph_objects as go

        if not iso3:
            return go.Figure()
        return legal_indicator_bars(LEGAL_IND, iso3)


app = App(app_ui, server)
