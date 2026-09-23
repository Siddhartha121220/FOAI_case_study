# Project Specification

The source of truth for this project is the root `CLAUDE.md` — it is the
brief this implementation was built against, section by section (agent
types, message format, algorithms, phases, testing requirements, etc.).
This file does not duplicate it; it records what "the spec" means in
practice for this codebase.

## Scope actually implemented

A Mesa-based multi-agent simulation of a hospital emergency department:
six agent types (`Patient`, `Doctor`, `Nurse`, `Lab`, `BedManager`,
`HospitalCoordinator`), explicit message-passing (no shared mutable state
between agents), a graph-based hospital environment with BFS/A* path
planning, a configurable triage priority policy, a configurable doctor
assignment cost function, dynamic events (failures, shortages, mass
casualty) with detection/reassignment, quantitative metrics with CSV
export, six reproducible experiments, and a minimal text + static-image
visualization. See `docs/SYSTEM_ARCHITECTURE.md` for how these fit
together and `docs/ASSUMPTIONS.md` for every place an implementation
decision had to fill a gap CLAUDE.md left open.

## No external rubric was supplied

Per CLAUDE.md #3 ("do not invent rubric requirements... document
assumptions"), `docs/RUBRIC_TRACEABILITY.md` maps CLAUDE.md's own stated
requirements to implementation/test/demo evidence, marked
`TO VERIFY AGAINST RUBRIC` throughout, since no separate grading rubric
document was ever provided to this project.

## Terminology

Used consistently with CLAUDE.md throughout the codebase and docs:
"priority" (not "urgency"), "severity" (1-10 scale), "task" (a coordinator-
tracked unit of work, not a Python `asyncio` task), "resource" (doctor,
nurse, lab capacity, or bed — anything contended for). See
`docs/COMMUNICATION_PROTOCOL.md` for message-type vocabulary.

## Explicit non-goals (CLAUDE.md #38)

No LLM APIs, no internet/cloud dependency, no database, no auth, no web
framework beyond what's needed for a local Mesa simulation. Confirmed: this
codebase's only third-party dependencies are `mesa`, `numpy`, `pandas`,
`matplotlib`, `networkx`, and `pytest` (see `requirements.txt`).

## Medical disclaimer (CLAUDE.md #40)

This project is an educational Multi-Agent Systems simulation. It is not a
clinical decision-support system and does not provide medical advice.
Patient, triage, treatment, and resource-allocation behavior are simulated
for academic purposes only.
