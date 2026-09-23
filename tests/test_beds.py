from smart_hospital.communication.message import Message, MessageType
from smart_hospital.model import HospitalModel


def test_bed_allocated_when_available():
    model = HospitalModel()
    bm = model.bed_manager
    bm.message_bus.send(Message(
        sender="PATIENT-0", receiver=bm.agent_id, message_type=MessageType.BED_REQUEST,
        timestamp=0, priority=9, payload={"patient_id": "PATIENT-0", "bed_type": "ICU"},
    ))
    bm.step()
    reply = model.message_bus.receive("PATIENT-0")
    assert reply[0].message_type is MessageType.BED_ALLOCATED
    assert bm.available_beds("ICU") == model.config.num_icu_beds - 1


def test_icu_contention_keeps_lowest_priority_pending():
    model = HospitalModel()
    bm = model.bed_manager
    assert model.config.num_icu_beds == 2
    for i, priority in enumerate([9, 8, 7]):
        bm.message_bus.send(Message(
            sender=f"PATIENT-{i}", receiver=bm.agent_id, message_type=MessageType.BED_REQUEST,
            timestamp=0, priority=priority, payload={"patient_id": f"PATIENT-{i}", "bed_type": "ICU"},
        ))
    bm.step()
    assert model.message_bus.receive("PATIENT-0")[0].message_type is MessageType.BED_ALLOCATED
    assert model.message_bus.receive("PATIENT-1")[0].message_type is MessageType.BED_ALLOCATED
    assert model.message_bus.receive("PATIENT-2") == []
    assert len(bm.pending_requests) == 1
    assert bm.pending_requests[0]["patient_id"] == "PATIENT-2"


def test_bed_release_frees_capacity_for_pending():
    model = HospitalModel()
    bm = model.bed_manager
    for i, priority in enumerate([9, 8, 7]):
        bm.message_bus.send(Message(
            sender=f"PATIENT-{i}", receiver=bm.agent_id, message_type=MessageType.BED_REQUEST,
            timestamp=0, priority=priority, payload={"patient_id": f"PATIENT-{i}", "bed_type": "ICU"},
        ))
    bm.step()  # P0, P1 allocated, P2 pending
    bm.message_bus.send(Message(
        sender="COORDINATOR", receiver=bm.agent_id, message_type=MessageType.TASK_COMPLETE,
        timestamp=1, payload={"patient_id": "PATIENT-0"},
    ))
    bm.step()
    reply = model.message_bus.receive("PATIENT-2")
    assert reply[0].message_type is MessageType.BED_ALLOCATED
