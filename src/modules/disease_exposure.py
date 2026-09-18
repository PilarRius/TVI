"""
Disease Exposure module — RMT adaptation (provisional global scale).

Uses curated EuFMD RMT disease-status and mitigation scores where available.
Pathway effectiveness comes from EuFMD-Nexus pathwaysConfig.
Bilateral connections are not yet wired (needs Comtrade / proximity CSVs);
provisional mid-level pathway connection scores are used so the RMT formula
can produce a comparable Disease Exposure Index for scored countries.

Countries without RMT inputs are left as N/A (never imputed to zero).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from config.rmt import (
    DISEASE_STATUS_LABELS,
    DISEASE_STATUS_SCALE,
    MITIGATION_LABELS,
    MITIGATION_SCALE,
    PATHWAY_DISPLAY_NAMES,
    PATHWAY_EFFECTIVENESS,
    PROVISIONAL_PATHWAY_CONNECTIONS,
)
from config.settings import ACTIVE_DISEASE, MISSING_DATA, RAW_DIR
from config.woah_regions import ISO3_TO_NAME, ISO3_TO_REGION
from src.calculations.rmt import pathway_term, rmt_raw_risk, rmt_to_100

MODULE_STATUS = (
    "RMT PROVISIONAL — EuFMD curated status/mitigation; "
    "provisional connections until Comtrade/proximity wired"
)

INDICATOR_META = {
    "domestic_exposure": "Disease status / circulation (RMT)",
    "trade_movement_exposure": "Mitigation gap (RMT inverted)",
    "network_exposure": "Pathway × provisional connection",
}


def _status_to_100(score: float | None) -> float | None:
    if score is None or (isinstance(score, float) and np.isnan(score)):
        return None
    lo, hi = DISEASE_STATUS_SCALE["min"], DISEASE_STATUS_SCALE["max"]
    return float(np.clip((float(score) - lo) / (hi - lo) * 100.0, 0, 100))


def _mitigation_gap_to_100(score: float | None) -> float | None:
    """Higher gap = weaker mitigation = more exposure contribution (0–100)."""
    if score is None or (isinstance(score, float) and np.isnan(score)):
        return None
    lo, hi = MITIGATION_SCALE["min"], MITIGATION_SCALE["max"]
    gap = hi - float(score)
    return float(np.clip(gap / (hi - lo) * 100.0, 0, 100))


def load_rmt_inputs(raw_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load curated RMT disease-status and mitigation CSVs."""
    base = Path(raw_dir) if raw_dir else RAW_DIR / "rmt"
    status_path = base / "rmt_disease_status.csv"
    mit_path = base / "rmt_mitigation.csv"
    if not status_path.exists() or not mit_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    status = pd.read_csv(status_path)
    mitigation = pd.read_csv(mit_path)
    return status, mitigation


def _long_indicators(
    iso3: str,
    country: str,
    disease_status: float | None,
    mitigation: float | None,
    pathway_score: float | None,
    disease: str,
    source_status: str,
    source_mit: str,
    year_status,
    year_mit,
) -> list[dict]:
    """Long-form rows for the Disease Exposure detail table/chart."""
    rows = []
    # Disease status
    missing_d = disease_status is None or (
        isinstance(disease_status, float) and np.isnan(disease_status)
    )
    d_label = None if missing_d else DISEASE_STATUS_LABELS.get(int(disease_status), "")
    rows.append(
        {
            "iso3": iso3,
            "country": country,
            "indicator_code": "DS-STATUS",
            "indicator_name": "Disease status / circulation",
            "component": "disease_status",
            "score": None if missing_d else float(disease_status),
            "score_100": None if missing_d else _status_to_100(float(disease_status)),
            "score_scale": "0-3",
            "assessment_year": None if missing_d else year_status,
            "source": source_status if not missing_d else "No RMT disease-status extract",
            "missing_data_flag": bool(missing_d),
            "interpretation": d_label or MISSING_DATA["missing_label"],
        }
    )
    # Mitigation
    missing_m = mitigation is None or (
        isinstance(mitigation, float) and np.isnan(mitigation)
    )
    m_label = None if missing_m else MITIGATION_LABELS.get(int(mitigation), "")
    rows.append(
        {
            "iso3": iso3,
            "country": country,
            "indicator_code": "DS-MITIG",
            "indicator_name": "Mitigation measures (gap as exposure)",
            "component": "mitigation",
            "score": None if missing_m else float(mitigation),
            "score_100": None if missing_m else _mitigation_gap_to_100(float(mitigation)),
            "score_scale": "0-4",
            "assessment_year": None if missing_m else year_mit,
            "source": source_mit if not missing_m else "No RMT mitigation extract",
            "missing_data_flag": bool(missing_m),
            "interpretation": m_label or MISSING_DATA["missing_label"],
        }
    )
    # Pathway bundle (provisional connections)
    missing_p = pathway_score is None or (
        isinstance(pathway_score, float) and np.isnan(pathway_score)
    )
    eff = PATHWAY_EFFECTIVENESS.get(disease, {})
    parts = [
        f"{PATHWAY_DISPLAY_NAMES[k]}:{eff[k]}×{PROVISIONAL_PATHWAY_CONNECTIONS[k]:g}"
        for k in eff
        if eff[k] > 0
    ]
    rows.append(
        {
            "iso3": iso3,
            "country": country,
            "indicator_code": "DS-PATH",
            "indicator_name": "Pathway × provisional connection",
            "component": "pathway_bundle",
            "score": None if missing_p else float(pathway_score),
            "score_100": None
            if missing_p
            else float(np.clip(float(pathway_score) / 15.0 * 100.0, 0, 100)),
            "score_scale": "pathway-term",
            "assessment_year": None,
            "source": "Nexus pathway effectiveness × provisional connections",
            "missing_data_flag": bool(missing_p),
            "interpretation": "; ".join(parts) if not missing_p else MISSING_DATA["missing_label"],
        }
    )
    return rows


