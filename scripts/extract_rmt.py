"""Extract EuFMD RMT disease-status / mitigation tables into data/raw/rmt/.

Looks for the FAST Excel next to this repo under:
  ../../New Programme/RMT/RMT_FAST_EuFmd_Clean_rv20231017.xlsx

Or pass --excel PATH.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from config.rmt import PATHWAY_EFFECTIVENESS, PATHWAY_DISPLAY_NAMES, RMT_NAME_TO_ISO3
from config.settings import RAW_DIR


DEFAULT_EXCEL = (
    Path(__file__).resolve().parents[3]
    / "New Programme"
    / "RMT"
    / "RMT_FAST_EuFmd_Clean_rv20231017.xlsx"
)


def extract(excel: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    ds = pd.read_excel(excel, sheet_name="disease status", header=0)
    ds = ds.rename(
        columns={
            "Country": "country",
            "Region": "rmt_region",
            "FMD": "disease_status_fmd",
            "PPR": "disease_status_ppr",
            "LSD": "disease_status_lsd",
            "RVF": "disease_status_rvf",
            "SGP": "disease_status_sgp",
        }
    )
    ds["iso3"] = ds["country"].map(RMT_NAME_TO_ISO3)
    missing = ds[ds["iso3"].isna()]["country"].tolist()
    if missing:
        raise ValueError(f"Unmapped RMT country names: {missing}")
    ds["source"] = "EuFMD RMT_FAST curated disease status (rv20231017)"
    ds["source_year"] = 2023
    ds.to_csv(out_dir / "rmt_disease_status.csv", index=False)

    mm = pd.read_excel(excel, sheet_name="mitigation measures", header=0)
    mm = mm.rename(
        columns={
            "Country": "country",
            "Region": "rmt_region",
            "FMD": "mitigation_fmd",
            "PPR": "mitigation_ppr",
            "LSD": "mitigation_lsd",
            "RVF": "mitigation_rvf",
            "SGP": "mitigation_sgp",
        }
    )
    mm["iso3"] = mm["country"].map(RMT_NAME_TO_ISO3)
    mm["source"] = "EuFMD RMT_FAST curated mitigation measures (rv20231017)"
    mm["source_year"] = 2023
    mm.to_csv(out_dir / "rmt_mitigation.csv", index=False)

    rows = []
    for key, label in PATHWAY_DISPLAY_NAMES.items():
        row = {"pathway": label, "pathway_key": key}
        for disease, eff in PATHWAY_EFFECTIVENESS.items():
            row[disease] = eff[key]
        row["source"] = "EuFMD-Nexus pathwaysConfig"
        rows.append(row)
    pd.DataFrame(rows).to_csv(out_dir / "rmt_pathway_effectiveness.csv", index=False)
    print(f"Wrote RMT extracts to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excel", type=Path, default=DEFAULT_EXCEL)
    parser.add_argument("--out", type=Path, default=RAW_DIR / "rmt")
    args = parser.parse_args()
    if not args.excel.exists():
        raise SystemExit(f"Excel not found: {args.excel}")
    extract(args.excel, args.out)


if __name__ == "__main__":
    main()
