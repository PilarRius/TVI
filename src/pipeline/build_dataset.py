"""
Build pipeline: RAW → CLEAN → INDICATORS → SCORES → DIMENSIONS → TVI

Run:  python -m scripts.build_data
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config.settings import CLEAN_DIR, PROCESSED_DIR, RAW_DIR
from config.woah_regions import ISO3_TO_NAME
from src.modules.disease_exposure import generate_disease_exposure
from src.modules.economic_sensitivity import generate_economic_sensitivity
from src.modules.legal_preparedness import (
    compute_legal_preparedness,
    generate_placeholder_pvs,
    load_pvs_file,
)
from src.calculations.tvi import compute_tvi


def _ensure_dirs() -> None:
    for d in (RAW_DIR, CLEAN_DIR, PROCESSED_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _load_or_generate_pvs(iso3_list: list[str]) -> pd.DataFrame:
    """
    Prefer a user-supplied file in data/raw/; otherwise generate placeholders.

    Supported filenames:
      pvs_indicators.csv | .xlsx | .json
    """
    candidates = [
        RAW_DIR / "pvs_indicators.csv",
        RAW_DIR / "pvs_indicators.xlsx",
        RAW_DIR / "pvs_indicators.json",
    ]
    for path in candidates:
        if path.exists():
            print(f"Loading legal data from {path}")
            return load_pvs_file(path)

    print("No raw PVS file found — generating PLACEHOLDER legal scores.")
    print(
        "Note: WOAH PVSIS publishes reports; no public bulk indicator API "
        "was available for this prototype. Drop a file at data/raw/pvs_indicators.csv "
        "to replace placeholders."
    )
    raw = generate_placeholder_pvs(iso3_list)
    raw.to_csv(RAW_DIR / "pvs_indicators_placeholder.csv", index=False)
    raw.to_parquet(RAW_DIR / "pvs_indicators_placeholder.parquet", index=False)
    return raw


def build_all() -> pd.DataFrame:
    """Execute the full data pipeline and write Parquet caches."""
    _ensure_dirs()
    iso3_list = sorted(ISO3_TO_NAME.keys())

    # --- Disease Exposure (mock module) ---
    disease = generate_disease_exposure(iso3_list)
    disease.to_parquet(PROCESSED_DIR / "disease_exposure.parquet", index=False)

    # --- Economic Sensitivity (mock module) ---
    economic = generate_economic_sensitivity(iso3_list)
    economic.to_parquet(PROCESSED_DIR / "economic_sensitivity.parquet", index=False)

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
        "disease_module": "MOCK",
        "economic_module": "MOCK",
        "legal_module": "PLACEHOLDER",
        "pvs_source": "placeholder" if not (RAW_DIR / "pvs_indicators.csv").exists() else "user_file",
    }
    (PROCESSED_DIR / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Built TVI for {meta['n_with_tvi']} / {meta['n_countries']} countries.")
    return tvi


def load_processed() -> dict[str, pd.DataFrame]:
    """Load precomputed Parquet files for the Shiny app."""
    required = {
        "tvi": PROCESSED_DIR / "tvi.parquet",
        "disease": PROCESSED_DIR / "disease_exposure.parquet",
        "economic": PROCESSED_DIR / "economic_sensitivity.parquet",
        "legal": PROCESSED_DIR / "legal_preparedness.parquet",
        "legal_indicators": PROCESSED_DIR / "legal_indicators.parquet",
    }
    missing = [k for k, p in required.items() if not p.exists()]
    if missing:
        print(f"Missing caches {missing} — running build_all()…")
        build_all()
    return {k: pd.read_parquet(p) for k, p in required.items()}
