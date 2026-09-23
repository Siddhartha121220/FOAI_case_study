"""Phase 1 smoke test: the model must construct and step without error."""
from smart_hospital.config import SimulationConfig
from smart_hospital.model import HospitalModel


def test_model_steps_without_agents():
    model = HospitalModel(SimulationConfig(random_seed=42))
    for _ in range(10):
        model.step()
    assert model.current_time == 10


def test_hospital_map_is_connected():
    model = HospitalModel()
    assert model.hospital_map.is_reachable("ICU", "LABORATORY")


def test_end_to_end_mini_simulation_discharges_patients():
    from smart_hospital.agents.patient import PatientState

    model = HospitalModel(SimulationConfig(random_seed=1))
    model.spawn_patient(age=50, symptoms="chest pain", severity=9)
    model.spawn_patient(age=25, symptoms="fever", severity=3)
    model.spawn_patient(age=70, symptoms="fall", severity=6)

    for _ in range(40):
        model.step()

    discharged = [p for p in model.patients if p.current_state == PatientState.DISCHARGED]
    assert len(discharged) == 3
    assert len(model.message_bus.log) > 0
