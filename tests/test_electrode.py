"""Tests for the electrode model."""
import numpy as np
from neural_recording_chain.electrode import extracellular_potential

def test_no_signal_when_soma_and_dendrite_are_equal():
    v = np.full(100, -65.0)
    assert np.allclose(extracellular_potential(v, v), 0.0)

def test_spike_in_soma_gives_negative_dip():
    v_soma = np.array([30.0])
    v_dend = np.array([-10.0])
    assert extracellular_potential(v_soma, v_dend)[0] < 0

def test_signal_is_smaller_further_away():
    v_soma = np.array([30.0])
    v_dend = np.array([-10.0])
    near = extracellular_potential(v_soma, v_dend, soma_distance_um=50, dend_distance_um=200)
    far = extracellular_potential(v_soma, v_dend, soma_distance_um=100, dend_distance_um=250)
    assert abs(far[0]) < abs(near[0])