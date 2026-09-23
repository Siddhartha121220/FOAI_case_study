from smart_hospital.communication.message import Message, MessageType
from smart_hospital.environment.events import (
    trigger_doctor_failure,
    trigger_doctor_recovery,
    trigger_icu_shortage,
    trigger_lab_failure,
    trigger_mass_casualty,
    trigger_sudden_critical_patient,
)
from smart_hospital.model import HospitalModel


def test_doctor_failure_triggers_reassignment_request():
    model = HospitalModel()
    doctor = model.doctors[0]
    doctor.current_patient = "PATIENT-0"
    doctor.workload = 1

    trigger_doctor_failure(model, doctor)

    assert not doctor.availability
    assert doctor.current_patient is None
    forwarded = model.message_bus.receive("COORDINATOR")
    assert forwarded[0].message_type is MessageType.REASSIGNMENT_REQUEST
    assert forwarded[0].payload["patient_id"] == "PATIENT-0"


def test_doctor_recovery_restores_availability():
    model = HospitalModel()
    doctor = model.doctors[0]
    trigger_doctor_failure(model, doctor)
    assert not doctor.availability
    trigger_doctor_recovery(doctor)
    assert doctor.availability


def test_coordinator_reassigns_to_a_different_doctor_after_failure():
    model = HospitalModel()
    failed_doctor = model.doctors[0]
    coordinator = model.coordinator

    coordinator.message_bus.send(Message(
        sender="PATIENT-0", receiver=coordinator.agent_id, message_type=MessageType.DOCTOR_REQUEST,
        timestamp=0, priority=9, payload={"patient_id": "PATIENT-0"},
    ))
    coordinator.step()
    assert coordinator.doctor_of_patient["PATIENT-0"] == failed_doctor.agent_id

    failed_doctor.current_patient = "PATIENT-0"
    trigger_doctor_failure(model, failed_doctor)
    coordinator.step()

    assert coordinator.reassignment_count == 1
    assert coordinator.doctor_of_patient["PATIENT-0"] != failed_doctor.agent_id
    reply = model.message_bus.receive(coordinator.doctor_of_patient["PATIENT-0"])
    assert reply[0].message_type is MessageType.DOCTOR_REQUEST


def test_lab_failure_reduces_capacity():
    model = HospitalModel()
    before = model.lab.max_capacity
    trigger_lab_failure(model, amount=1)
    assert model.lab.max_capacity == before - 1
    assert model.lab.available_capacity == before - 1


def test_icu_shortage_reduces_available_beds():
    model = HospitalModel()
    before = model.bed_manager.available_beds("ICU")
    trigger_icu_shortage(model, amount=1)
    assert model.bed_manager.available_beds("ICU") == before - 1


def test_sudden_critical_patient_is_added_to_model():
    model = HospitalModel()
    before = len(model.patients)
    patient = trigger_sudden_critical_patient(model)
    assert len(model.patients) == before + 1
    assert patient.severity == 10


def test_mass_casualty_spawns_multiple_critical_patients():
    model = HospitalModel()
    before = len(model.patients)
    spawned = trigger_mass_casualty(model, count=5)
    assert len(spawned) == 5
    assert len(model.patients) == before + 5
    assert all(p.severity == 10 for p in spawned)


def test_dynamic_event_scheduler_is_inert_by_default():
    model = HospitalModel()  # default event_probabilities are all 0.0
    for _ in range(20):
        model.step()
    assert all(d.is_available for d in model.doctors)
    assert model.lab.max_capacity == model.config.lab_capacity
