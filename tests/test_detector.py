"""Tests for the spike detector."""

import numpy as np
from neural_recording_chain.detector import detect_spikes

def make_recording(dip_times_ms):
    """Noisy recording with a -300 uV dip at each of the given times."""
    time_ms = np.arange(0, 1000, 0.05)
    rng = np.random.default_rng(0)
    recording = rng.normal(0.0, 15.0, len(time_ms))
    for dip_time in dip_times_ms:
        index = int(round(dip_time / 0.05))
        recording[index] = -300.0
    return time_ms, recording

def test_finds_the_dips():
    time_ms, recording = make_recording([200, 500, 800])
    detected_times, threshold = detect_spikes(recording, time_ms)
    assert len(detected_times) == 3

def test_finds_nothing_in_pure_noise():
    time_ms, recording = make_recording([])
    detected_times, threshold = detect_spikes(recording, time_ms, threshold_factor=6.0)
    assert len(detected_times) == 0

def test_threshold_follows_the_noise_size():
    time_ms, recording = make_recording([])
    detected_times, threshold = detect_spikes(recording, time_ms, threshold_factor=4.5)
    assert abs(threshold - 4.5 * 15.0) < 3.0