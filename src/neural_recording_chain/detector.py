"""Spike detection on a noisy electrode recording."""
import numpy as np

def detect_spikes(recording_uV, time_ms, threshold_factor=4.5, min_gap_ms=1.0, threshold_uV=None):
    # if no threshold is given, estimate it from the recording itself
    if threshold_uV is None:
        absolute_values = np.abs(recording_uV)
        noise_estimate_uV = np.median(absolute_values) / 0.6745
        threshold_uV = threshold_factor * noise_estimate_uV

    detected_times = []
    last_spike_time = -1000.0

    # go through the recording one point at a time
    for i in range(1, len(recording_uV) - 1):
        value = recording_uV[i]

        # a spike has to dip below minus the threshold
        is_below_threshold = value < -threshold_uV
        is_lowest_point = value < recording_uV[i - 1] and value <= recording_uV[i + 1]
        is_far_enough = time_ms[i] - last_spike_time >= min_gap_ms

        if is_below_threshold and is_lowest_point and is_far_enough:
            detected_times.append(time_ms[i])
            last_spike_time = time_ms[i]

    detected_times = np.array(detected_times)
    return detected_times, threshold_uV

def detect_spikes_integer(codes, threshold_code, min_gap_samples):
    detected_samples = []
    last_spike_sample = -1000000
    for i in range(1, len(codes) - 1):
        code = codes[i]
        is_below_threshold = code < -threshold_code
        is_lowest_point = code < codes[i - 1] and code <= codes[i + 1]
        is_far_enough = i - last_spike_sample >= min_gap_samples
        if is_below_threshold and is_lowest_point and is_far_enough:
            detected_samples.append(i)
            last_spike_sample = i
    return np.array(detected_samples)