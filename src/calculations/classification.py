"""Shared classification helpers."""

from __future__ import annotations

from config.settings import CLASSIFICATION_THRESHOLDS, PREPAREDNESS_LABELS


def classify_score(score: float | None, *, preparedness: bool = False) -> str:
    """Map a 0–100 score to a qualitative label using configured thresholds."""
    if score is None or (isinstance(score, float) and score != score):  # NaN
        return "Data unavailable"
    for band in CLASSIFICATION_THRESHOLDS:
        if score <= band["max"]:
            label = band["label"]
            if preparedness:
                return PREPAREDNESS_LABELS.get(label, label)
            return label
    label = CLASSIFICATION_THRESHOLDS[-1]["label"]
    if preparedness:
        return PREPAREDNESS_LABELS.get(label, label)
    return label


def classify_css_class(score: float | None) -> str:
    """CSS modifier for score colouring."""
    if score is None or (isinstance(score, float) and score != score):
        return "na"
    label = classify_score(score)
    return {
        "Very Low": "very-low",
        "Low": "low",
        "Moderate": "moderate",
        "High": "high",
        "Very High": "very-high",
    }.get(label, "na")
