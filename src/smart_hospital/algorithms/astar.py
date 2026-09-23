"""A* search with a Manhattan-distance heuristic (CLAUDE.md #15)."""
from __future__ import annotations

import heapq


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_path(graph, start: str, goal: str, positions: dict[str, tuple[int, int]],
                blocked: set[str] | None = None) -> list[str] | None:
    blocked = blocked or set()
    if start in blocked or goal in blocked or start not in graph or goal not in graph:
        return None

    open_set = [(0, start)]
    came_from: dict[str, str] = {}
    g_score = {start: 0}
    visited: set[str] = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return _reconstruct(came_from, current)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in graph.neighbors(current):
            if neighbor in blocked:
                continue
            weight = graph[current][neighbor].get("weight", 1)
            tentative = g_score[current] + weight
            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f_score = tentative + _manhattan(positions[neighbor], positions[goal])
                heapq.heappush(open_set, (f_score, neighbor))
    return None


def _reconstruct(came_from: dict[str, str], current: str) -> list[str]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))
