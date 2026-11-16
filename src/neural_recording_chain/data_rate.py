"""How much data a recording chip produces."""
def raw_data_rate(n_electrodes, sampling_rate_Hz, n_bits):
    # every electrode produces n_bits for every sample
    bits_per_second = n_electrodes * sampling_rate_Hz * n_bits
    return bits_per_second

def spike_data_rate(n_electrodes, spikes_per_second, bits_per_spike):
    # every detected spike is sent as one short message
    bits_per_second = n_electrodes * spikes_per_second * bits_per_spike
    return bits_per_second 
