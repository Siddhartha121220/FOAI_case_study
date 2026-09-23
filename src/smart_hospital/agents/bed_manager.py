"""BedManagerAgent: scarce-resource arbiter (CLAUDE.md #11, #17)."""
from __future__ import annotations

from ..communication.message import MessageType
from .base_agent import BaseAgent


class BedManagerAgent(BaseAgent):
    def __init__(self, model, agent_id, message_bus, bed_counts: dict[str, int]):
        super().__init__(model, agent_id, message_bus)
        self.bed_counts = dict(bed_counts)
        self.occupied: dict[str, str] = {}  # bed_id -> patient_id
        self.pending_requests: list[dict] = []
        self._next_bed_index = {bed_type: 0 for bed_type in bed_counts}

    def available_beds(self, bed_type: str) -> int:
        total = self.bed_counts.get(bed_type, 0)
        used = sum(1 for bed_id in self.occupied if bed_id.startswith(bed_type))
        return total - used

    def decide(self, messages) -> None:
        for msg in messages:
            if msg.message_type is MessageType.BED_REQUEST:
                self.pending_requests.append({
                    "patient_id": msg.payload["patient_id"],
                    "bed_type": msg.payload["bed_type"],
                    "priority": msg.priority,
                    "requester": msg.payload["patient_id"],
                })
            elif msg.message_type is MessageType.TASK_COMPLETE:
                self._release_bed(msg.payload.get("patient_id"))
        self._allocate_pending()

    def reduce_capacity(self, bed_type: str, amount: int = 1) -> None:
        """An ICU bed goes offline/is otherwise unavailable (CLAUDE.md #21)."""
        self.bed_counts[bed_type] = max(0, self.bed_counts.get(bed_type, 0) - amount)

    def restore_capacity(self, bed_type: str, amount: int = 1) -> None:
        self.bed_counts[bed_type] = self.bed_counts.get(bed_type, 0) + amount

    def _release_bed(self, patient_id: str | None) -> None:
        for bed_id, occupant in list(self.occupied.items()):
            if occupant == patient_id:
                del self.occupied[bed_id]

    def _allocate_pending(self) -> None:
        self.pending_requests.sort(key=lambda r: -r["priority"])
        still_pending = []
        for req in self.pending_requests:
            if self.available_beds(req["bed_type"]) <= 0:
                still_pending.append(req)
                continue
            bed_id = f"{req['bed_type']}-{self._next_bed_index[req['bed_type']]:02d}"
            self._next_bed_index[req["bed_type"]] += 1
            self.occupied[bed_id] = req["patient_id"]
            self.send(req["requester"], MessageType.BED_ALLOCATED, self.model.current_time,
                       priority=req["priority"], payload={"patient_id": req["patient_id"], "bed_id": bed_id})
        self.pending_requests = still_pending
