# Agent Specifications

All agents subclass `BaseAgent` (`agents/base_agent.py`): private `knowledge`
dict, `agent_id`-addressed messaging via `MessageBus`, `step()` = receive
then `decide()`.

## PatientAgent (`agents/patient.py`)

**State**: `age`, `symptoms`, `severity`, `arrival_time`, `waiting_time`,
`current_state` (see below), `assigned_doctor`, `assigned_nurse` (field
exists, unused — see Assumptions), `required_tests`, `completed_tests`,
`test_results`, `assigned_bed`, `treatment_status`, `location`, `priority`
(recomputed every tick by `algorithms/triage.compute_priority`).

**Goals**: reach DISCHARGED, minimize waiting time, complete required tasks.

**States** (`PatientState` enum), each with its own handler — not a single
conditional: `ARRIVED -> TRIAGED -> WAITING -> DOCTOR_ASSIGNED -> TESTING ->
DIAGNOSIS -> TREATMENT -> RECOVERY -> DISCHARGED`. `CRITICAL` is defined but
unused — severity-driven behavior differences (ICU vs GENERAL bed, priority
score) are handled via the severity value itself rather than a separate
state; `PARTIALLY IMPLEMENTED` relative to CLAUDE.md's optional
CRITICAL/ICU_REQUEST/ICU states.

**Decisions**: which resource to request next (state-driven), when to
re-request after `RESOURCE_UNAVAILABLE`, when to move vs. wait (only moves
once its bed is allocated; doctor comes to it).

## DoctorAgent (`agents/doctor.py`)

**State**: `specialization` (one of General Medicine/Cardiology/Trauma/
Neurology, round-robin assigned), `workload`, `maximum_workload` (default 2),
`current_patient`, `location`, `home_location`, `is_available` (failure
override).

**Goals**: accept patients within capacity, physically reach the patient,
return home when free.

**Decisions**: accept/reject a `DOCTOR_REQUEST` based on `availability`
(`is_available and workload < maximum_workload`) — the coordinator has
already picked *this* doctor via the cost function, so the doctor's own
decision is a capacity check, not a re-selection.

## NurseAgent (`agents/nurse.py`)

Same shape as `DoctorAgent` (accept/reject by workload, `fail`/`recover`),
built and tested (`tests/test_nurses.py`) but **not yet called** by
`PatientAgent`'s state machine — see `docs/ASSUMPTIONS.md`.

## LabAgent (`agents/lab.py`)

**State**: `available_capacity`, `max_capacity`, `processing_times` (per
test name), `test_queue`, `active_tests`, `completed_tests`.

**Goals**: process queued tests within capacity, return results.

**Decisions**: which queued test to start next (priority-sorted), when a
test finishes (`processing_times[test_name]` ticks). `fail`/`recover` model
equipment breakdown. Test results are `random.uniform(0, 100)` — simulated
values, no clinical meaning, per CLAUDE.md #10/#40.

## BedManagerAgent (`agents/bed_manager.py`)

**State**: `bed_counts` (per type: ICU/EMERGENCY/GENERAL), `occupied`
(bed_id -> patient_id), `pending_requests`.

**Goals**: allocate beds to the highest-priority pending request without
ever silently overwriting an existing allocation.

**Decisions**: on contention, sorts `pending_requests` by priority
descending and allocates while capacity allows; unmet requests stay
`pending_requests` and are re-evaluated every tick (including after a
`TASK_COMPLETE` release) — this is the literal mechanism behind CLAUDE.md
#17's "detect contention, compare priorities, allocate, keep unresolved,
re-evaluate."

## HospitalCoordinatorAgent (`agents/coordinator.py`)

**Knowledge**: `tasks` (Task objects, one per forwarded request, chained
via `dependencies`), `patient_priority`, `doctor_of_patient`,
`reassignment_count`, `emergency_count`.

**Goals**: route each request to the right resource agent, track task
state/dependencies, detect and act on reassignment/emergency signals.

**Decisions**: which resource agent to forward to (delegated to
`HospitalModel.find_available_doctor` / fixed `lab`/`bed_manager` targets —
the coordinator does not reimplement resource-picking logic itself, keeping
it a router rather than a monolith, per CLAUDE.md #12).
