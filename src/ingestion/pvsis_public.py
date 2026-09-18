"""
Ingest public WOAH PVS Evaluation / Follow-Up reports from PVSIS.

Public catalog (no login):
  GET https://pvs.woah.org/pvs-is-be/api/document-management/public

Public PDF download:
  GET https://pvs.woah.org/pvs-is-be/api/document-management/download-public/{id}

This does NOT unlock confidential Member-only Critical Competency tables.
It only uses reports WOAH has already marked public.

Run:
  python -m scripts.ingest_public_pvs
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from collections import defaultdict
from io import BytesIO
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from config.settings import RAW_DIR
from config.woah_regions import ISO3_TO_NAME, name_for

PUBLIC_LIST_URL = "https://pvs.woah.org/pvs-is-be/api/document-management/public"
PUBLIC_DOWNLOAD_URL = (
    "https://pvs.woah.org/pvs-is-be/api/document-management/download-public/{doc_id}"
)

# Country name variants appearing in PVSIS → ISO3
COUNTRY_NAME_TO_ISO3: dict[str, str] = {
    v.lower(): k for k, v in ISO3_TO_NAME.items()
}
COUNTRY_NAME_TO_ISO3.update(
    {
        "south sudan (rep. of)": "SSD",
        "south sudan": "SSD",
        "united arab emirates": "ARE",
        "republic of moldova": "MDA",
        "moldova": "MDA",
        "kingdom of tonga": "TON",
        "tonga": "TON",
        "lao people's democratic republic": "LAO",
        "lao pdr": "LAO",
        "viet nam": "VNM",
        "vietnam": "VNM",
        "czechia": "CZE",
        "czech republic": "CZE",
        "türkiye": "TUR",
        "turkey": "TUR",
        "cote d'ivoire": "CIV",
        "côte d'ivoire": "CIV",
        "democratic republic of the congo": "COD",
        "congo (dem. rep. of the)": "COD",
        "congo": "COG",
        "iran (islamic republic of)": "IRN",
        "iran": "IRN",
        "russian federation": "RUS",
        "bolivia (plurinational state of)": "BOL",
        "tanzania": "TZA",
        "united republic of tanzania": "TZA",
        "korea (rep. of)": "KOR",
        "republic of korea": "KOR",
        "united states of america": "USA",
        "united kingdom": "GBR",
        "china (people's rep. of)": "CHN",
        "people's republic of china": "CHN",
    }
)

# Canonical TVI indicators
TARGET_CODES = ["IV-1A", "IV-1B", "IV-4", "IV-6", "IV-7"]

# Map text labels / older PVS Tool numbering → canonical codes
LABEL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("IV-1A", re.compile(r"IV-1\.?\s*A\.?\s*(?:Veterinary\s+Legislation[:\s]*)?(?:Legal quality|Integrity and coverage)", re.I)),
    ("IV-1B", re.compile(r"IV-1\.?\s*B\.?\s*(?:Veterinary\s+Legislation[:\s]*)?(?:Implementation|Implementation of and compliance)", re.I)),
    ("IV-4", re.compile(r"IV-4\.?\s+Equivalence and other types of sanitary agreements", re.I)),
    ("IV-6", re.compile(r"IV-6\.?\s+Zoning", re.I)),
    ("IV-7", re.compile(r"IV-7\.?\s+Compartmentalisation", re.I)),
    # Older PVS Tool editions
    ("IV-4", re.compile(r"IV-5\.?\s+Equivalence and other types of sanitary agreements", re.I)),
    ("IV-6", re.compile(r"IV-7\.?\s+Zoning", re.I)),
    ("IV-7", re.compile(r"IV-8\.?\s+Compartmentalisation", re.I)),
]

SCORE_AFTER = re.compile(
    r"^(?P<label>.+?)\s+(?P<score>N/?A|NA|\d(?:\.\d)?)\s*$",
    re.I | re.M,
)


def _http_get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TVI-Datathon/1.0 (research prototype)", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_get_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TVI-Datathon/1.0 (research prototype)"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def fetch_public_catalog() -> pd.DataFrame:
    payload = _http_get_json(PUBLIC_LIST_URL)
    rows = payload.get("data") or []
    df = pd.DataFrame(rows)
    out_dir = RAW_DIR / "pvsis_public"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_json(out_dir / "public_catalog.json", orient="records", indent=2)
    return df


def filter_terrestrial_evaluation_reports(catalog: pd.DataFrame) -> pd.DataFrame:
    """Keep public terrestrial Evaluation / Follow Up reports (not Aquatic-only / JEE / NBW)."""
    df = catalog.copy()
    df["document_type"] = df["document_type"].fillna("")
    df["title"] = df["title"].fillna("")
    df["document_name"] = df["document_name"].fillna("")

    mask_type = df["document_type"].isin(["Evaluation", "Follow Up"])
    blob = (
        df["title"].str.lower()
        + " "
        + df["document_name"].str.lower()
        + " "
        + df["document_type"].str.lower()
    )
    # Exclude aquatic-only and bridging / JEE noise if mis-tagged
    exclude = blob.str.contains(
        r"aquatic|national bridging|jee\b|joint external|vlsp|workforce|ppp workshop",
        regex=True,
        na=False,
    )
    out = df.loc[mask_type & ~exclude].copy()

    def to_iso3(name: str) -> str | None:
        if not isinstance(name, str):
            return None
        key = name.strip().lower()
        if key in COUNTRY_NAME_TO_ISO3:
            return COUNTRY_NAME_TO_ISO3[key]
        # fuzzy contains
        for k, iso in COUNTRY_NAME_TO_ISO3.items():
            if k in key or key in k:
                return iso
        return None

    out["iso3"] = out["country_name"].map(to_iso3)
    out = out[out["iso3"].notna()].copy()
    # Prefer newest report per country
    out = out.sort_values(["iso3", "report_year", "id"], ascending=[True, False, False])
    out = out.drop_duplicates(subset=["iso3"], keep="first")
    return out.reset_index(drop=True)


def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 40) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    parts = []
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def parse_cc_scores(text: str) -> dict[str, float | None]:
    """
    Parse Levels of Advancement for target CCs from report text.

    Looks for summary-table style lines:
      IV-1.A. Veterinary Legislation: Legal quality and coverage 3
    """
    found: dict[str, float | None] = {}
    # Normalise whitespace
    compact = re.sub(r"[ \t]+", " ", text)
    lines = [ln.strip() for ln in compact.splitlines() if ln.strip()]

    for line in lines:
        m = SCORE_AFTER.match(line)
        if not m:
            continue
        label = m.group("label").strip()
        raw_score = m.group("score").strip().upper().replace(" ", "")
        score: float | None
        if raw_score in {"NA", "N/A"}:
            score = None
        else:
            try:
                score = float(raw_score)
            except ValueError:
                continue
            if not (1.0 <= score <= 5.0):
                continue

        for code, pattern in LABEL_PATTERNS:
            if pattern.search(label) and code not in found:
                found[code] = score
                break

    # Fallback: code + score on same line without full label
    if len(found) < 3:
        for code, alt in [
            ("IV-1A", r"IV-1\.?\s*A[^\n]{0,80}?\b([1-5](?:\.\d)?|N/?A)\b"),
            ("IV-1B", r"IV-1\.?\s*B[^\n]{0,80}?\b([1-5](?:\.\d)?|N/?A)\b"),
            ("IV-4", r"IV-4\.?[^\n]{0,80}Equivalence[^\n]{0,40}?\b([1-5](?:\.\d)?|N/?A)\b"),
            ("IV-6", r"IV-6\.?[^\n]{0,40}Zoning[^\n]{0,20}?\b([1-5](?:\.\d)?|N/?A)\b"),
            ("IV-7", r"IV-7\.?[^\n]{0,40}Compartmentalisation[^\n]{0,20}?\b([1-5](?:\.\d)?|N/?A)\b"),
        ]:
            if code in found:
                continue
            m = re.search(alt, compact, re.I)
            if not m:
                continue
            raw = m.group(1).upper().replace(" ", "")
            found[code] = None if raw in {"NA", "N/A"} else float(raw)

    return found


def ingest_public_pvs(
    *,
    max_reports: int | None = None,
    sleep_s: float = 0.4,
    keep_placeholders_for_missing_countries: bool = False,
) -> pd.DataFrame:
    """
    Download public Evaluation/Follow-Up PDFs, extract CC scores, write CSV.

    Countries without public extracts are omitted from the scored file; the
    pipeline expands to a full country grid with explicit N/A (null) scores.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pdf_dir = RAW_DIR / "pvsis_public" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    catalog = fetch_public_catalog()
    reports = filter_terrestrial_evaluation_reports(catalog)
    if max_reports is not None:
        reports = reports.head(max_reports)

    print(f"Public terrestrial Evaluation/Follow-Up reports selected: {len(reports)}")

    rows: list[dict] = []
    extraction_log: list[dict] = []

    for i, r in reports.iterrows():
        doc_id = int(r["id"])
        iso3 = r["iso3"]
        year = r.get("report_year")
        country = name_for(iso3)
        source_url = PUBLIC_DOWNLOAD_URL.format(doc_id=doc_id)
        title = r.get("title") or r.get("document_display_name") or ""
        print(f"[{i+1}/{len(reports)}] {iso3} ({year}) doc {doc_id}…", flush=True)

        pdf_path = pdf_dir / f"{iso3}_{year}_{doc_id}.pdf"
        try:
            if not pdf_path.exists():
                pdf_bytes = _http_get_bytes(source_url)
                pdf_path.write_bytes(pdf_bytes)
            else:
                pdf_bytes = pdf_path.read_bytes()
            text = extract_text_from_pdf(pdf_bytes)
            scores = parse_cc_scores(text)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            extraction_log.append(
                {"iso3": iso3, "doc_id": doc_id, "status": "error", "error": str(exc)}
            )
            time.sleep(sleep_s)
            continue

        n_found = sum(1 for c in TARGET_CODES if c in scores)
        print(f"  extracted {n_found}/5 -> {scores}")
        extraction_log.append(
            {
                "iso3": iso3,
                "doc_id": doc_id,
                "status": "ok" if n_found else "no_scores",
                "n_found": n_found,
                "scores": scores,
                "title": title,
                "source_url": source_url,
            }
        )

        for code in TARGET_CODES:
            if code not in scores:
                # Explicit missing for this public report (could not parse / not rated)
                rows.append(
                    {
                        "country": country,
                        "iso3": iso3,
                        "assessment_year": year,
                        "pvs_assessment_version": "Public PVS report (edition varies)",
                        "indicator": code,
                        "indicator_code": code,
                        "indicator_name": code,
                        "score": None,
                        "score_scale": "1-5",
                        "source": f"Public PVSIS report (parse incomplete): {title}",
                        "source_url": source_url,
                        "data_availability": "unavailable",
                        "missing_data_flag": True,
                    }
                )
                continue
            val = scores[code]
            missing = val is None
            rows.append(
                {
                    "country": country,
                    "iso3": iso3,
                    "assessment_year": year,
                    "pvs_assessment_version": "Public PVS report (edition varies)",
                    "indicator": code,
                    "indicator_code": code,
                    "indicator_name": code,
                    "score": val,
                    "score_scale": "1-5",
                    "source": f"Public PVSIS report: {title}",
                    "source_url": source_url,
                    "data_availability": "unavailable" if missing else "public_report",
                    "missing_data_flag": missing,
                }
            )
        time.sleep(sleep_s)

    public_df = pd.DataFrame(rows)

    # Optionally fill remaining countries with no rows as missing (not fake scores)
    if keep_placeholders_for_missing_countries:
        # Prefer: keep synthetic placeholders ONLY where no public country data at all
        from src.modules.legal_preparedness import generate_placeholder_pvs

        public_iso = set(public_df["iso3"].unique()) if not public_df.empty else set()
        # Countries with at least one non-missing public score
        real_iso = set()
        if not public_df.empty:
            real_iso = set(
                public_df.loc[~public_df["missing_data_flag"], "iso3"].unique()
            )

        placeholder = generate_placeholder_pvs()
        placeholder = placeholder[~placeholder["iso3"].isin(real_iso)].copy()
        placeholder["source"] = (
            "PLACEHOLDER — no public PVS Evaluation/Follow-Up extract yet; "
            "awaiting PVSIS access or approved data extract"
        )
        placeholder["data_availability"] = "placeholder"
        combined = pd.concat([public_df, placeholder], ignore_index=True)
        # If a country is in public_df but all missing, drop placeholder for that country too
        # (already excluded only real_iso; countries with only missing public rows still get placeholders
        #  — prefer public explicit missing over placeholder)
        public_attempted = set(public_df["iso3"].unique()) if not public_df.empty else set()
        combined = combined[
            ~((combined["data_availability"] == "placeholder") & combined["iso3"].isin(public_attempted))
        ]
    else:
        combined = public_df

    out_csv = RAW_DIR / "pvs_indicators.csv"
    combined.to_csv(out_csv, index=False)
    public_df.to_csv(RAW_DIR / "pvsis_public" / "pvs_indicators_public_only.csv", index=False)
    (RAW_DIR / "pvsis_public" / "extraction_log.json").write_text(
        json.dumps(extraction_log, indent=2, default=str), encoding="utf-8"
    )

    n_public_scores = int((combined["data_availability"] == "public_report").sum())
    n_countries_public = (
        combined.loc[combined["data_availability"] == "public_report", "iso3"].nunique()
        if n_public_scores
        else 0
    )
    print(f"Wrote {out_csv}")
    print(f"Public scored indicator cells: {n_public_scores} across {n_countries_public} countries")
    return combined


if __name__ == "__main__":
    ingest_public_pvs()
