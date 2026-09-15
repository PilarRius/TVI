"""
MOCK — REPLACE WITH REAL ECONOMIC SENSITIVITY MODEL

Generates realistic placeholder Economic Sensitivity Index values (0–100)
plus explanatory sub-indicators. Replace `generate_economic_sensitivity`
with the real economic module without changing the TVI layer.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import MOCK_SEED_ECONOMIC
from config.woah_regions import ISO3_TO_NAME, ISO3_TO_REGION

MODULE_STATUS = "MOCK — REPLACE WITH REAL ECONOMIC SENSITIVITY MODEL"

INDICATOR_META = {
    "livestock_importance": "Livestock economic importance",
    "export_exposure": "Livestock / animal-product export exposure",
    "import_dependence": "Import dependence for animal products",
    "trade_concentration": "Trade partner concentration risk",
}


def generate_economic_sensitivity(iso3_list: list[str] | None = None) -> pd.DataFrame:
    """
    Return country-level Economic Sensitivity Index and sub-indicators.

    Columns:
        iso3, country, region, economic_sensitivity,
        livestock_importance, export_exposure, import_dependence,
        trade_concentration, module_status
    """
    iso3_list = iso3_list or sorted(ISO3_TO_NAME.keys())
    rng = np.random.default_rng(MOCK_SEED_ECONOMIC)

    region_base = {
        "Africa": 55,
        "Americas": 48,
        "Asia and the Pacific": 50,
        "Europe": 42,
        "Middle East": 45,
    }

    rows = []
    for iso3 in iso3_list:
        region = ISO3_TO_REGION.get(iso3, "Europe")
        base = region_base.get(region, 45)
        livestock = float(np.clip(base + rng.normal(0, 15), 5, 95))
        export = float(np.clip(base + rng.normal(0, 18), 5, 95))
        imports = float(np.clip(base * 0.9 + rng.normal(0, 16), 5, 95))
        concentration = float(np.clip(base * 0.85 + rng.normal(0, 14), 5, 95))
        index = float(np.round((livestock + export + imports + concentration) / 4.0, 1))
        rows.append(
            {
                "iso3": iso3,
                "country": ISO3_TO_NAME.get(iso3, iso3),
                "region": region,
                "economic_sensitivity": index,
                "livestock_importance": round(livestock, 1),
                "export_exposure": round(export, 1),
                "import_dependence": round(imports, 1),
                "trade_concentration": round(concentration, 1),
                "module_status": MODULE_STATUS,
            }
        )
    return pd.DataFrame(rows)
