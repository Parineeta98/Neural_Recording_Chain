"""Tests for the band-pass filter."""
import numpy as np
from neural_recording_chain.filter import bandpass_filter
from neural_recording_chain.noise import slow_wave_uV

def test_slow_wave_has_requested_size():
    wave = slow_wave_uV(n_samples=20_000, dt_ms=0.05, amplitude_uV=1000.0)
    assert abs(wave.max() - 1000.0) < 1.0
    assert abs(wave.min() + 1000.0) < 1.0

def test_filter_removes_the_slow_wave():
    wave = slow_wave_uV(n_samples=40_000, dt_ms=0.05, amplitude_uV=1000.0)
    filtered = bandpass_filter(wave, dt_ms=0.05)
    # skip the first 100 ms, where the filter is still settling
    settled = filtered[2000:]
    assert np.abs(settled).max() < 5.0

def test_filter_keeps_a_fast_wave():
    fast_wave = slow_wave_uV(n_samples=40_000, dt_ms=0.05, amplitude_uV=100.0, frequency_Hz=1000.0)
    filtered = bandpass_filter(fast_wave, dt_ms=0.05)
    settled = filtered[2000:]
    assert np.abs(settled).max() > 90.0