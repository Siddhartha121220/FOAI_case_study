"""Reproducible experiments A-F (CLAUDE.md #25). Real runs, real numbers,
no fabricated results.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from smart_hospital.config import SimulationConfig  # noqa: E402
from smart_hospital.environment.events import (  # noqa: E402
    trigger_doctor_failure,
    trigger_lab_failure,
    trigger_mass_casualty,
)
from smart_hospital.model import HospitalModel  # noqa: E402

SYMPTOMS_POOL = ["chest pain", "fever", "fall", "headache", "abdominal pain"]
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _spawn_arrivals(model: HospitalModel, rate_per_minute: float, rng: np.random.Generator) -> None:
    """Poisson-distributed arrivals per simulated minute (numpy, not hand-rolled)."""
    count = rng.poisson(rate_per_minute)
    for _ in range(count):
        severity = int(np.clip(rng.normal(5, 2.5), 1, 10))
        symptoms = SYMPTOMS_POOL[rng.integers(len(SYMPTOMS_POOL))]
        age = int(rng.integers(5, 90))
        model.spawn_patient(age=age, symptoms=symptoms, severity=severity)


def run_experiment(name: str, config: SimulationConfig, duration: int, disruption: dict | None = None) -> dict:
    model = HospitalModel(config)
    rng = np.random.default_rng(config.random_seed)
    for t in range(1, duration + 1):
        _spawn_arrivals(model, config.arrival_rate_per_minute, rng)
        if disruption and disruption["tick"] == t:
            disruption["fn"](model)
        model.step()
    summary = model.metrics.summary()
    summary["experiment"] = name
    return summary


EXPERIMENTS = {
    "A_normal_load": dict(
        config=SimulationConfig(arrival_rate_per_minute=2, random_seed=42), duration=120,
    ),
    "B_high_load": dict(
        config=SimulationConfig(arrival_rate_per_minute=5, random_seed=42), duration=120,
    ),
    "C_mass_casualty": dict(
        config=SimulationConfig(arrival_rate_per_minute=2, random_seed=42), duration=60,
        disruption={"tick": 20, "fn": lambda m: trigger_mass_casualty(m, count=15)},
    ),
    "D_doctor_failure": dict(
        config=SimulationConfig(arrival_rate_per_minute=2, random_seed=42), duration=120,
        disruption={"tick": 30, "fn": lambda m: trigger_doctor_failure(m, m.doctors[0])},
    ),
    "E_icu_shortage": dict(
        config=SimulationConfig(arrival_rate_per_minute=2, num_icu_beds=1, random_seed=42), duration=120,
    ),
    "F_lab_failure": dict(
        config=SimulationConfig(arrival_rate_per_minute=2, random_seed=42), duration=120,
        disruption={"tick": 30, "fn": lambda m: trigger_lab_failure(m, amount=1)},
    ),
}


def generate_charts(df: pd.DataFrame, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for metric in ["average_waiting_time", "doctor_utilization", "reassigned_tasks", "failed_resource_requests"]:
        fig, ax = plt.subplots()
        ax.bar(df["experiment"], df[metric])
        ax.set_title(metric.replace("_", " ").title())
        ax.set_ylabel(metric)
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout()
        fig.savefig(out_dir / f"{metric}.png")
        plt.close(fig)


def main() -> pd.DataFrame:
    RESULTS_DIR.mkdir(exist_ok=True)
    results = [run_experiment(name, spec["config"], spec["duration"], spec.get("disruption"))
               for name, spec in EXPERIMENTS.items()]
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_DIR / "experiment_results.csv", index=False)
    generate_charts(df, RESULTS_DIR)
    return df


if __name__ == "__main__":
    df = main()
    print(df.to_string(index=False))
