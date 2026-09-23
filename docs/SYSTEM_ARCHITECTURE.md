# System Architecture

## Overview

`HospitalModel` (Mesa `Model`, `src/smart_hospital/model.py`) owns:
- `message_bus` — the only channel agents use to reach each other.
- `hospital_map` — a graph environment service (locations, routes, A*/BFS).
- `event_scheduler` — draws dynamic disruptions each tick from config.
- `metrics` — records per-tick state, computes/export summary stats.
- Six agent types, registered with Mesa on construction.

## Agent model

Every agent (`agents/base_agent.py::BaseAgent`, a Mesa `Agent`) has:
- Local `knowledge: dict` (private; nothing external mutates it).
- An `agent_id` used for message routing (not Mesa's internal `unique_id`).
- `step()` = pull messages from its own inbox, then `decide(messages)`.

Agents never call methods on each other or read each other's attributes to
decide. They act only on messages received through `MessageBus`, or on
read-only environment services (`HospitalModel.find_available_doctor`,
`HospitalMap.plan_path`) that query state without mutating another agent.

## Data flow (one patient's care path)

```
PatientAgent                 HospitalCoordinatorAgent        Resource agent
-----------                  -----------------------         --------------
ARRIVED
  --PATIENT_ARRIVAL-------->  records priority
TRIAGED -> WAITING
  --DOCTOR_REQUEST--------->  cost-based doctor selection
                              --DOCTOR_REQUEST------------->  DoctorAgent
                                                               accepts/rejects
  <--DOCTOR_ASSIGNMENT---------------------------------------
DOCTOR_ASSIGNED
  --TEST_REQUEST (via COORDINATOR)------------------------->  LabAgent
  <--TEST_RESULT--------------------------------------------
DIAGNOSIS
  --TASK_COMPLETE (direct, frees doctor)-------------------->  DoctorAgent
  --BED_REQUEST (via COORDINATOR)---------------------------> BedManagerAgent
  <--BED_ALLOCATED-------------------------------------------
TREATMENT (walks to bed via A*) -> RECOVERY -> DISCHARGED
  --TASK_COMPLETE (direct, frees bed)------------------------> BedManagerAgent
```

The coordinator forwards requests and tracks a `Task` per stage with
`dependencies` chained to the previous stage (see `AI_ALGORITHMS.md`), but it
does not compute doctor/lab/bed decisions itself — that logic lives in each
resource agent and in `algorithms/task_allocation.py`, so the coordinator
stays a router, not a monolith.

## Simulation loop (`HospitalModel.step`)

```
1. current_time += 1
2. event_scheduler.maybe_trigger(self)   # dynamic events, seeded RNG
3. self.agents.shuffle_do("step")        # every agent: receive -> decide
4. metrics.record_step()                 # per-tick sampling
```

Mesa 3.x removed the `RandomActivation` scheduler class; `AgentSet.shuffle_do`
is its direct successor and is used instead — this is a Mesa API change, not
a design choice to build a custom scheduler.

## Package layout

See `README.md` for the directory tree. Each `src/smart_hospital/<package>`
maps 1:1 to a CLAUDE.md concept: `agents/` (autonomy), `communication/`
(messaging), `algorithms/` (triage, task allocation, BFS/A*),
`environment/` (map, dynamic events), `tasks/` (task model), `metrics/`
(collection/export), `visualization/` (dashboard).

## What is deliberately not built

See `docs/ASSUMPTIONS.md` for the full, phase-by-phase list. The two
structural ones: `NurseAgent` exists and is tested but is not yet called by
`PatientAgent`'s state machine; lab-transport movement is not wired. Both
reuse existing, tested machinery (`MessageBus`, `BaseAgent.move_toward`) and
were left out only because nothing in the current care path needs them yet.
