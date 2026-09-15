"""
Central configuration for the Trade Vulnerability Index (TVI).

All weights, thresholds, and transformation rules live here so the UI
never hard-codes methodology parameters.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
PROCESSED_DIR = DATA_DIR / "processed"
ASSETS_DIR = PROJECT_ROOT / "assets"

# ---------------------------------------------------------------------------
# Disease focus
# ---------------------------------------------------------------------------
ACTIVE_DISEASE = "FMD"
DISEASE_LABELS = {
    "FMD": "Foot-and-Mouth Disease",
    "PPR": "Peste des Petits Ruminants (coming soon)",
    "ASF": "African Swine Fever (coming soon)",
    "HPAI": "Highly Pathogenic Avian Influenza (coming soon)",
}
AVAILABLE_DISEASES = ["FMD"]  # others shown as disabled in UI

# ---------------------------------------------------------------------------
# Dimension weights (must sum to 1.0)
# ---------------------------------------------------------------------------
DIMENSION_WEIGHTS = {
    "disease_exposure": 1.0 / 3.0,
    "economic_sensitivity": 1.0 / 3.0,
    "legal_preparedness": 1.0 / 3.0,
}

# Legal preparedness is a resilience score. Convert to vulnerability
# contribution before aggregating into TVI.
# Formula: vulnerability_contribution = LEGAL_VULN_TRANSFORM(preparedness)
# Default: 100 - preparedness
LEGAL_VULN_TRANSFORM = "invert_100"  # options: invert_100, none

# ---------------------------------------------------------------------------
# Legal preparedness — component & indicator weights
# ---------------------------------------------------------------------------
LEGAL_COMPONENT_WEIGHTS = {
    "domestic_legal_readiness": 0.50,
    "trade_continuity_preparedness": 0.50,
}

LEGAL_INDICATOR_WEIGHTS = {
    # Domestic Legal Readiness
    "IV-1A": 0.50,
    "IV-1B": 0.50,
    # Trade-Continuity Preparedness
    "IV-4": 1.0 / 3.0,
    "IV-6": 1.0 / 3.0,
    "IV-7": 1.0 / 3.0,
}

LEGAL_INDICATORS = {
    "IV-1A": {
        "name": "Veterinary legislation: legal quality and coverage",
        "component": "domestic_legal_readiness",
        "description": "Quality and coverage of veterinary legislation relevant to animal-health governance.",
    },
    "IV-1B": {
        "name": "Veterinary legislation: implementation and compliance",
        "component": "domestic_legal_readiness",
        "description": "Implementation and compliance of veterinary legislation in practice.",
    },
    "IV-4": {
        "name": "Equivalence and other types of sanitary agreements",
        "component": "trade_continuity_preparedness",
        "description": "Use of equivalence and sanitary agreements to support trade continuity.",
    },
    "IV-6": {
        "name": "Zoning",
        "component": "trade_continuity_preparedness",
        "description": "Capacity to establish and recognise disease-free zones.",
    },
    "IV-7": {
        "name": "Compartmentalisation",
        "component": "trade_continuity_preparedness",
        "description": "Capacity to establish and recognise disease-free compartments.",
    },
}

# PVS Critical Competency levels are typically 1–5.
PVS_SCORE_SCALE = {"min": 1.0, "max": 5.0}
# Normalisation target for all dimension indices
INDEX_SCALE = {"min": 0.0, "max": 100.0}

# ---------------------------------------------------------------------------
# Qualitative classification thresholds (inclusive upper bounds on 0–100)
# Configurable — never hard-code in UI.
# ---------------------------------------------------------------------------
CLASSIFICATION_THRESHOLDS = [
    {"label": "Very Low", "max": 20},
    {"label": "Low", "max": 40},
    {"label": "Moderate", "max": 60},
    {"label": "High", "max": 80},
    {"label": "Very High", "max": 100},
]

# For preparedness (higher = better), labels are inverted in presentation
PREPAREDNESS_LABELS = {
    "Very Low": "Very Weak",
    "Low": "Weak",
    "Moderate": "Moderate",
    "High": "Strong",
    "Very High": "Very Strong",
}

# ---------------------------------------------------------------------------
# Missing-data rules
# ---------------------------------------------------------------------------
MISSING_DATA = {
    # Never silently replace missing with zero.
    "impute_with_zero": False,
    # If a component has no available indicators, component score is null.
    "require_min_indicators_per_component": 1,
    # Country included in TVI only if all three dimensions are non-null,
    # OR if partial_tvi is True (weighted among available dimensions).
    "partial_tvi": False,
    "missing_label": "Data unavailable",
}

# ---------------------------------------------------------------------------
# Mock module seeds (reproducible placeholder data)
# ---------------------------------------------------------------------------
MOCK_SEED_DISEASE = 42
MOCK_SEED_ECONOMIC = 43
MOCK_SEED_LEGAL = 44

# ---------------------------------------------------------------------------
# Visual / brand tokens (institutional palette)
# ---------------------------------------------------------------------------
BRAND = {
    "navy": "#0B3A5B",
    "slate": "#1F3A4D",
    "teal": "#1A6B6B",
    "steel": "#4A6FA5",
    "sand": "#F4F6F8",
    "paper": "#FFFFFF",
    "ink": "#1A2332",
    "muted": "#5A6A7A",
    "line": "#D0D7DE",
    # Semantic
    "exposure": "#B85C38",       # warm earth — risk/exposure
    "economic": "#8B6914",       # ochre — economic
    "preparedness": "#2E6B5E",   # deep green — resilience
    "vulnerability": "#8B3A4A",  # muted burgundy — overall vulnerability
    "protective": "#2E6B5E",
    "contribute": "#8B3A4A",
}

# Choropleth scale for TVI (low → high vulnerability)
TVI_COLORSCALE = [
    [0.0, "#E8F0F5"],
    [0.25, "#A8C4D4"],
    [0.5, "#5B8FA8"],
    [0.75, "#8B5A6B"],
    [1.0, "#6B2D3C"],
]

APP_TITLE = "Trade Vulnerability Index"
APP_SUBTITLE = "Animal-Health Shocks · WOAH Datathon"
