"""Tests for the burst label."""

import numpy as np
from neural_recording_chain.burst_label import label_event, true_type, wobble_after

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

def test_true_type_finds_false_alarms():
    true_events = [[10.0], [50.0, 53.0, 56.0]]
    assert true_type([10.2], true_events) == "single"
    assert true_type([52.9], true_events) == "burst"
    assert true_type([80.0], true_events) == "none"