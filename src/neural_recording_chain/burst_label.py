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

def match_true_events(true_event_times, detected_events, tolerance_ms=1.0):
    # for each true event, the position of the detected event that caught it,
    # or -1 if no detected event caught it (a miss)
    matches = []
    for true_time in true_event_times:
        found_index = -1
        for k in range(len(detected_events)):
            for detection_time in detected_events[k]:
                if abs(detection_time - true_time) <= tolerance_ms:
                    found_index = k
        matches.append(found_index)
    return matches

def count_unmatched(detected_events, matches):
    # detected events that did not catch any true event: false positives
    unmatched = 0
    for k in range(len(detected_events)):
        if k not in matches:
            unmatched = unmatched + 1
    return unmatched