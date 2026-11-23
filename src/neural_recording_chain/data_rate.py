"""How much data a recording chip produces."""

# Sources and choices for the values in this file:
# - heat limit 0.8 mW per mm2 (80 mW per cm2, about 1 degree C of warming):
#   Kim et al. (2006), citing Seese et al. (1998), whose data are from muscle tissue
# - the radio's energy per bit is an input, not fixed here; the notebook uses
#   5.8 pJ/bit (Song et al., 2022) and 38 pJ/bit (Mercier et al., 2014)
# - front end 0.41 uW per electrode (amplifier and digitiser, 9 bits, 20 kHz output),
#   measured on a 22 nm chip: Guo et al. (2024)

def raw_data_rate(n_electrodes, sampling_rate_Hz, n_bits):
    # every electrode produces n_bits for every sample
    bits_per_second = n_electrodes * sampling_rate_Hz * n_bits
    return bits_per_second

def spike_data_rate(n_electrodes, spikes_per_second, bits_per_spike):
    # every detected spike is sent as one short message
    bits_per_second = n_electrodes * spikes_per_second * bits_per_spike
    return bits_per_second 

def radio_power_mW(bits_per_second, energy_pJ_per_bit):
    # the power the radio needs to send this many bits per second
    energy_J_per_bit = energy_pJ_per_bit * 1e-12   # picojoules to joules
    power_W = bits_per_second * energy_J_per_bit    # joules per second = watts
    power_mW = power_W * 1000                       # watts to milliwatts
    return power_mW

def heat_limit_mW(area_mm2, limit_mW_per_mm2=0.8):
    # the most power an implant of this area may use: 80 mW per cm2 of tissue
    # (0.8 mW per mm2), which keeps the warming to about 1 degree C
    # (Kim et al., 2006, citing Seese et al., 1998, whose data are from muscle tissue)
    allowed_mW = area_mm2 * limit_mW_per_mm2
    return allowed_mW

def frontend_power_mW(n_electrodes, power_uW_per_electrode=0.41):
    # amplifier and digitiser on every electrode, running all the time
    power_uW = n_electrodes * power_uW_per_electrode
    power_mW = power_uW / 1000                       # microwatts to milliwatts
    return power_mW