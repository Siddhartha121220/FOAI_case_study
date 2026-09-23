"""HospitalCoordinatorAgent: routes requests, tracks tasks, handles
reassignment/emergencies (CLAUDE.md #12). Delegates the actual resource
picking to the model's read-only lookups — it does not become a monolith
that reimplements doctor/lab/bed logic itself.
"""
from __future__ import annotations

from ..communication.message import MessageType
from ..tasks.task import Task, TaskStatus
from .base_agent import BaseAgent


class HospitalCoordinatorAgent(BaseAgent):
    def __init__(self, model, agent_id, message_bus):
        super().__init__(model, agent_id, message_bus)
        self.tasks: dict[str, Task] = {}
        self.patient_priority: dict[str, int] = {}
        self.doctor_of_patient: dict[str, str] = {}
        self.emergency_count = 0
        self.reassignment_count = 0
        self._last_task_for_patient: dict[str, str] = {}

    def decide(self, messages) -> None:
        for msg in messages:
            if msg.message_type is MessageType.PATIENT_ARRIVAL:
                self.patient_priority[msg.payload["patient_id"]] = msg.payload.get("severity", 0)
            elif msg.message_type is MessageType.DOCTOR_REQUEST:
                self._forward_doctor_request(msg)
            elif msg.message_type is MessageType.TEST_REQUEST:
                self._forward(msg, self.model.lab.agent_id)
            elif msg.message_type is MessageType.BED_REQUEST:
                self._forward(msg, self.model.bed_manager.agent_id)
            elif msg.message_type is MessageType.REASSIGNMENT_REQUEST:
                self._reassign_doctor(msg)
            elif msg.message_type is MessageType.EMERGENCY_ALERT:
                self.emergency_count += 1

    def _completed_task_ids(self) -> set[str]:
        return {task_id for task_id, task in self.tasks.items() if task.status is TaskStatus.COMPLETE}

    def _new_task(self, patient_id: str, required_agent_type: str, priority: int) -> Task:
        """Chain onto the patient's previous task. A later-stage request
        arriving proves the previous stage finished, so it's marked COMPLETE
        here rather than tracked via a reply the coordinator never sees
        (see docs/ASSUMPTIONS.md, Phase 3)."""
        previous_task_id = self._last_task_for_patient.get(patient_id)
        if previous_task_id is not None:
            self.tasks[previous_task_id].status = TaskStatus.COMPLETE
        dependencies = [previous_task_id] if previous_task_id else []
        task = Task(patient_id=patient_id, required_agent_type=required_agent_type, priority=priority,
                    dependencies=dependencies)
        self.tasks[task.task_id] = task
        self._last_task_for_patient[patient_id] = task.task_id
        return task

    def _ready_to_forward(self, task: Task) -> bool:
        return task.is_ready(self._completed_task_ids())

    def _forward_doctor_request(self, msg) -> None:
        patient_id = msg.payload["patient_id"]
        task = self._new_task(patient_id, "DOCTOR", msg.priority)
        if not self._ready_to_forward(task):
            task.status = TaskStatus.PENDING
            return
        doctor_id = self.model.find_available_doctor(msg.payload.get("symptoms", ""))
        if doctor_id is None:
            task.status = TaskStatus.FAILED
            self.send(patient_id, MessageType.RESOURCE_UNAVAILABLE, self.model.current_time,
                       priority=msg.priority, payload={"resource": "doctor"})
            return
        task.assigned_agent = doctor_id
        task.status = TaskStatus.ASSIGNED
        self.doctor_of_patient[patient_id] = doctor_id
        self.send(doctor_id, MessageType.DOCTOR_REQUEST, self.model.current_time,
                   priority=msg.priority, payload=msg.payload)

    def _forward(self, msg, target_agent_id: str) -> None:
        task = self._new_task(msg.payload["patient_id"], msg.message_type.name, msg.priority)
        if not self._ready_to_forward(task):
            task.status = TaskStatus.PENDING
            return
        task.assigned_agent = target_agent_id
        task.status = TaskStatus.ASSIGNED
        self.send(target_agent_id, msg.message_type, self.model.current_time,
                   priority=msg.priority, payload=msg.payload)

    def _reassign_doctor(self, msg) -> None:
        patient_id = msg.payload["patient_id"]
        self.reassignment_count += 1
        doctor_id = self.model.find_available_doctor(msg.payload.get("symptoms", ""))
        if doctor_id is None:
            self.send(patient_id, MessageType.RESOURCE_UNAVAILABLE, self.model.current_time,
                       priority=msg.priority, payload={"resource": "doctor"})
            return
        self.doctor_of_patient[patient_id] = doctor_id
        self.send(doctor_id, MessageType.DOCTOR_REQUEST, self.model.current_time,
                   priority=msg.priority, payload={"patient_id": patient_id})
