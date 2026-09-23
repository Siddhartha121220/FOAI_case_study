"""Simplest reliable visualization (CLAUDE.md #26): a text dashboard that
works in any terminal, plus an optional static hospital-map snapshot. No
GUI/browser dependency, since a headless run must not fail to visualize.
"""
from __future__ import annotations

import statistics
from collections import Counter

from ..agents.patient import PatientState


def render_text(model) -> str:
    active = [p for p in model.patients if p.current_state is not PatientState.DISCHARGED]
    waiting = [p for p in active if p.current_state is PatientState.WAITING]
    critical = [p for p in active if p.severity >= 9]
    avg_wait = statistics.mean(p.waiting_time for p in active) if active else 0.0
    available_doctors = sum(1 for d in model.doctors if d.availability)
    available_nurses = sum(1 for n in model.nurses if n.availability)
    available_icu = model.bed_manager.available_beds("ICU")

    return "\n".join([
        f"t={model.current_time}",
        f"Patients waiting: {len(waiting):<3d} Critical: {len(critical):<3d} "
        f"Avg waiting time: {avg_wait:.1f}",
        f"Doctors available: {available_doctors}/{len(model.doctors)}  "
        f"Nurses available: {available_nurses}/{len(model.nurses)}  "
        f"ICU beds available: {available_icu}/{model.bed_manager.bed_counts.get('ICU', 0)}",
        f"Lab: {len(model.lab.active_tests)} active, {len(model.lab.test_queue)} queued  "
        f"Patients served: {len(model.patients) - len(active)}/{len(model.patients)}",
    ])


def render_map_snapshot(model, path: str) -> None:
    """Static PNG of the hospital graph with per-location occupant counts."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx

    counts = Counter(agent.location for agent in (*model.doctors, *model.nurses, *model.patients))

    fig, ax = plt.subplots(figsize=(6, 5))
    pos = model.hospital_map.positions
    nx.draw(model.hospital_map.graph, pos, ax=ax, node_color="lightblue", node_size=900,
             edge_color="gray", with_labels=False)
    labels = {node: f"{node}\n({counts.get(node, 0)})" for node in pos}
    nx.draw_networkx_labels(model.hospital_map.graph, pos, labels=labels, font_size=7, ax=ax)
    ax.set_title(f"Hospital Map — t={model.current_time}")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
