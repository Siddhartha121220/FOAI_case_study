from smart_hospital.communication.message import Message, MessageType
from smart_hospital.model import HospitalModel


def test_lab_processes_test_and_returns_result():
    model = HospitalModel()
    lab = model.lab
    lab.message_bus.send(Message(
        sender="PATIENT-0", receiver=lab.agent_id, message_type=MessageType.TEST_REQUEST,
        timestamp=0, priority=5, payload={"patient_id": "PATIENT-0", "test_name": "ECG"},
    ))
    lab.step()  # queued -> active (ECG takes 1 tick)
    lab.step()  # active -> complete
    reply = model.message_bus.receive("PATIENT-0")
    assert reply[0].message_type is MessageType.TEST_RESULT
    assert 0 <= reply[0].payload["result"] <= 100


def test_lab_respects_capacity():
    model = HospitalModel()
    lab = model.lab
    lab.available_capacity = 0
    lab.message_bus.send(Message(
        sender="PATIENT-0", receiver=lab.agent_id, message_type=MessageType.TEST_REQUEST,
        timestamp=0, payload={"patient_id": "PATIENT-0", "test_name": "CT Scan"},
    ))
    lab.step()
    assert len(lab.test_queue) == 1
    assert len(lab.active_tests) == 0
