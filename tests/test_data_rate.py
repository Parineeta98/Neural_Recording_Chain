"""Tests for the data rate calculations."""

from neural_recording_chain.data_rate import raw_data_rate, spike_data_rate

def test_raw_rate_matches_published_neuralink_figure():
    rate = raw_data_rate(n_electrodes=1024, sampling_rate_Hz=20000, n_bits=10)
    assert rate == 204_800_000

def test_spike_rate_is_a_simple_product():
    rate = spike_data_rate(n_electrodes=1000, spikes_per_second=5, bits_per_spike=32)
    assert rate == 160_000

def test_sending_spikes_takes_less_data_than_sending_everything():
    everything = raw_data_rate(n_electrodes=100, sampling_rate_Hz=20000, n_bits=8)
    spikes_only = spike_data_rate(n_electrodes=100, spikes_per_second=5, bits_per_spike=32)
    assert spikes_only < everything