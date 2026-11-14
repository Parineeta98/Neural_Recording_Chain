"""Tests for the digitiser."""

import numpy as np
from neural_recording_chain.adc import digitise

def test_step_size():
    signal = np.array([0.0])
    digitised, step = digitise(signal, n_bits=10, input_range_uV=1000.0)
    assert abs(step - 1.953125) < 0.0001

def test_values_are_rounded_to_steps():
    signal = np.array([0.0, 40.0, 120.0])
    digitised, step = digitise(signal, n_bits=4, input_range_uV=1000.0)
    assert digitised[0] == 0.0
    assert digitised[1] == 0.0
    assert digitised[2] == 125.0

def test_values_outside_the_range_are_cut_off():
    signal = np.array([5000.0, -5000.0])
    digitised, step = digitise(signal, n_bits=10, input_range_uV=1000.0)
    assert digitised[0] == 1000.0
    assert digitised[1] == -1000.0

def test_more_bits_give_a_smaller_error():
    rng = np.random.default_rng(0)
    signal = rng.normal(0.0, 50.0, 10_000)
    coarse, coarse_step = digitise(signal, n_bits=6)
    fine, fine_step = digitise(signal, n_bits=10)
    coarse_error = np.abs(coarse - signal).mean()
    fine_error = np.abs(fine - signal).mean()
    assert fine_error < coarse_error