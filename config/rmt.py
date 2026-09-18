"""
RMT (Risk Monitoring Tool) parameters for Disease Exposure.

Adapted from EuFMD-Nexus:
  - frontend/src/utils/pathwaysConfig.ts
  - frontend/src/utils/calculateRiskScores.ts
  - frontend/src/utils/calculateConnectionScoresPerPathway.ts

Formula (source→target risk for one disease):
  risk = (disease_status + (4 - mitigation)) × Σ(pathway_effectiveness × connection_score)

Without bilateral connection inputs, the prototype uses provisional mid-level
pathway connection scores so countries with curated status/mitigation can still
be ranked. Replace with Comtrade / proximity / transport proxies when available.
"""

from __future__ import annotations

# Disease status scale (RMT expert / curated scores)
DISEASE_STATUS_SCALE = {"min": 0, "max": 3}
DISEASE_STATUS_LABELS = {
    0: "Free — pathogen not present",
    1: "Subclinical / sporadic — no current active livestock cases",
    2: "Low-level endemic — active cases in one region or sporadic now",
    3: "Highly endemic — active cases in multiple regions / sectors",
}

# Mitigation scale (higher = stronger control)
MITIGATION_SCALE = {"min": 0, "max": 4}
MITIGATION_LABELS = {
    0: "Uncontrolled risk — no meaningful mitigation",
    1: "Measures present but insufficient to substantially reduce risk",
    2: "Effective in some areas/sectors; important residual risks",
    3: "Strong mitigation with limited residual gaps",
    4: "Comprehensive mitigation substantially reducing spread risk",
}

# Pathway effectiveness 0–3 (Nexus PATHWAYS_EFFECTIVENESS)
PATHWAY_EFFECTIVENESS = {
    "FMD": {
        "airborne": 2,
        "vectorborne": 0,
        "wildAnimals": 1,
        "animalProduct": 2,
        "liveAnimal": 3,
        "fomite": 2,
    },
    "PPR": {
        "airborne": 0,
        "vectorborne": 0,
        "wildAnimals": 2,
        "animalProduct": 0,
        "liveAnimal": 3,
        "fomite": 2,
    },
    "LSD": {
        "airborne": 0,
        "vectorborne": 3,
        "wildAnimals": 0,
        "animalProduct": 1,
        "liveAnimal": 3,
        "fomite": 1,
    },
    "RVF": {
        "airborne": 0,
        "vectorborne": 3,
        "wildAnimals": 1,
        "animalProduct": 2,
        "liveAnimal": 3,
        "fomite": 0,
    },
    "SPGP": {
        "airborne": 0,
        "vectorborne": 1,
        "wildAnimals": 0,
        "animalProduct": 1,
        "liveAnimal": 3,
        "fomite": 2,
    },
}

PATHWAY_DISPLAY_NAMES = {
    "airborne": "Airborne",
    "vectorborne": "Vector-borne",
    "wildAnimals": "Wild animals",
    "animalProduct": "Animal product",
    "liveAnimal": "Live animal",
    "fomite": "Fomite",
}

# Provisional connection→pathway scores when bilateral inputs are missing.
# Same 0–2 style units as Nexus calculateConnectionScoresPerPathway outputs.
PROVISIONAL_PATHWAY_CONNECTIONS = {
    "airborne": 1.0,
    "vectorborne": 1.0,
    "wildAnimals": 1.0,
    "animalProduct": 1.5,
    "liveAnimal": 1.5,
    "fomite": 1.0,
}

# Theoretical max raw risk for normalisation (worst status, no mitigation, provisional connections)
def max_raw_risk(disease: str = "FMD") -> float:
    eff = PATHWAY_EFFECTIVENESS[disease]
    pathway_term = sum(eff[k] * PROVISIONAL_PATHWAY_CONNECTIONS[k] for k in eff)
    return float((DISEASE_STATUS_SCALE["max"] + (4 - MITIGATION_SCALE["min"])) * pathway_term)


RMT_NAME_TO_ISO3 = {
    "Mauritania": "MRT",
    "Morocco": "MAR",
    "Tunisia": "TUN",
    "Algeria": "DZA",
    "Mali": "MLI",
    "Afghanistan": "AFG",
    "Pakistan": "PAK",
    "Iraq": "IRQ",
    "Turkey": "TUR",
    "Georgia": "GEO",
    "Armenia": "ARM",
    "Azerbaijan": "AZE",
    "Iran": "IRN",
    "Syria": "SYR",
    "Palestine": "PSE",
    "Sudan": "SDN",
    "Libya": "LBY",
    "Egypt": "EGY",
    "Lebanon": "LBN",
    "Jordan": "JOR",
}
