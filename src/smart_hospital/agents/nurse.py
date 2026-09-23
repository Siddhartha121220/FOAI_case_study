"""NurseAgent (CLAUDE.md #9). Not yet wired into the patient flow — Phase 3."""
from __future__ import annotations

from ..communication.message import MessageType
from .base_agent import BaseAgent


class NurseAgent(BaseAgent):
    def __init__(self, model, agent_id, message_bus, maximum_workload: int = 3, location: str = "NURSE_STATION"):
        super().__init__(model, agent_id, message_bus)
        self.maximum_workload = maximum_workload
        self.workload = 0
        self.current_assignments: list[str] = []
        self.location = location
        self.is_available = True

    @property
    def availability(self) -> bool:
        return self.is_available and self.workload < self.maximum_workload

    def fail(self) -> None:
        self.is_available = False

    def recover(self) -> None:
        self.is_available = True

    def decide(self, messages) -> None:
        for msg in messages:
            if msg.message_type is MessageType.NURSE_REQUEST:
                self._handle_request(msg)
            elif msg.message_type is MessageType.TASK_COMPLETE:
                patient_id = msg.payload.get("patient_id")
                if patient_id in self.current_assignments:
                    self.current_assignments.remove(patient_id)
                    self.workload = max(0, self.workload - 1)

    def _handle_request(self, msg) -> None:
        patient_id = msg.payload["patient_id"]
        if not self.availability:
            self.send(patient_id, MessageType.RESOURCE_UNAVAILABLE, self.model.current_time,
                       payload={"resource": "nurse"})
            return
        self.workload += 1
        self.current_assignments.append(patient_id)
        self.send(patient_id, MessageType.NURSE_ASSIGNMENT, self.model.current_time,
                   priority=msg.priority, payload={"nurse_id": self.agent_id})
