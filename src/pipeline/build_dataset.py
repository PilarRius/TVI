"""
Build pipeline: RAW → CLEAN → INDICATORS → SCORES → DIMENSIONS → TVI

Run:  python -m scripts.build_data
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config.settings import CLEAN_DIR, PROCESSED_DIR, RAW_DIR, LEGAL_INDICATORS
from config.woah_regions import ISO3_TO_NAME
from src.modules.disease_exposure import generate_disease_exposure
from src.modules.economic_sensitivity import generate_economic_sensitivity
from src.modules.legal_preparedness import (
    compute_legal_preparedness,
    load_pvs_file,
)
from src.calculations.tvi import compute_tvi


def _ensure_dirs() -> None:
    for d in (RAW_DIR, CLEAN_DIR, PROCESSED_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _empty_legal_grid(iso3_list: list[str]) -> pd.DataFrame:
    """Full country × indicator grid with explicit null scores (N/A)."""
    rows = []
    for iso3 in iso3_list:
        for code, meta in LEGAL_INDICATORS.items():
            rows.append(
                {
                    "country": ISO3_TO_NAME.get(iso3, iso3),
                    "iso3": iso3,
                    "assessment_year": None,
                    "pvs_assessment_version": None,
                    "indicator": code,
                    "indicator_code": code,
                    "indicator_name": meta["name"],
                    "score": None,
                    "score_scale": "1-5",
                    "source": "No public PVS extract available",
                    "source_url": None,
                    "data_availability": "unavailable",
                    "missing_data_flag": True,
                }
            )
    return pd.DataFrame(rows)


def _load_or_generate_pvs(iso3_list: list[str]) -> pd.DataFrame:
    """
    Load legal indicators from data/raw/. Drop any leftover placeholder rows.
    Expand to a full country grid so missing countries/indicators are explicit N/A.
    """
    candidates = [
        RAW_DIR / "pvs_indicators.csv",
        RAW_DIR / "pvs_indicators.xlsx",
        RAW_DIR / "pvs_indicators.json",
        RAW_DIR / "pvsis_public" / "pvs_indicators_public_only.csv",
    ]
    raw = None
    source_path = None
    for path in candidates:
        if path.exists():
            print(f"Loading legal data from {path}")
            raw = load_pvs_file(path)
            source_path = path
            break

    grid = _empty_legal_grid(iso3_list)
    if raw is None:
        print(
            "No raw PVS file found — legal scores will be N/A for all countries. "
            "Run `python -m scripts.ingest_public_pvs` to populate public extracts."
        )
        return grid

    # Never keep synthetic placeholders in the live dataset
    if "data_availability" in raw.columns:
        raw = raw[raw["data_availability"].astype(str).str.lower() != "placeholder"].copy()
    if "source" in raw.columns:
        raw = raw[~raw["source"].astype(str).str.contains("PLACEHOLDER", case=False, na=False)].copy()

    if raw.empty:
        print("Legal file had no non-placeholder rows — all legal scores N/A.")
        return grid

    raw = raw.drop_duplicates(subset=["iso3", "indicator_code"], keep="first")
    g = grid.set_index(["iso3", "indicator_code"])
    r = raw.set_index(["iso3", "indicator_code"])
    # Align columns: update grid with non-null values from public/real extracts
    for col in r.columns:
        if col not in g.columns:
            g[col] = pd.NA
    g.update(r)
    # Force-copy availability/source even when score is null (explicit N/A from a public report)
    for col in ("data_availability", "source", "source_url", "assessment_year", "missing_data_flag"):
        if col in r.columns:
            overlap = r.index.intersection(g.index)
            g.loc[overlap, col] = r.loc[overlap, col]
    out = g.reset_index()
    n_scored = int(out["score"].notna().sum())
    n_countries = int(out.loc[out["score"].notna(), "iso3"].nunique())
    print(f"Legal overlay from {source_path.name}: {n_scored} scored cells across {n_countries} countries; rest N/A.")
    return out


def build_all() -> pd.DataFrame:
    """Execute the full data pipeline and write Parquet caches."""
    _ensure_dirs()
    iso3_list = sorted(ISO3_TO_NAME.keys())

    # --- Disease Exposure (RMT provisional) ---
    disease, disease_indicators = generate_disease_exposure(iso3_list)
    disease.to_parquet(PROCESSED_DIR / "disease_exposure.parquet", index=False)
    disease_indicators.to_parquet(PROCESSED_DIR / "disease_indicators.parquet", index=False)

    # --- Economic Sensitivity (mock module) ---
    economic, economic_indicators = generate_economic_sensitivity(iso3_list)
    economic.to_parquet(PROCESSED_DIR / "economic_sensitivity.parquet", index=False)
    economic_indicators.to_parquet(PROCESSED_DIR / "economic_indicators.parquet", index=False)

    # --- Legal Preparedness ---
    raw_pvs = _load_or_generate_pvs(iso3_list)
    raw_pvs.to_parquet(CLEAN_DIR / "clean_pvs.parquet", index=False)
    legal_country, legal_indicators = compute_legal_preparedness(raw_pvs)
    legal_country.to_parquet(PROCESSED_DIR / "legal_preparedness.parquet", index=False)
    legal_indicators.to_parquet(PROCESSED_DIR / "legal_indicators.parquet", index=False)

    # --- TVI ---
    tvi = compute_tvi(disease, economic, legal_country)
    tvi.to_parquet(PROCESSED_DIR / "tvi.parquet", index=False)
    tvi.to_csv(PROCESSED_DIR / "tvi.csv", index=False)

    meta = {
        "n_countries": len(tvi),
        "n_with_tvi": int(tvi["tvi"].notna().sum()),
        "n_with_disease": int(tvi["disease_exposure"].notna().sum()),
        "n_with_legal": int(tvi["legal_preparedness"].notna().sum()),
        "disease_module": "RMT_PROVISIONAL",
        "economic_module": "MOCK",
        "legal_module": "PUBLIC_REPORTS_OR_NA",
        "rmt_source": "data/raw/rmt" if (RAW_DIR / "rmt" / "rmt_disease_status.csv").exists() else "none",
        "pvs_source": "public_pvsis" if (RAW_DIR / "pvs_indicators.csv").exists() else "none",
        "missing_label": "N/A",
    }
    (PROCESSED_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Built TVI for {meta['n_with_tvi']} / {meta['n_countries']} countries.")
    return tvi


def load_processed() -> dict[str, pd.DataFrame]:
    """Load precomputed Parquet files for the Shiny app."""
    required = {
        "tvi": PROCESSED_DIR / "tvi.parquet",
        "disease": PROCESSED_DIR / "disease_exposure.parquet",
        "disease_indicators": PROCESSED_DIR / "disease_indicators.parquet",
        "economic": PROCESSED_DIR / "economic_sensitivity.parquet",
        "economic_indicators": PROCESSED_DIR / "economic_indicators.parquet",
        "legal": PROCESSED_DIR / "legal_preparedness.parquet",
        "legal_indicators": PROCESSED_DIR / "legal_indicators.parquet",
    }
    missing = [k for k, p in required.items() if not p.exists()]
    # Rebuild when disease module schema is outdated (pre-RMT caches)
    disease_path = required["disease"]
    if disease_path.exists() and "disease_indicators" not in missing:
        try:
            cols = set(pd.read_parquet(disease_path, columns=None).columns)
            if "disease_status_raw" not in cols or not required["disease_indicators"].exists():
                missing.append("disease_schema")
        except Exception:
            missing.append("disease_schema")
    econ_path = required["economic"]
    if econ_path.exists() and "economic_indicators" not in missing:
        try:
            if not required["economic_indicators"].exists():
                missing.append("economic_schema")
        except Exception:
            missing.append("economic_schema")
    if missing:
        print(f"Missing caches {missing} — running build_all()…")
        build_all()
    return {k: pd.read_parquet(p) for k, p in required.items()}
