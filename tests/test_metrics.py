from smart_hospital.config import SimulationConfig
from smart_hospital.model import HospitalModel


def test_metrics_summary_reflects_a_completed_run(tmp_path):
    model = HospitalModel(SimulationConfig(random_seed=2))
    model.spawn_patient(age=50, symptoms="chest pain", severity=9)
    model.spawn_patient(age=25, symptoms="fever", severity=3)

    for _ in range(30):
        model.step()

    summary = model.metrics.summary()
    assert summary["patients_served"] == 2
    assert summary["patients_remaining"] == 0
    assert summary["average_waiting_time"] >= 0
    assert summary["average_treatment_time"] > 0
    assert summary["communication_messages"] > 0
    assert summary["path_replans"] > 0
    assert 0.0 <= summary["doctor_utilization"] <= 1.0
    assert 0.0 <= summary["bed_utilization"] <= 1.0

    csv_path = tmp_path / "results.csv"
    model.metrics.export_csv(csv_path)
    assert csv_path.exists()
    contents = csv_path.read_text()
    assert "patients_served" in contents


def test_critical_patient_response_time_only_counts_critical_patients():
    model = HospitalModel(SimulationConfig(random_seed=4))
    model.spawn_patient(age=70, symptoms="fall", severity=9)
    model.spawn_patient(age=20, symptoms="fever", severity=2)
    for _ in range(30):
        model.step()

    critical_patient = model.patients[0]
    assert critical_patient.wait_until_doctor is not None
    summary = model.metrics.summary()
    assert summary["critical_patient_response_time"] == critical_patient.wait_until_doctor


def test_failed_resource_requests_counted_when_resources_exhausted():
    model = HospitalModel(SimulationConfig(random_seed=6))
    for doctor in model.doctors:
        doctor.workload = doctor.maximum_workload
    model.spawn_patient(age=40, symptoms="fever", severity=3)
    for _ in range(5):
        model.step()
    summary = model.metrics.summary()
    assert summary["failed_resource_requests"] >= 1
