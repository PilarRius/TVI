"""Plotly chart builders — pure functions, no Shiny dependency."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import BRAND, TVI_COLORSCALE, MISSING_DATA
from src.calculations.benchmarks import METRIC_LABELS


def _json_safe(value):
    """Convert NaN/Inf to JSON-safe values for shinywidgets/plotly."""
    if value is None:
        return None
    if isinstance(value, (float, np.floating)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _fmt_hover(value, digits: int = 1) -> str:
    v = _json_safe(value)
    if v is None:
        return MISSING_DATA["missing_label"]
    if isinstance(v, (int, float)):
        return f"{v:.{digits}f}"
    return str(v)


def _base_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=BRAND["ink"], size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig


def choropleth_tvi(tvi_df: pd.DataFrame, selected_iso3: str | None = None) -> go.Figure:
    df = tvi_df.copy()
    hover = (
        "<b>%{customdata[0]}</b><br>"
        "TVI: %{customdata[1]}<br>"
        "Disease Exposure: %{customdata[2]}<br>"
        "Economic Sensitivity: %{customdata[3]}<br>"
        "Legal Preparedness: %{customdata[4]}<br>"
        "Data: %{customdata[5]}"
        "<extra></extra>"
    )
    # All customdata must be JSON-safe (no NaN) for shinywidgets
    custom = [
        [
            str(r.country),
            _fmt_hover(r.tvi, 1),
            _fmt_hover(r.disease_exposure, 1),
            _fmt_hover(r.economic_sensitivity, 1),
            _fmt_hover(r.legal_preparedness, 1),
            str(r.data_availability)
            if pd.notna(r.data_availability)
            else MISSING_DATA["missing_label"],
        ]
        for r in df.itertuples(index=False)
    ]
    z_plot = [_json_safe(v) for v in df["tvi"].tolist()]

    fig = go.Figure(
        go.Choropleth(
            locations=df["iso3"].astype(str).tolist(),
            z=z_plot,
            text=df["country"].astype(str).tolist(),
            customdata=custom,
            colorscale=TVI_COLORSCALE,
            zmin=0,
            zmax=100,
            marker_line_color="#FFFFFF",
            marker_line_width=0.4,
            colorbar=dict(
                title=dict(text="TVI", side="right"),
                thickness=12,
                len=0.6,
                bgcolor="rgba(255,255,255,0.85)",
            ),
            hovertemplate=hover,
        )
    )
    fig.update_geos(
        projection_type="natural earth",
        showcoastlines=False,
        showframe=False,
        showland=True,
        landcolor="#EEF2F5",
        showocean=True,
        oceancolor="#F7F9FA",
        showlakes=False,
        showcountries=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig = _base_layout(fig, height=520)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    if selected_iso3:
        fig.add_trace(
            go.Choropleth(
                locations=[str(selected_iso3)],
                z=[1],
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False,
                marker_line_color=BRAND["navy"],
                marker_line_width=2,
                hoverinfo="skip",
            )
        )
    return fig


def dimension_contribution_bars(row: pd.Series) -> go.Figure:
    """Horizontal bars: vulnerability contribution of each dimension."""
    labels = ["Disease Exposure", "Economic Sensitivity", "Legal (vuln. contrib.)"]
    values = [
        _json_safe(row.get("contrib_disease")) or 0.0,
        _json_safe(row.get("contrib_economic")) or 0.0,
        _json_safe(row.get("contrib_legal")) or 0.0,
    ]
    colors = [BRAND["exposure"], BRAND["economic"], BRAND["preparedness"]]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="outside",
            hovertemplate="%{y}: %{x:.1f}<extra></extra>",
        )
    )
    fig = _base_layout(fig, height=220)
    fig.update_layout(
        xaxis=dict(title="Weighted contribution to TVI", range=[0, max(values + [20]) * 1.25]),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        margin=dict(l=160, r=40, t=20, b=40),
    )
    return fig


def comparison_grouped_bars(comp_df: pd.DataFrame) -> go.Figure:
    df = comp_df.copy()
    df["metric_label"] = df["metric"].map(METRIC_LABELS)
    df["value"] = df["value"].map(_json_safe)
    df = df[df["value"].notna()].copy()
    if df.empty:
        return _base_layout(go.Figure(), height=380)
    fig = px.bar(
        df,
        x="metric_label",
        y="value",
        color="group",
        barmode="group",
        color_discrete_sequence=[
            BRAND["vulnerability"],
            BRAND["steel"],
            BRAND["teal"],
            BRAND["economic"],
        ],
    )
    fig = _base_layout(fig, height=380)
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Score (0–100)",
        yaxis=dict(range=[0, 100]),
        legend_title_text="",
    )
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y:.1f}<extra></extra>")
    return fig


def disease_indicator_bars(ind_df: pd.DataFrame, iso3: str) -> go.Figure:
    """Horizontal bars for RMT disease-exposure indicators (same pattern as legal)."""
    return _component_indicator_bars(
        ind_df,
        iso3,
        order={"DS-STATUS": 0, "DS-MITIG": 1, "DS-PATH": 2},
        empty_title=f"No disease indicator rows for {iso3}",
        color_high=BRAND["exposure"],
        color_low=BRAND["steel"],
        y_margin_l=90,
    )


def economic_indicator_bars(ind_df: pd.DataFrame, iso3: str) -> go.Figure:
    """Horizontal bars for economic sensitivity indicators."""
    return _component_indicator_bars(
        ind_df,
        iso3,
        order={"EC-LIV": 0, "EC-EXP": 1, "EC-IMP": 2, "EC-CON": 3},
        empty_title=f"No economic indicator rows for {iso3}",
        color_high=BRAND["economic"],
        color_low=BRAND["steel"],
        y_margin_l=90,
    )


def _component_indicator_bars(
    ind_df: pd.DataFrame,
    iso3: str,
    *,
    order: dict[str, int],
    empty_title: str,
    color_high: str,
    color_low: str,
    y_margin_l: int = 70,
) -> go.Figure:
    sub = ind_df[ind_df["iso3"] == iso3].copy()
    if sub.empty:
        fig = go.Figure()
        fig.update_layout(
            title=empty_title,
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig
    sub["_ord"] = sub["indicator_code"].map(lambda c: order.get(c, 9))
    sub = sub.sort_values("_ord")
    y = [str(r.indicator_code) for _, r in sub.iterrows()]
    x = [_json_safe(v) for v in sub["score_100"]]
    colors = [
        BRAND["line"] if v is None else (color_high if v >= 50 else color_low)
        for v in x
    ]
    display_x = [0.0 if v is None else float(v) for v in x]
    texts = [MISSING_DATA["missing_label"] if v is None else f"{v:.0f}" for v in x]
    names = []
    for code, v in zip(y, sub["indicator_name"].tolist()):
        safe = _json_safe(v)
        names.append(str(safe) if safe is not None else code)

    fig = go.Figure(
        go.Bar(
            x=display_x,
            y=y,
            orientation="h",
            marker_color=colors,
            text=texts,
            textposition="outside",
            customdata=names,
            hovertemplate="<b>%{y}</b><br>%{customdata}<br>Score: %{text}<extra></extra>",
        )
    )
    fig = _base_layout(fig, height=280)
    fig.update_layout(
        xaxis=dict(title="Normalised score (0–100)", range=[0, 115]),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        margin=dict(l=y_margin_l, r=80, t=20, b=40),
    )
    return fig


def legal_indicator_bars(ind_df: pd.DataFrame, iso3: str) -> go.Figure:
    sub = ind_df[ind_df["iso3"] == iso3].copy()
    if sub.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"No indicator rows for {iso3}",
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig
    sub = sub.sort_values("indicator_code")
    y = [str(r.indicator_code) for _, r in sub.iterrows()]
    x = [_json_safe(v) for v in sub["score_100"]]
    colors = [
        BRAND["line"] if v is None else (BRAND["preparedness"] if v >= 50 else BRAND["contribute"])
        for v in x
    ]
    display_x = [0.0 if v is None else float(v) for v in x]
    texts = [MISSING_DATA["missing_label"] if v is None else f"{v:.0f}" for v in x]
    names = []
    for code, v in zip(y, sub["indicator_name"].tolist()):
        safe = _json_safe(v)
        names.append(str(safe) if safe is not None else code)

    fig = go.Figure(
        go.Bar(
            x=display_x,
            y=y,
            orientation="h",
            marker_color=colors,
            text=texts,
            textposition="outside",
            customdata=names,
            hovertemplate="<b>%{y}</b><br>%{customdata}<br>Score: %{text}<extra></extra>",
        )
    )
    fig = _base_layout(fig, height=280)
    fig.update_layout(
        xaxis=dict(title="Normalised score (0–100)", range=[0, 115]),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        margin=dict(l=70, r=80, t=20, b=40),
    )
    return fig


def ranking_table_data(tvi_df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    cols = [
        "country",
        "iso3",
        "region",
        "tvi",
        "disease_exposure",
        "economic_sensitivity",
        "legal_preparedness",
    ]
    return (
        tvi_df[cols]
        .dropna(subset=["tvi"])
        .head(n)
        .rename(
            columns={
                "country": "Country",
                "iso3": "ISO3",
                "region": "WOAH Region",
                "tvi": "TVI",
                "disease_exposure": "Disease",
                "economic_sensitivity": "Economic",
                "legal_preparedness": "Legal Prep.",
            }
        )
    )
