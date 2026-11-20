# Neural Recording Chain

Simulating the path from neuron to bits: how electrode noise, filtering, ADC and
on-chip spike detection choices affect what a brain-computer interface can read.

**Status:** work in progress. The spike source, recording chain, data-rate calculation and burst label are done. Whole-number arithmetic, a power budget and real recordings are still to do.

## What this project does

A brain-computer interface never sees a neuron directly. Between the cell and
the data sits a chain of hardware, and every stage loses something:

```
neuron -> electrode -> (amplifier, not modelled separately) -> filter -> ADC -> spike detection -> data link
```

This project models each stage in Python and measures how its settings change
one concrete outcome: can the spikes still be detected?

## Roadmap

| Phase | What | Status |
|---|---|---|
| 0 | Project setup | done |
| 1 | Spike source: input, neuron, true spike times, electrode signal | done |
| 2 | Recording chain: noise, filter, digitiser, spike detector, scoring | done |
| 3 | Data rate at 100, 1,000 and 10,000 channels | done |
| 3b | Power budget | planned |
| 3c | Burst or single-spike label from the chip's own detections | done |
| 4 | Spike detection with whole-number arithmetic, as on a chip | planned |
| 5 | Validation on real recordings | planned |
| 6 | Write-up | planned |

## Spike source

The ground-truth spikes come from my hippocampal microcircuit model
(a Pinsky-Rinzel pyramidal cell and a Wang-Buzsaki interneuron). Only the pyramidal cell is used in this project:
<https://github.com/Parineeta98/Hippocampal-Microcircuit-Model-of-Pyramidal-Cell-and-Interneuron>

The model is driven by the frozen noise protocol of Zeldenrust et al. (2017),
*Estimating the Information Extracted by a Single Spiking Neuron from a
Continuous Input Time Series*, Frontiers in Computational Neuroscience 11:49.
<https://doi.org/10.3389/fncom.2017.00049>

## Research questions

The questions below were refined during the work, not fixed in advance.

1. **Detection.** How do the choices in a recording chain (filtering, bit depth, input range, detection threshold and dead time) affect whether spikes from a single simulated neuron can still be detected? The electrode noise level was kept fixed.
2. **Data budget.** How much less data does a chip need to send if it detects spikes on the chip instead of sending the raw signal, and how many electrodes would then fit through a wireless link of about 1 Mbps?
3. **Bursts versus single spikes.** Can a chip that only sees the extracellular signal tell bursts from single spikes, and does this still work on a recording with a new input and on one with a much higher firing rate?

## Expectations and status

- **H1.** Detection gets worse as bit depth falls, with a minimum bit depth below which it breaks down. *Status: retested with the threshold fixed before the digitiser (notebook 03). Every tall spike was found from 6 bits upwards (±1000 µV range). False alarms do not fall steadily with more bits (4 bits: 142, 5: 0 with 3 tall spikes missed, 6: 1, 7: 18, 8: 5, 10: 2), because rounding to the digitiser's steps moves the effective threshold by up to half a step. A design should check the threshold against the step size, not only choose enough bits. The earlier "7 to 8 bits" result is withdrawn: the threshold was then measured on the digitised signal and collapsed with it. These runs use the signal before the filter and without the slow wave, so they test the digitiser alone.*
- **H2.** Sending only detected spikes reduces the data rate by about three orders of magnitude. *Status: supported in this simulation (about 1,163 times smaller), but it depends on the firing rate and on an assumed 32 bits per spike.*
- **H3.** Bursts leave a longer-lasting signal after the first detection (the "wobble") than single spikes do, because of the dendritic calcium spike. *Status: supported by a control (see below). The difference is there (median 26 uV versus 16 uV on recording A) and it needs the calcium current, but the control cannot separate the dendritic current itself from the extra spikes it causes.*
- **Question 3, outcome.** On recording B (same input level) the burst label reaches a balanced accuracy of 91.7% (only 26 single spikes, so this number is uncertain). On recording C (about four times more spikes) it drops to 79.9%: all 414 caught bursts are labelled correctly, but only 405 of 677 caught single spikes are (683 true singles; 6 were never detected). Of the 272 wrong singles, 257 sat in a group of two or more detections, and in 253 of these the group also held another true event; only 15 were wrong because of the wobble cut-off. The rule "two or more detections = burst" therefore only works when events are well spaced. This is a limitation of the method and is not fixed here.

## Detection results

All chip settings (4.5 times the noise, 3 ms dead time, 8 bits, ±500 µV) were chosen on recording A and then run unchanged on B and C (notebook 03). Spike-level key, ±1 ms.

| | A (tuning) | B (test) | C (test, stronger input) |
|---|---|---|---|
| Tall spikes found | 209 / 211 (99.1%) | 164 / 164 (100%) | 1,090 / 1,099 (99.2%) |
| Small spikes found | 43 / 331 (13%) | 38 / 291 (13%) | 250 / 964 (26%) |
| False alarms in 60 s | 6 | 4 | 11 |

