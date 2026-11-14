"""Compare detected spikes with the true spikes."""

def score_detection(true_times_ms, detected_times_ms, tolerance_ms=1.0):
    # count the true spikes that the detector found
    hits = 0
    for true_time in true_times_ms:
        was_found = False
        for detected_time in detected_times_ms:
            if abs(detected_time - true_time) <= tolerance_ms:
                was_found = True
        if was_found:
            hits = hits + 1

    # the true spikes that were not found
    misses = len(true_times_ms) - hits

    # count the detections that do not belong to any true spike
    false_alarms = 0
    for detected_time in detected_times_ms:
        is_real = False
        for true_time in true_times_ms:
            if abs(detected_time - true_time) <= tolerance_ms:
                is_real = True
        if not is_real:
            false_alarms = false_alarms + 1

    return hits, misses, false_alarms