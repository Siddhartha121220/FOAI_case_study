"""Central configuration for the simulation. No magic numbers elsewhere."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SeverityWeights:
    """Weights for the triage priority score (see docs/AI_ALGORITHMS.md)."""

    severity_weight: float = 1.0
    waiting_weight: float = 0.5


@dataclass
class AllocationWeights:
    """Weights for doctor/nurse assignment cost function."""

    workload_weight: float = 1.0
    distance_weight: float = 0.5
    mismatch_penalty: float = 5.0


@dataclass
class SimulationConfig:
    num_doctors: int = 4
    num_nurses: int = 6
    num_icu_beds: int = 2
    num_emergency_beds: int = 4
    num_general_beds: int = 6
    lab_capacity: int = 2

    arrival_rate_per_minute: float = 2.0
    duration_minutes: int = 120

    random_seed: int = 42

    triage: SeverityWeights = field(default_factory=SeverityWeights)
    allocation: AllocationWeights = field(default_factory=AllocationWeights)

    event_probabilities: dict = field(
        default_factory=lambda: {
            "doctor_unavailable": 0.0,
            "nurse_unavailable": 0.0,
            "lab_failure": 0.0,
            "critical_arrival_boost": 0.0,
        }
    )

    log_level: str = "INFO"
