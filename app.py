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
    LEGAL_INDICATORS,
    LEGAL_VULN_TRANSFORM,
    MISSING_DATA,
)
from config.woah_regions import WOAH_REGIONS
from src.calculations.benchmarks import comparison_frame
from src.calculations.classification import classify_css_class, classify_score
from src.calculations.drivers import country_drivers
from src.modules.economic_sensitivity import ECONOMIC_INDICATORS
from src.pipeline.build_dataset import load_processed
from src.ui.charts import (
    choropleth_tvi,
    comparison_grouped_bars,
    dimension_contribution_bars,
    disease_indicator_bars,
    economic_indicator_bars,
    legal_indicator_bars,
    ranking_table_data,
)
from src.ui.methodology_disease import disease_methodology_section
from src.ui.methodology_economic import economic_methodology_section
from src.ui.methodology_intro import methodology_intro_section
from src.ui.methodology_legal import legal_methodology_section

# ---------------------------------------------------------------------------
# Pre-load processed data (fast UI; rebuild via scripts.build_data)
# ---------------------------------------------------------------------------
DATA = load_processed()
TVI = DATA["tvi"]
DISEASE = DATA["disease"].set_index("iso3")
DISEASE_IND = DATA["disease_indicators"]
ECONOMIC = DATA["economic"].set_index("iso3")
ECONOMIC_IND = DATA["economic_indicators"]
LEGAL = DATA["legal"].set_index("iso3")
LEGAL_IND = DATA["legal_indicators"]

COUNTRY_CHOICES = {
    "": "— Select a country —",
    **{
        r.iso3: r.country
        for r in TVI.sort_values("country").itertuples()
    },
}

# Disease Exposure tab: countries with a non-null Disease Exposure score
_ISO3_WITH_DISEASE = set(
    DISEASE.index[DISEASE["disease_exposure"].notna()].astype(str)
)
_disease_rows = TVI.sort_values("country")
_DISEASE_WITH = {
    r.iso3: r.country
    for r in _disease_rows.itertuples()
    if r.iso3 in _ISO3_WITH_DISEASE
}
_DISEASE_WITHOUT = {
    r.iso3: f"{r.country} (N/A)"
    for r in _disease_rows.itertuples()
    if r.iso3 not in _ISO3_WITH_DISEASE
}
DISEASE_COUNTRY_CHOICES_WITH_DATA = {
    "": "— Select a country with disease data —",
    **_DISEASE_WITH,
}
DISEASE_COUNTRY_CHOICES_ALL = {
    "": "— Select a country —",
    f"Disease data available ({len(_DISEASE_WITH)})": _DISEASE_WITH,
    f"No disease data — N/A ({len(_DISEASE_WITHOUT)})": _DISEASE_WITHOUT,
}

# Economic Sensitivity tab (mock: all countries currently scored)
_ISO3_WITH_ECONOMIC = set(
    ECONOMIC.index[ECONOMIC["economic_sensitivity"].notna()].astype(str)
)
_econ_rows = TVI.sort_values("country")
_ECONOMIC_WITH = {
    r.iso3: r.country
    for r in _econ_rows.itertuples()
    if r.iso3 in _ISO3_WITH_ECONOMIC
}
_ECONOMIC_WITHOUT = {
    r.iso3: f"{r.country} (N/A)"
    for r in _econ_rows.itertuples()
    if r.iso3 not in _ISO3_WITH_ECONOMIC
}
ECONOMIC_COUNTRY_CHOICES_WITH_DATA = {
    "": "— Select a country with economic data —",
    **_ECONOMIC_WITH,
}
ECONOMIC_COUNTRY_CHOICES_ALL = {
    "": "— Select a country —",
    f"Economic data available ({len(_ECONOMIC_WITH)})": _ECONOMIC_WITH,
    f"No economic data — N/A ({len(_ECONOMIC_WITHOUT)})": _ECONOMIC_WITHOUT,
}

