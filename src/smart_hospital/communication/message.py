"""Explicit message format for inter-agent communication (CLAUDE.md #13)."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class MessageType(Enum):
    PATIENT_ARRIVAL = auto()
    TRIAGE_RESULT = auto()
    DOCTOR_REQUEST = auto()
    DOCTOR_ASSIGNMENT = auto()
    NURSE_REQUEST = auto()
    NURSE_ASSIGNMENT = auto()
    TEST_REQUEST = auto()
    TEST_RESULT = auto()
    BED_REQUEST = auto()
    BED_ALLOCATED = auto()
    BED_UNAVAILABLE = auto()
    RESOURCE_UNAVAILABLE = auto()
    EMERGENCY_ALERT = auto()
    TASK_COMPLETE = auto()
    REASSIGNMENT_REQUEST = auto()


_id_counter = itertools.count(1)


@dataclass
class Message:
    sender: str
    receiver: str
    message_type: MessageType
    timestamp: int
    priority: float = 0
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: f"MSG-{next(_id_counter):04d}")
