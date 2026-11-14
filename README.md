# Neural Recording Chain

Simulating the path from neuron to bits: how electrode, amplifier, ADC and
on-chip spike detection choices affect what a brain-computer interface can read.

**Status:** work in progress (Phase 0 done, Phase 1 next).

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

## Setup

Requires Python 3.10 or newer.

```
python -m venv .venv
.venv\Scripts\activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
