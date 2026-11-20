import numpy as np
from neural_recording_chain.answer_key import upward_crossings, classify_events

def make_traces(dend_time_ms, dend_value_mV):
    # 50 ms of fake recording, one sample every 0.05 ms
    time_ms = np.arange(0, 50, 0.05)
    # soma rests at -65 mV and fires one spike at 10 ms, which is 200 steps in
    v_soma_mV = np.full(len(time_ms), -65.0)
    v_soma_mV[200:210] = 20.0

    # dendrite rests at -60 mV and has one short bump at dend_time_ms
    v_dend_mV = np.full(len(time_ms), -60.0)
    bump_index = round(dend_time_ms / 0.05)
    v_dend_mV[bump_index] = dend_value_mV

    return v_soma_mV, v_dend_mV, time_ms


def test_crossings_found_at_the_right_places():
    voltage = [-5, -2, 1, 3, -1, 2]
    assert upward_crossings(voltage, 0) == [2, 5]

def test_staying_above_is_not_a_new_crossing():
    voltage = [1, 2, 3, 4]
    assert upward_crossings(voltage, 0) == []

def test_dendrite_reaching_threshold_in_window_is_a_burst():
    # dendrite reaches -5 mV at 15 ms, which is 5 ms after the somatic spike
    v_soma, v_dend, time = make_traces(dend_time_ms=15.0, dend_value_mV=-5.0)
    times, types = classify_events(v_soma, v_dend, time)
    assert len(times) == 1
    assert types == ["burst"]

def test_dendrite_staying_low_is_a_single_spike():
    # dendrite only reaches -30 mV, below -11 mV
    v_soma, v_dend, time = make_traces(dend_time_ms=15.0, dend_value_mV=-30.0)
    times, types = classify_events(v_soma, v_dend, time)
    assert types == ["single"]

def test_dendrite_too_early_is_a_single_spike():
    # dendrite reaches -5 mV only 1 ms after the somatic spike, before the window
    v_soma, v_dend, time = make_traces(dend_time_ms=11.0, dend_value_mV=-5.0)
    times, types = classify_events(v_soma, v_dend, time)
    assert types == ["single"]

def test_dendrite_too_late_is_a_single_spike():
    # dendrite reaches -5 mV 12 ms after the somatic spike, after the window
    v_soma, v_dend, time = make_traces(dend_time_ms=22.0, dend_value_mV=-5.0)
    times, types = classify_events(v_soma, v_dend, time)
    assert types == ["single"]

def test_spike_at_the_very_end_is_skipped():
    time = np.arange(0, 50, 0.05)
    v_soma = np.full(len(time), -65.0)
    v_dend = np.full(len(time), -60.0)
    v_soma[-5:] = 20.0  # a spike in the last 0.25 ms, so no window after it
    times, types = classify_events(v_soma, v_dend, time)
    assert times == []
    assert types == []