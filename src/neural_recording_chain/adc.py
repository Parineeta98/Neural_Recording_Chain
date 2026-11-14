"""The digitiser: turns a smooth voltage into whole-number steps."""
import numpy as np

def digitise(signal_uV, n_bits=10, input_range_uV=1000.0):
    # how many different values the digitiser can output
    n_levels = 2 ** n_bits

    # the size of one step, in microvolts
    step_uV = (2 * input_range_uV) / n_levels

    # anything outside the input range gets cut off
    clipped = np.clip(signal_uV, -input_range_uV, input_range_uV)

    # round every value to the nearest step
    step_numbers = np.round(clipped / step_uV)
    digitised_uV = step_numbers * step_uV

    return digitised_uV, step_uV