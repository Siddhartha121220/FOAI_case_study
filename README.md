# Smart Hospital Emergency Room Management — MAS Case Study

Academic Multi-Agent Systems simulation of a hospital emergency department.
Built incrementally per `CLAUDE.md`, Phases 1-10 complete.

> This project is an educational Multi-Agent Systems simulation. It is not a
> clinical decision-support system and does not provide medical advice.
> Patient, triage, treatment, and resource-allocation behavior are simulated
> for academic purposes only.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run tests

```bash
.venv/bin/python -m pytest -q
```

## Run the demo scenario

```bash
.venv/bin/python scripts/run_demo.py
```

## Run the six experiments

```bash
.venv/bin/python experiments/run_experiments.py
```

Writes `experiments/results/experiment_results.csv` and four charts.

## Documentation

- `docs/PROJECT_SPECIFICATION.md` — what "the spec" means for this codebase
- `docs/SYSTEM_ARCHITECTURE.md` — agent model, data flow, simulation loop
- `docs/AGENT_SPECIFICATIONS.md` — per-agent state/goals/decisions
- `docs/AI_ALGORITHMS.md` — triage, assignment cost, BFS/A*, dependencies
- `docs/COMMUNICATION_PROTOCOL.md` — message format, routing, delivery
- `docs/EXPERIMENTS_AND_METRICS.md` — metric definitions, real results
- `docs/DEMO_PLAN.md` — what the live demo shows and why
- `docs/RUBRIC_TRACEABILITY.md` — requirement -> evidence matrix
- `docs/ASSUMPTIONS.md` — every implementation decision CLAUDE.md left open,
  organized by phase, including real bugs found and fixed along the way

## Status

50/50 tests passing. All 6 agent types implemented; `NurseAgent` is built
and tested but not yet wired into the active patient flow (see
`ASSUMPTIONS.md`). Six reproducible experiments with real CSV/chart output.
Known limitations are documented, not hidden — see `RUBRIC_TRACEABILITY.md`
§"Known gaps".
