"""LabAgent: autonomous test-processing resource (CLAUDE.md #10).

Test results are simulated values only; no clinical validity implied.
"""
from __future__ import annotations

from ..communication.message import MessageType
from .base_agent import BaseAgent

DEFAULT_PROCESSING_TIMES = {"Blood Test": 2, "ECG": 1, "X-Ray": 2, "CT Scan": 3}


class LabAgent(BaseAgent):
    def __init__(self, model, agent_id, message_bus, capacity: int = 2,
                 processing_times: dict[str, int] | None = None):
        super().__init__(model, agent_id, message_bus)
        self.available_capacity = capacity
        self.max_capacity = capacity
        self.processing_times = processing_times or DEFAULT_PROCESSING_TIMES
        self.test_queue: list[dict] = []
        self.active_tests: list[dict] = []
        self.completed_tests: list[dict] = []

    def decide(self, messages) -> None:
        for msg in messages:
            if msg.message_type is MessageType.TEST_REQUEST:
                self.test_queue.append({
                    "patient_id": msg.payload["patient_id"],
                    "test_name": msg.payload["test_name"],
                    "priority": msg.priority,
                    "requester": msg.payload["patient_id"],
                })
        self._start_queued_tests()
        self._advance_active_tests()

    def fail(self, amount: int = 1) -> None:
        """A machine goes down: capacity drops until recover() is called."""
        self.max_capacity = max(0, self.max_capacity - amount)
        self.available_capacity = max(0, self.available_capacity - amount)

    def recover(self, amount: int = 1) -> None:
        self.max_capacity += amount
        self.available_capacity += amount

    def _start_queued_tests(self) -> None:
        self.test_queue.sort(key=lambda t: -t["priority"])
        while self.available_capacity > 0 and self.test_queue:
            test = self.test_queue.pop(0)
            test["remaining"] = self.processing_times.get(test["test_name"], 1)
            self.active_tests.append(test)
            self.available_capacity -= 1

    def _advance_active_tests(self) -> None:
        still_active = []
        for test in self.active_tests:
            test["remaining"] -= 1
            if test["remaining"] <= 0:
                result = self.model.random.uniform(0, 100)
                self.completed_tests.append(test)
                self.available_capacity += 1
                self.send(test["requester"], MessageType.TEST_RESULT, self.model.current_time,
                           priority=test["priority"],
                           payload={"patient_id": test["patient_id"], "test_name": test["test_name"], "result": result})
            else:
                still_active.append(test)
        self.active_tests = still_active
