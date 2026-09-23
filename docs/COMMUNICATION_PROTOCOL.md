# Communication Protocol

## Message format (`communication/message.py`)

```python
Message(
    message_id: str,       # auto "MSG-0001", ...
    timestamp: int,
    sender: str,            # agent_id
    receiver: str,          # agent_id
    message_type: MessageType,
    priority: float,        # triage/cost-derived, see AI_ALGORITHMS.md
    payload: dict,
)
```

Matches CLAUDE.md #13's example shape exactly.

## Message types in active use

| Type | Sender -> Receiver | Purpose |
|---|---|---|
| `PATIENT_ARRIVAL` | Patient -> Coordinator | register priority |
| `DOCTOR_REQUEST` | Patient -> Coordinator -> Doctor | request/forward assignment |
| `DOCTOR_ASSIGNMENT` | Doctor -> Patient | accept |
| `TEST_REQUEST` | Patient -> Coordinator -> Lab | request/forward test |
| `TEST_RESULT` | Lab -> Patient | simulated result |
| `BED_REQUEST` | Patient -> Coordinator -> BedManager | request/forward bed |
| `BED_ALLOCATED` | BedManager -> Patient | bed assigned |
| `RESOURCE_UNAVAILABLE` | Doctor/Coordinator -> Patient | rejection |
| `TASK_COMPLETE` | Patient -> Doctor (at diagnosis) / Patient -> BedManager (at discharge) | releases capacity |
| `REASSIGNMENT_REQUEST` | Doctor -> Coordinator | self-reported disruption |
| `EMERGENCY_ALERT` | (handler exists, not yet triggered by any agent) | counted by coordinator |

`NURSE_REQUEST`/`NURSE_ASSIGNMENT` are implemented and tested on
`NurseAgent` but not yet sent by any active flow (`NurseAgent` isn't called
by `PatientAgent` — see `ASSUMPTIONS.md`).

## Routing rule: coordinator relabels `sender`

When the coordinator forwards a request, the outgoing message's `sender` is
`"COORDINATOR"`, not the original patient. Resource agents (`LabAgent`,
`BedManagerAgent`) therefore reply using `payload["patient_id"]`, never
`msg.sender` — this was a real bug found and fixed in Phase 3 (see
`ASSUMPTIONS.md`) when routing through the coordinator broke direct-reply
addressing that had worked when patients messaged resource agents directly.
`DoctorAgent` always used `payload["patient_id"]` and was unaffected.

## Delivery semantics (`communication/message_bus.py`)

`MessageBus` is a pure pull model: `send()` appends to the receiver's inbox
and to a global `log` (used for the communication-count metric and for
demonstrating message flow); `receive(agent_id)` pops and clears that
agent's entire inbox, sorted by `(-priority, timestamp)`. There is no
push/callback delivery and no message expiry — every message is eventually
read by exactly the agent it names, in priority order, on that agent's next
`step()`.

## Logging

Every message ever sent is retained in `MessageBus.log` for the life of a
run (used by `MetricsCollector.summary()["communication_messages"]` and
available for post-hoc inspection, e.g. `model.message_bus.log`). No
separate console message log exists — CLAUDE.md #32's example console log
lines are approximated by `visualization.dashboard.render_text`, which
summarizes state rather than echoing every message (kept simple per #26's
"do not flood the console").