The small spikes inside bursts are mostly missed on all three recordings. Two settings cause this: the threshold (they are smaller than it) and the 3 ms dead time (on recording A, 1 ms finds 76 small spikes but with 169 false alarms; 3 ms finds 46 with 6). B and C use a new input and new noise, but the same neuron, electrode model and noise model.

## Control: calcium switched off

As a control, recording A's input was simulated with the dendritic calcium conductance set to zero. This produced no bursts (466 single spikes). The wobble after detection, for the 463 events the chip saw as one detection, had a median of 15.9 uV. That matches normal single spikes (16.2 uV) and sits above the noise floor (11.3 uV), which reflects the spike tail and filter ringing that every spike has. Only bursts with the calcium current on reached the higher level (25.8 uV), and 8 of the 463 calcium-off events (1.7%) crossed the burst cut-off. The burst wobble therefore depends on the calcium current, though this control cannot separate the dendritic current itself from the extra small spikes it causes.

| Situation | Typical wobble |
|---|---|
| Noise only (no spike) | 11.3 uV |
| Single spike, calcium off | 15.9 uV |
| Single spike, normal neuron | 16.2 uV |
| Burst, normal neuron | 25.8 uV |

## Step-size check

The first 10 s of recording A's input were simulated with the 0.05 ms step used everywhere and with a 0.025 ms step (same input, each value repeated twice; notebook 02).

| | 0.05 ms | 0.025 ms |
|---|---|---|
| Spikes | 97 | 96 |
| Events | 37 | 35 |
| Bursts | 29 | 28 |
| Single spikes | 8 | 7 |
| First event times (ms) | 65.45, 339.50, 508.25, 544.95, 882.25 | 65.38, 339.42, 508.18, 544.83, 882.12 |

Event times shifted by about 0.1 ms (0.07 to 0.13 ms), well within the 1 ms scoring tolerance. The counts differ by 1 spike and 2 events (the share of bursts is 78% against 80%). The 0.05 ms step was kept. Exact counts can shift by a few percent with the step size, so they are not converged, which fits the note that counts also differ slightly between computers. The check covers the neuron simulation only, over 10 s; the chain results were not re-run with the smaller step.

## Methods

**Neuron model.** A two-compartment Pinsky-Rinzel pyramidal cell (soma and dendrite), simulated in Brian2 (Euler method, 0.05 ms step). The calcium gate constants (53.3) follow Zeldenrust and Wadman (2013), Appendix A.1. Interneurons are not included.

**Input.** Frozen noise following Zeldenrust et al. (2017): a hidden on/off state (time constant 50 ms) driving 1,000 artificial input neurons, filtered with a 5 ms kernel. The input is regenerated with fixed seeds, not loaded from the thesis files. Settings: scale 20, baseline -0.4 (units to be confirmed).

**Recordings** (60 s each).
- **A** (seed 0): used to choose all chip settings (tuning) and the burst-label cut-off. Its results are in-sample.
- **B** (seed 1, same input level): a test recording, never used for tuning.
- **C** (seed 2, baseline 3.0): a test recording with a much higher firing rate (2,063 spikes in 60 s, against 542 on A).

**Answer keys.**
- *Spike level:* every somatic spike, found with a peak finder (above -40 mV, prominence 5 mV). Used to score detection. The count depends on these settings (prominence 2, 5, 10 and 20 mV gave 572, 543, 517 and 449 spikes before the calcium constant was changed to 53.3; with 5 mV the count is now 542); the tall spikes are stable.
- *Event level:* the burst rule from Zeldenrust and Wadman (2013), section 2.4. Each somatic spike crossing 0 mV starts one event. It is a burst if the dendrite reaches -11 mV within 2 to 9 ms afterwards; otherwise it is a single spike. The code tests the highest dendrite voltage in that window, not an upward crossing. On recording A, 30 of the 211 events already had the dendrite above -11 mV when the window opened (their calcium spike started within 2 ms), so a strict crossing rule would call up to 30 bursts singles. In none of the 211 was the dendrite already above -11 mV at the somatic spike itself.
- *Gap rule (what the chip can do on its own):* spikes less than 10 ms apart belong to one event, since the chip cannot see the dendrite.

**Recording chain.**
1. Extracellular potential at the electrode: a two-point-source approximation (soma 50 um, dendrite 200 um away, tissue conductivity 0.3 S/m).
2. Noise: thermal noise (1 MOhm, 310 K, about 13 uV rms), background activity (10 uV rms, 300 to 3000 Hz) and a slow wave (8 Hz, 1000 uV).
3. Band-pass filter: Butterworth, order 2, 300 to 3000 Hz.
4. Digitiser: chosen bit depth and input range, with clipping.
5. Detector: a negative threshold at a multiple of the noise level (median-based estimate), with a dead time between detections.

