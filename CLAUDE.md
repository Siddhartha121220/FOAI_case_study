# CLAUDE.md

# Smart Hospital Emergency Room Management
## Multi-Agent Systems Academic Project

You are Claude Code operating inside a real software repository.

You are the lead software engineer, AI systems architect, and testing engineer for this project.

Your job is to **actually build, test, debug, and document** the project in the repository. Do not merely describe code that should be written.

---

# 1. PROJECT OVERVIEW

Build an academic Multi-Agent System (MAS) called:

**Smart Hospital Emergency Room Management System**

The system simulates an emergency department in which multiple autonomous agents cooperate to manage patients, doctors, nurses, laboratory resources, beds, and treatment tasks.

The project must demonstrate genuine Multi-Agent Systems concepts rather than being a conventional hospital CRUD application.

The core concepts to demonstrate are:

- Autonomous agents
- Agent goals
- Agent decision-making
- Multi-agent communication
- Cooperation
- Coordination
- Resource contention
- Task allocation
- Search/path planning
- Dynamic planning
- Knowledge representation
- Dynamic environments
- Partial observability
- Conflict resolution
- Reassignment
- Performance measurement
- Stress testing

This is an **educational simulation**, not a medical system.

---

# 2. IMPORTANT ACADEMIC CONSTRAINT

This project is being developed for a Multi-Agent Systems case study.

The implementation must make it possible to explain:

1. What the agents are.
2. What each agent knows.
3. What each agent wants to achieve.
4. How agents make decisions.
5. How agents communicate.
6. How agents cooperate.
7. How agents compete for limited resources.
8. How the environment changes.
9. How agents react to changes.
10. Which AI algorithms are being used.
11. Why those algorithms were selected.
12. How the system is evaluated experimentally.

Do not build features merely for visual appeal.

Every major feature must have a clear academic purpose.

---

# 3. SOURCE OF TRUTH

The project requirements and rubric-related documents provided to this project should be treated as the source of truth.

Do not invent rubric requirements.

If a requirement is unclear or absent from the available specification, do not silently assume that it is mandatory.

If you need to make an implementation assumption, document it in:

`docs/ASSUMPTIONS.md`

Use the terminology from the project specification consistently.

---

# 4. TECHNOLOGY STACK

Use the simplest appropriate technology stack.

Primary stack:

- Python 3.11+
- Mesa for Multi-Agent Simulation
- NumPy where useful
- Pandas for experiment results
- Matplotlib for charts
- Pytest for testing
- NetworkX only where useful for graph representation

The core simulation must NOT require:

- OpenAI API
- Anthropic API
- Any LLM API
- Internet access
- Cloud services
- External databases

The system must run locally.

Do not introduce additional frameworks unless there is a strong technical reason.

---

# 5. CORE DESIGN PRINCIPLE

This must be a genuine multi-agent system.

Do NOT implement the project as:

