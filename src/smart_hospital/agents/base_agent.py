"""Common autonomous-agent abstraction (CLAUDE.md #5).

Every concrete agent has: local knowledge, a state, an inbox reachable only
via the MessageBus, and a step() that reads messages then decides. Agents
must not reach into another agent's attributes directly.
"""
from __future__ import annotations

from typing import Any

import mesa

from ..communication.message import Message
from ..communication.message_bus import MessageBus


class BaseAgent(mesa.Agent):
    def __init__(self, model: mesa.Model, agent_id: str, message_bus: MessageBus) -> None:
        super().__init__(model)
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.knowledge: dict[str, Any] = {}

    def send(self, receiver: str, message_type, timestamp: int, priority: int = 0, payload: dict | None = None) -> None:
        self.message_bus.send(
            Message(
                sender=self.agent_id,
                receiver=receiver,
                message_type=message_type,
                timestamp=timestamp,
                priority=priority,
                payload=payload or {},
            )
        )

    def receive_messages(self) -> list[Message]:
        return self.message_bus.receive(self.agent_id)

    def move_toward(self, target_location: str, algorithm: str = "astar") -> bool:
        """One hop per call toward target_location via the hospital map.
        Replanning is implicit: the path is recomputed fresh every call, so
        a newly blocked route is automatically routed around next step.
        Requires the subclass to maintain self.location. Returns True once
        arrived."""
        if self.location == target_location:
            return True
        path = self.model.hospital_map.plan_path(self.location, target_location, algorithm=algorithm)
        if not path or len(path) < 2:
            return False
        self.location = path[1]
        return self.location == target_location

    def decide(self, messages: list[Message]) -> None:
        """Override in subclasses: inspect messages/knowledge, act."""
        raise NotImplementedError

    def step(self) -> None:
        messages = self.receive_messages()
        self.decide(messages)
