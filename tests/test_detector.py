"""Tests for the spike detector."""

import numpy as np
from neural_recording_chain.detector import detect_spikes, detect_spikes_integer, running_threshold, detect_spikes_on_chip

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

def test_running_threshold_settles_at_the_right_size():
    # a signal whose size is always 4 codes
    codes = np.array([4, -4] * 50000)
    thresholds = running_threshold(codes)
    # it starts at zero and has to warm up
    assert thresholds[0] == 0
    # after 100,000 samples it has settled: 4 x 5.64 = 22.56, so 22 in whole codes
    assert thresholds[-1] == 22

def test_chip_detector_uses_its_own_threshold_and_warm_up():
    # background of size 4 codes, so the threshold settles at about 21-22 codes
    codes = np.array([4, -4] * 20000)
    codes[1000] = -40     # a big dip, but while the threshold is still settling
    codes[30000] = -40    # a big dip after settling
    codes[30010] = -30    # too soon after the last one (dead time 60 samples)
    codes[35000] = -15    # smaller than the threshold
    detected = detect_spikes_on_chip(codes, min_gap_samples=60, samples_to_settle=20000)
    assert list(detected) == [30000]

def test_chip_detector_pauses_the_average_after_a_detection():
    # background of size 4 codes, so the threshold settles at about 22 codes
    codes = np.array([4, -4] * 20000)
    codes[30000] = -40          # a detection
    codes[30001:30060] = 127    # a huge signal right after it, inside the dead time
    codes[30100] = -24          # a dip just above the settled threshold
    detected = detect_spikes_on_chip(codes, min_gap_samples=60, samples_to_settle=20000)
    assert list(detected) == [30000, 30100]