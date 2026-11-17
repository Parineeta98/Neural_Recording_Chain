"""Tests for the detection score."""
from neural_recording_chain.scoring import score_detection

def test_perfect_detection():
    hits, misses, false_alarms = score_detection([10, 20, 30], [10, 20, 30])
    assert hits == 3
    assert misses == 0
    assert false_alarms == 0

def test_one_missed_spike():
    hits, misses, false_alarms = score_detection([10, 20, 30], [10, 30])
    assert hits == 2
    assert misses == 1
    assert false_alarms == 0

def test_one_false_alarm():
    hits, misses, false_alarms = score_detection([10, 20], [10, 20, 55])
    assert hits == 2
    assert misses == 0
    assert false_alarms == 1

def test_small_timing_difference_still_counts():
    hits, misses, false_alarms = score_detection([10.0], [10.4])
    assert hits == 1

def test_one_detection_cannot_hit_two_spikes():
    # one detection between two close spikes: one hit, one miss
    hits, misses, false_alarms = score_detection([10.0, 11.5], [10.8])
    assert hits == 1
    assert misses == 1
    assert false_alarms == 0

def test_double_detection_is_a_false_alarm():
    # two detections on one spike: one hit, one extra detection
    hits, misses, false_alarms = score_detection([10.0], [9.7, 10.4])
    assert hits == 1
    assert misses == 0
    assert false_alarms == 1

def test_closest_detection_is_used():
    hits, misses, false_alarms = score_detection([10.0, 11.5], [10.1, 11.4])
    assert hits == 2
    assert misses == 0
    assert false_alarms == 0