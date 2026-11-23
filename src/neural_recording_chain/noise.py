"""Noise sources that a real electrode adds to the signal.
boltzmann_J_per_K is a constant of nature that links temperature to energy.
resistance_ohm is the magnitude for a small recording electrode. 
temperature_K is the temperature of the tissue in Kelvin -- body temperature, 37 °C, in kelvin
"""

# Sources and choices for the values in this file:
# - thermal noise sqrt(4kTRB): Johnson (1928); Nyquist (1928)
# - 1 MOhm: an assumed order of magnitude; only the resistive part of a real
#   electrode's impedance makes thermal noise (Obien et al., 2015)
# - 310 K: body temperature, 37 degrees C
# - 10 uV background activity: assumed
# - 8 Hz and 1000 uV slow wave: within the range of hippocampal theta in rodents
#   (Buzsaki, 2002; Bland, 2008)

import numpy as np
from scipy.signal import butter, sosfilt
from neural_recording_chain.filter import bandpass_filter

boltzmann_J_per_K = 1.380649e-23 #a constant of nature that links temperature to energy

def thermal_noise_uV(n_samples, dt_ms, resistance_ohm=1e6, temperature_K=310.0, seed=0):
    rng = np.random.default_rng(seed)
    bandwidth_Hz = 1.0 / (2.0 * dt_ms * 1e-3)
    rms_V = np.sqrt(4.0 * boltzmann_J_per_K * temperature_K * resistance_ohm * bandwidth_Hz)
    rms_uV = rms_V * 1e6
    return rng.normal(0.0, rms_uV, n_samples)

def background_noise_uV(n_samples, dt_ms, rms_uV=10.0, low_Hz=300.0, high_Hz=3000.0, seed=1):
    rng = np.random.default_rng(seed)
    white = rng.normal(0.0, 1.0, n_samples)
    sampling_rate_Hz = 1000.0 / dt_ms
    sos = butter(2, [low_Hz, high_Hz], btype="bandpass", fs=sampling_rate_Hz, output="sos")
    shaped = bandpass_filter(white, dt_ms, low_Hz, high_Hz)
    return shaped * (rms_uV / shaped.std())

def slow_wave_uV(n_samples, dt_ms, amplitude_uV=1000.0, frequency_Hz=8.0):
    # the time of every sample, in seconds
    sample_numbers = np.arange(n_samples)
    time_s = sample_numbers * dt_ms / 1000.0
    # a smooth wave that goes up and down "frequency_Hz" times per second
    wave = amplitude_uV * np.sin(2 * np.pi * frequency_Hz * time_s)
    return wave