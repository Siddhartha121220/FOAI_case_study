from smart_hospital.communication.message import Message, MessageType
from smart_hospital.model import HospitalModel
from smart_hospital.tasks.task import TaskStatus


def test_coordinator_forwards_doctor_request_and_tracks_task():
    model = HospitalModel()
    coordinator = model.coordinator
    coordinator.message_bus.send(Message(
        sender="PATIENT-0", receiver=coordinator.agent_id, message_type=MessageType.DOCTOR_REQUEST,
        timestamp=0, priority=5, payload={"patient_id": "PATIENT-0", "severity": 5, "symptoms": "pain"},
    ))
    coordinator.step()
    assert len(coordinator.tasks) == 1
    task = next(iter(coordinator.tasks.values()))
    assert task.status is TaskStatus.ASSIGNED
    assert task.assigned_agent == "DOCTOR-0"
    forwarded = model.message_bus.receive("DOCTOR-0")
    assert forwarded[0].message_type is MessageType.DOCTOR_REQUEST


def test_coordinator_reassigns_after_doctor_becomes_unavailable():
    model = HospitalModel()
    coordinator = model.coordinator
    coordinator.message_bus.send(Message(
        sender="COORDINATOR", receiver=coordinator.agent_id, message_type=MessageType.REASSIGNMENT_REQUEST,
        timestamp=0, priority=9, payload={"patient_id": "PATIENT-0"},
    ))
    coordinator.step()
    assert coordinator.doctor_of_patient["PATIENT-0"] == "DOCTOR-0"
    forwarded = model.message_bus.receive("DOCTOR-0")
    assert forwarded[0].message_type is MessageType.DOCTOR_REQUEST


def test_coordinator_chains_task_dependencies_across_requests():
    model = HospitalModel()
    coordinator = model.coordinator
    coordinator.message_bus.send(Message(
        sender="PATIENT-0", receiver=coordinator.agent_id, message_type=MessageType.DOCTOR_REQUEST,
        timestamp=0, priority=5, payload={"patient_id": "PATIENT-0", "symptoms": "fever"},
    ))
    coordinator.step()
    doctor_task = next(iter(coordinator.tasks.values()))

    coordinator.message_bus.send(Message(
        sender="PATIENT-0", receiver=coordinator.agent_id, message_type=MessageType.TEST_REQUEST,
        timestamp=1, priority=5, payload={"patient_id": "PATIENT-0", "test_name": "ECG"},
    ))
    coordinator.step()
    assert doctor_task.status is TaskStatus.COMPLETE
    test_task = next(t for t in coordinator.tasks.values() if t.required_agent_type == "TEST_REQUEST")
    assert test_task.dependencies == [doctor_task.task_id]
    assert test_task.status is TaskStatus.ASSIGNED


def test_coordinator_reports_unavailable_when_no_doctors_free():
    model = HospitalModel()
    for doctor in model.doctors:
        doctor.workload = doctor.maximum_workload
    coordinator = model.coordinator
    coordinator.message_bus.send(Message(
        sender="PATIENT-0", receiver=coordinator.agent_id, message_type=MessageType.DOCTOR_REQUEST,
        timestamp=0, priority=5, payload={"patient_id": "PATIENT-0"},
    ))
    coordinator.step()
    reply = model.message_bus.receive("PATIENT-0")
    assert reply[0].message_type is MessageType.RESOURCE_UNAVAILABLE
