# Assumptions

No rubric document was provided to this project. Rubric traceability
(`docs/RUBRIC_TRACEABILITY.md`) will be built from CLAUDE.md's stated
requirements only, marked `TO VERIFY AGAINST RUBRIC`.

## Phase 1

- Mesa 3.5 removed `RandomActivation`; scheduling is implemented via
  `model.agents.shuffle_do("step")` (Mesa 3.x's built-in `AgentSet`
  activation), not a custom scheduler class.
- `HospitalMap` graph in Phase 1 is a star topology through the Emergency
  Room, purely to prove connectivity; Phase 5 will decide whether a grid or
  a richer graph is used for A*/BFS.
- `MessageBus.receive` returns and clears an agent's full inbox each call,
  sorted by priority then timestamp — a pull model, not push/callback.

## Phase 2

- Doctor selection (`HospitalModel.find_available_doctor`) is a simple
  first-available scan, ignoring specialization/workload/distance cost.
  This is a placeholder; the real assignment cost function (CLAUDE.md #18)
  arrives in Phase 4.
- Triage in `PatientAgent` is a pass-through (severity already set at
  spawn) — the configurable triage policy (CLAUDE.md #14) arrives in
  Phase 4.
- `NurseAgent` exists with request/accept/release logic but is not yet
  invoked by `PatientAgent`'s state machine; nurse assignment is wired in
  when the Coordinator decomposes tasks in Phase 3.
- There is no `HospitalCoordinatorAgent` yet: `PatientAgent` sends
  requests directly to `DOCTOR-*`/`LAB-1`/`BED-MANAGER`. Phase 3
  introduces the coordinator and routes allocation decisions through it.

## Phase 3

- `PatientAgent` now sends `DOCTOR_REQUEST`/`TEST_REQUEST`/`BED_REQUEST`
  to `COORDINATOR`, which forwards to the chosen resource agent. Reply
  routing (`LabAgent`, `BedManagerAgent`) uses `payload["patient_id"]`,
  not `msg.sender`, since the coordinator relabels `sender` when it
  forwards — this keeps the resource agents unaware of who originated a
  request, matching "explicit messages, not direct state access."
- Coordinator marks a forwarded task `COMPLETE`-equivalent implicitly by
  not tracking the resource agent's reply; `Task.status` only reflects
  ASSIGNED/FAILED at forward time. Full task-lifecycle tracking (closing
  the loop on TASK_COMPLETE) is deferred to Phase 4 alongside real
  prioritization/assignment-cost logic.
- `HospitalCoordinatorAgent._reassign_doctor` exists and is tested
  directly; it is not yet triggered automatically by a doctor-failure
  event — that wiring is Phase 6 (Dynamic Environment).

## Phase 4

- Doctor selection now uses `algorithms/task_allocation.select_best_doctor`
  (assignment cost = workload + distance + specialization mismatch
  penalty), replacing the naive first-available scan from Phase 2/3.
  Distance uses `networkx.shortest_path_length` over the existing
  `HospitalMap` graph (a stdlib-adjacent, already-installed dependency —
  not a duplicate of the Phase 5 BFS/A* deliverable, which is about
  planning *movement*, not scoring a distance number).
  `symptoms -> specialization` is a small fixed lookup table, documented
  as an academic simplification, not a clinical mapping.
- Triage priority (`algorithms/triage.compute_priority`) is now live:
  `PatientAgent.priority` is recomputed every step from severity and
  waiting time and used as the message priority everywhere, so priority
  ages upward the longer a patient waits (visible starvation avoidance).
- `Task.dependencies` is a real, tested mechanism now
  (`Task.is_ready`), not just a data field: `HospitalCoordinatorAgent`
  chains each patient's tasks (doctor -> test -> bed) and marks the
  previous one `COMPLETE` when the next stage's request arrives — the
  coordinator infers completion from progression, since resource-agent
  replies bypass it by design (Phase 3).

## Phase 5

- `HospitalMap` now carries a fixed (x, y) grid position per location for
  A*'s Manhattan heuristic, plus 4 extra ring edges beyond the
  emergency-room hub (`DOCTOR_ROOM_1`-`DOCTOR_ROOM_2`,
  `LABORATORY`-`NURSE_STATION`, `ICU`-`GENERAL_WARD`,
  `PHARMACY`-`DOCTOR_ROOM_1`) so a single blocked route still has an
  alternate path — otherwise a pure star topology makes "replanning"
  vacuous (only ever one route to lose).
- `BaseAgent.move_toward` recomputes the path via `HospitalMap.plan_path`
  every call, so replanning is implicit — there is no separate "replan"
  API, a changed graph is simply picked up on the next hop.
- Movement is wired for two of the four flows CLAUDE.md names as
  "meaningful": Doctor -> Patient (on acceptance, doctor walks to the
  requesting patient's location; returns to `home_location` on
  `TASK_COMPLETE`) and Patient -> ICU/GENERAL_WARD (walks to the
  allocated bed before treatment ticks start counting down). Nurse ->
  Patient and Lab-transport -> Laboratory are not wired because
  `NurseAgent` and physical lab transport are not yet part of the active
  patient flow (see Phase 2/3 assumptions) — `move_toward` is generic and
  reusable for them once they are.

## Phase 6

- Failure/recovery is a boolean override (`is_available`) layered on top
  of the existing workload-based `availability` property on
  `DoctorAgent`/`NurseAgent`, not a new resource model. A failing doctor
  with a current patient sends its own `REASSIGNMENT_REQUEST` to the
  coordinator — the doctor detects and reports its own disruption, which
  is how CLAUDE.md #21's "detect -> communicate -> reassign" reads most
  naturally for a single-resource failure (vs. the coordinator having to
  poll every doctor's health each tick).
- `DynamicEventScheduler` draws from `config.event_probabilities` each
  tick using `model.random` (the seeded RNG), so organic events stay
  reproducible for a given seed. All four probabilities default to 0.0,
  so an ordinary run/test is unaffected unless a config explicitly
  enables them (Phase 8 experiments will).
- `trigger_mass_casualty`/`trigger_sudden_critical_patient` are explicit,
  deterministic functions (not scheduler-probability-driven) so
  Experiment C (Phase 8) can call them at an exact simulation tick.

## Phase 7

- "Waiting time" is defined as time from arrival to first doctor
  assignment (`PatientAgent.wait_until_doctor`), not the raw
  `waiting_time` field, which keeps incrementing every tick for the life
  of the agent (including after discharge) since `decide()` runs
  unconditionally each step. Treatment time is time spent physically in
  the TREATMENT state (captured between entering TREATMENT and leaving
  it for RECOVERY), separate from travel time to the bed.
- Doctor/nurse utilization = mean per-tick `workload / maximum_workload`
  across all agents of that type. Nurse utilization is always 0.0 since
  `NurseAgent` isn't wired into the active patient flow yet (Phase 2/3/5
  assumptions) — reported honestly rather than faked.
- "Number of path replans" is `HospitalMap.plan_count`: every call to
  `plan_path`, which happens once per hop per moving agent per tick. This
  is a literal count of planning invocations, not a narrower "the route
  changed due to a block" count — the latter isn't distinguishable from
  an ordinary multi-hop plan without extra bookkeeping this project
  doesn't need yet.
- `MetricsCollector.record_step()` runs at the end of every
  `HospitalModel.step()`, so utilization/queue-length series are
  full-resolution; `summary()`/`export_csv()` are called on demand, not
  automatically, so a caller controls when a run's numbers are frozen.

## Phase 8

- **Bug found and fixed while running real experiments at scale**: no
  agent ever sent `TASK_COMPLETE`, so `DoctorAgent.workload` and
  `BedManagerAgent.occupied` only ever grew — under sustained arrivals
  the hospital permanently saturated after ~7 patients and everyone
  after that starved forever. This was invisible in Phase 2-7's
  small (2-3 patient) tests, where capacity always happened to suffice.
  Fixed: `PatientAgent` now sends `TASK_COMPLETE` to its doctor on
  reaching DIAGNOSIS (consultation is done once diagnosis is reached)
  and to `BED-MANAGER` on reaching DISCHARGED. This is why the
  pre-existing test suite still passes unchanged — those tests never
  had enough patients to hit the leak — while the experiment numbers
  before/after the fix differ by an order of magnitude.
- Arrivals use `numpy.random.Generator.poisson(rate_per_minute)` per
  tick (numpy is already a required dependency; not a hand-rolled
  Poisson sampler). Severity is `clip(normal(5, 2.5), 1, 10)`, an
  academic approximation, not a real ED severity distribution.
- Experiments E (ICU Shortage) and F (Lab Failure) are implemented as
  reusing the Phase 6 event triggers (`num_icu_beds=1` at construction
  for E; `trigger_lab_failure` mid-run for F) rather than inventing a
  second mechanism — CLAUDE.md's wording for E/F doesn't specify
  "during execution" the way D does, so a static/config-level and a
  runtime-event approach were both defensible; picked whichever reused
  existing Phase 6 code.
- `lab_utilization` reads ~0.0 in every experiment. Confirmed via direct
  inspection this is not a bug — the lab genuinely processes tests
  (`completed_tests` grows) — but a 1-tick test (`ECG`, the only test
  requested at these severities) occupies `available_capacity` for
  exactly the tick it's queued *and* finishes in, so end-of-step
  sampling in `MetricsCollector.record_step()` never observes it busy.
  Left as an honest, documented measurement limitation rather than
  lengthening test processing times just to make the metric look
  nonzero — that would change simulated behavior to flatter a metric,
  backwards.

## Phase 9

- Visualization is a text dashboard (`render_text`, prints in any
  terminal, no GUI/display dependency) plus an optional static
  matplotlib map snapshot (`render_map_snapshot`, Agg backend, no
  interactive window needed) — not a live animated GUI or a Mesa
  SolaraViz browser app. CLAUDE.md #26 explicitly asks for "the simplest
  reliable visualization" and warns against spending excessive time on
  UI styling; a browser-based interactive dashboard would add a new
  dependency (solara) and a failure mode (needs a display/server) for
  marginal benefit over a snapshot + text readout in an academic demo
  context.
- `scripts/run_demo.py` needed hand-tuned timing to interrupt an
  *active* doctor-patient assignment: the Phase 8 fix frees a doctor as
  soon as its patient reaches DIAGNOSIS, so triggering `doctor_failure`
  too late in the script hit an already-idle doctor and produced zero
  reassignments — not a bug, just a demo script needing to trigger the
  disruption while the doctor is still genuinely busy.
