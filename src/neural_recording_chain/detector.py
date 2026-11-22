"""Spike detection on a noisy electrode recording."""

# Sources and choices for the values in this file:
# - noise level = median(|x|) / 0.6745: Quian Quiroga et al. (2004), equation 3.1
#   (their threshold is 4 x the noise level; 4.5 was chosen here on recording A)
# - an average instead of a median, the usual low-cost choice in hardware: Oprea et al. (2022)
# - running average with additions and bit shifts, as in hardware spike detectors:
#   Harrison (2003); Zhang & Constandinou (2021)
# - no update of the average during the dead time after a detection: Zhang & Constandinou (2021)
# - 5.64 = 4.5 / 0.798, because for Gaussian noise mean(|x|) = 0.798 x the standard deviation
# - shift 13 (8,192 samples, 410 ms) and 32,768 samples to settle (four time constants): chosen here

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

def running_threshold(codes, shift=13, extra_bits=6, multiplier=361, multiplier_shift=6):
    # the chip's own threshold, worked out with whole numbers as the signal comes in.
    # "total" holds the running average size, kept 2**extra_bits times bigger so its
    # decimals are not lost, and 2**shift times bigger as part of the running average.
    total = 0
    thresholds = []
    for code in codes:
        if code >= 0:
            size = code
        else:
            size = -code
        total = total + (size << extra_bits) - (total >> shift)
        # threshold = 5.64 x the average size (361 / 64 = 5.64)
        threshold_code = (total * multiplier) >> (shift + extra_bits + multiplier_shift)
        thresholds.append(threshold_code)
    return np.array(thresholds)

def detect_spikes_on_chip(codes, min_gap_samples, samples_to_settle=32768,
                          shift=13, extra_bits=6, multiplier=361, multiplier_shift=6):
    total = 0
    detected_samples = []
    thresholds = []
    last_spike_sample = -1000000

    for i in range(len(codes)):
        code = codes[i]
        if code >= 0:
            size = code
        else:
            size = -code
        # update the running average, but not during the dead time after a detection,
        # so the spikes themselves do not push the threshold up (Zhang & Constandinou, 2021)
        if i - last_spike_sample >= min_gap_samples:
            total = total + (size << extra_bits) - (total >> shift)
        # threshold = 5.64 x the average size
        threshold_code = (total * multiplier) >> (shift + extra_bits + multiplier_shift)
        thresholds.append(threshold_code)
        # no detections while the threshold settles, and none at the first or last sample, which have no neighbour on one side
        if i < samples_to_settle or i == 0 or i == len(codes) - 1:
            continue
    
        is_below_threshold = code < -threshold_code
        is_lowest_point = code < codes[i - 1] and code <= codes[i + 1]
        is_far_enough = i - last_spike_sample >= min_gap_samples

        if is_below_threshold and is_lowest_point and is_far_enough:
            detected_samples.append(i)
            last_spike_sample = i
    return np.array(detected_samples), np.array(thresholds)