"""Frozen noise input current protocol (Zeldenrust et al., 2017)"""
import numpy as np

def make_hidden_state(n_steps, dt_ms, tau_ms, off_on_ratio, rng):
    """Generate a hidden state for frozen noise input current protocol.

    Parameters
    ----------
    n_steps : int
        Number of time steps.
    dt_ms : float
        Time step size in milliseconds.
    tau_ms : float
        Time constant of the hidden state in milliseconds.
    off_on_ratio : float
        Ratio of off to on states.
    rng : np.random.Generator
        Random number generator for reproducibility.

    Returns
    -------
    hidden_state : np.ndarray
        Array of shape (n_steps,) with the hidden state values (0 or 1).
    """
    r_on = 1.0 / (tau_ms *(1.0 + off_on_ratio)) 
    r_off = r_on * off_on_ratio 
    draws = rng.random(n_steps)
    x = np.zeros(n_steps, dtype=np.int8)
    x[0] = draws[0] < r_on / (r_on + r_off)
    for n in range(1,n_steps): 
        if x[n-1] == 0:
            if draws[n] < r_on * dt_ms:
                x[n] = 1
            else:
                x[n] = 0
        else:
            if draws[n] < r_off * dt_ms:
                x[n] = 0
            else:
                x[n] = 1
    return x 

def make_frozen_noise(
        duration_ms,
        dt_ms,
        tau_ms = 50.0,
        off_on_ratio = 2.0,
        mean_rate_hz = 0.5,
        n_neurons = 1000,
        kernel_tau_ms = 5.0,
        seed = 0,
):
    """Generate frozen noise input current protocol.

    Parameters
    ----------
    duration_ms : float
        Total duration of the simulation in milliseconds.
    dt_ms : float
        Time step size in milliseconds.
    tau_ms : float, optional
        Time constant of the hidden state in milliseconds (default is 50.0).
    off_on_ratio : float, optional
        Ratio of off to on states (default is 2.0).
    mean_rate_hz : float, optional
        Mean firing rate in Hz (default is 0.5).
    n_neurons : int, optional
        Number of neurons (default is 1000).
    kernel_tau_ms : float, optional
        Time constant of the kernel in milliseconds (default is 5.0).
    seed : int, optional
        Random seed for reproducibility (default is 0).

        Returns
    -------
    input_theory : np.ndarray
        Array of shape (n_steps,) with the unscaled input current.
    hidden_state : np.ndarray
        Array of shape (n_steps,) with the hidden state values (0 or 1).
    """
    rng = np.random.default_rng(seed)
    n_steps = int(round(duration_ms / dt_ms))
    hidden_state = make_hidden_state(n_steps, dt_ms, tau_ms, off_on_ratio, rng)
    is_on = hidden_state == 1
    mean_rate = mean_rate_hz / 1000.0
    std_rate = np.sqrt(1.0 / 8.0 ) * mean_rate 
    q_on = np.abs(rng.normal(mean_rate, std_rate, n_neurons))
    q_off = np.abs(rng.normal(mean_rate, std_rate, n_neurons))
    weights = np.log(q_on / q_off)
    summed = np.zeros(n_steps) 
    for q1, q0, w in zip(q_on, q_off, weights): 
        p_spike = np.where(is_on, q1, q0) * dt_ms 
        summed = summed + w * (rng.random(n_steps) < p_spike) 
    t_kernel = np.arange(0.0, 5.0 * kernel_tau_ms + dt_ms, dt_ms)
    ratio = t_kernel / kernel_tau_ms
    kernel =np.exp(-ratio)
    area = kernel.sum() * dt_ms 
    kernel = kernel / area 
    input_theory = np.convolve(summed, kernel)[:n_steps]

    return input_theory, hidden_state 
