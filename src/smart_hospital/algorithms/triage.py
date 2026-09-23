"""Configurable simulated triage priority policy (CLAUDE.md #14).

This is an academic simulation policy, not a clinically validated triage
algorithm.
"""
from __future__ import annotations

from ..config import SeverityWeights

MAX_WAITING_TIME_FOR_NORMALIZATION = 60


def compute_priority(severity: int, waiting_time: int, weights: SeverityWeights) -> float:
    normalized_waiting = min(waiting_time / MAX_WAITING_TIME_FOR_NORMALIZATION, 1.0)
    return weights.severity_weight * severity + weights.waiting_weight * normalized_waiting * 10
