from smart_hospital.communication.message import Message, MessageType
from smart_hospital.communication.message_bus import MessageBus


def test_message_delivery():
    bus = MessageBus()
    bus.send(Message(sender="A", receiver="B", message_type=MessageType.TASK_COMPLETE, timestamp=1))
    inbox = bus.receive("B")
    assert len(inbox) == 1
    assert inbox[0].sender == "A"


def test_priority_ordering():
    bus = MessageBus()
    bus.send(Message(sender="A", receiver="B", message_type=MessageType.TASK_COMPLETE, timestamp=1, priority=1))
    bus.send(Message(sender="C", receiver="B", message_type=MessageType.EMERGENCY_ALERT, timestamp=2, priority=9))
    inbox = bus.receive("B")
    assert inbox[0].sender == "C"


def test_empty_inbox_returns_empty_list():
    bus = MessageBus()
    assert bus.receive("NOBODY") == []
