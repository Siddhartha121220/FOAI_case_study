"""DoctorAgent: heterogeneous specialization, workload-limited (CLAUDE.md #8)."""
from __future__ import annotations

from ..communication.message import MessageType
from .base_agent import BaseAgent


class DoctorAgent(BaseAgent):
    def __init__(self, model, agent_id, message_bus, specialization: str, maximum_workload: int = 2,
                 location: str = "DOCTOR_ROOM_1"):
        super().__init__(model, agent_id, message_bus)
        self.specialization = specialization
        self.maximum_workload = maximum_workload
        self.workload = 0
        self.current_patient: str | None = None
        self.home_location = location
        self.location = location
        self.target_location: str | None = None
        self.is_available = True

    @property
    def availability(self) -> bool:
        return self.is_available and self.workload < self.maximum_workload

    def fail(self) -> None:
        """CLAUDE.md #21: detect disruption -> communicate -> reassign."""
        self.is_available = False
        if self.current_patient is not None:
            self.send("COORDINATOR", MessageType.REASSIGNMENT_REQUEST, self.model.current_time,
                       priority=10, payload={"patient_id": self.current_patient})
            self.workload = max(0, self.workload - 1)
            self.current_patient = None
            self.target_location = self.home_location

    def recover(self) -> None:
        self.is_available = True

    def decide(self, messages) -> None:
        for msg in messages:
            if msg.message_type is MessageType.DOCTOR_REQUEST:
                self._handle_request(msg)
            elif msg.message_type is MessageType.TASK_COMPLETE:
                self.workload = max(0, self.workload - 1)
                self.current_patient = None
                self.target_location = self.home_location
        if self.target_location is not None:
            self.move_toward(self.target_location)

    def _handle_request(self, msg) -> None:
        patient_id = msg.payload["patient_id"]
        if not self.availability:
            self.send(patient_id, MessageType.RESOURCE_UNAVAILABLE, self.model.current_time,
                       payload={"resource": "doctor"})
            return
        self.workload += 1
        self.current_patient = patient_id
        self.target_location = msg.payload.get("patient_location", "EMERGENCY_ROOM")
        self.send(patient_id, MessageType.DOCTOR_ASSIGNMENT, self.model.current_time,
                   priority=msg.priority, payload={"doctor_id": self.agent_id})
