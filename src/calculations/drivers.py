"""Driver analysis — generate explanatory contributors from indicator data."""

from __future__ import annotations

import pandas as pd

from src.modules.disease_exposure import INDICATOR_META as DISEASE_META
from src.modules.economic_sensitivity import INDICATOR_META as ECONOMIC_META
from config.settings import LEGAL_INDICATORS


def country_drivers(
    iso3: str,
    tvi_row: pd.Series,
    disease_row: pd.Series,
    economic_row: pd.Series,
    legal_indicators: pd.DataFrame,
    *,
    top_n: int = 4,
) -> dict:
    """
    Derive HIGH CONTRIBUTION and PROTECTIVE FACTORS from indicator values.

    Drivers are generated from data, not hand-written per country.
    """
    risk_candidates: list[tuple[float, str]] = []
    protective: list[tuple[float, str]] = []

    # Disease sub-indicators (higher = more vulnerability)
    for col, label in DISEASE_META.items():
        val = disease_row.get(col)
        if pd.notna(val):
            risk_candidates.append((float(val), f"Elevated {label.lower()} ({val:.0f}/100)"))

    # Economic sub-indicators
    for col, label in ECONOMIC_META.items():
        val = economic_row.get(col)
        if pd.notna(val):
            risk_candidates.append((float(val), f"Elevated {label.lower()} ({val:.0f}/100)"))

    # Dimension-level fallbacks
    if pd.notna(tvi_row.get("disease_exposure")):
        risk_candidates.append(
            (
                float(tvi_row["disease_exposure"]),
                f"High disease exposure ({tvi_row['disease_exposure']:.0f}/100)",
            )
        )
    if pd.notna(tvi_row.get("economic_sensitivity")):
        risk_candidates.append(
            (
                float(tvi_row["economic_sensitivity"]),
                f"High economic sensitivity ({tvi_row['economic_sensitivity']:.0f}/100)",
            )
        )

    # Legal indicators: low preparedness → risk; high → protective
    ind = legal_indicators[legal_indicators["iso3"] == iso3]
    for _, r in ind.iterrows():
        if r.get("missing_data_flag") or pd.isna(r.get("score_100")):
            continue
        code = r["indicator_code"]
        name = LEGAL_INDICATORS.get(code, {}).get("name", code)
        score100 = float(r["score_100"])
        if score100 < 40:
            risk_candidates.append(
                (100 - score100, f"Low {name.lower()} ({code}: {score100:.0f}/100)")
            )
        elif score100 >= 60:
            protective.append(
                (score100, f"Strong {name.lower()} ({code}: {score100:.0f}/100)")
            )

    if pd.notna(tvi_row.get("legal_preparedness")):
        lp = float(tvi_row["legal_preparedness"])
        if lp >= 60:
            protective.append((lp, f"Overall legal preparedness ({lp:.0f}/100)"))
        elif lp < 40:
            risk_candidates.append((100 - lp, f"Limited legal preparedness ({lp:.0f}/100)"))

    # Deduplicate by text, keep highest score
    def _dedupe(items: list[tuple[float, str]]) -> list[tuple[float, str]]:
        best: dict[str, float] = {}
        for score, text in items:
            # Normalise key roughly
            key = text.split("(")[0].strip().lower()
            if key not in best or score > best[key]:
                best[key] = score
        # Rebuild with original texts preferring highest
        out = []
        seen = set()
        for score, text in sorted(items, key=lambda x: -x[0]):
            key = text.split("(")[0].strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append((score, text))
        return out

    risk_sorted = _dedupe(risk_candidates)[:top_n]
    prot_sorted = _dedupe(protective)[:top_n]

    return {
        "high_contribution": [t for _, t in risk_sorted],
        "protective_factors": [t for _, t in prot_sorted],
    }