def generate_disease_exposure(
    iso3_list: list[str] | None = None,
    disease: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return country Disease Exposure Index and long-form RMT indicators.

    Countries with RMT disease-status are scored. Mitigation may be missing
    (defaults to 0 in the raw risk formula, flagged in indicators). Countries
    without disease-status remain N/A.
    """
    disease = disease or ACTIVE_DISEASE
    iso3_list = iso3_list or sorted(ISO3_TO_NAME.keys())
    status_df, mit_df = load_rmt_inputs()

    status_map: dict[str, dict] = {}
    if not status_df.empty:
        col = f"disease_status_{disease.lower()}"
        if col not in status_df.columns and disease == "FMD":
            col = "disease_status_fmd"
        for _, r in status_df.iterrows():
            iso = str(r["iso3"])
            status_map[iso] = {
                "value": r.get(col),
                "source": r.get("source", "EuFMD RMT"),
                "year": r.get("source_year"),
            }

    mit_map: dict[str, dict] = {}
    if not mit_df.empty:
        col = f"mitigation_{disease.lower()}"
        if col not in mit_df.columns and disease == "FMD":
            col = "mitigation_fmd"
        for _, r in mit_df.iterrows():
            iso = str(r["iso3"])
            mit_map[iso] = {
                "value": r.get(col),
                "source": r.get("source", "EuFMD RMT"),
                "year": r.get("source_year"),
            }

    p_term = pathway_term(disease)
    country_rows: list[dict] = []
    indicator_rows: list[dict] = []

    for iso3 in iso3_list:
        country = ISO3_TO_NAME.get(iso3, iso3)
        region = ISO3_TO_REGION.get(iso3)
        st = status_map.get(iso3)
        mt = mit_map.get(iso3)

        d_val = None if st is None else st["value"]
        if d_val is not None and (isinstance(d_val, float) and np.isnan(d_val)):
            d_val = None
        m_val = None if mt is None else mt["value"]
        if m_val is not None and (isinstance(m_val, float) and np.isnan(m_val)):
            m_val = None

        has_status = d_val is not None
        raw = rmt_raw_risk(d_val, m_val, disease=disease) if has_status else None
        index = rmt_to_100(raw, disease=disease) if has_status else None

        domestic = _status_to_100(d_val) if has_status else None
        mitig_gap = _mitigation_gap_to_100(m_val) if m_val is not None else (
            100.0 if has_status else None
        )  # Nexus default mitigation=0 → full gap when status known but mit missing
        network = float(np.clip(p_term / 15.0 * 100.0, 0, 100)) if has_status else None

        n_avail = int(has_status) + int(m_val is not None)
        country_rows.append(
            {
                "iso3": iso3,
                "country": country,
                "region": region,
                "disease_exposure": index,
                "domestic_exposure": None if domestic is None else round(domestic, 1),
                "network_exposure": None if network is None else round(network, 1),
                "trade_movement_exposure": None if mitig_gap is None else round(mitig_gap, 1),
                "disease_status_raw": d_val,
                "mitigation_raw": m_val,
                "rmt_raw_risk": None if raw is None else round(float(raw), 2),
                "pathway_term": p_term if has_status else None,
                "disease_indicators_available": n_avail,
                "disease_indicators_total": 2,
                "module_status": MODULE_STATUS if has_status else "N/A — no RMT disease-status extract",
                "connection_mode": "provisional" if has_status else None,
            }
        )
        indicator_rows.extend(
            _long_indicators(
                iso3=iso3,
                country=country,
                disease_status=d_val,
                mitigation=m_val,
                pathway_score=p_term if has_status else None,
                disease=disease,
                source_status=(st or {}).get("source", "—"),
                source_mit=(mt or {}).get("source", "—"),
                year_status=(st or {}).get("year"),
                year_mit=(mt or {}).get("year"),
            )
        )

    return pd.DataFrame(country_rows), pd.DataFrame(indicator_rows)
