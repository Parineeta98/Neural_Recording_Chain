"""Find spike times in a simulated membrane potential."""
from scipy.signal import find_peaks

def find_spikes(v_soma_mV, time_ms, min_height_mV=-40.0, min_prominence_mV=5.0):
    peak_indices, _ = find_peaks(v_soma_mV, height=min_height_mV, prominence=min_prominence_mV)
    spike_times_ms = time_ms[peak_indices]
    spike_heights_mV = v_soma_mV[peak_indices]
    return spike_times_ms, spike_heights_mV