**Thermal noise.** Electrode thermal noise is modelled as Johnson-Nyquist noise, sqrt(4kTRB) (Johnson, 1928; Nyquist, 1928), with T = 310 K, R = 1 MOhm and B = 10 kHz (half the sampling rate), giving 13.1 uV rms. It is generated as white noise over that whole band, and the 300 to 3000 Hz filter then keeps only part of it. The 1 MOhm is an assumed order of magnitude, not a measured value. In real electrodes only the resistive (real) part of the impedance produces thermal noise (Obien et al., 2015), so treating the full 1 MOhm as a resistor probably overestimates this noise.

**Background activity.** Activity from distant neurons is modelled as band-limited noise (300 to 3000 Hz) of 10 uV rms. This value is assumed, not sourced; how the total noise splits between thermal noise and background activity is a choice made here. After band-pass filtering, the total noise in the simulated recording is about 12 uV (the detector's estimate is 52.1 uV / 4.5 = 11.6 uV). For comparison, noise measured per channel in tetrode recordings from visual cortex had a mean of 21 uV rms (range 12 to 35 uV; Mechler & Victor, 2012), so this simulation is at the quiet end. The spikes are large by comparison: the tall spikes reach about 283 uV at the electrode (179 uV after filtering) at the assumed 50 um distance, against a measured mean of 91 uV (range 25 to 313 uV) in the same data. The filter band of those recordings was not checked, so the noise comparison is approximate. Real recordings are often noisier, with smaller spikes, so the detection results here are on the optimistic side. Mains interference (50 Hz) is not modelled.

**Scoring.**
- Detection: each true spike is matched to at most one detection (within 1 ms). Hits, misses and false alarms (detections matching no true spike) are reported. Tall spikes are those that reach above 0 mV in the cell body; small spikes are the rest (mostly later spikes inside a burst).
- Burst label: each true event is counted once, with misses and false alarms reported. Here a false alarm is a detected group of detections that matches no true event, which is a different count from the detection false alarms above. Balanced accuracy is used, because the recordings contain unequal numbers of bursts and single spikes.

**Data budget.** Raw rate = electrodes x sampling rate x bits. Spike rate = electrodes x spikes per second x 32 bits. The spike rate comes from the detections in recording A (about 4.3 per second) and assumes every electrode sits next to a neuron like it. Both are compared with Neuralink's published figures (about 200 Mbps produced, about 1 Mbps wireless). The extra bit for the burst label and the chip's computing cost are not included.

**Assumptions without a source yet:** the background-noise size, the electrode resistance (1 MOhm), the slow-wave size, the membrane area, the electrode distances, the tissue conductivity, the 20 kHz sampling rate, the input units, the 32 bits per spike, and the chip settings chosen on recording A (4.5 times the noise, 3 ms dead time, 8 bits, +-500 uV). Spike counts can also differ slightly between computers.

## What this project does not model

An amplifier, a real electrode's impedance, a surface (ECoG) electrode, more than one neuron, real recorded data, a fixed-point implementation, a power budget, or any specific company's device.

## References

- Pinsky, P. F., & Rinzel, J. (1994). Intrinsic and network rhythmogenesis in a reduced Traub model for CA3 neurons. *Journal of Computational Neuroscience*, 1, 39-60.
- Mechler, F., & Victor, J. D. (2012). Dipole characterization of single neurons from their extracellular action potentials. *Journal of Computational Neuroscience*, 32(1), 73-100. <https://doi.org/10.1007/s10827-011-0341-0>
- Johnson, J. B. (1928). Thermal agitation of electricity in conductors. *Physical Review*, 32(1), 97-109. <https://doi.org/10.1103/PhysRev.32.97>
- Nyquist, H. (1928). Thermal agitation of electric charge in conductors. *Physical Review*, 32(1), 110-113. <https://doi.org/10.1103/PhysRev.32.110>
- Obien, M. E. J., Deligkaris, K., Bullmann, T., Bakkum, D. J., & Frey, U. (2015). Revealing neuronal function through microelectrode array recordings. *Frontiers in Neuroscience*, 8, 423. <https://doi.org/10.3389/fnins.2014.00423>
- Zeldenrust, F., & Wadman, W. J. (2013). Modulation of spike and burst rate in a minimal neuronal circuit with feed-forward inhibition. *Neural Networks*, 40, 1-17.
- Zeldenrust, F., de Knecht, S., Wadman, W. J., Deneve, S., & Gutkin, B. (2017). Estimating the information extracted by a single spiking neuron from a continuous input time series. *Frontiers in Computational Neuroscience*, 11, 49.
- Neuralink compression challenge: <https://content.neuralink.com/compression-challenge/README.html>

## Setup

Requires Python 3.10 or newer.

```
python -m venv .venv
.venv\Scripts\activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
