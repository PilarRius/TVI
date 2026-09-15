"""
MOCK — REPLACE WITH REAL DISEASE EXPOSURE MODEL

Generates realistic placeholder Disease Exposure Index values (0–100)
plus explanatory sub-indicators. Replace `generate_disease_exposure`
with the real epidemiological module without changing the TVI layer.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.settings import MOCK_SEED_DISEASE
from config.woah_regions import ISO3_TO_NAME, ISO3_TO_REGION

# Marker for documentation / data lineage
MODULE_STATUS = "MOCK — REPLACE WITH REAL DISEASE EXPOSURE MODEL"

INDICATOR_META = {
    "domestic_exposure": "Domestic disease status / exposure pressure",
    "network_exposure": "Exposure through connected trading partners",
    "trade_movement_exposure": "Trade and animal-movement exposure",
}


def generate_disease_exposure(iso3_list: list[str] | None = None) -> pd.DataFrame:
    """
    Return country-level Disease Exposure Index and sub-indicators.

    Columns:
        iso3, country, region, disease_exposure,
        domestic_exposure, network_exposure, trade_movement_exposure,
        module_status
    """
    iso3_list = iso3_list or sorted(ISO3_TO_NAME.keys())
    rng = np.random.default_rng(MOCK_SEED_DISEASE)

    # Regional baselines to create geographically plausible variation
    region_base = {
        "Africa": 58,
        "Americas": 32,
        "Asia and the Pacific": 48,
        "Europe": 28,
        "Middle East": 52,
    }

    rows = []
    for iso3 in iso3_list:
        region = ISO3_TO_REGION.get(iso3, "Europe")
        base = region_base.get(region, 40)
        domestic = float(np.clip(base + rng.normal(0, 14), 5, 95))
        network = float(np.clip(base * 0.9 + rng.normal(0, 16), 5, 95))
        trade = float(np.clip(base * 0.85 + rng.normal(0, 15), 5, 95))
        # Equal-weight composite for mock
        index = float(np.round((domestic + network + trade) / 3.0, 1))
        rows.append(
            {
                "iso3": iso3,
                "country": ISO3_TO_NAME.get(iso3, iso3),
                "region": region,
                "disease_exposure": index,
                "domestic_exposure": round(domestic, 1),
                "network_exposure": round(network, 1),
                "trade_movement_exposure": round(trade, 1),
                "module_status": MODULE_STATUS,
            }
        )
    return pd.DataFrame(rows)