```text
HospitalManager
    |
    +-- patient functions
    +-- doctor functions
    +-- nurse functions
Instead implement autonomous agents with:

Internal state
Goals
Local knowledge
Decision-making
Actions
Communication
Interactions with the environment

Agents should not freely modify each other's private state.

Communication should occur through explicit messages or well-defined environment services.

6. AGENT TYPES

The initial system must contain at least these agent types:

PatientAgent
DoctorAgent
NurseAgent
LabAgent
BedManagerAgent
HospitalCoordinatorAgent

Additional agent types may be introduced only when they provide clear academic value.

7. PATIENT AGENT

Each patient is an autonomous agent.

Patient state should include, as appropriate:

patient_id
age
symptoms
severity
arrival_time
waiting_time
current_state
assigned_doctor
assigned_nurse
required_tests
completed_tests
test_results
assigned_bed
treatment_status
location

Patient goals:

Receive appropriate simulated care.
Minimize unnecessary waiting.
Complete required tasks.
Reach an appropriate terminal state.

Patient states should be explicitly modeled.

At minimum:

ARRIVED
TRIAGED
WAITING
DOCTOR_ASSIGNED
DIAGNOSIS
TESTING
TREATMENT
RECOVERY
DISCHARGED

Critical cases may additionally use:

CRITICAL
ICU_REQUEST
ICU

Do not encode the patient workflow as one giant conditional function.

Use a clear state-machine or equivalent state-transition design.

8. DOCTOR AGENT

Doctors must be heterogeneous.

Possible specializations:

General Medicine
Cardiology
Trauma
Neurology

Doctor state:

doctor_id
specialization
availability
current_patient
workload
maximum_workload
location

Doctor decisions should consider:

Patient severity
Required specialization
Availability
Workload
Location
Current assignments

Do not make every doctor behave identically.

9. NURSE AGENT

Nurses should have:

nurse_id
availability
workload
maximum_workload
current_assignments
location

Nurse task selection can consider:

Patient priority
Patient waiting time
Workload
Distance/location
Task urgency
10. LAB AGENT

The laboratory is an autonomous resource-management agent.

Maintain:

test_queue
available_capacity
active_tests
processing_times
completed_tests

Support simulated tests such as:

Blood Test
ECG
X-Ray
CT Scan

The Lab Agent must:

Receive test requests.
Prioritize requests.
Process tests.
Complete tests.
Send results back to the relevant agent/coordinator.

Medical test results are simulated values only.

Do NOT claim medical validity.

11. BED MANAGER AGENT

Manage different simulated bed categories:

ICU
EMERGENCY
GENERAL

Maintain:

bed inventory
occupied beds
available beds
reservations
pending requests

The Bed Manager receives explicit requests.

When multiple patients request the same scarce resource:

Receive all requests.
Evaluate priorities.
Allocate available beds.
Keep unresolved requests pending.
Send allocation/rejection/pending messages.
Re-evaluate when resources become available.

Never silently overwrite an existing allocation.

12. HOSPITAL COORDINATOR AGENT

The HospitalCoordinatorAgent coordinates the system.

Responsibilities:

Receive messages.
Maintain coordination information.
Allocate tasks.
Resolve conflicts.
Coordinate resources.
Trigger reassignment.
Respond to emergencies.
Coordinate doctors, nurses, laboratory and beds.

The Coordinator should not become a giant monolithic controller.

Keep its responsibilities clearly defined.

13. COMMUNICATION SYSTEM

Implement explicit message passing.

Every message should contain:

message_id
timestamp
sender
receiver
message_type
priority
payload

Example:

{
    "message_id": "MSG-001",
    "timestamp": 42,
    "sender": "DOCTOR-03",
    "receiver": "BED-MANAGER",
    "message_type": "BED_REQUEST",
    "priority": 10,
    "payload": {
        "patient_id": "P-17",
        "bed_type": "ICU"
    }
}

At minimum support:

PATIENT_ARRIVAL
TRIAGE_RESULT
DOCTOR_REQUEST
DOCTOR_ASSIGNMENT
NURSE_REQUEST
NURSE_ASSIGNMENT
TEST_REQUEST
TEST_RESULT
BED_REQUEST
BED_ALLOCATED
BED_UNAVAILABLE
RESOURCE_UNAVAILABLE
EMERGENCY_ALERT
TASK_COMPLETE
REASSIGNMENT_REQUEST

Maintain communication logs so the communication process can be demonstrated during the presentation.

14. TRIAGE

Implement a configurable simulated triage policy.

Example severity scale:

1–3  Low
4–6  Moderate
7–8  Serious
9–10 Critical

Implement a configurable priority score.

For example:

priority =
    severity_weight * severity
    +
    waiting_weight * normalized_waiting_time

Weights must be configurable.

Do NOT describe this as a clinically validated triage algorithm.

It is an academic simulation policy.

Document this clearly.

15. SEARCH AND PATH PLANNING

Represent the hospital using a grid or graph.

Possible locations:

Emergency Room
Doctor Rooms
Nurse Station
Laboratory
Pharmacy
General Ward
ICU

Implement:

BFS
A*

A* should be the primary path-planning algorithm.

For a grid, Manhattan distance may be used as the heuristic:

h(n) = |x1-x2| + |y1-y2|

Implement support for:

Blocked locations
Unavailable routes
Replanning
Different start/end points

Use path planning for meaningful agent movements, such as:

Doctor → Patient
Nurse → Patient
Patient → ICU
Lab transport → Laboratory

Do not add pathfinding merely for decoration.

16. TASK ALLOCATION

The system must support explicit tasks.

Example:

Patient P17 requires:

Cardiologist
ECG
ICU
Treatment

The Coordinator can decompose this into:

TASK-1 → Doctor assignment
TASK-2 → ECG
TASK-3 → ICU allocation
TASK-4 → Treatment

Tasks should contain:

task_id
patient_id
required_agent_type
priority
status
assigned_agent
dependencies

Support dependencies.

Example:

Doctor assignment
        ↓
ECG
        ↓
Diagnosis
        ↓
ICU allocation
        ↓
Treatment
17. RESOURCE CONTENTION

Resource contention must be an explicit part of the simulation.

Example:

3 critical patients
2 ICU beds

The system must:

Detect contention.
Compare priorities.
Allocate resources according to the defined policy.
Keep unresolved requests.
Re-evaluate later.

The policy must be deterministic when given the same random seed and configuration.

18. NEGOTIATION / COORDINATION

Where appropriate, support a simple task-allocation or bidding mechanism.

Example:

Two doctors are eligible for a patient.

The system can compare:

specialization match
availability
workload
distance

and compute an explicit assignment cost.

Example:

cost =
    workload_weight * workload
    +
    distance_weight * distance
    +
    mismatch_penalty

The implementation must make the policy visible and configurable.

Do not claim that the system has "intelligent negotiation" if it is only a hard-coded random selection.

19. KNOWLEDGE REPRESENTATION

Agents should maintain local knowledge.

Doctor knowledge may include:

specialization
availability
own workload
assigned patients
relevant patient information
received messages

Bed Manager knowledge:

bed availability
bed type
reservations
pending requests

Coordinator knowledge:

task states
agent availability
resource requests
hospital-level coordination information

Avoid giving every agent unrestricted access to every other agent's internal state.

20. ENVIRONMENT PROPERTIES

The system should demonstrate the following characteristics where appropriate:

Partially observable
Dynamic
Sequential
Multi-agent
Resource-constrained
Stochastic where appropriate
Primarily discrete for simulation decisions
Cooperative overall, with local competition for scarce resources

Do not merely write these terms in documentation.

The implementation and experiments must demonstrate them.

For example:

Partially observable

A DoctorAgent should not automatically have complete hospital-wide information.

Dynamic

Doctor availability and patient arrivals can change during execution.

Sequential

A patient must complete dependent stages.

Stochastic

Patient arrivals and selected environmental events can use controlled randomness.

Cooperative

Agents work toward hospital-level objectives.

Resource contention

Multiple patients may request the same bed or doctor.

21. DYNAMIC EVENTS

Implement configurable environmental events.

Examples:

Doctor becomes unavailable
Nurse becomes unavailable
Lab machine failure
ICU bed becomes occupied
Equipment recovery
Sudden critical patient
Mass-casualty event
Increased patient arrival rate

When an event affects an active task:

Detect the disruption.
Mark the task appropriately.
Communicate the disruption.
Find alternatives.
Reassign if possible.
Re-plan.
Continue execution.
22. PLANNING

Implement goal-oriented dynamic planning.

Example:

Patient
 ↓
Triage
 ↓
Doctor
 ↓
Test
 ↓
Diagnosis
 ↓
Bed
 ↓
Treatment
 ↓
Recovery
 ↓
Discharge

If a resource becomes unavailable:

Doctor D1 unavailable
        ↓
Task fails/requires reassignment
        ↓
Find eligible doctor
        ↓
Assign D2
        ↓
Continue plan

The system must demonstrate that plans can change during execution.

23. SIMULATION LOOP

Design a clear simulation lifecycle.

Conceptually:

1. Advance simulation time
2. Generate environmental events
3. Generate new patients
4. Update waiting times
5. Process incoming messages
6. Run coordinator decisions
7. Run patient decisions
8. Run doctor decisions
9. Run nurse decisions
10. Process laboratory tasks
11. Process bed allocation
12. Execute movement/path planning
13. Complete treatment tasks
14. Update metrics
15. Render visualization

The actual Mesa scheduling mechanism may differ.

Document the chosen scheduling design and why it is appropriate.

24. METRICS

Collect at least:

Average waiting time
Median waiting time
Maximum waiting time
Critical patient response time
Average treatment time
Patients served
Patients remaining
Average queue length
Maximum queue length
Doctor utilization
Nurse utilization
Lab utilization
Bed utilization
Number of reassigned tasks
Number of failed resource requests
Number of communication messages
Number of path replans

Export experiment results to CSV.

Generate charts using Matplotlib.

25. EXPERIMENTS

Implement reproducible experiments.

Experiment A — Normal Load
Patients/minute = 2
Normal staffing
Normal resources
Experiment B — High Load
Patients/minute = 5
Same staffing
Experiment C — Mass Casualty
Patients/minute = 15
Large increase in critical patients
Experiment D — Doctor Failure

Make one doctor unavailable during execution.

Experiment E — ICU Shortage

Reduce ICU capacity.

Experiment F — Laboratory Failure

Reduce laboratory capacity.

Every experiment must produce actual data.

Never fabricate experiment results.

26. VISUALIZATION

Create a functional visualization.

Display:

Hospital map
Patients
Doctors
Nurses
Laboratory
Beds
Current simulation time

Also show:

Patients waiting
Critical patients
Available doctors
Available nurses
Available ICU beds
Average waiting time

Keep the visualization simple and reliable.

Do not spend excessive development time on UI styling.

27. PROJECT STRUCTURE

Use a structure similar to:

smart-hospital-mas/
│
├── CLAUDE.md
├── README.md
├── requirements.txt
├── pyproject.toml
│
├── docs/
│   ├── PROJECT_SPECIFICATION.md
│   ├── RUBRIC_TRACEABILITY.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── AGENT_SPECIFICATIONS.md
│   ├── AI_ALGORITHMS.md
│   ├── COMMUNICATION_PROTOCOL.md
│   ├── EXPERIMENTS_AND_METRICS.md
│   ├── DEMO_PLAN.md
│   └── ASSUMPTIONS.md
│
├── src/
│   └── smart_hospital/
│       ├── __init__.py
│       ├── config.py
│       ├── model.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base_agent.py
│       │   ├── patient.py
│       │   ├── doctor.py
│       │   ├── nurse.py
│       │   ├── lab.py
│       │   ├── bed_manager.py
│       │   └── coordinator.py
│       │
│       ├── communication/
│       │   ├── __init__.py
│       │   ├── message.py
│       │   └── message_bus.py
│       │
│       ├── algorithms/
│       │   ├── __init__.py
│       │   ├── bfs.py
│       │   ├── astar.py
│       │   ├── triage.py
│       │   └── task_allocation.py
│       │
│       ├── environment/
│       │   ├── __init__.py
│       │   ├── hospital_map.py
│       │   └── events.py
│       │
│       ├── tasks/
│       │   ├── __init__.py
│       │   └── task.py
│       │
│       ├── metrics/
│       │   ├── __init__.py
│       │   └── collector.py
│       │
│       └── visualization/
│           ├── __init__.py
│           └── dashboard.py
│
├── tests/
│   ├── test_patients.py
│   ├── test_doctors.py
│   ├── test_nurses.py
│   ├── test_lab.py
│   ├── test_beds.py
│   ├── test_messages.py
│   ├── test_triage.py
│   ├── test_astar.py
│   ├── test_task_allocation.py
│   └── test_simulation.py
│
├── experiments/
│   ├── configs/
│   ├── run_experiments.py
│   └── results/
│
└── scripts/
    └── run_demo.py

You may modify this structure if there is a good technical reason.

28. TESTING REQUIREMENTS

Use pytest.

Test at least:

Agents
Patient creation
Patient state transitions
Doctor assignment
Nurse assignment
Lab processing
Bed allocation
Communication
Message creation
Message delivery
Message ordering/priority where applicable
Invalid message handling
Algorithms
BFS
A*
Blocked path
Replanning
Triage
Task allocation
Resources
ICU contention
No available doctors
No available nurses
No lab capacity
Bed release
Dynamic events
Doctor failure
Lab failure
New critical patient
Reassignment
End-to-end

Run a complete small simulation.

29. CODE QUALITY

Follow:

PEP 8
Clear naming
Type hints where useful
Docstrings for important public interfaces
Small focused classes
Separation of concerns
No duplicated business logic
No unnecessary global state
No hidden magic numbers

Configuration should control:

number of doctors
number of nurses
number of beds
arrival rate
simulation duration
triage weights
allocation weights
random seed
event probabilities

Do not scatter hard-coded values throughout the code.

30. REPRODUCIBILITY

The simulation must support a random seed.

For example:

python -m smart_hospital --seed 42

Running the same experiment with the same configuration and seed should produce reproducible results, subject to documented framework behavior.

31. ERROR HANDLING

The system must gracefully handle:

No available doctor
No matching specialist
No available nurse
No ICU bed
No laboratory capacity
Invalid message
Failed path
Blocked destination
Agent becoming unavailable
Unexpected resource failure

Do not silently ignore errors.

Use appropriate logging.

32. LOGGING

Provide useful logs such as:

[10:32] Patient P17 arrived.
[10:32] P17 triaged with priority 9.
[10:33] Coordinator assigned Doctor D2.
[10:34] D2 requested ECG.
[10:35] Lab accepted ECG request.
[10:38] ECG completed.
[10:39] D2 requested ICU bed.
[10:39] ICU-02 allocated to P17.

Make logging configurable.

Do not flood the console unnecessarily.

33. DOCUMENTATION

Create and maintain:

docs/PROJECT_SPECIFICATION.md
docs/RUBRIC_TRACEABILITY.md
docs/SYSTEM_ARCHITECTURE.md
docs/AGENT_SPECIFICATIONS.md
docs/AI_ALGORITHMS.md
docs/COMMUNICATION_PROTOCOL.md
docs/EXPERIMENTS_AND_METRICS.md
docs/DEMO_PLAN.md
docs/ASSUMPTIONS.md

Documentation must describe the actual implementation.

Never document a feature before it exists as if it were already implemented.

After implementing a feature, update the relevant documentation.

34. RUBRIC TRACEABILITY

Create a traceability matrix.

Each rubric criterion should map to:

Criterion
↓
Design decision
↓
Implementation file
↓
Test
↓
Demo evidence
↓
Presentation/report evidence

Example:

Multi-agent communication
    ↓
MessageBus + Message
    ↓
src/.../communication/
    ↓
test_messages.py
    ↓
Communication demo
    ↓
Presentation section

Do not fabricate rubric mappings.

If the actual rubric is unavailable, explicitly mark the mapping as:

TO VERIFY AGAINST RUBRIC

35. DEMONSTRATION SCENARIO

The final demonstration should show:

Start simulation
        ↓
Patients arrive
        ↓
Triage
        ↓
Doctor assignment
        ↓
Nurse assignment
        ↓
Diagnostic test
        ↓
Bed request
        ↓
Treatment
        ↓
Discharge

Then introduce a disruption:

Doctor becomes unavailable
        ↓
Active task affected
        ↓
Coordinator detects failure
        ↓
Message sent
        ↓
Alternative doctor selected
        ↓
Task reassigned
        ↓
Simulation continues

Then introduce resource contention:

3 critical patients
2 ICU beds
        ↓
Bed Manager evaluates requests
        ↓
Resources allocated according to policy
        ↓
Pending patient remains queued
        ↓
Bed becomes available
        ↓
Pending request reconsidered

This should be the main live demonstration.

36. DEVELOPMENT PROCESS

DO NOT build everything at once.

Work incrementally.

PHASE 1 — Foundation

Implement:

Repository structure
Configuration
Base Agent abstraction
Hospital environment skeleton
Message model
Task model
Test infrastructure
Minimal Mesa model

Run tests.

Run a minimal simulation.

Fix all errors.

PHASE 2 — Core Agents

Implement:

PatientAgent
DoctorAgent
NurseAgent
LabAgent
BedManagerAgent

Create tests.

Run an end-to-end mini simulation.

PHASE 3 — Communication

Implement:

HospitalCoordinatorAgent
MessageBus
Message types
Communication logging
Task allocation
Resource requests

Test agent communication.

PHASE 4 — AI Decision-Making

Implement:

Triage
Task prioritization
Task dependencies
Resource allocation
Assignment cost function
Reassignment

Test decision-making.

PHASE 5 — Search

Implement:

BFS
A*
Hospital graph/grid
Blocked locations
Replanning

Create unit tests.

Demonstrate actual paths.

PHASE 6 — Dynamic Environment

Implement:

Doctor failure
Nurse failure
Lab failure
ICU shortage
Sudden critical patients
Mass-casualty events
Dynamic replanning

Test each event.

PHASE 7 — Metrics

Implement:

Waiting time
Treatment time
Queue length
Utilization
Reassignments
Communication count
Path replanning count

Export CSV.

PHASE 8 — Experiments

Implement:

Normal load
High load
Mass casualty
Doctor failure
ICU shortage
Lab failure

Generate actual charts.

PHASE 9 — Visualization

Implement the simplest reliable visualization.

Do not sacrifice system correctness for UI.

PHASE 10 — Final Audit

Perform:

Full test run.
End-to-end simulation.
Experiment run.
Documentation review.
Architecture review.
Rubric traceability review.
Demo verification.

Produce a final implementation report.

37. DEVELOPMENT RULE

After every phase:

Inspect existing code.
Implement only the requested phase.
Run tests.
Run a real simulation.
Inspect output.
Fix failures.
Update documentation.
Report what changed.
Report remaining limitations.

Do not proceed to the next phase if the current phase is broken.

38. DO NOT OVER-ENGINEER

Avoid:

Microservices
Kubernetes
Docker unless genuinely needed
Cloud deployment
Authentication
Databases
LLM APIs
Complex web applications
Unnecessary frontend frameworks

This is primarily an AI/Multi-Agent Systems simulation.

Focus engineering effort on:

Agents
Communication
Coordination
Planning
Search
Resource allocation
Dynamic adaptation
Experiments
39. DO NOT FAKE RESULTS

Never:

Invent experiment results.
Invent screenshots.
Invent performance numbers.
Claim tests passed without running them.
Claim an algorithm exists when only pseudocode exists.
Claim a rubric requirement is satisfied without evidence.

If something is incomplete, explicitly say:

NOT IMPLEMENTED

or:

PARTIALLY IMPLEMENTED
40. MEDICAL DISCLAIMER

The project is an educational simulation.

Include this disclaimer in the README and appropriate documentation:

This project is an educational Multi-Agent Systems simulation. It is not a clinical decision-support system and does not provide medical advice. Patient, triage, treatment, and resource-allocation behavior are simulated for academic purposes only.

Do not claim clinical validity.

41. FIRST ACTION

When Claude Code starts in this repository:

Read this entire CLAUDE.md.
Inspect the repository.
Inspect any existing documentation.
Do not immediately generate the whole project.
First present:
Architecture
Agent model
Data flow
Directory structure
Implementation phases
Major technical decisions
Then implement Phase 1 only.
Run tests.
Run a minimal simulation.
Fix all errors.
Report the results.

Do not proceed to Phase 2 until explicitly instructed.

42. FINAL SUCCESS CRITERIA

The project is considered complete only when it has:

Working multi-agent simulation
Multiple autonomous agent types
Explicit communication
Task allocation
Resource contention
Dynamic events
Dynamic replanning
BFS implementation
A* implementation
Knowledge representation
State-based patient workflow
Configurable experiments
Quantitative metrics
Visualization
Automated tests
Reproducible experiments
Complete documentation
Rubric traceability
Demonstrable end-to-end scenario

Most importantly:

The code, documentation, experiments, and presentation evidence must all describe the same system and must reflect what is actually implemented.