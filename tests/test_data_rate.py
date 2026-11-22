"""Tests for the data rate calculations."""

from neural_recording_chain.data_rate import raw_data_rate, spike_data_rate, radio_power_mW, heat_limit_mW, frontend_power_mW

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

def test_radio_power():
    # 160 million bits per second with a 5.8 pJ/bit radio: 0.928 mW
    assert abs(radio_power_mW(160_000_000, 5.8) - 0.928) < 1e-9
    # 1 million bits per second with a 38 pJ/bit radio: 0.038 mW
    assert abs(radio_power_mW(1_000_000, 38) - 0.038) < 1e-9

def test_heat_limit():
    # a 6 x 6 mm chip: 36 mm2 x 0.8 mW/mm2 = 28.8 mW
    assert abs(heat_limit_mW(36) - 28.8) < 1e-9
    # 1 cm2 = 100 mm2: the 80 mW/cm2 of the source
    assert abs(heat_limit_mW(100) - 80) < 1e-9

def test_frontend_power():
    # 1,000 electrodes x 0.41 uW = 410 uW = 0.41 mW
    assert abs(frontend_power_mW(1000) - 0.41) < 1e-9

    # a different power per electrode, e.g. a measured one: 100 x 2 uW = 0.2 mW
    assert abs(frontend_power_mW(100, power_uW_per_electrode=2.0) - 0.2) < 1e-9