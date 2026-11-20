"""Compare detected spikes with the true spikes."""
# hits + misses always equals the number of true spikes, and hits + false alarms always equals the number of detections.

def score_detection(true_times_ms, detected_times_ms, tolerance_ms=1.0):
    used = []
    for detected_time in detected_times_ms:
        used.append(False)
    hits = 0
    for true_time in true_times_ms:
        best_index = -1
        best_distance = tolerance_ms
        for j in range(len(detected_times_ms)):
            distance = abs(detected_times_ms[j] - true_time)
            if not used[j] and distance <= best_distance:
                best_index = j
                best_distance = distance

        if best_index != -1:
            used[best_index] = True
            hits = hits + 1 
    missed = len(true_times_ms) - hits
    false_positives = len(detected_times_ms) - hits
    return hits, missed, false_positives