"""Top-level Mesa model wiring agents together via the MessageBus."""
from __future__ import annotations

import mesa

from .agents.bed_manager import BedManagerAgent
from .agents.coordinator import HospitalCoordinatorAgent
from .agents.doctor import DoctorAgent
from .agents.lab import LabAgent
from .agents.nurse import NurseAgent
from .agents.patient import PatientAgent
from .algorithms.task_allocation import select_best_doctor
from .communication.message_bus import MessageBus
from .config import SimulationConfig
from .environment.events import DynamicEventScheduler
from .environment.hospital_map import HospitalMap
from .metrics.collector import MetricsCollector

SPECIALIZATIONS = ["General Medicine", "Cardiology", "Trauma", "Neurology"]


class HospitalModel(mesa.Model):
    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        super().__init__(rng=self.config.random_seed)
        self.message_bus = MessageBus()
        self.hospital_map = HospitalMap()
        self.current_time = 0
        self._next_patient_index = 0

        self.doctors: list[DoctorAgent] = []
        self.nurses: list[NurseAgent] = []
        self.patients: list[PatientAgent] = []
        self._setup_agents()

    def _setup_agents(self) -> None:
        for i in range(self.config.num_doctors):
            doctor = DoctorAgent(
                self, f"DOCTOR-{i}", self.message_bus,
                specialization=SPECIALIZATIONS[i % len(SPECIALIZATIONS)],
            )
            self.doctors.append(doctor)

        for i in range(self.config.num_nurses):
            nurse = NurseAgent(self, f"NURSE-{i}", self.message_bus)
            self.nurses.append(nurse)

        self.lab = LabAgent(self, "LAB-1", self.message_bus, capacity=self.config.lab_capacity)

        self.bed_manager = BedManagerAgent(
            self, "BED-MANAGER", self.message_bus,
            bed_counts={
                "ICU": self.config.num_icu_beds,
                "EMERGENCY": self.config.num_emergency_beds,
                "GENERAL": self.config.num_general_beds,
            },
        )

        self.coordinator = HospitalCoordinatorAgent(self, "COORDINATOR", self.message_bus)
        self.event_scheduler = DynamicEventScheduler(self.config)
        self.metrics = MetricsCollector(self)

    def find_available_doctor(self, symptoms: str, target_location: str = "EMERGENCY_ROOM") -> str | None:
        """Read-only environment-service lookup; not a write into doctor state."""
        doctor = select_best_doctor(self.doctors, symptoms, target_location, self.hospital_map, self.config.allocation)
        return doctor.agent_id if doctor else None

    def spawn_patient(self, age: int, symptoms: str, severity: int) -> PatientAgent:
        patient = PatientAgent(
            self, f"PATIENT-{self._next_patient_index}", self.message_bus,
            age=age, symptoms=symptoms, severity=severity, arrival_time=self.current_time,
        )
        self._next_patient_index += 1
        self.patients.append(patient)
        return patient

    def step(self) -> None:
        self.current_time += 1
        self.event_scheduler.maybe_trigger(self)
        self.agents.shuffle_do("step")
        self.metrics.record_step()
