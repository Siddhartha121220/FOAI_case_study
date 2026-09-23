"""Quantitative metrics collection and CSV export (CLAUDE.md #24)."""
from __future__ import annotations

import statistics

import pandas as pd

from ..agents.patient import PatientState
from ..communication.message import MessageType


class MetricsCollector:
    def __init__(self, model) -> None:
        self.model = model
        self.queue_lengths: list[int] = []
        self.doctor_utilizations: list[float] = []
        self.nurse_utilizations: list[float] = []
        self.lab_utilizations: list[float] = []
        self.bed_utilizations: list[float] = []

    def record_step(self) -> None:
        m = self.model
        self.queue_lengths.append(sum(1 for p in m.patients if p.current_state is PatientState.WAITING))
        self.doctor_utilizations.append(self._workload_utilization(m.doctors))
        self.nurse_utilizations.append(self._workload_utilization(m.nurses))
        self.lab_utilizations.append(self._capacity_utilization(m.lab.max_capacity, m.lab.available_capacity))
        total_beds = sum(m.bed_manager.bed_counts.values())
        used_beds = len(m.bed_manager.occupied)
        self.bed_utilizations.append(used_beds / total_beds if total_beds else 0.0)

    @staticmethod
    def _workload_utilization(agents) -> float:
        total_capacity = sum(a.maximum_workload for a in agents)
        used = sum(a.workload for a in agents)
        return used / total_capacity if total_capacity else 0.0

    @staticmethod
    def _capacity_utilization(max_capacity: int, available: int) -> float:
        return (max_capacity - available) / max_capacity if max_capacity else 0.0

    def summary(self) -> dict:
        m = self.model
        waiting_times = [p.wait_until_doctor for p in m.patients if p.wait_until_doctor is not None]
        treatment_times = [p.treatment_duration for p in m.patients if p.treatment_duration is not None]
        critical_response = [p.wait_until_doctor for p in m.patients
                              if p.severity >= 9 and p.wait_until_doctor is not None]
        served = sum(1 for p in m.patients if p.current_state is PatientState.DISCHARGED)
        failed_requests = sum(1 for msg in m.message_bus.log if msg.message_type is MessageType.RESOURCE_UNAVAILABLE)

        return {
            "average_waiting_time": statistics.mean(waiting_times) if waiting_times else 0.0,
            "median_waiting_time": statistics.median(waiting_times) if waiting_times else 0.0,
            "maximum_waiting_time": max(waiting_times) if waiting_times else 0.0,
            "critical_patient_response_time": statistics.mean(critical_response) if critical_response else 0.0,
            "average_treatment_time": statistics.mean(treatment_times) if treatment_times else 0.0,
            "patients_served": served,
            "patients_remaining": len(m.patients) - served,
            "average_queue_length": statistics.mean(self.queue_lengths) if self.queue_lengths else 0.0,
            "maximum_queue_length": max(self.queue_lengths) if self.queue_lengths else 0,
            "doctor_utilization": statistics.mean(self.doctor_utilizations) if self.doctor_utilizations else 0.0,
            "nurse_utilization": statistics.mean(self.nurse_utilizations) if self.nurse_utilizations else 0.0,
            "lab_utilization": statistics.mean(self.lab_utilizations) if self.lab_utilizations else 0.0,
            "bed_utilization": statistics.mean(self.bed_utilizations) if self.bed_utilizations else 0.0,
            "reassigned_tasks": m.coordinator.reassignment_count,
            "failed_resource_requests": failed_requests,
            "communication_messages": len(m.message_bus.log),
            "path_replans": m.hospital_map.plan_count,
        }

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([self.summary()])

    def export_csv(self, path: str) -> None:
        self.to_dataframe().to_csv(path, index=False)
