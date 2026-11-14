"""Tests for the noise sources."""
import numpy as np
from neural_recording_chain.noise import thermal_noise_uV

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