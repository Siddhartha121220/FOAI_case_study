# Demo Plan

Run: `.venv/bin/python scripts/run_demo.py`

Implements CLAUDE.md #35 exactly, in three phases:

## Phase 1 — Normal flow

Two patients spawn (severity 9 chest pain, severity 3 fever). The script
steps until the severity-9 patient has a doctor but hasn't reached diagnosis
yet (so Phase 2's failure interrupts *active* care, not an idle doctor —
see `ASSUMPTIONS.md` for why this timing needed hand-tuning after the Phase
8 fix). Dashboard shows: patients waiting, critical count, doctor/nurse/ICU
availability.

**What to point at**: the ARRIVED -> TRIAGED -> WAITING -> DOCTOR_ASSIGNED
progression in `render_text` output.

## Phase 2 — Disruption

`trigger_doctor_failure` is called on the patient's assigned doctor
mid-care. The doctor self-reports (`REASSIGNMENT_REQUEST`) to the
coordinator, which reassigns via the same cost function used for initial
assignment. Output: `Reassignments so far: 1`.

**What to point at**: `model.coordinator.reassignment_count`, and that the
patient's `assigned_doctor` changes without the patient's own state machine
needing to know a failure happened — the coordinator handled it invisibly
to the patient.

## Phase 3 — ICU contention

Three severity 9-10 patients spawn against 2 ICU beds. The bed manager
allocates to the 2 highest-priority requests and keeps the third pending;
dashboard shows `ICU beds available: 0/2`, then a bed frees as a patient is
discharged and the pending request is reconsidered.

**What to point at**: `model.bed_manager.pending_requests` non-empty at the
contention peak, then empty once a bed is released — this is
`BedManagerAgent._allocate_pending`, tested directly in
`tests/test_beds.py::test_icu_contention_keeps_lowest_priority_pending` and
`test_bed_release_frees_capacity_for_pending`.

## Artifacts produced

- Console dashboard output (all three phases).
- `experiments/results/demo_map_snapshot.png` — static hospital-graph
  snapshot with live per-location occupant counts, taken at the end of
  Phase 3.
- Final `model.metrics.summary()` printed to console.

## If asked "what's not shown here"

- Nurse assignment (`NurseAgent` is built/tested, not wired into this
  flow — see `ASSUMPTIONS.md`).
- BFS vs A* side-by-side (both exist and are tested in
  `tests/test_astar.py`; the demo only exercises A*, the default algorithm
  used by `move_toward`).
- The six formal experiments (`EXPERIMENTS_AND_METRICS.md`) — a separate,
  longer-running script (`experiments/run_experiments.py`), not part of
  this live demo's runtime budget.
