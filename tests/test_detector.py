"""Tests for the spike detector."""

import numpy as np
from neural_recording_chain.detector import detect_spikes, detect_spikes_integer

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

def test_fixed_threshold_is_used():
    time_ms = np.arange(0, 100, 0.05)
    recording = np.zeros(len(time_ms))
    recording[1000] = -60.0   # a big dip
    recording[1500] = -30.0   # a smaller dip

    # threshold 50: only the big dip counts
    detected, threshold = detect_spikes(recording, time_ms, threshold_uV=50.0)
    assert threshold == 50.0
    assert len(detected) == 1

    # threshold 20: both dips count
    detected, threshold = detect_spikes(recording, time_ms, threshold_uV=20.0)
    assert len(detected) == 2

def test_integer_detector_uses_codes_and_samples():
    codes = np.zeros(200, dtype=int)
    codes[50] = -20    # a big dip
    codes[80] = -15    # a second dip, 30 samples later
    codes[150] = -10   # a small dip
    # threshold 12 codes, dead time 40 samples:
    # the dip at 80 is too soon after 50, and the dip at 150 is too small
    detected = detect_spikes_integer(codes, threshold_code=12, min_gap_samples=40)
    assert list(detected) == [50]

    # a shorter dead time of 20 samples lets the second dip through
    detected = detect_spikes_integer(codes, threshold_code=12, min_gap_samples=20)
    assert list(detected) == [50, 80]