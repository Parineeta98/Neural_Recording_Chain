"""The answer key: check whether the neuronal activity is a burst or a single spike.

The rule follows Zeldenrust & Wadman (2013), section 2.4. Each somatic spike above 0 mV is one event. 
It is a burst if the first or second dendritic spike after it (the dendrite crossing −11 mV) comes 2 to 9 ms later. 
Otherwise it is a single spike.
"""

def upward_crossings(voltage_mV, threshold_mV):
    crossing_indices = []
    for i in range(1, len(voltage_mV)):
        below_before = voltage_mV[i - 1] < threshold_mV
        above_now = voltage_mV[i] >= threshold_mV
        if below_before and above_now:
            crossing_indices.append(i)
    return crossing_indices

def classify_events(v_soma_mV, v_dend_mV, time_ms, soma_threshold_mV=0.0,
                    dend_threshold_mV=-11.0, window_start_ms=2.0, window_end_ms=9.0):
    dt_ms = time_ms[1] - time_ms[0]
    start_steps = round(window_start_ms / dt_ms)
    end_steps = round(window_end_ms / dt_ms)

    # every somatic spike that goes above 0 mV is one event
    soma_indices = upward_crossings(v_soma_mV, soma_threshold_mV)
    event_times = []
    event_types = []

    for i in soma_indices:
        # the dendrite voltage from 2 to 9 ms after this somatic spike
        window = v_dend_mV[i + start_steps : i + end_steps + 1]

        # skip a spike so close to the end of the recording that there is no window
        if len(window) == 0:
            continue
        highest_dend_mV = max(window)
        event_times.append(time_ms[i])
        if highest_dend_mV >= dend_threshold_mV:
            event_types.append("burst")
        else:
            event_types.append("single")

    return event_times, event_types