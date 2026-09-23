"""Hospital layout graph with grid positions for A* (CLAUDE.md #15)."""
from __future__ import annotations

import networkx as nx

from ..algorithms.astar import astar_path
from ..algorithms.bfs import bfs_path

# (x, y) grid position per location, used only as the A* heuristic input.
DEFAULT_POSITIONS = {
    "EMERGENCY_ROOM": (0, 0),
    "DOCTOR_ROOM_1": (1, 1),
    "DOCTOR_ROOM_2": (1, -1),
    "NURSE_STATION": (-1, 1),
    "LABORATORY": (-1, -1),
    "PHARMACY": (2, 0),
    "GENERAL_WARD": (0, 2),
    "ICU": (0, -2),
}

# Extra edges beyond the emergency-room hub, so a single blocked route still
# leaves an alternate path to demonstrate replanning.
EXTRA_ROUTES = [
    ("DOCTOR_ROOM_1", "DOCTOR_ROOM_2"),
    ("LABORATORY", "NURSE_STATION"),
    ("ICU", "GENERAL_WARD"),
    ("PHARMACY", "DOCTOR_ROOM_1"),
]


class HospitalMap:
    """Graph representation of hospital locations and connecting routes."""

    def __init__(self, positions: dict[str, tuple[int, int]] | None = None) -> None:
        self.positions = dict(positions or DEFAULT_POSITIONS)
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.positions)
        hub = "EMERGENCY_ROOM"
        for loc in self.positions:
            if loc != hub:
                self.graph.add_edge(hub, loc, weight=1)
        for a, b in EXTRA_ROUTES:
            self.graph.add_edge(a, b, weight=1)
        self.blocked_locations: set[str] = set()
        self.plan_count = 0

    def block_route(self, a: str, b: str) -> None:
        if self.graph.has_edge(a, b):
            self.graph.remove_edge(a, b)

    def block_location(self, location: str) -> None:
        self.blocked_locations.add(location)

    def unblock_location(self, location: str) -> None:
        self.blocked_locations.discard(location)

    def is_reachable(self, a: str, b: str) -> bool:
        return nx.has_path(self.graph, a, b)

    def plan_path(self, start: str, goal: str, algorithm: str = "astar") -> list[str] | None:
        """Recomputed on every call, so a changed graph is automatically
        replanned around on the next request — no separate replan API."""
        self.plan_count += 1
        if algorithm == "bfs":
            return bfs_path(self.graph, start, goal, blocked=self.blocked_locations)
        return astar_path(self.graph, start, goal, self.positions, blocked=self.blocked_locations)
