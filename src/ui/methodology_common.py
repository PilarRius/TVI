"""Shared UI helpers for Methodology data-source cards."""

from __future__ import annotations

from htmltools import TagList, tags


def source_card(
    name: str,
    role: str,
    availability: str,
    access: str,
    usage: str,
    proposal: str,
    *,
    primary: bool = False,
) -> tags.div:
    cls = "tvi-source-card primary" if primary else "tvi-source-card"
    return tags.div(
        {"class": cls},
        tags.div(
            {"class": "tvi-source-head"},
            tags.h4(name),
            tags.span({"class": "tvi-source-role"}, role),
        ),
        tags.dl(
            {"class": "tvi-source-meta"},
            tags.dt("Availability"),
            tags.dd(availability),
            tags.dt("Access"),
            tags.dd(access),
            tags.dt("Usage in the Index"),
            tags.dd(usage),
        ),
        tags.p({"class": "tvi-source-proposal"}, tags.strong("Proposal: "), proposal),
    )


def model_questions_block(title: str, intro: str, questions: list[str]) -> TagList:
    """Questions colleagues should answer before coding the mathematical model."""
    return TagList(
        tags.h3(title),
        tags.p({"class": "tvi-questions-intro"}, intro),
        tags.ol(
            {"class": "tvi-model-questions"},
            *[tags.li(q) for q in questions],
        ),
    )
