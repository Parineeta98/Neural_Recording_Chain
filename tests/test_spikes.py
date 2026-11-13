"""Tests for the spike finder."""
import numpy as np
from neural_recording_chain.spikes import find_spikes

def make_trace(bumps):
    """Flat trace at -65 mV with a bump at each (time_ms, height_mV)."""
    time_ms = np.arange(0, 100, 0.05)
    v = np.full(len(time_ms), -65.0)
    for bump_time, bump_height in bumps:
        v = v + bump_height * np.exp(-((time_ms - bump_time) ** 2) / 0.5)
    return time_ms, v

def test_finds_one_spike_at_the_right_time():
    time_ms, v = make_trace([(50, 95)])
    spike_times, spike_heights = find_spikes(v, time_ms)
    assert len(spike_times) == 1
    assert abs(spike_times[0] - 50) < 0.1
    assert abs(spike_heights[0] - 30) < 0.1

def test_flat_trace_has_no_spikes():
    time_ms, v = make_trace([])
    spike_times, _ = find_spikes(v, time_ms)
    assert len(spike_times) == 0

def test_small_wobble_is_not_a_spike():
    time_ms, v = make_trace([(50, 10)])
    spike_times, _ = find_spikes(v, time_ms)
    assert len(spike_times) == 0

def test_finds_every_spike_in_a_burst():
    time_ms, v = make_trace([(50, 95), (53, 55), (58, 45)])
    spike_times, _ = find_spikes(v, time_ms)
    assert len(spike_times) == 3