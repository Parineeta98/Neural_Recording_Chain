"""Group spikes into events-- single spikes and bursts."""

def group_into_events(spike_times_ms, max_gap_ms=10.0):
    # each event is a list of the spike times that belong together based on the gap between them ie ISI
    events = []
    if len(spike_times_ms) == 0:
        return events
    current_event = [spike_times_ms[0]]
    for i in range(1, len(spike_times_ms)):
        gap = spike_times_ms[i] - spike_times_ms[i - 1]
        if gap <= max_gap_ms:
            # if its close to the previous spike: it belongs to the same event
            current_event.append(spike_times_ms[i])
        else:
            # away from the previous spike: the old event is finished, start a new one
            events.append(current_event)
            current_event = [spike_times_ms[i]]

    events.append(current_event)
    return events

def split_singles_and_bursts(events):
    single_spikes = []
    bursts = []
    for event in events:
        if len(event) == 1:
            single_spikes.append(event)
        else:
            bursts.append(event)
    return single_spikes, bursts

def count_detections_per_event(events, detected_times_ms, tolerance_ms=1.0):
    # for every event, count how many detections fall inside it
    counts = []
    for event in events:
        event_start = event[0] - tolerance_ms
        event_end = event[-1] + tolerance_ms
        count = 0
        for detected_time in detected_times_ms:
            if detected_time >= event_start and detected_time <= event_end:
                count = count + 1
        counts.append(count)
    return counts