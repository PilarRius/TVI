"""Benchmark calculations: global, regional, and peer averages."""

from __future__ import annotations

import pandas as pd


SCORE_COLS = [
    "tvi",
    "disease_exposure",
    "economic_sensitivity",
    "legal_preparedness",
]


def global_benchmarks(tvi_df: pd.DataFrame) -> dict[str, float]:
    out = {}
    for col in SCORE_COLS:
        out[col] = float(tvi_df[col].mean(skipna=True)) if tvi_df[col].notna().any() else float("nan")
    return out


def regional_benchmarks(tvi_df: pd.DataFrame, region: str) -> dict[str, float]:
    sub = tvi_df[tvi_df["region"] == region]
    out = {}
    for col in SCORE_COLS:
        out[col] = float(sub[col].mean(skipna=True)) if sub[col].notna().any() else float("nan")
    return out


def peer_benchmarks(tvi_df: pd.DataFrame, peer_iso3: list[str]) -> dict[str, float]:
    sub = tvi_df[tvi_df["iso3"].isin(peer_iso3)]
    out = {}
    for col in SCORE_COLS:
        out[col] = float(sub[col].mean(skipna=True)) if sub[col].notna().any() else float("nan")
    return out


def comparison_frame(
    country_row: pd.Series,
    tvi_df: pd.DataFrame,
    peer_iso3: list[str] | None = None,
) -> pd.DataFrame:
    """Long-form frame for comparison charts."""
    region = country_row.get("region")
    g = global_benchmarks(tvi_df)
    r = regional_benchmarks(tvi_df, region) if region else {c: float("nan") for c in SCORE_COLS}

    rows = []
    for label, source in [
        ("Country", {c: country_row.get(c) for c in SCORE_COLS}),
        ("Global average", g),
        ("Regional average", r),
    ]:
        for col in SCORE_COLS:
            rows.append({"group": label, "metric": col, "value": source.get(col)})

    if peer_iso3:
        p = peer_benchmarks(tvi_df, peer_iso3)
        for col in SCORE_COLS:
            rows.append({"group": "Peer average", "metric": col, "value": p.get(col)})

    return pd.DataFrame(rows)


METRIC_LABELS = {
    "tvi": "Trade Vulnerability Index",
    "disease_exposure": "Disease Exposure",
    "economic_sensitivity": "Economic Sensitivity",
    "legal_preparedness": "Legal Preparedness",
}
