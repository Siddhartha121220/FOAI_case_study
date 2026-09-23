from smart_hospital.algorithms.task_allocation import select_best_doctor, specialization_for_symptoms
from smart_hospital.config import AllocationWeights
from smart_hospital.model import HospitalModel
from smart_hospital.tasks.task import Task, TaskStatus


def test_specialization_match_wins_over_lower_workload():
    model = HospitalModel()
    cardiologist = next(d for d in model.doctors if d.specialization == "Cardiology")
    generalist = next(d for d in model.doctors if d.specialization == "General Medicine")
    generalist.workload = 0
    cardiologist.workload = 1
    weights = AllocationWeights(workload_weight=1, distance_weight=0, mismatch_penalty=5)
    best = select_best_doctor(model.doctors, "chest pain", "EMERGENCY_ROOM", model.hospital_map, weights)
    assert best is cardiologist


def test_select_best_doctor_returns_none_when_all_full():
    model = HospitalModel()
    for d in model.doctors:
        d.workload = d.maximum_workload
    best = select_best_doctor(model.doctors, "fever", "EMERGENCY_ROOM", model.hospital_map, model.config.allocation)
    assert best is None


def test_specialization_lookup_defaults_to_general_medicine():
    assert specialization_for_symptoms("unknown symptom") == "General Medicine"
    assert specialization_for_symptoms("chest pain") == "Cardiology"


def test_task_dependency_readiness():
    upstream = Task(patient_id="P1", required_agent_type="DOCTOR")
    downstream = Task(patient_id="P1", required_agent_type="LAB", dependencies=[upstream.task_id])
    assert not downstream.is_ready(completed_task_ids=set())
    upstream.status = TaskStatus.COMPLETE
    assert downstream.is_ready(completed_task_ids={upstream.task_id})
