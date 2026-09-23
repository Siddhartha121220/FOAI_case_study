from smart_hospital.communication.message import Message, MessageType
from smart_hospital.model import HospitalModel


def test_nurse_accepts_and_releases():
    model = HospitalModel()
    nurse = model.nurses[0]
    nurse.message_bus.send(Message(
        sender="PATIENT-0", receiver=nurse.agent_id, message_type=MessageType.NURSE_REQUEST,
        timestamp=0, payload={"patient_id": "PATIENT-0"},
    ))
    nurse.step()
    assert nurse.workload == 1
    assert "PATIENT-0" in nurse.current_assignments

    nurse.message_bus.send(Message(
        sender="COORDINATOR", receiver=nurse.agent_id, message_type=MessageType.TASK_COMPLETE,
        timestamp=1, payload={"patient_id": "PATIENT-0"},
    ))
    nurse.step()
    assert nurse.workload == 0
    assert "PATIENT-0" not in nurse.current_assignments


def test_nurse_rejects_when_full():
    model = HospitalModel()
    nurse = model.nurses[0]
    nurse.workload = nurse.maximum_workload
    nurse.message_bus.send(Message(
        sender="PATIENT-0", receiver=nurse.agent_id, message_type=MessageType.NURSE_REQUEST,
        timestamp=0, payload={"patient_id": "PATIENT-0"},
    ))
    nurse.step()
    reply = model.message_bus.receive("PATIENT-0")
    assert reply[0].message_type is MessageType.RESOURCE_UNAVAILABLE
