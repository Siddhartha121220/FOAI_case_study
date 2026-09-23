"""Assignment cost function for doctor selection (CLAUDE.md #18).

cost = workload_weight * workload + distance_weight * distance + mismatch_penalty

Not "intelligent negotiation" — a visible, configurable scoring policy.
"""
from __future__ import annotations

import networkx as nx

from ..config import AllocationWeights

SYMPTOM_SPECIALIZATION = {
    "chest pain": "Cardiology",
    "fall": "Trauma",
    "trauma": "Trauma",
    "head injury": "Neurology",
    "seizure": "Neurology",
}


def specialization_for_symptoms(symptoms: str) -> str:
    return SYMPTOM_SPECIALIZATION.get(symptoms, "General Medicine")


def assignment_cost(doctor, symptoms: str, target_location: str, hospital_map, weights: AllocationWeights) -> float:
    try:
        distance = nx.shortest_path_length(hospital_map.graph, doctor.location, target_location)
    except nx.NetworkXNoPath:
        distance = float("inf")
    mismatch = 0 if doctor.specialization == specialization_for_symptoms(symptoms) else weights.mismatch_penalty
    return weights.workload_weight * doctor.workload + weights.distance_weight * distance + mismatch


def select_best_doctor(doctors, symptoms: str, target_location: str, hospital_map, weights: AllocationWeights):
    available = [d for d in doctors if d.availability]
    if not available:
        return None
    return min(available, key=lambda d: assignment_cost(d, symptoms, target_location, hospital_map, weights))
