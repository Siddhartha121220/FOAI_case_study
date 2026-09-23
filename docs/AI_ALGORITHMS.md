# AI Algorithms

## Triage priority (`algorithms/triage.py`)

```
priority = severity_weight * severity + waiting_weight * normalized_waiting * 10
normalized_waiting = min(waiting_time / 60, 1.0)
```

Weights come from `SimulationConfig.triage` (`SeverityWeights`), configurable,
default `severity_weight=1.0`, `waiting_weight=0.5`. This is an academic
simulation policy — not a clinically validated triage instrument (CLAUDE.md
#14, #40). Recomputed every tick per patient, so priority ages upward the
longer a patient waits, which is what drives message-queue ordering in
`MessageBus`, `LabAgent`, and `BedManagerAgent` (all sort by `-priority`).

**Why this algorithm**: a linear weighted sum is the simplest policy that (a)
is trivially configurable, (b) is deterministic given a seed, and (c)
visibly demonstrates starvation avoidance (a long-waiting low-severity
patient's priority eventually approaches a just-arrived high-severity one).

## Assignment cost function (`algorithms/task_allocation.py`)

```
cost = workload_weight * doctor.workload
     + distance_weight * shortest_path_length(doctor.location, target)
     + (mismatch_penalty if doctor.specialization != expected_specialization else 0)
```

`select_best_doctor` picks the minimum-cost doctor among those with spare
capacity. Weights come from `SimulationConfig.allocation`
(`AllocationWeights`). Distance uses `networkx.shortest_path_length` over
`HospitalMap.graph` — reusing the existing graph rather than a bespoke
distance metric. `symptoms -> specialization` is a small fixed lookup table
(`SYMPTOM_SPECIALIZATION`), an academic simplification, not a clinical
mapping (CLAUDE.md #18: "do not claim intelligent negotiation" — this is a
visible, configurable scoring policy, nothing more).

**Why this algorithm**: matches CLAUDE.md #18's example cost formula
directly; a greedy `min()` over a small doctor pool is the simplest
mechanism that produces specialization-aware, workload-aware, distance-aware
assignment without a combinatorial matching algorithm the project doesn't
need at this scale (documented via ponytail's `ladder` — see project
history, not the smallest correct approach isn't a bidding/auction protocol).

## Search: BFS and A* (`algorithms/bfs.py`, `algorithms/astar.py`)

Both operate over `HospitalMap.graph` (a `networkx.Graph`), with an optional
`blocked` node set that both respect identically.

- **BFS**: standard queue-based shortest-hop-count search, no heuristic.
- **A***: priority-queue (`heapq`) search using a Manhattan-distance
  heuristic (`|x1-x2| + |y1-y2|`) over `HospitalMap.positions` (a fixed
  (x, y) layout per location), per CLAUDE.md #15's example formula.

`HospitalMap.plan_path(start, goal, algorithm="astar"|"bfs")` is the single
entry point used everywhere (agent movement, tests, demo script) — no
duplicate pathfinding logic exists elsewhere. Both are exercised directly in
`tests/test_astar.py`, including a blocked-route reroute test and a
BFS/A* hop-count agreement test on the unweighted graph.

**Replanning**: `plan_path` recomputes from scratch on every call — there is
no separate "replan" API or cached-path invalidation logic. `BaseAgent.move_toward`
calls it once per hop, so a route blocked mid-journey is automatically
routed around on the agent's next step. This is the simplest correct
mechanism: a stale cached path is a class of bug a stateless recompute
cannot have.

## Task allocation and dependencies (`tasks/task.py`, `agents/coordinator.py`)

`Task.dependencies` is a list of prerequisite `task_id`s; `Task.is_ready()`
checks all of them are in a `completed_task_ids` set. The coordinator chains
each patient's tasks (DOCTOR -> TEST_REQUEST -> BED_REQUEST) via
`_new_task`, marking the previous task `COMPLETE` when the next stage's
request arrives (see `docs/ASSUMPTIONS.md`, Phase 3/4, for why completion is
inferred from progression rather than tracked via a reply message). Gating
on `is_ready()` before forwarding is real, tested logic
(`tests/test_task_allocation.py::test_task_dependency_readiness`,
`tests/test_coordinator.py::test_coordinator_chains_task_dependencies_across_requests`),
even though in the current single-path-per-patient flow it is always
satisfied by construction — the mechanism is there for a future multi-branch
task graph (e.g., parallel nurse + lab tasks) to use without redesign.

## Dynamic reassignment (`environment/events.py`, `agents/coordinator.py`)

When a doctor fails mid-care, it sends its own `REASSIGNMENT_REQUEST` to the
coordinator (self-reporting disruption, see `AGENT_SPECIFICATIONS.md`); the
coordinator re-runs `select_best_doctor` against the remaining available
pool. This reuses the same cost function as initial assignment — no separate
reassignment-scoring algorithm exists, since the problem (pick the best
available doctor) is identical.
