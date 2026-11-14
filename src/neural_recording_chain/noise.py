"""Noise sources that a real electrode adds to the signal.
boltzman_j_per_k is a constant of nature that links temperature to energy.
resistance_ohm is the magnitude for a small recording electrode. 
temperature_K is the temperature of the tissue in Kelvin -- body temperature, 37 °C, in kelvin
"""
import numpy as np
from scipy.signal import butter, sosfilt

boltzman_j_per_k = 1.380649e-23 #a constant of nature that links temperature to energy

def thermal_noise_uV(n_samples, dt_ms, resistance_ohm=1e6, temperature_K=310.0, seed=0):
    rng = np.random.default_rng(seed)
    bandwidth_Hz = 1.0 / (2.0 * dt_ms * 1e-3)
    rms_V = np.sqrt(4.0 * boltzman_j_per_k * temperature_K * resistance_ohm * bandwidth_Hz)
    rms_uV = rms_V * 1e6
    return rng.normal(0.0, rms_uV, n_samples)

def background_noise_uV(n_samples, dt_ms, rms_uV=10.0, low_Hz=300.0, high_Hz=3000.0, seed=1):
    rng = np.random.default_rng(seed)
    white = rng.normal(0.0, 1.0, n_samples)

    sampling_rate_Hz = 1000.0 / dt_ms
    sos = butter(2, [low_Hz, high_Hz], btype="bandpass", fs=sampling_rate_Hz, output="sos")
    shaped = sosfilt(sos, white)

    return shaped * (rms_uV / shaped.std())