import numpy as np
from neural_recording_chain.pyramidal_cell import simulate_pyramidal_cell

def test_output_has_one_value_per_step():
    input_theory = np.zeros(2000)   # 100 ms at 0.05 ms steps
    result = simulate_pyramidal_cell(input_theory, dt_ms=0.05)
    assert len(result["time_ms"]) == 2000
    assert len(result["v_soma_mV"]) == 2000
    assert len(result["v_dend_mV"]) == 2000

def test_no_input_means_no_spikes():
    input_theory = np.zeros(4000)   # 200 ms
    result = simulate_pyramidal_cell(input_theory, dt_ms=0.05)
    assert max(result["v_soma_mV"]) < 0

def test_strong_input_makes_spikes():
    input_theory = np.ones(4000)    # 200 ms
    result = simulate_pyramidal_cell(input_theory, dt_ms=0.05)
    assert max(result["v_soma_mV"]) > 0