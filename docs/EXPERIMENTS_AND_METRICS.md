# Experiments and Metrics

## Metrics (`metrics/collector.py`)

All 17 metrics from CLAUDE.md #24 are implemented in `MetricsCollector`.
Definitions that aren't self-evident:

- **Waiting time** = time from arrival to *first* doctor assignment
  (`PatientAgent.wait_until_doctor`), not the raw `waiting_time` field
  (which keeps incrementing for the agent's whole life, including after
  discharge, since `decide()` runs every tick unconditionally).
- **Treatment time** = ticks spent physically in the TREATMENT state,
  excluding travel time to the bed.
- **Utilization** (doctor/nurse/lab/bed) = mean of a per-tick snapshot
  (`workload/maximum_workload` for doctor/nurse; `(max-available)/max` for
  lab; `occupied/total` for bed), sampled at the end of every
  `HospitalModel.step()`.
- **Path replans** = total calls to `HospitalMap.plan_path` (one per hop
  per moving agent per tick) — a literal count of planning invocations, not
  narrowed to "the route actually changed due to a block."

Known measurement limitation, not a functional bug: `lab_utilization` reads
~0.0 in every run. Confirmed by direct inspection that the lab does process
tests; a 1-tick test (`ECG`, the only one requested at these severities)
starts and finishes within the same tick, so end-of-step sampling never
observes it mid-test. See `docs/ASSUMPTIONS.md`, Phase 8.

## Experiments (`experiments/run_experiments.py`)

Arrivals are `numpy.random.Generator.poisson(rate_per_minute)` per tick;
severity is `clip(normal(5, 2.5), 1, 10)`. All six use `random_seed=42` and
are reproducible — rerunning `python experiments/run_experiments.py`
reproduces the table below exactly.

| Experiment | Config | Disruption |
|---|---|---|
| A Normal Load | rate=2/min, 120 ticks | none |
| B High Load | rate=5/min, 120 ticks | none |
| C Mass Casualty | rate=2/min, 60 ticks | +15 critical patients at t=20 |
| D Doctor Failure | rate=2/min, 120 ticks | `trigger_doctor_failure` at t=30 |
| E ICU Shortage | rate=2/min, 120 ticks, `num_icu_beds=1` | none (static config) |
| F Lab Failure | rate=2/min, 120 ticks | `trigger_lab_failure` at t=30 |

### Actual results (last run, seed 42; see `experiments/results/experiment_results.csv`)

| experiment | avg_wait | served | remaining | doctor_util | reassigned | failed_requests |
|---|---|---|---|---|---|---|
| A_normal_load | 19.0 | 147 | 104 | 0.671 | 0 | 2790 |
| B_high_load | 24.1 | 153 | 451 | 0.734 | 0 | 13094 |
| C_mass_casualty | 12.2 | 59 | 90 | 0.683 | 0 | 1100 |
| D_doctor_failure | 20.0 | 127 | 124 | 0.551 | 1 | 3882 |
| E_icu_shortage | 19.0 | 146 | 105 | 0.671 | 0 | 2790 |
| F_lab_failure | 20.7 | 130 | 121 | 0.738 | 0 | 3733 |

Full precision in the CSV; charts (`average_waiting_time.png`,
`doctor_utilization.png`, `reassigned_tasks.png`,
`failed_resource_requests.png`) are in `experiments/results/`.

### Reading these numbers honestly

- **B vs A**: 2.5x the arrival rate produces far more `patients_remaining`
  (451 vs 104) with only a modest `avg_wait` increase for those who *do* get
  seen — the bottleneck shows up as a growing backlog, not as slower
  individual care, which is the expected signature of a capacity-bound
  queue.
- **D vs A**: doctor failure drops `doctor_utilization` (0.551 vs 0.671, one
  fewer effective doctor) and produces exactly 1 `reassigned_tasks` — the
  single doctor failure triggered exactly one reassignment, as expected.
- **`failed_resource_requests`** is large everywhere (thousands) because it
  counts every `RESOURCE_UNAVAILABLE` message, and a saturated doctor pool
  under Poisson arrivals produces many rejected requests before a slot
  frees — this is real contention, not a bug (see the Phase 8 resource-leak
  fix in `ASSUMPTIONS.md`, which reduced this number by roughly an order of
  magnitude from its pre-fix value).
- **These are the actual, reproducible outputs of this codebase at this
  commit** — not illustrative/invented numbers. Rerun the script to verify.
