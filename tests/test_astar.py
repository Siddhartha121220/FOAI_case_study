from smart_hospital.algorithms.astar import astar_path
from smart_hospital.algorithms.bfs import bfs_path
from smart_hospital.environment.hospital_map import HospitalMap


def test_astar_finds_direct_hub_route():
    hmap = HospitalMap()
    path = astar_path(hmap.graph, "DOCTOR_ROOM_1", "EMERGENCY_ROOM", hmap.positions)
    assert path == ["DOCTOR_ROOM_1", "EMERGENCY_ROOM"]


def test_astar_matches_bfs_hop_count_on_unweighted_graph():
    hmap = HospitalMap()
    a_path = astar_path(hmap.graph, "ICU", "LABORATORY", hmap.positions)
    b_path = bfs_path(hmap.graph, "ICU", "LABORATORY")
    assert len(a_path) == len(b_path)


def test_astar_returns_none_for_unreachable_goal():
    hmap = HospitalMap()
    hmap.graph.add_node("ISOLATED_ROOM")
    path = astar_path(hmap.graph, "EMERGENCY_ROOM", "ISOLATED_ROOM", {**hmap.positions, "ISOLATED_ROOM": (5, 5)})
    assert path is None


def test_astar_reroutes_around_blocked_route():
    hmap = HospitalMap()
    hmap.block_route("EMERGENCY_ROOM", "ICU")
    path = astar_path(hmap.graph, "EMERGENCY_ROOM", "ICU", hmap.positions)
    assert path is not None
    assert "GENERAL_WARD" in path  # only remaining route: via the extra ICU-GENERAL_WARD edge


def test_astar_respects_blocked_locations():
    hmap = HospitalMap()
    hmap.block_location("GENERAL_WARD")
    hmap.block_route("EMERGENCY_ROOM", "ICU")
    path = astar_path(hmap.graph, "EMERGENCY_ROOM", "ICU", hmap.positions, blocked=hmap.blocked_locations)
    assert path is None


def test_bfs_blocked_start_or_goal_returns_none():
    hmap = HospitalMap()
    assert bfs_path(hmap.graph, "EMERGENCY_ROOM", "ICU", blocked={"ICU"}) is None


def test_plan_path_replans_after_route_is_blocked():
    hmap = HospitalMap()
    before = hmap.plan_path("EMERGENCY_ROOM", "ICU")
    assert before == ["EMERGENCY_ROOM", "ICU"]
    hmap.block_route("EMERGENCY_ROOM", "ICU")
    after = hmap.plan_path("EMERGENCY_ROOM", "ICU")
    assert after != before
    assert after is not None
