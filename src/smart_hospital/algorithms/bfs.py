"""Breadth-first search over the hospital graph (CLAUDE.md #15)."""
from __future__ import annotations

from collections import deque


def bfs_path(graph, start: str, goal: str, blocked: set[str] | None = None) -> list[str] | None:
    blocked = blocked or set()
    if start in blocked or goal in blocked or start not in graph or goal not in graph:
        return None
    visited = {start}
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for neighbor in graph.neighbors(node):
            if neighbor in visited or neighbor in blocked:
                continue
            visited.add(neighbor)
            queue.append(path + [neighbor])
    return None
