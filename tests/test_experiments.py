import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

from run_experiments import run_experiment  # noqa: E402
from smart_hospital.config import SimulationConfig  # noqa: E402


def test_run_experiment_returns_full_summary():
    config = SimulationConfig(arrival_rate_per_minute=2, random_seed=1)
    summary = run_experiment("smoke_test", config, duration=15)
    assert summary["experiment"] == "smoke_test"
    assert "average_waiting_time" in summary
    assert "path_replans" in summary


def test_doctors_release_capacity_after_diagnosis_under_sustained_load():
    """Regression test for the Phase 8 resource-leak bug: without
    TASK_COMPLETE on diagnosis, doctor workload only ever grows."""
    config = SimulationConfig(arrival_rate_per_minute=3, random_seed=1)
    summary = run_experiment("leak_check", config, duration=40)
    assert summary["patients_served"] > 10
