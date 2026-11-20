"""The answer key: when the neuron fired, and whether each event was a burst or a single spike.

The rule follows Zeldenrust & Wadman (2013), section 2.4: each somatic spike above 0 mV
is one event, and it is a burst if the dendrite reaches -11 mV within 2 to 9 ms after it.
The code tests the highest dendritic voltage in that window, not an upward crossing.
On recording A, 30 of 211 events had the dendrite already above -11 mV when the window
opened, because their calcium spike started before 2 ms; a crossing rule would miss these.
In none of the 211 was the dendrite already above -11 mV at the somatic spike itself,
so the rule does not pick up calcium spikes left over from an earlier event.
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