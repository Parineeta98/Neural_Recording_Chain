"""Find spike times in a simulated membrane potential. This function does not handle flat topped peaks that can sometimes be found in real data."""
import numpy as np

def find_spikes(v_soma_mV, time_ms, min_height_mV=-40.0, min_prominence_mV=5.0):
    spike_times = []
    spike_heights = []
    n_samples = len(v_soma_mV)

    for i in range(1, n_samples - 1):
        height = v_soma_mV[i]

        # a peak is higher than the sample before and the sample after it
        is_peak = height > v_soma_mV[i - 1] and height > v_soma_mV[i + 1]
        if not is_peak or height < min_height_mV:
            continue

        # walk left until the voltage goes higher than the peak, remembering the lowest point
        left_lowest = height
        j = i - 1
        while j >= 0 and v_soma_mV[j] <= height:
            if v_soma_mV[j] < left_lowest:
                left_lowest = v_soma_mV[j]
            j = j - 1

        # the same to the right
        right_lowest = height
        j = i + 1
        while j < n_samples and v_soma_mV[j] <= height:
            if v_soma_mV[j] < right_lowest:
                right_lowest = v_soma_mV[j]
            j = j + 1

        # prominence: how far the peak rises above the higher of the two valleys
        prominence = height - max(left_lowest, right_lowest)
        if prominence >= min_prominence_mV:
            spike_times.append(time_ms[i])
            spike_heights.append(height)

    return np.array(spike_times), np.array(spike_heights)