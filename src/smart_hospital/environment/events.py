"""Dynamic environmental events (CLAUDE.md #21).

Two layers: explicit trigger_* functions for deterministic use in tests and
experiments (Phase 8), and DynamicEventScheduler for organic, seeded-random
occurrence during an ordinary run.
"""
from __future__ import annotations


def trigger_doctor_failure(model, doctor=None):
    doctor = doctor or model.random.choice(model.doctors)
    doctor.fail()
    return doctor


def trigger_doctor_recovery(doctor) -> None:
    doctor.recover()


def trigger_nurse_failure(model, nurse=None):
    nurse = nurse or model.random.choice(model.nurses)
    nurse.fail()
    return nurse


def trigger_nurse_recovery(nurse) -> None:
    nurse.recover()


def trigger_lab_failure(model, amount: int = 1) -> None:
    model.lab.fail(amount)


def trigger_lab_recovery(model, amount: int = 1) -> None:
    model.lab.recover(amount)


def trigger_icu_shortage(model, amount: int = 1) -> None:
    model.bed_manager.reduce_capacity("ICU", amount)


def trigger_icu_recovery(model, amount: int = 1) -> None:
    model.bed_manager.restore_capacity("ICU", amount)


def trigger_sudden_critical_patient(model):
    age = model.random.randint(18, 90)
    return model.spawn_patient(age=age, symptoms="trauma", severity=10)


def trigger_mass_casualty(model, count: int = 5) -> list:
    return [trigger_sudden_critical_patient(model) for _ in range(count)]


class DynamicEventScheduler:
    """Draws events each tick from config.event_probabilities, using the
    model's seeded RNG so a run is reproducible for a given seed."""

    def __init__(self, config) -> None:
        self.config = config

    def maybe_trigger(self, model) -> None:
        probs = self.config.event_probabilities
        if model.random.random() < probs.get("doctor_unavailable", 0):
            trigger_doctor_failure(model)
        if model.random.random() < probs.get("nurse_unavailable", 0):
            trigger_nurse_failure(model)
        if model.random.random() < probs.get("lab_failure", 0):
            trigger_lab_failure(model)
        if model.random.random() < probs.get("critical_arrival_boost", 0):
            trigger_sudden_critical_patient(model)
