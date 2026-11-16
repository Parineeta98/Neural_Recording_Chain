"""Segregating and labelling signal as part of a burst or a single spike."""

import numpy as np

def wobble_after(signal_uV, time_ms, event_time_ms, start_ms=2.0, end_ms=10.0):
    # how much the signal wobbles in a short window after a detection
    dt_ms = time_ms[1] - time_ms[0]
    first_index = int(round((event_time_ms + start_ms) / dt_ms))
    last_index = int(round((event_time_ms + end_ms) / dt_ms))
    window = signal_uV[first_index:last_index]
    return np.std(window)

def label_event(detected_event, signal_uV, time_ms, cutoff_uV):
    # two or more detections close together: certainly a burst
    if len(detected_event) > 1:
        return "burst"
    # only one detection: look at the wobble after it
    wobble = wobble_after(signal_uV, time_ms, detected_event[0])
    if wobble >= cutoff_uV:
        return "burst"
    else:
        return "single"

def true_type(detected_event, true_events, tolerance_ms=1.0):
    detection_time = detected_event[0]
    for true_event in true_events:
        if detection_time >= true_event[0] - tolerance_ms and detection_time <= true_event[-1] + tolerance_ms:
            if len(true_event) > 1:
                return "burst"
            else:
                return "single"
    # no true event here: it was a false alarm
    return "none"