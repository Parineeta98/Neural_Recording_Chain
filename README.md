# Neural Recording Chain

Simulating the path from neuron to bits: how electrode, amplifier, ADC and
on-chip spike detection choices affect what a brain-computer interface can read.

**Status:** work in progress (Phase 0, project setup).

## What this project does

A brain-computer interface never sees a neuron directly. Between the cell and
the data sits a chain of hardware, and every stage loses something:

```
neuron -> electrode -> amplifier -> filter -> ADC -> spike detection -> data link
```

This project models each stage in Python and measures how its settings change
one concrete outcome: can the spikes still be detected?

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| 0 | Project setup | in progress |
| 1 | Spike source with known spike times, baseline detector and scoring | planned |
| 2 | Recording chain: electrode noise, amplifier, filters, ADC | planned |
| 3 | Parameter sweeps: signal-to-noise ratio and detection accuracy | planned |
| 4 | Fixed-point spike detection | planned |
| 5 | Data rate and power budget at 100, 1,000 and 10,000 channels | planned |
| 6 | Validation on real recordings, write-up | planned |

## Spike source

The ground-truth spikes come from my hippocampal microcircuit model
(a Pinsky-Rinzel pyramidal cell and a Wang-Buzsaki interneuron):
<https://github.com/Parineeta98/Hippocampal-Microcircuit-Model-of-Pyramidal-Cell-and-Interneuron>

The model is driven by the frozen noise protocol of Zeldenrust et al. (2017),
*Estimating the Information Extracted by a Single Spiking Neuron from a
Continuous Input Time Series*, Frontiers in Computational Neuroscience 11:49.
<https://doi.org/10.3389/fncom.2017.00049>

## Git conventions

- Small commits, one change each.
- One branch per phase (`phase-0-setup`, `phase-1-spike-source`, ...), merged into `main` when the phase is done.
- A tag at the end of each phase (`v0.1-recording-chain`, ...).
