"""The digitiser: turns a smooth voltage into whole-number steps."""
import numpy as np

def digitise(signal_uV, n_bits=10, input_range_uV=1000.0):
    # how many different values the digitiser can output
    n_levels = 2 ** n_bits
    # the size of one step
    step_uV = (2 * input_range_uV) / n_levels
    digitised = []
    for value in signal_uV:
        # anything outside the input range gets cut off
        if value > input_range_uV:
            value = input_range_uV
        if value < -input_range_uV:
            value = -input_range_uV
        step_number = round(value / step_uV)
        digitised.append(step_number * step_uV)

    digitised_uV = np.array(digitised)
    return digitised_uV, step_uV