from smart_hospital.communication.message import Message, MessageType
from smart_hospital.model import HospitalModel


def test_doctor_accepts_request_within_capacity():
    model = HospitalModel()
    doctor = model.doctors[0]
    doctor.message_bus.send(Message(
        sender="PATIENT-0", receiver=doctor.agent_id, message_type=MessageType.DOCTOR_REQUEST,
        timestamp=0, priority=5, payload={"patient_id": "PATIENT-0", "severity": 5},
    ))
    doctor.step()
    assert doctor.workload == 1
    assert doctor.current_patient == "PATIENT-0"
    reply = model.message_bus.receive("PATIENT-0")
    assert reply[0].message_type is MessageType.DOCTOR_ASSIGNMENT


def test_doctor_rejects_when_full():
    model = HospitalModel()
    doctor = model.doctors[0]
    doctor.workload = doctor.maximum_workload
    doctor.message_bus.send(Message(
        sender="PATIENT-0", receiver=doctor.agent_id, message_type=MessageType.DOCTOR_REQUEST,
        timestamp=0, payload={"patient_id": "PATIENT-0", "severity": 5},
    ))
    doctor.step()
    reply = model.message_bus.receive("PATIENT-0")
    assert reply[0].message_type is MessageType.RESOURCE_UNAVAILABLE
