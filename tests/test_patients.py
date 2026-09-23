from smart_hospital.agents.patient import PatientState
from smart_hospital.model import HospitalModel


def test_patient_starts_arrived_and_progresses():
    model = HospitalModel()
    patient = model.spawn_patient(age=40, symptoms="chest pain", severity=8)
    assert patient.current_state == PatientState.ARRIVED
    model.step()
    assert patient.current_state != PatientState.ARRIVED


def test_patient_reaches_discharged_eventually():
    model = HospitalModel()
    patient = model.spawn_patient(age=30, symptoms="fever", severity=2)
    for _ in range(30):
        model.step()
        if patient.current_state == PatientState.DISCHARGED:
            break
    assert patient.current_state == PatientState.DISCHARGED
    assert patient.assigned_doctor is not None
    assert patient.assigned_bed is not None
