"""Tests for the frozen noise generator."""

import numpy as np

from neural_recording_chain.frozen_noise import make_frozen_noise, make_hidden_state


def test_output_length_matches_duration():
    input_theory, hidden_state = make_frozen_noise(duration_ms=1000, dt_ms=0.05)
    assert len(input_theory) == 20_000
    assert len(hidden_state) == 20_000


def test_hidden_state_is_only_zeros_and_ones():
    _, hidden_state = make_frozen_noise(duration_ms=1000, dt_ms=0.05)
    assert set(np.unique(hidden_state)) <= {0, 1}


def test_same_seed_gives_same_noise():
    first, _ = make_frozen_noise(duration_ms=1000, dt_ms=0.05, seed=7)
    second, _ = make_frozen_noise(duration_ms=1000, dt_ms=0.05, seed=7)
    assert np.array_equal(first, second)


def test_different_seed_gives_different_noise():
    first, _ = make_frozen_noise(duration_ms=1000, dt_ms=0.05, seed=7)
    second, _ = make_frozen_noise(duration_ms=1000, dt_ms=0.05, seed=8)
    assert not np.array_equal(first, second)


def test_hidden_state_is_on_about_a_third_of_the_time():
    rng = np.random.default_rng(0)
    hidden_state = make_hidden_state(
        n_steps=2_000_000, dt_ms=0.05, tau_ms=50.0, off_on_ratio=2.0, rng=rng
    )
    assert abs(hidden_state.mean() - 1 / 3) < 0.05


def test_input_is_higher_when_hidden_state_is_on():
    input_theory, hidden_state = make_frozen_noise(duration_ms=20_000, dt_ms=0.05)
    mean_on = input_theory[hidden_state == 1].mean()
    mean_off = input_theory[hidden_state == 0].mean()
    assert mean_on > mean_off