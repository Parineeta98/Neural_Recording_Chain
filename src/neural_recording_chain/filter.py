"""Filters that keep the spike frequencies and remove the rest."""
from scipy.signal import butter, sosfilt

def bandpass_filter(signal_uV, dt_ms, low_Hz=300.0, high_Hz=3000.0):
    sampling_rate_Hz = 1000.0 / dt_ms
    filter_design = butter(2, [low_Hz, high_Hz], btype="bandpass", fs=sampling_rate_Hz, output="sos")
    filtered_uV = sosfilt(filter_design, signal_uV)
    return filtered_uV