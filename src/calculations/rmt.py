"""RMT risk-score helpers mirroring EuFMD-Nexus calculateRiskScores."""

from __future__ import annotations

from config.rmt import (
    PATHWAY_EFFECTIVENESS,
    PROVISIONAL_PATHWAY_CONNECTIONS,
    max_raw_risk,
)


def pathway_term(
    disease: str = "FMD",
    connection_scores: dict[str, float] | None = None,
) -> float:
    """Σ(pathway_effectiveness × connection_score) for one disease."""
    eff = PATHWAY_EFFECTIVENESS[disease]
    conn = connection_scores or PROVISIONAL_PATHWAY_CONNECTIONS
    return float(sum(eff[k] * float(conn.get(k, 0.0)) for k in eff))


def rmt_raw_risk(
    disease_status: float | None,
    mitigation: float | None,
    disease: str = "FMD",
    connection_scores: dict[str, float] | None = None,
) -> float | None:
    """
    Raw RMT risk for one source country / disease.

    Nexus rules:
      - disease_status 0 or null → risk 0 (free / unknown treated as no scored risk here)
      - mitigation null → default 0 (uncontrolled)
    """
    if disease_status is None:
        return None
    try:
        d = float(disease_status)
    except (TypeError, ValueError):
        return None
    if d != d:  # NaN
        return None
    if d == 0:
        return 0.0

    if mitigation is None or (isinstance(mitigation, float) and mitigation != mitigation):
        m = 0.0
    else:
        m = float(mitigation)

    return float((d + (4.0 - m)) * pathway_term(disease, connection_scores))


def rmt_to_100(raw: float | None, disease: str = "FMD") -> float | None:
    """Normalise raw RMT risk to 0–100 using theoretical max under provisional connections."""
    if raw is None:
        return None
    if raw != raw:
        return None
    cap = max_raw_risk(disease)
    if cap <= 0:
        return None
    return float(round(min(100.0, max(0.0, (raw / cap) * 100.0)), 1))
