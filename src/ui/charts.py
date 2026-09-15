"""Plotly chart builders — pure functions, no Shiny dependency."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import BRAND, TVI_COLORSCALE
from src.calculations.benchmarks import METRIC_LABELS


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
        "TVI: %{z:.1f}<br>"
        "Disease Exposure: %{customdata[1]}<br>"
        "Economic Sensitivity: %{customdata[2]}<br>"
        "Legal Preparedness: %{customdata[3]}<br>"
        "Data: %{customdata[4]}"
        "<extra></extra>"
    )
    custom = df[
        ["country", "disease_exposure", "economic_sensitivity", "legal_preparedness", "data_availability"]
    ].values

    fig = go.Figure(
        go.Choropleth(
            locations=df["iso3"],
            z=df["tvi"],
            text=df["country"],
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
            selectedpoints=[],
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
                locations=[selected_iso3],
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
        float(row["contrib_disease"]) if pd.notna(row.get("contrib_disease")) else 0,
        float(row["contrib_economic"]) if pd.notna(row.get("contrib_economic")) else 0,
        float(row["contrib_legal"]) if pd.notna(row.get("contrib_legal")) else 0,
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


def legal_indicator_bars(ind_df: pd.DataFrame, iso3: str) -> go.Figure:
    sub = ind_df[ind_df["iso3"] == iso3].copy()
    sub = sub.sort_values("indicator_code")
    y = [f"{r.indicator_code}" for _, r in sub.iterrows()]
    x = [None if pd.isna(v) else float(v) for v in sub["score_100"]]
    colors = [
        BRAND["line"] if v is None else (BRAND["preparedness"] if v >= 50 else BRAND["contribute"])
        for v in x
    ]
    display_x = [0 if v is None else v for v in x]
    texts = ["Data unavailable" if v is None else f"{v:.0f}" for v in x]

    fig = go.Figure(
        go.Bar(
            x=display_x,
            y=y,
            orientation="h",
            marker_color=colors,
            text=texts,
            textposition="outside",
            customdata=sub["indicator_name"],
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
    cols = ["country", "iso3", "region", "tvi", "disease_exposure", "economic_sensitivity", "legal_preparedness"]
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
