"""Tests for the noise sources."""
import numpy as np
from scipy.signal import welch
from neural_recording_chain.noise import background_noise_uV, thermal_noise_uV  

def test_thermal_noise_has_expected_size():
    noise = thermal_noise_uV(n_samples=200_000, dt_ms=0.05)
    assert abs(noise.std() - 13.1) < 0.2

def test_thermal_noise_is_centred_on_zero():
    noise = thermal_noise_uV(n_samples=200_000, dt_ms=0.05)
    assert abs(noise.mean()) < 0.2

def test_higher_resistance_gives_more_noise():
    low = thermal_noise_uV(n_samples=50_000, dt_ms=0.05, resistance_ohm=1e5)
    high = thermal_noise_uV(n_samples=50_000, dt_ms=0.05, resistance_ohm=1e6)
    assert high.std() > low.std()

def test_same_seed_gives_same_noise():
    first = thermal_noise_uV(n_samples=1000, dt_ms=0.05, seed=3)
    second = thermal_noise_uV(n_samples=1000, dt_ms=0.05, seed=3)
    assert np.array_equal(first, second)

def test_background_noise_has_requested_size():
    hum = background_noise_uV(n_samples=50_000, dt_ms=0.05, rms_uV=10.0)
    assert abs(hum.std() - 10.0) < 0.01

def test_background_noise_sits_in_the_spike_band():
    hum = background_noise_uV(n_samples=200_000, dt_ms=0.05)
    frequencies, power = welch(hum, fs=20_000, nperseg=4096)
    in_band = (frequencies > 300) & (frequencies < 3000)
    assert power[in_band].sum() / power.sum() > 0.7

def test_background_and_thermal_noise_are_unrelated():
    hum = background_noise_uV(n_samples=50_000, dt_ms=0.05)
    thermal = thermal_noise_uV(n_samples=50_000, dt_ms=0.05)
    assert abs(np.corrcoef(hum, thermal)[0, 1]) < 0.05