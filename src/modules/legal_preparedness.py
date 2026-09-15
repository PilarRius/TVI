"""
Legal Preparedness module.

PLACEHOLDER METHODOLOGY — replace indicator sourcing and scoring logic
when the real PVS-based methodology is finalised.

Architecture:
  raw PVS observations
    → standardised legal indicators (0–100)
    → component scores (Domestic Legal Readiness, Trade-Continuity)
    → Legal Preparedness Index (0–100, higher = more prepared)

Higher Legal Preparedness REDUCES vulnerability. The TVI layer applies
the configured invert transform; this module returns preparedness only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import (
    LEGAL_COMPONENT_WEIGHTS,
    LEGAL_INDICATOR_WEIGHTS,
    LEGAL_INDICATORS,
    MISSING_DATA,
    MOCK_SEED_LEGAL,
    PVS_SCORE_SCALE,
)
from config.woah_regions import ISO3_TO_NAME, ISO3_TO_REGION

MODULE_STATUS = "PLACEHOLDER — REPLACE WITH REAL LEGAL PREPAREDNESS METHODOLOGY"

# Intentionally leave ~25% of country–indicator cells missing to demonstrate
# explicit missing-data handling (never imputed to zero).
MISSING_RATE = 0.22


def _pvs_to_100(score: float | None) -> float | None:
    """Normalise a PVS 1–5 Critical Competency level to 0–100."""
    if score is None or (isinstance(score, float) and np.isnan(score)):
        return None
    lo, hi = PVS_SCORE_SCALE["min"], PVS_SCORE_SCALE["max"]
    return float(np.clip((score - lo) / (hi - lo) * 100.0, 0, 100))


def generate_placeholder_pvs(iso3_list: list[str] | None = None) -> pd.DataFrame:
    """
    Generate placeholder raw PVS-style observations.

    Schema (legal data model):
        country, iso3, assessment_year, pvs_assessment_version, indicator,
        indicator_code, indicator_name, score, score_scale, source,
        source_url, data_availability, missing_data_flag
    """
    iso3_list = iso3_list or sorted(ISO3_TO_NAME.keys())
    rng = np.random.default_rng(MOCK_SEED_LEGAL)

    region_base = {
        "Africa": 2.6,
        "Americas": 3.4,
        "Asia and the Pacific": 3.0,
        "Europe": 3.8,
        "Middle East": 2.9,
    }

    rows = []
    for iso3 in iso3_list:
        region = ISO3_TO_REGION.get(iso3, "Europe")
        base = region_base.get(region, 3.0)
        year = int(rng.choice([2016, 2018, 2019, 2021, 2022, 2023, 2024]))
        for code, meta in LEGAL_INDICATORS.items():
            missing = rng.random() < MISSING_RATE
            raw = None if missing else float(np.clip(base + rng.normal(0, 0.7), 1.0, 5.0))
            if raw is not None:
                raw = round(raw * 2) / 2  # half-step PVS-like scores
            rows.append(
                {
                    "country": ISO3_TO_NAME.get(iso3, iso3),
                    "iso3": iso3,
                    "assessment_year": None if missing else year,
                    "pvs_assessment_version": "PVS Tool 2019 (placeholder)",
                    "indicator": code,
                    "indicator_code": code,
                    "indicator_name": meta["name"],
                    "score": raw,
                    "score_scale": "1-5",
                    "source": "PLACEHOLDER — not real PVS data",
                    "source_url": "https://www.woah.org/en/what-we-offer/improving-veterinary-services/pvs-pathway/",
                    "data_availability": "unavailable" if missing else "placeholder",
                    "missing_data_flag": bool(missing),
                }
            )
    return pd.DataFrame(rows)


def load_pvs_file(path) -> pd.DataFrame:
    """
    Ingest downloaded PVS / legal indicator files (CSV, Excel, JSON).

    Expected columns (flexible aliases accepted):
        iso3 | ISO3, indicator_code | indicator, score, ...
    """
    path = str(path)
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    elif path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    elif path.lower().endswith(".json"):
        df = pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    rename = {
        "ISO3": "iso3",
        "Iso3": "iso3",
        "Country": "country",
        "Indicator": "indicator_code",
        "indicator": "indicator_code",
        "Score": "score",
        "Year": "assessment_year",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    required = {"iso3", "indicator_code", "score"}
    missing_cols = required - set(df.columns)
    if missing_cols:
        raise ValueError(f"Legal data file missing columns: {missing_cols}")

    if "missing_data_flag" not in df.columns:
        df["missing_data_flag"] = df["score"].isna()
    if "data_availability" not in df.columns:
        df["data_availability"] = np.where(df["missing_data_flag"], "unavailable", "available")
    if "source" not in df.columns:
        df["source"] = "User-provided file"
    if "score_scale" not in df.columns:
        df["score_scale"] = "1-5"
    if "indicator_name" not in df.columns:
        df["indicator_name"] = df["indicator_code"].map(
            lambda c: LEGAL_INDICATORS.get(c, {}).get("name", c)
        )
    if "indicator" not in df.columns:
        df["indicator"] = df["indicator_code"]
    return df


def standardised_indicators(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert raw PVS scores to 0–100 standardised indicators. Missing stay null."""
    df = raw.copy()
    df["score_100"] = df["score"].apply(_pvs_to_100)
    # Explicit: do NOT fillna(0)
    if MISSING_DATA["impute_with_zero"]:
        raise RuntimeError("impute_with_zero is disallowed by project policy")
    return df


