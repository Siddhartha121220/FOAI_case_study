"""Live demonstration scenario (CLAUDE.md #35): normal flow, a doctor-failure
disruption, then ICU resource contention (3 critical patients, 2 ICU beds).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from smart_hospital.config import SimulationConfig  # noqa: E402
from smart_hospital.environment.events import trigger_doctor_failure  # noqa: E402
from smart_hospital.model import HospitalModel  # noqa: E402
from smart_hospital.visualization.dashboard import render_map_snapshot, render_text  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent.parent / "experiments" / "results"


def run_until(model, ticks, print_every=5):
    for _ in range(ticks):
        model.step()
        if model.current_time % print_every == 0:
            print(render_text(model))
            print("-" * 60)


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    model = HospitalModel(SimulationConfig(random_seed=42, num_icu_beds=2))

    print("=== Phase 1: normal flow — patients arrive, triage, treat, discharge ===")
    p1 = model.spawn_patient(age=50, symptoms="chest pain", severity=9)
    p2 = model.spawn_patient(age=25, symptoms="fever", severity=3)
    # Stop as soon as p1 has a doctor but hasn't reached diagnosis yet (where
    # the doctor is freed), so the failure below actually interrupts care.
    for _ in range(10):
        model.step()
        if p1.assigned_doctor is not None and p1.current_state.name in ("DOCTOR_ASSIGNED", "TESTING"):
            break
    print(render_text(model))
    print("-" * 60)

    print("=== Phase 2: disruption — assigned doctor becomes unavailable ===")
    if p1.assigned_doctor is not None:
        failing_doctor = next(d for d in model.doctors if d.agent_id == p1.assigned_doctor)
        print(f"Doctor {failing_doctor.agent_id} failing while treating {p1.agent_id}")
        trigger_doctor_failure(model, failing_doctor)
    run_until(model, 10)
    print(f"Reassignments so far: {model.coordinator.reassignment_count}")

    print("=== Phase 3: ICU contention — 3 critical patients, 2 ICU beds ===")
    critical_patients = [
        model.spawn_patient(age=60, symptoms="chest pain", severity=10),
        model.spawn_patient(age=70, symptoms="fall", severity=9),
        model.spawn_patient(age=45, symptoms="chest pain", severity=9),
    ]
    run_until(model, 15)
    pending_icu = [r for r in model.bed_manager.pending_requests if r["bed_type"] == "ICU"]
    print(f"ICU beds occupied: {len(model.bed_manager.occupied)}  Pending ICU requests: {len(pending_icu)}")

    render_map_snapshot(model, RESULTS_DIR / "demo_map_snapshot.png")
    print(f"Saved hospital map snapshot to {RESULTS_DIR / 'demo_map_snapshot.png'}")

    print("=== Final metrics ===")
    print(model.metrics.summary())


if __name__ == "__main__":
    main()
