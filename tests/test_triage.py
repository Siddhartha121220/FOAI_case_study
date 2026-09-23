from smart_hospital.algorithms.triage import compute_priority
from smart_hospital.config import SeverityWeights


def test_priority_increases_with_severity():
    weights = SeverityWeights()
    low = compute_priority(severity=2, waiting_time=0, weights=weights)
    high = compute_priority(severity=9, waiting_time=0, weights=weights)
    assert high > low


def test_priority_increases_with_waiting_time():
    weights = SeverityWeights()
    early = compute_priority(severity=5, waiting_time=0, weights=weights)
    later = compute_priority(severity=5, waiting_time=30, weights=weights)
    assert later > early


def test_weights_are_configurable():
    severity_only = compute_priority(5, waiting_time=60, weights=SeverityWeights(severity_weight=1, waiting_weight=0))
    assert severity_only == 5
