"""Tests for grouping spikes into single spikes and bursts."""

from neural_recording_chain.events import (
    count_detections_per_event,
    group_into_events,
    split_singles_and_bursts,
)

def test_close_spikes_form_one_burst():
    events = group_into_events([100, 103, 106])
    assert events == [[100, 103, 106]]

def test_far_apart_spikes_are_separate_events():
    events = group_into_events([100, 200, 300])
    assert len(events) == 3

def test_last_event_is_not_lost():
    events = group_into_events([100, 103, 500])
    assert events == [[100, 103], [500]]

def test_no_spikes_gives_no_events():
    events = group_into_events([])
    assert events == []

def test_split_singles_and_bursts():
    events = [[100], [200, 203, 206], [500]]
    single_spikes, bursts = split_singles_and_bursts(events)
    assert len(single_spikes) == 2
    assert len(bursts) == 1

def test_count_detections_per_event():
    events = [[100], [200, 203, 206]]
    detected_times = [100.2, 200.1, 206.3, 900.0]
    counts = count_detections_per_event(events, detected_times)
    assert counts == [1, 2]