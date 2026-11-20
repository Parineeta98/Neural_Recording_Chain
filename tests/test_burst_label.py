"""Tests for the burst label."""

import numpy as np
from neural_recording_chain.burst_label import label_event, match_true_events, count_unmatched, wobble_after

def make_signal(busy_after_ms=None):
    """Flat signal, with a busy stretch after a given time if asked."""
    time_ms = np.arange(0, 100, 0.05)
    signal = np.zeros(len(time_ms))
    if busy_after_ms is not None:
        rng = np.random.default_rng(0)
        start = int(round((busy_after_ms + 2) / 0.05))
        end = int(round((busy_after_ms + 10) / 0.05))
        signal[start:end] = rng.normal(0.0, 30.0, end - start)
    return time_ms, signal

def test_flat_signal_has_no_wobble():
    time_ms, signal = make_signal()
    assert wobble_after(signal, time_ms, 50.0) == 0.0

def test_busy_signal_has_more_wobble():
    time_ms, signal = make_signal(busy_after_ms=50.0)
    assert wobble_after(signal, time_ms, 50.0) > 20.0

def test_two_detections_are_always_a_burst():
    time_ms, signal = make_signal()
    assert label_event([50.0, 54.0], signal, time_ms, cutoff_uV=18.5) == "burst"

def test_one_detection_with_calm_signal_is_a_single_spike():
    time_ms, signal = make_signal()
    assert label_event([50.0], signal, time_ms, cutoff_uV=18.5) == "single"

def test_one_detection_with_busy_signal_is_a_burst():
    time_ms, signal = make_signal(busy_after_ms=50.0)
    assert label_event([50.0], signal, time_ms, cutoff_uV=18.5) == "burst"

def test_each_true_event_finds_its_group():
    matches = match_true_events([10.0, 50.0], [[10.2, 14.0], [50.1]])
    assert matches == [0, 1]

def test_missed_event_gets_minus_one():
    matches = match_true_events([10.0, 80.0], [[10.2]])
    assert matches == [0, -1]

def test_group_with_no_true_event_is_unmatched():
    groups = [[10.2], [30.0], [50.1]]
    matches = match_true_events([10.0, 50.0], groups)
    assert count_unmatched(groups, matches) == 1

def test_two_true_events_can_share_a_group():
    # a doublet: two true events 5 ms apart, detected as one group
    matches = match_true_events([10.0, 15.0], [[10.1, 15.1]])
    assert matches == [0, 0]