def _weighted_mean(values: pd.Series, weights: dict[str, float], codes: pd.Series) -> float | None:
    """Weighted mean over non-null values only. Returns None if none available."""
    usable = []
    wts = []
    for code, val in zip(codes, values):
        if val is not None and not (isinstance(val, float) and np.isnan(val)):
            usable.append(float(val))
            wts.append(weights.get(code, 1.0))
    if len(usable) < MISSING_DATA["require_min_indicators_per_component"]:
        return None
    wts = np.array(wts, dtype=float)
    wts = wts / wts.sum()
    return float(np.round(np.dot(usable, wts), 1))


def compute_legal_preparedness(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute component and overall Legal Preparedness scores.

    Returns
    -------
    country_scores : DataFrame with domestic, trade_continuity, legal_preparedness
    indicators : standardised indicator-level DataFrame
    """
    indicators = standardised_indicators(raw)

    component_of = {code: meta["component"] for code, meta in LEGAL_INDICATORS.items()}
    indicators["component"] = indicators["indicator_code"].map(component_of)

    country_rows = []
    for iso3, grp in indicators.groupby("iso3"):
        components = {}
        for comp_name in LEGAL_COMPONENT_WEIGHTS:
            sub = grp[grp["component"] == comp_name]
            # Restrict weights to indicators belonging to this component
            comp_weights = {
                c: LEGAL_INDICATOR_WEIGHTS[c]
                for c in sub["indicator_code"]
                if c in LEGAL_INDICATOR_WEIGHTS
            }
            components[comp_name] = _weighted_mean(
                sub["score_100"], comp_weights, sub["indicator_code"]
            )

        # Overall legal preparedness
        avail = {k: v for k, v in components.items() if v is not None}
        if not avail:
            legal = None
        else:
            w = np.array([LEGAL_COMPONENT_WEIGHTS[k] for k in avail], dtype=float)
            w = w / w.sum()
            vals = np.array([avail[k] for k in avail], dtype=float)
            legal = float(np.round(np.dot(vals, w), 1))

        n_available = int((~grp["missing_data_flag"]).sum())
        n_total = len(LEGAL_INDICATORS)

        country_rows.append(
            {
                "iso3": iso3,
                "country": ISO3_TO_NAME.get(iso3, iso3),
                "region": ISO3_TO_REGION.get(iso3),
                "domestic_legal_readiness": components.get("domestic_legal_readiness"),
                "trade_continuity_preparedness": components.get("trade_continuity_preparedness"),
                "legal_preparedness": legal,
                "legal_indicators_available": n_available,
                "legal_indicators_total": n_total,
                "module_status": MODULE_STATUS,
            }
        )

    return pd.DataFrame(country_rows), indicators
