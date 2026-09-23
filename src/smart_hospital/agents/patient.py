"""PatientAgent: explicit state machine, no giant conditional (CLAUDE.md #7)."""
from __future__ import annotations

from enum import Enum, auto

from ..algorithms.triage import compute_priority
from ..communication.message import MessageType
from .base_agent import BaseAgent


class PatientState(Enum):
    ARRIVED = auto()
    TRIAGED = auto()
    WAITING = auto()
    DOCTOR_ASSIGNED = auto()
    TESTING = auto()
    DIAGNOSIS = auto()
    TREATMENT = auto()
    RECOVERY = auto()
    DISCHARGED = auto()
    CRITICAL = auto()


BED_TYPE_LOCATION = {"ICU": "ICU", "GENERAL": "GENERAL_WARD", "EMERGENCY": "EMERGENCY_ROOM"}


class PatientAgent(BaseAgent):
    def __init__(self, model, agent_id, message_bus, age: int, symptoms: str, severity: int, arrival_time: int):
        super().__init__(model, agent_id, message_bus)
        self.age = age
        self.symptoms = symptoms
        self.severity = severity
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.current_state = PatientState.ARRIVED
        self.assigned_doctor: str | None = None
        self.assigned_nurse: str | None = None
        self.required_tests: list[str] = ["ECG"] if severity >= 4 else []
        self.completed_tests: list[str] = []
        self.test_results: dict[str, float] = {}
        self.assigned_bed: str | None = None
        self.treatment_status = "NONE"
        self.location = "EMERGENCY_ROOM"
        self.priority = severity
        self._treatment_ticks_remaining = 0

        # Metrics (Phase 7): timestamps captured at state transitions.
        self.wait_until_doctor: int | None = None
        self.treatment_start_time: int | None = None
        self.treatment_duration: int | None = None
        self.discharge_time: int | None = None

        self._handlers = {
            PatientState.ARRIVED: self._handle_arrived,
            PatientState.TRIAGED: self._handle_triaged,
            PatientState.WAITING: self._handle_waiting,
            PatientState.DOCTOR_ASSIGNED: self._handle_doctor_assigned,
            PatientState.TESTING: self._handle_testing,
            PatientState.DIAGNOSIS: self._handle_diagnosis,
            PatientState.TREATMENT: self._handle_treatment,
            PatientState.RECOVERY: self._handle_recovery,
        }

    def decide(self, messages) -> None:
        self.waiting_time = self.model.current_time - self.arrival_time
        self.priority = compute_priority(self.severity, self.waiting_time, self.model.config.triage)
        for msg in messages:
            self._apply_message(msg)
        handler = self._handlers.get(self.current_state)
        if handler is not None:
            handler()

    def _apply_message(self, msg) -> None:
        if msg.message_type is MessageType.DOCTOR_ASSIGNMENT:
            self.assigned_doctor = msg.payload["doctor_id"]
            self.current_state = PatientState.DOCTOR_ASSIGNED
            if self.wait_until_doctor is None:
                self.wait_until_doctor = self.waiting_time
        elif msg.message_type is MessageType.TEST_RESULT:
            test_name = msg.payload["test_name"]
            self.completed_tests.append(test_name)
            self.test_results[test_name] = msg.payload["result"]
        elif msg.message_type is MessageType.BED_ALLOCATED:
            self.assigned_bed = msg.payload["bed_id"]
            bed_type = self.assigned_bed.split("-")[0]
            self.knowledge["bed_location"] = BED_TYPE_LOCATION.get(bed_type, "EMERGENCY_ROOM")
        elif msg.message_type is MessageType.RESOURCE_UNAVAILABLE and msg.payload.get("resource") == "doctor":
            self.knowledge["doctor_requested"] = False

    # -- state handlers -------------------------------------------------
    def _handle_arrived(self) -> None:
        self.send("COORDINATOR", MessageType.PATIENT_ARRIVAL, self.model.current_time,
                   priority=self.priority, payload={"patient_id": self.agent_id, "severity": self.severity})
        self.current_state = PatientState.TRIAGED

    def _handle_triaged(self) -> None:
        self.current_state = PatientState.WAITING

    def _handle_waiting(self) -> None:
        if self.knowledge.get("doctor_requested"):
            return
        self.send("COORDINATOR", MessageType.DOCTOR_REQUEST, self.model.current_time,
                   priority=self.priority, payload={"patient_id": self.agent_id, "severity": self.severity,
                                                     "symptoms": self.symptoms, "patient_location": self.location})
        self.knowledge["doctor_requested"] = True

    def _handle_doctor_assigned(self) -> None:
        if not self.required_tests:
            self.current_state = PatientState.DIAGNOSIS
            return
        pending = [t for t in self.required_tests if t not in self.completed_tests]
        if not pending:
            self.current_state = PatientState.DIAGNOSIS
            return
        self.send("COORDINATOR", MessageType.TEST_REQUEST, self.model.current_time,
                   priority=self.priority, payload={"patient_id": self.agent_id, "test_name": pending[0]})
        self.current_state = PatientState.TESTING

    def _handle_testing(self) -> None:
        pending = [t for t in self.required_tests if t not in self.completed_tests]
        if not pending:
            self.current_state = PatientState.DIAGNOSIS

    def _handle_diagnosis(self) -> None:
        if self.assigned_doctor is not None:
            # Consultation is done once diagnosis is reached; free the doctor
            # for the next patient rather than holding them through treatment.
            self.send(self.assigned_doctor, MessageType.TASK_COMPLETE, self.model.current_time,
                       payload={"patient_id": self.agent_id})
        bed_type = "ICU" if self.severity >= 9 else "GENERAL"
        self.send("COORDINATOR", MessageType.BED_REQUEST, self.model.current_time,
                   priority=self.priority, payload={"patient_id": self.agent_id, "bed_type": bed_type})
        self.current_state = PatientState.TREATMENT
        self._treatment_ticks_remaining = 3
        self.treatment_status = "IN_PROGRESS"
        self.treatment_start_time = self.model.current_time

    def _handle_treatment(self) -> None:
        if self.assigned_bed is None:
            return
        bed_location = self.knowledge.get("bed_location", self.location)
        if self.location != bed_location:
            self.move_toward(bed_location)
            return
        self._treatment_ticks_remaining -= 1
        if self._treatment_ticks_remaining <= 0:
            self.current_state = PatientState.RECOVERY
            self.treatment_status = "COMPLETE"
            self.treatment_duration = self.model.current_time - self.treatment_start_time

    def _handle_recovery(self) -> None:
        self.current_state = PatientState.DISCHARGED
        self.discharge_time = self.model.current_time
        self.send("BED-MANAGER", MessageType.TASK_COMPLETE, self.model.current_time,
                   payload={"patient_id": self.agent_id})
