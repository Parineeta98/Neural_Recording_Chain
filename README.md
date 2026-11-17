# Neural Recording Chain

Simulating the path from neuron to bits: how electrode, amplifier, ADC and
on-chip spike detection choices affect what a brain-computer interface can read.

**Status:** work in progress (Phase 2 done, Phase 3 next).

## What this project does

A brain-computer interface never sees a neuron directly. Between the cell and
the data sits a chain of hardware, and every stage loses something:

```
neuron -> electrode -> amplifier -> filter -> ADC -> spike detection -> data link
```

This project models each stage in Python and measures how its settings change
one concrete outcome: can the spikes still be detected?

## Roadmap
| 0 | Project setup | done |
| 1 | Spike source: input, neuron, true spike times, electrode signal | done |
| 2 | Recording chain: noise, filter, digitiser, spike detector, scoring | done |
| 3 | Data rate and power budget at 100, 1,000 and 10,000 channels | planned |
| 4 | Spike detection with whole-number arithmetic, as on a chip | planned |
| 5 | Validation on real recordings | planned |
| 6 | Write-up | planned |

## Spike source

The ground-truth spikes come from my hippocampal microcircuit model
(a Pinsky-Rinzel pyramidal cell and a Wang-Buzsaki interneuron):
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

- **H1.** Detection gets worse as bit depth falls, with a minimum bit depth below which it breaks down. *Status: to be retested with a fixed threshold. The earlier "7 to 8 bits" result is withdrawn, because the threshold was computed from the digitised signal and collapsed with it.*
- **H2.** Sending only detected spikes reduces the data rate by about three orders of magnitude. *Status: supported in this simulation (about 1,163 times smaller), but it depends on the firing rate and on an assumed 32 bits per spike.*
- **H3.** Bursts leave a longer-lasting signal after the first detection (the "wobble") than single spikes do, because of the dendritic calcium spike. *Status: the difference is there (median 26 uV versus 16 uV on recording A), but the link to the calcium spike is untested. The wobble also includes filter ringing.*
- **Question 3, outcome so far.** On recording B (same input level) the burst label reaches a balanced accuracy of 91.7%. On recording C (much higher firing rate) it drops to 79.9%: bursts are all labelled correctly, but only 405 of 677 single spikes are. A likely cause is pairs of fast single spikes (doublets) that the chip groups together; this has not been tested yet.

## Methods

**Neuron model.** A two-compartment Pinsky-Rinzel pyramidal cell (soma and dendrite), simulated in Brian2 (Euler method, 0.05 ms step). The calcium gate constants (53.3) follow Zeldenrust and Wadman (2013), Appendix A.1. Interneurons are not included.

**Input.** Frozen noise following Zeldenrust et al. (2017): a hidden on/off state (time constant 50 ms) driving 1,000 artificial input neurons, filtered with a 5 ms kernel. The input is regenerated with fixed seeds, not loaded from the thesis files. Settings: scale 20, baseline -0.4 (units to be confirmed).

**Recordings** (60 s each).
- **A** (seed 0): used to choose all chip settings (tuning). Detection results are therefore measured on the same recording.
- **B** (seed 1, same input level): a test recording for the burst label, never used for tuning.
- **C** (seed 2, baseline 3.0): a test recording with a much higher firing rate.

**Answer keys.**
- *Spike level:* every somatic spike, found with a peak finder (above -40 mV, prominence 5 mV). Used to score detection. The count depends on these settings (prominence 2, 5, 10 and 20 mV give 572, 543, 517 and 449 spikes on the earlier run); the tall spikes are stable.
- *Event level:* the burst rule from Zeldenrust and Wadman (2013), section 2.4. Each somatic spike crossing 0 mV starts one event. It is a burst if the dendrite reaches -11 mV within 2 to 9 ms afterwards; otherwise it is a single spike. The code reads -11 mV as a level, not as an upward crossing.
- *Gap rule (what the chip can do on its own):* spikes less than 10 ms apart belong to one event, since the chip cannot see the dendrite.

**Recording chain.**
1. Extracellular potential at the electrode: a two-point-source approximation (soma 50 um, dendrite 200 um away, tissue conductivity 0.3 S/m).
2. Noise: thermal noise (1 MOhm, 310 K, about 13 uV rms), background activity (10 uV rms, 300 to 3000 Hz) and a slow wave (8 Hz, 1000 uV).
3. Band-pass filter: Butterworth, order 2, 300 to 3000 Hz.
4. Digitiser: chosen bit depth and input range, with clipping.
5. Detector: a negative threshold at a multiple of the noise level (median-based estimate), with a dead time between detections.

**Scoring.**
- Detection: each true spike is matched to at most one detection (within 1 ms). Hits, misses and false alarms are reported.
- Burst label: each true event is counted once, with misses and false alarms reported. Balanced accuracy is used, because the recordings contain unequal numbers of bursts and single spikes.

**Data budget.** Raw rate = electrodes x sampling rate x bits. Spike rate = electrodes x spikes per second x 32 bits. The spike rate comes from the detections in recording A (about 4.3 per second) and assumes every electrode sits next to a neuron like it. Both are compared with Neuralink's published figures (about 200 Mbps produced, about 1 Mbps wireless). The extra bit for the burst label and the chip's computing cost are not included.

**Assumptions without a source yet:** the noise levels, the electrode resistance, the slow-wave size, the membrane area, the electrode distances, the tissue conductivity, the 20 kHz sampling rate, the input units, the 32 bits per spike, and the chip settings chosen on recording A (4.5 times the noise, 3 ms dead time, 8 bits, +-500 uV). Spike counts can also differ slightly between computers.

## What this project does not model

An amplifier, a real electrode's impedance, a surface (ECoG) electrode, more than one neuron, real recorded data, a fixed-point implementation, a power budget, or any specific company's device.

## References

- Pinsky, P. F., & Rinzel, J. (1994). Intrinsic and network rhythmogenesis in a reduced Traub model for CA3 neurons. *Journal of Computational Neuroscience*, 1, 39-60.
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