# Legal tab: countries with a non-null Legal Preparedness score
_ISO3_WITH_LEGAL = set(
    LEGAL.index[LEGAL["legal_preparedness"].notna()].astype(str)
)
_legal_rows = TVI.sort_values("country")
_LEGAL_WITH = {
    r.iso3: r.country
    for r in _legal_rows.itertuples()
    if r.iso3 in _ISO3_WITH_LEGAL
}
_LEGAL_WITHOUT = {
    r.iso3: f"{r.country} (N/A)"
    for r in _legal_rows.itertuples()
    if r.iso3 not in _ISO3_WITH_LEGAL
}
# Default dropdown = only countries with data (browsers cannot reliably colour <option> text)
LEGAL_COUNTRY_CHOICES_WITH_DATA = {
    "": "— Select a country with legal data —",
    **_LEGAL_WITH,
}
LEGAL_COUNTRY_CHOICES_ALL = {
    "": "— Select a country —",
    f"Legal data available ({len(_LEGAL_WITH)})": _LEGAL_WITH,
    f"No legal data — N/A ({len(_LEGAL_WITHOUT)})": _LEGAL_WITHOUT,
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
                                "Hover for dimension scores; open Country profile to inspect a country.",
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
                # ========== DISEASE EXPOSURE ==========
                ui.nav_panel(
                    "Disease exposure",
                    ui.div(
                        {"class": "tvi-controls tvi-legal-controls"},
                        ui.input_select(
                            "disease_country",
                            f"Country with disease data ({len(_DISEASE_WITH)})",
                            choices=DISEASE_COUNTRY_CHOICES_WITH_DATA,
                            selected=next(iter(_DISEASE_WITH), ""),
                        ),
                        ui.input_checkbox(
                            "disease_show_all",
                            f"Also list countries without disease data ({len(_DISEASE_WITHOUT)} N/A)",
                            value=False,
                        ),
                        ui.div(
                            {"class": "tvi-legal-select-legend"},
                            tags.span(
                                {"class": "tvi-legal-hint"},
                                "Dropdown lists countries with RMT disease-status scores by default. "
                                "Tick the box only if you need N/A countries.",
                            ),
                        ),
                    ),
                    ui.output_ui("disease_body"),
                ),
                # ========== ECONOMIC SENSITIVITY ==========
                ui.nav_panel(
                    "Economic sensitivity",
                    ui.div(
                        {"class": "tvi-controls tvi-legal-controls"},
                        ui.input_select(
                            "economic_country",
                            f"Country with economic data ({len(_ECONOMIC_WITH)})",
                            choices=ECONOMIC_COUNTRY_CHOICES_WITH_DATA,
                            selected=next(iter(_ECONOMIC_WITH), ""),
                        ),
                        ui.input_checkbox(
                            "economic_show_all",
                            f"Also list countries without economic data ({len(_ECONOMIC_WITHOUT)} N/A)",
                            value=False,
                        ),
                        ui.div(
                            {"class": "tvi-legal-select-legend"},
                            tags.span(
                                {"class": "tvi-legal-hint"},
                                "Mock module — all countries currently have placeholder scores. "
                                "Replace with FAOSTAT / Comtrade when colleagues confirm.",
                            ),
                        ),
                    ),
                    ui.output_ui("economic_body"),
                ),
                # ========== LEGAL DETAIL ==========
                ui.nav_panel(
                    "Legal preparedness",
                    ui.div(
                        {"class": "tvi-controls tvi-legal-controls"},
                        ui.input_select(
                            "legal_country",
                            f"Country with legal data ({len(_LEGAL_WITH)})",
                            choices=LEGAL_COUNTRY_CHOICES_WITH_DATA,
                            selected=next(iter(_LEGAL_WITH), ""),
                        ),
                        ui.input_checkbox(
                            "legal_show_all",
                            f"Also list countries without legal data ({len(_LEGAL_WITHOUT)} N/A)",
                            value=False,
                        ),
                        ui.div(
                            {"class": "tvi-legal-select-legend"},
                            tags.span(
                                {"class": "tvi-legal-hint"},
                                "Dropdown lists countries with PVS legal scores by default "
                                "(green selector). Tick the box only if you need N/A countries.",
                            ),
                        ),
                    ),
                    ui.output_ui("legal_body"),
                ),
                # ========== METHODOLOGY ==========
                ui.nav_panel(
                    "About / Methodology",
                    ui.div(
                        {"class": "tvi-panel tvi-prose"},
                        methodology_intro_section(),
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
                                "<strong>Current data status:</strong> Disease Exposure uses "
                                "<strong>EuFMD RMT curated disease-status and mitigation</strong> "
                                f"for {len(_DISEASE_WITH)} neighbourhood countries, with "
                                "<strong>provisional pathway connections</strong> "
                                "(bilateral Comtrade/proximity not yet wired). Other countries are "
                                f"<strong>{MISSING_DATA['missing_label']}</strong>. "
                                "Economic Sensitivity is still a <strong>mock module</strong> "
                                "(see Economic Sensitivity tab). "
                                "Legal Preparedness is scored from <strong>public WOAH PVS reports</strong> "
                                "where Levels of Advancement could be extracted; otherwise "
                                f"<strong>{MISSING_DATA['missing_label']}</strong> "
                                "(never imputed to zero)."
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
                        tags.h2("Dimension methodology (detail)"),
                        tags.p(
                            "The sections below document each dimension’s concept note, candidate "
                            "data sources and open questions for colleagues."
                        ),
                        disease_methodology_section(),
                        economic_methodology_section(),
                        legal_methodology_section(),
                        tags.h3("Missing data"),
                        tags.p(
                            "Missing observations are flagged explicitly and displayed as "
                            f"“{MISSING_DATA['missing_label']}”. They are never replaced with zero."
                        ),
                        tags.h3("Limitations"),
                        tags.ul(
                            tags.li("Prototype for the WOAH Datathon — not an official WOAH product."),
                            tags.li(
                                "Disease Exposure is an RMT provisional adaptation: curated EuFMD "
                                "status/mitigation for a limited country set; connections are "
                                "provisional until bilateral trade/proximity data are added."
                            ),
                            tags.li("Economic Sensitivity remains a mock module."),
                            tags.li(
                                "Legal scores are PVS-based proxies; public coverage is incomplete; "
                                "assessment years and PVS Tool editions differ across countries."
                            ),
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
    # Keep country selectors in sync from Country profile
    @reactive.effect
    def _sync_from_profile():
        c = input.country_profile()
        if c:
            ui.update_select("compare_country", selected=c)
            if c in _ISO3_WITH_DISEASE or input.disease_show_all():
                ui.update_select("disease_country", selected=c)
            if c in _ISO3_WITH_ECONOMIC or input.economic_show_all():
                ui.update_select("economic_country", selected=c)
            if c in _ISO3_WITH_LEGAL or input.legal_show_all():
                ui.update_select("legal_country", selected=c)

    @reactive.effect
    @reactive.event(input.disease_show_all, ignore_none=False)
    def _disease_country_choices():
        """Default: only countries with RMT disease data."""
        show_all = bool(input.disease_show_all())
        current = input.disease_country()
        if show_all:
            choices = DISEASE_COUNTRY_CHOICES_ALL
            label = "Country"
            selected = current if current else next(iter(_DISEASE_WITH), "")
        else:
            choices = DISEASE_COUNTRY_CHOICES_WITH_DATA
            label = f"Country with disease data ({len(_DISEASE_WITH)})"
            if current and current in _DISEASE_WITH:
                selected = current
            else:
                selected = next(iter(_DISEASE_WITH), "")
        ui.update_select(
            "disease_country",
            label=label,
            choices=choices,
            selected=selected,
        )

    @reactive.effect
    @reactive.event(input.economic_show_all, ignore_none=False)
    def _economic_country_choices():
        """Default: only countries with economic data."""
        show_all = bool(input.economic_show_all())
        current = input.economic_country()
        if show_all:
            choices = ECONOMIC_COUNTRY_CHOICES_ALL
            label = "Country"
            selected = current if current else next(iter(_ECONOMIC_WITH), "")
        else:
            choices = ECONOMIC_COUNTRY_CHOICES_WITH_DATA
            label = f"Country with economic data ({len(_ECONOMIC_WITH)})"
            if current and current in _ECONOMIC_WITH:
                selected = current
            else:
                selected = next(iter(_ECONOMIC_WITH), "")
        ui.update_select(
            "economic_country",
            label=label,
            choices=choices,
            selected=selected,
        )

    @reactive.effect
    @reactive.event(input.legal_show_all, ignore_none=False)
    def _legal_country_choices():
        """Default: only countries with legal data so users can pick them directly."""
        show_all = bool(input.legal_show_all())
        current = input.legal_country()
        if show_all:
            choices = LEGAL_COUNTRY_CHOICES_ALL
            label = "Country"
            selected = current if current else next(iter(_LEGAL_WITH), "")
        else:
            choices = LEGAL_COUNTRY_CHOICES_WITH_DATA
            label = f"Country with legal data ({len(_LEGAL_WITH)})"
            if current and current in _LEGAL_WITH:
                selected = current
            else:
                selected = next(iter(_LEGAL_WITH), "")
        ui.update_select(
            "legal_country",
            label=label,
            choices=choices,
            selected=selected,
        )

    @reactive.calc
    def filtered_tvi() -> pd.DataFrame:
        df = TVI.copy()
        region = input.region_filter()
        if region and region != "All":
            df = df[df["region"] == region]
        return df

    @reactive.calc
    def active_iso3() -> str | None:
        for key in (
            input.country_profile,
            input.compare_country,
            input.disease_country,
            input.economic_country,
            input.legal_country,
        ):
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
        coverage_d = (
            f"{int(DISEASE['disease_exposure'].notna().sum())} / {len(DISEASE)}"
        )
        coverage_l = (
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
                tags.p({"class": "tvi-stat-label"}, "Disease coverage"),
                tags.p({"class": "tvi-stat-value"}, coverage_d.split("/")[0].strip()),
                tags.p({"class": "tvi-stat-note"}, f"of {coverage_d.split('/')[-1].strip()} (RMT)"),
            ),
            ui.div(
                {"class": "tvi-stat"},
                tags.p({"class": "tvi-stat-label"}, "Legal coverage"),
                tags.p({"class": "tvi-stat-value"}, coverage_l.split("/")[0].strip()),
                tags.p({"class": "tvi-stat-note"}, f"of {coverage_l.split('/')[-1].strip()} countries"),
            ),
        )

    @render_widget
    def world_map():
        df = filtered_tvi()
        return choropleth_tvi(df, selected_iso3=input.country_profile() or None)

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
    def disease_body():
        iso3 = input.disease_country()
        if not iso3:
            return ui.div(
                {"class": "tvi-panel"},
                tags.p(
                    {"class": "tvi-panel-intro"},
                    "Inspect RMT disease status, mitigation, and pathway×connection components "
                    "for Foot-and-Mouth Disease.",
                ),
            )
        if iso3 not in DISEASE.index:
            return tags.p("No disease data for this country.")
        dr = DISEASE.loc[iso3]
        ind = DISEASE_IND[DISEASE_IND["iso3"] == iso3].copy()

        n_avail = int(dr.get("disease_indicators_available", 0) or 0)
        n_tot = int(dr.get("disease_indicators_total", 2) or 2)
        countries_with_any = int(DISEASE["disease_exposure"].notna().sum())
        n_countries = len(DISEASE)

        def ind_rows(codes):
            rows = []
            for code in codes:
                sub = ind[ind["indicator_code"] == code]
                if sub.empty:
                    continue
                r = sub.iloc[0]
                missing = bool(r.get("missing_data_flag")) or pd.isna(r.get("score_100"))
                raw = r.get("score")
                scale = r.get("score_scale", "")
                raw_txt = (
                    MISSING_DATA["missing_label"]
                    if missing or pd.isna(raw)
                    else f"{float(raw):g}"
                )
                score_cell = (
                    tags.td({"class": "tvi-missing"}, MISSING_DATA["missing_label"])
                    if missing
                    else tags.td(f"{float(r['score_100']):.0f} / 100 (raw {raw_txt} · {scale})")
                )
                year_val = r.get("assessment_year")
                year = (
                    "—"
                    if missing or year_val is None or pd.isna(year_val)
                    else str(int(year_val))
                )
                name = r.get("indicator_name", "")
                if name is None or (isinstance(name, float) and pd.isna(name)):
                    name = code
                source = r.get("source", "—")
                if source is None or (isinstance(source, float) and pd.isna(source)):
                    source = "—"
                interp = r.get("interpretation", "")
                if interp is None or (isinstance(interp, float) and pd.isna(interp)):
                    interp = ""
                rows.append(
                    tags.tr(
                        tags.td(tags.strong(code)),
                        tags.td(str(name)),
                        score_cell,
                        tags.td(year),
                        tags.td(str(source)),
                        tags.td(str(interp)),
                    )
                )
            return rows

        status_raw = dr.get("disease_status_raw")
        mit_raw = dr.get("mitigation_raw")
        raw_risk = dr.get("rmt_raw_risk")
        formula_note = (
            f"RMT raw risk = (status {MISSING_DATA['missing_label'] if pd.isna(status_raw) else int(status_raw)} "
            f"+ (4 − mitigation "
            f"{'0*' if pd.isna(mit_raw) else f'{float(mit_raw):g}'})) "
            f"× pathway term → {_fmt(raw_risk, 1)}"
        )
        if pd.isna(mit_raw) and not pd.isna(status_raw):
            formula_note += " (*mitigation missing defaults to 0 per Nexus RMT)"

        return TagList(
            ui.div(
                {"class": "tvi-panel"},
                tags.h2(f"Disease exposure — {dr['country']}"),
                ui.div(
                    {"class": "tvi-coverage"},
                    tags.span(f"Country RMT inputs: {n_avail} / {n_tot}"),
                    tags.span("·"),
                    tags.span(
                        f"RMT coverage (disease status): {countries_with_any} / {n_countries} countries"
                    ),
                ),
                tags.p(
                    {"class": "tvi-panel-intro"},
                    formula_note,
                ),
                ui.div(
                    {"class": "tvi-grid-3"},
                    scorecard(
                        "Disease status (circulation)",
                        "exposure",
                        dr["domestic_exposure"],
                        classify_score(
                            None
                            if pd.isna(dr["domestic_exposure"])
                            else float(dr["domestic_exposure"])
                        ),
                        "RMT disease-status score normalised 0–100 (0=free … 3=highly endemic).",
                        "Source-country circulation component",
                    ),
                    scorecard(
                        "Mitigation gap",
                        "exposure",
                        dr["trade_movement_exposure"],
                        classify_score(
                            None
                            if pd.isna(dr["trade_movement_exposure"])
                            else float(dr["trade_movement_exposure"])
                        ),
                        "Higher = weaker mitigation (RMT 0–4 inverted). Missing mitigation → full gap.",
                        "Source-country control component",
                    ),
                    scorecard(
                        "Disease Exposure (overall)",
                        "exposure",
                        dr["disease_exposure"],
                        classify_score(
                            None
                            if pd.isna(dr["disease_exposure"])
                            else float(dr["disease_exposure"])
                        ),
                        "RMT formula with provisional pathway connections, scaled 0–100.",
                        f"TVI weight {DIMENSION_WEIGHTS['disease_exposure']:.0%}",
                    ),
                ),
            ),
            ui.div(
                {"class": "tvi-panel"},
                tags.h2("RMT component detail"),
                output_widget("disease_chart", height="300px"),
                tags.h3("Disease status & mitigation"),
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
                    tags.tbody(*ind_rows(["DS-STATUS", "DS-MITIG"])),
                ),
                tags.h3("Pathways (provisional connections)"),
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
                    tags.tbody(*ind_rows(["DS-PATH"])),
                ),
                tags.p(
                    {"class": "tvi-panel-intro"},
                    "Connections are provisional mid-level pathway scores until bilateral "
                    "UN Comtrade / proximity / transport inputs are added. This is source-hazard "
                    "potential under the RMT formula — not yet a full target←source entry matrix.",
                ),
            ),
        )

    @render_widget
    def disease_chart():
        iso3 = input.disease_country()
        import plotly.graph_objects as go

        if not iso3:
            fig = go.Figure()
            fig.update_layout(
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        text="Select a country to view RMT components",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(color="#5A6A7A"),
                    )
                ],
            )
            return fig
        return disease_indicator_bars(DISEASE_IND, iso3)

    @render.ui
    def economic_body():
        iso3 = input.economic_country()
        if not iso3:
            return ui.div(
                {"class": "tvi-panel"},
                tags.p(
                    {"class": "tvi-panel-intro"},
                    "Inspect livestock importance, export exposure, import dependence, "
                    "and trade concentration (mock scores until FAOSTAT / Comtrade are wired).",
                ),
            )
        if iso3 not in ECONOMIC.index:
            return tags.p("No economic data for this country.")
        er = ECONOMIC.loc[iso3]
        ind = ECONOMIC_IND[ECONOMIC_IND["iso3"] == iso3].copy()

        n_avail = int(er.get("economic_indicators_available", 0) or 0)
        n_tot = int(er.get("economic_indicators_total", len(ECONOMIC_INDICATORS)) or 4)
        countries_with_any = int(ECONOMIC["economic_sensitivity"].notna().sum())
        n_countries = len(ECONOMIC)

        def ind_rows(codes):
            rows = []
            for code in codes:
                sub = ind[ind["indicator_code"] == code]
                if sub.empty:
                    continue
                r = sub.iloc[0]
                missing = bool(r.get("missing_data_flag")) or pd.isna(r.get("score_100"))
                score_cell = (
                    tags.td({"class": "tvi-missing"}, MISSING_DATA["missing_label"])
                    if missing
                    else tags.td(f"{float(r['score_100']):.0f} / 100")
                )
                name = r.get("indicator_name", "")
                if name is None or (isinstance(name, float) and pd.isna(name)):
                    name = code
                source = r.get("source", "—")
                if source is None or (isinstance(source, float) and pd.isna(source)):
                    source = "—"
                interp = r.get("interpretation", "")
                if interp is None or (isinstance(interp, float) and pd.isna(interp)):
                    interp = ECONOMIC_INDICATORS.get(code, {}).get("description", "")
                if not missing and pd.notna(r.get("score_100")):
                    interp = (
                        f"{classify_score(float(r['score_100']))} sensitivity. " + str(interp)
                    )
                rows.append(
                    tags.tr(
                        tags.td(tags.strong(code)),
                        tags.td(str(name)),
                        score_cell,
                        tags.td("—"),
                        tags.td(str(source)),
                        tags.td(str(interp)),
                    )
                )
            return rows

        return TagList(
            ui.div(
                {"class": "tvi-panel"},
                tags.h2(f"Economic sensitivity — {er['country']}"),
                ui.div(
                    {"class": "tvi-coverage"},
                    tags.span(f"Country indicator coverage: {n_avail} / {n_tot}"),
                    tags.span("·"),
                    tags.span(
                        f"Economic coverage: {countries_with_any} / {n_countries} countries"
                    ),
                    tags.span("·"),
                    tags.span("MOCK data"),
                ),
                ui.div(
                    {"class": "tvi-grid-3"},
                    scorecard(
                        "Production at risk",
                        "economic",
                        er["livestock_importance"],
                        classify_score(
                            None
                            if pd.isna(er["livestock_importance"])
                            else float(er["livestock_importance"])
                        ),
                        "Livestock economic importance (mock).",
                        "EC-LIV",
                    ),
                    scorecard(
                        "Trade exposure",
                        "economic",
                        (
                            round(
                                (
                                    float(er["export_exposure"])
                                    + float(er["import_dependence"])
                                    + float(er["trade_concentration"])
                                )
                                / 3.0,
                                1,
                            )
                            if all(
                                pd.notna(er[c])
                                for c in (
                                    "export_exposure",
                                    "import_dependence",
                                    "trade_concentration",
                                )
                            )
                            else None
                        ),
                        classify_score(
                            None
                            if any(
                                pd.isna(er[c])
                                for c in (
                                    "export_exposure",
                                    "import_dependence",
                                    "trade_concentration",
                                )
                            )
                            else (
                                float(er["export_exposure"])
                                + float(er["import_dependence"])
                                + float(er["trade_concentration"])
                            )
                            / 3.0
                        ),
                        "Mean of export, import and concentration (mock).",
                        "EC-EXP · EC-IMP · EC-CON",
                    ),
                    scorecard(
                        "Economic Sensitivity (overall)",
                        "economic",
                        er["economic_sensitivity"],
                        classify_score(
                            None
                            if pd.isna(er["economic_sensitivity"])
                            else float(er["economic_sensitivity"])
                        ),
                        "Equal-weight mean of the four mock indicators.",
                        f"TVI weight {DIMENSION_WEIGHTS['economic_sensitivity']:.0%}",
                    ),
                ),
            ),
            ui.div(
                {"class": "tvi-panel"},
                tags.h2("Indicator detail"),
                output_widget("economic_chart", height="300px"),
                tags.h3("Production at risk"),
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
                    tags.tbody(*ind_rows(["EC-LIV"])),
                ),
                tags.h3("Export, import & concentration"),
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
                    tags.tbody(*ind_rows(["EC-EXP", "EC-IMP", "EC-CON"])),
                ),
            ),
        )

    @render_widget
    def economic_chart():
        iso3 = input.economic_country()
        import plotly.graph_objects as go

        if not iso3:
            fig = go.Figure()
            fig.update_layout(
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        text="Select a country to view economic indicators",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(color="#5A6A7A"),
                    )
                ],
            )
            return fig
        return economic_indicator_bars(ECONOMIC_IND, iso3)

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
                missing = bool(r.get("missing_data_flag")) or pd.isna(r.get("score_100"))
                raw = r.get("score")
                raw_txt = (
                    MISSING_DATA["missing_label"]
                    if missing or pd.isna(raw)
                    else f"{float(raw):g}"
                )
                score_cell = (
                    tags.td({"class": "tvi-missing"}, MISSING_DATA["missing_label"])
                    if missing
                    else tags.td(f"{float(r['score_100']):.0f} / 100 (raw {raw_txt} / 5)")
                )
                year_val = r.get("assessment_year")
                year = (
                    "—"
                    if missing or year_val is None or pd.isna(year_val)
                    else str(int(year_val))
                )
                name = r.get("indicator_name", "")
                if name is None or (isinstance(name, float) and pd.isna(name)):
                    name = code
                source = r.get("source", "—")
                if source is None or (isinstance(source, float) and pd.isna(source)):
                    source = "—"
                interp = LEGAL_INDICATORS.get(code, {}).get("description", "")
                if not missing and pd.notna(r.get("score_100")):
                    interp = (
                        f"{classify_score(float(r['score_100']), preparedness=True)} preparedness. "
                        + interp
                    )
                rows.append(
                    tags.tr(
                        tags.td(tags.strong(code)),
                        tags.td(str(name)),
                        score_cell,
                        tags.td(year),
                        tags.td(str(source)),
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
            fig = go.Figure()
            fig.update_layout(
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        text="Select a country to view indicators",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(color="#5A6A7A"),
                    )
                ],
            )
            return fig
        return legal_indicator_bars(LEGAL_IND, iso3)


app = App(app_ui, server)
