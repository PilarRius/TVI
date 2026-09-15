"""Central Trade Vulnerability Index calculation layer."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import DIMENSION_WEIGHTS, LEGAL_VULN_TRANSFORM, MISSING_DATA
from src.calculations.classification import classify_score


def legal_to_vulnerability(preparedness: float | None) -> float | None:
    """
    Convert Legal Preparedness (resilience) into a vulnerability contribution.

    Configured via LEGAL_VULN_TRANSFORM:
      - invert_100: 100 - preparedness
      - none:       use preparedness as-is (not recommended)
    """
    if preparedness is None or (isinstance(preparedness, float) and np.isnan(preparedness)):
        return None
    if LEGAL_VULN_TRANSFORM == "invert_100":
        return float(np.round(100.0 - preparedness, 1))
    if LEGAL_VULN_TRANSFORM == "none":
        return float(preparedness)
    raise ValueError(f"Unknown LEGAL_VULN_TRANSFORM: {LEGAL_VULN_TRANSFORM}")


def compute_tvi(
    disease: pd.DataFrame,
    economic: pd.DataFrame,
    legal: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Aggregate dimension indices into the Trade Vulnerability Index.

    Parameters
    ----------
    disease, economic, legal : DataFrames with iso3 and respective index columns
    weights : optional override of DIMENSION_WEIGHTS (for sensitivity testing)
    """
    w = weights or DIMENSION_WEIGHTS
    # Normalise weights to sum 1
    w_sum = sum(w.values())
    w = {k: v / w_sum for k, v in w.items()}

    df = (
        disease[["iso3", "country", "region", "disease_exposure"]]
        .merge(
            economic[["iso3", "economic_sensitivity"]],
            on="iso3",
            how="outer",
        )
        .merge(
            legal[
                [
                    "iso3",
                    "legal_preparedness",
                    "domestic_legal_readiness",
                    "trade_continuity_preparedness",
                    "legal_indicators_available",
                    "legal_indicators_total",
                ]
            ],
            on="iso3",
            how="outer",
        )
    )

    df["legal_vulnerability"] = df["legal_preparedness"].apply(legal_to_vulnerability)

    tvi_vals = []
    data_avail = []
    for _, row in df.iterrows():
        parts = {
            "disease_exposure": row["disease_exposure"],
            "economic_sensitivity": row["economic_sensitivity"],
            "legal_preparedness": row["legal_vulnerability"],
        }
        available = {k: v for k, v in parts.items() if pd.notna(v)}
        n_dim = len(available)
        if n_dim == 3 or (MISSING_DATA["partial_tvi"] and n_dim >= 1):
            ww = np.array([w[k] for k in available], dtype=float)
            ww = ww / ww.sum()
            vals = np.array([available[k] for k in available], dtype=float)
            tvi = float(np.round(np.dot(vals, ww), 1))
        else:
            tvi = np.nan
        tvi_vals.append(tvi)

        flags = []
        if pd.notna(row["disease_exposure"]):
            flags.append("D")
        if pd.notna(row["economic_sensitivity"]):
            flags.append("E")
        if pd.notna(row["legal_preparedness"]):
            flags.append("L")
        data_avail.append("/".join(flags) if flags else "none")

    df["tvi"] = tvi_vals
    df["data_availability"] = data_avail
    df["tvi_class"] = df["tvi"].apply(lambda x: classify_score(None if pd.isna(x) else float(x)))
    df["disease_class"] = df["disease_exposure"].apply(
        lambda x: classify_score(None if pd.isna(x) else float(x))
    )
    df["economic_class"] = df["economic_sensitivity"].apply(
        lambda x: classify_score(None if pd.isna(x) else float(x))
    )
    df["legal_class"] = df["legal_preparedness"].apply(
        lambda x: classify_score(None if pd.isna(x) else float(x), preparedness=True)
    )

    # Weighted contributions (for scorecards / drivers)
    df["contrib_disease"] = df["disease_exposure"] * w["disease_exposure"]
    df["contrib_economic"] = df["economic_sensitivity"] * w["economic_sensitivity"]
    df["contrib_legal"] = df["legal_vulnerability"] * w["legal_preparedness"]

    return df.sort_values("tvi", ascending=False, na_position="last").reset_index(drop=True)
