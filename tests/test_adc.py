"""Tests for the digitiser."""

import numpy as np
from neural_recording_chain.adc import digitise, to_codes 

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

def test_codes_are_whole_numbers_in_range():
    signal = np.array([0.0, 40.0, 120.0, -5000.0, 5000.0])
    codes, step = to_codes(signal, n_bits=8, input_range_uV=500.0)
    # one step is 1000 / 256 = 3.90625 uV
    assert codes[0] == 0
    assert codes[1] == 10      # 40 / 3.90625 = 10.24, rounds to 10
    assert codes[2] == 31      # 120 / 3.90625 = 30.72, rounds to 31
    assert codes[3] == -128    # far below the range: the lowest code
    assert codes[4] == 127     # far above the range: the highest code