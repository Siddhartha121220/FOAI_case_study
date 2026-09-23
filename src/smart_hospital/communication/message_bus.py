"""Central message routing service. Agents never call each other directly."""
from __future__ import annotations

from collections import defaultdict

from .message import Message


class MessageBus:
    def __init__(self) -> None:
        self._inboxes: dict[str, list[Message]] = defaultdict(list)
        self.log: list[Message] = []

    def send(self, message: Message) -> None:
        self._inboxes[message.receiver].append(message)
        self.log.append(message)

    def receive(self, agent_id: str) -> list[Message]:
        """Pop all pending messages for an agent, highest priority first."""
        messages = self._inboxes.pop(agent_id, [])
        messages.sort(key=lambda m: (-m.priority, m.timestamp))
        return messages
