# Rubric Traceability

No external grading rubric was supplied to this project (see
`docs/ASSUMPTIONS.md`, `docs/PROJECT_SPECIFICATION.md`). Every row below
maps a requirement *stated in CLAUDE.md* to design/implementation/test/demo
evidence, and is marked `TO VERIFY AGAINST RUBRIC` since the actual grading
criteria may weight or phrase things differently.

| Criterion (CLAUDE.md #) | Design decision | Implementation | Test | Demo evidence |
|---|---|---|---|---|
| Autonomous agents (#5, #6) | `BaseAgent`: private knowledge, message-only interaction | `agents/base_agent.py` + 6 subclasses | `tests/test_patients.py`, `test_doctors.py`, `test_nurses.py`, `test_lab.py`, `test_beds.py`, `test_coordinator.py` | `scripts/run_demo.py` |
| Agent goals/decision-making (#5,#7-12) | State machine (Patient), cost function (Doctor selection), priority queue (Lab/Bed) | `agents/patient.py`, `algorithms/task_allocation.py` | `test_task_allocation.py` | dashboard state transitions |
| Multi-agent communication (#13) | Explicit `Message`/`MessageBus`, no direct calls | `communication/` | `test_messages.py` | `model.message_bus.log` |
| Cooperation/coordination (#12) | `HospitalCoordinatorAgent` routes, doesn't decide | `agents/coordinator.py` | `test_coordinator.py` | Demo Phase 1-2 |
| Resource contention (#17) | Priority-sorted pending queue, re-evaluated on release | `agents/bed_manager.py` | `test_beds.py::test_icu_contention_keeps_lowest_priority_pending` | Demo Phase 3 |
| Task allocation (#16) | `Task` with `dependencies`, coordinator-chained | `tasks/task.py`, `agents/coordinator.py` | `test_task_allocation.py::test_task_dependency_readiness`, `test_coordinator.py::test_coordinator_chains_task_dependencies_across_requests` | `coordinator.tasks` inspection |
| Search/path planning (#15) | BFS + A* (Manhattan heuristic), blocked-route reroute | `algorithms/bfs.py`, `algorithms/astar.py`, `environment/hospital_map.py` | `tests/test_astar.py` (7 tests incl. blocked reroute) | `demo_map_snapshot.png` |
| Dynamic planning / reassignment (#22, #21) | Doctor self-reports failure -> coordinator reassigns via same cost function | `agents/doctor.py::fail`, `agents/coordinator.py::_reassign_doctor` | `test_dynamic_events.py` (8 tests) | Demo Phase 2, `reassignment_count` |
| Knowledge representation (#19) | Per-agent private `knowledge` dict; no agent reads another's state directly | `agents/base_agent.py` | — (structural; enforced by design, not a runtime-checkable property) | code review |
| Dynamic environments (#20, #21) | `DynamicEventScheduler` (seeded, probability-driven) + explicit trigger functions | `environment/events.py` | `test_dynamic_events.py` | Experiment D/E/F |
| Partial observability (#20) | Doctor selection reads only `doctor.workload`/`.location`/`.specialization` via a read-only service, not full hospital state | `model.py::find_available_doctor` | implicit in `test_task_allocation.py` | — |
| Conflict resolution / reassignment (#21, #12) | See "Dynamic planning" row above | — | — | — |
| Performance measurement (#24) | 17 metrics, all computed from real run data | `metrics/collector.py` | `test_metrics.py` | `experiment_results.csv` |
| Stress testing (#25) | Six experiments incl. High Load, Mass Casualty | `experiments/run_experiments.py` | `test_experiments.py` | `experiments/results/` |
| Triage algorithm (#14) | Configurable linear weighted score | `algorithms/triage.py` | `test_triage.py` | priority visibly ages in long runs |
| Assignment cost function (#18) | workload + distance + mismatch penalty | `algorithms/task_allocation.py` | `test_task_allocation.py` | specialization-aware routing verified manually (Phase 4) |
| Automated tests (#28) | pytest, one file per component | `tests/` (15 files, 50 tests) | — | `pytest -q` output |
| Reproducibility (#30) | `random_seed` in config, `model.random`/numpy `default_rng(seed)` used everywhere randomness occurs | `config.py`, `model.py`, `experiments/run_experiments.py` | re-running experiments reproduces identical CSV | `EXPERIMENTS_AND_METRICS.md` |
| Error handling (#31) | `RESOURCE_UNAVAILABLE` replies, `None` returns from `find_available_doctor`/`plan_path` handled at every call site | throughout `agents/` | `test_doctors.py::test_doctor_rejects_when_full`, similar in nurse/lab/bed tests | — |
| Visualization (#26) | Text dashboard + static map snapshot | `visualization/dashboard.py` | `test_dashboard.py` | `demo_map_snapshot.png` |
| Documentation (#33) | All 9 listed docs present | `docs/*.md` | — | this file |
| Medical disclaimer (#40) | Present in README and PROJECT_SPECIFICATION | `README.md`, `docs/PROJECT_SPECIFICATION.md` | — | — |

## Known gaps (honestly, not glossed over)

- `NurseAgent`/`NURSE_REQUEST` flow: **PARTIALLY IMPLEMENTED** — agent and
  messages exist and are tested in isolation, not called by the active
  patient care path.
- `PatientState.CRITICAL`/`ICU_REQUEST`/`ICU` (CLAUDE.md's optional extra
  states): **NOT IMPLEMENTED** as separate states — severity drives bed-type
  and priority directly instead. See `AGENT_SPECIFICATIONS.md`.
- Lab-transport movement (#15's fourth example): **NOT IMPLEMENTED** —
  `move_toward` is generic and ready for it, no active flow needs it yet.
- `lab_utilization` metric reads ~0.0 due to a sampling-resolution
  limitation (documented in `EXPERIMENTS_AND_METRICS.md`), not a missing
  feature.
