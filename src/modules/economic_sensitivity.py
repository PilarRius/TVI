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

# Long-form codes for the Economic Sensitivity detail tab
ECONOMIC_INDICATORS = {
    "EC-LIV": {
        "column": "livestock_importance",
        "name": "Livestock economic importance",
        "component": "production_at_risk",
        "description": "Proxy for livestock’s share of economic activity at risk from an FMD shock.",
    },
    "EC-EXP": {
        "column": "export_exposure",
        "name": "Export exposure",
        "component": "export_sensitivity",
        "description": "Importance of susceptible livestock / product exports relative to the economy.",
    },
    "EC-IMP": {
        "column": "import_dependence",
        "name": "Import dependence",
        "component": "import_sensitivity",
        "description": "Reliance on imported livestock and animal products (partner-shock vulnerability).",
    },
    "EC-CON": {
        "column": "trade_concentration",
        "name": "Trade partner concentration",
        "component": "trade_structure",
        "description": "Concentration of livestock-related trade among few partners (market-access risk).",
    },
}


def generate_economic_sensitivity(
    iso3_list: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return country-level Economic Sensitivity Index and long-form indicators.

    Columns (country):
        iso3, country, region, economic_sensitivity,
        livestock_importance, export_exposure, import_dependence,
        trade_concentration, economic_indicators_available,
        economic_indicators_total, module_status
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

    country_rows = []
    indicator_rows = []
    n_tot = len(ECONOMIC_INDICATORS)

    for iso3 in iso3_list:
        region = ISO3_TO_REGION.get(iso3, "Europe")
        country = ISO3_TO_NAME.get(iso3, iso3)
        base = region_base.get(region, 45)
        livestock = float(np.clip(base + rng.normal(0, 15), 5, 95))
        export = float(np.clip(base + rng.normal(0, 18), 5, 95))
        imports = float(np.clip(base * 0.9 + rng.normal(0, 16), 5, 95))
        concentration = float(np.clip(base * 0.85 + rng.normal(0, 14), 5, 95))
        values = {
            "livestock_importance": round(livestock, 1),
            "export_exposure": round(export, 1),
            "import_dependence": round(imports, 1),
            "trade_concentration": round(concentration, 1),
        }
        index = float(np.round(sum(values.values()) / 4.0, 1))
        country_rows.append(
            {
                "iso3": iso3,
                "country": country,
                "region": region,
                "economic_sensitivity": index,
                **values,
                "economic_indicators_available": n_tot,
                "economic_indicators_total": n_tot,
                "module_status": MODULE_STATUS,
            }
        )
        for code, meta in ECONOMIC_INDICATORS.items():
            score = values[meta["column"]]
            indicator_rows.append(
                {
                    "iso3": iso3,
                    "country": country,
                    "indicator_code": code,
                    "indicator_name": meta["name"],
                    "component": meta["component"],
                    "score": score,
                    "score_100": score,
                    "score_scale": "0-100",
                    "assessment_year": None,
                    "source": MODULE_STATUS,
                    "missing_data_flag": False,
                    "interpretation": meta["description"],
                }
            )

    return pd.DataFrame(country_rows), pd.DataFrame(indicator_rows)
