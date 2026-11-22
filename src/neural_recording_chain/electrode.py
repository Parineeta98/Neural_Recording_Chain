"""Voltage at an electrode outside the pyramidal cell."""

# Sources and choices for the values in this file:
# - point-source approximation: Ness et al. (2022)
# - 0.3 S/m: a common modelling value, as in the LFPy examples (Linden et al., 2014)
# - coupling 2.1 mS/cm2: the soma-dendrite coupling of Pinsky & Rinzel (1994)
# - distances (50 and 200 um) and membrane area: assumed

import numpy as np

def extracellular_potential(
    v_soma_mV,
    v_dend_mV,
    soma_distance_um=50.0,
    dend_distance_um=200.0,
    conductivity_S_per_m=0.3,
    membrane_area_cm2=5e-4,
    coupling_mS_per_cm2=2.1,
):
    current_uA = coupling_mS_per_cm2 * (v_dend_mV - v_soma_mV) * membrane_area_cm2
    current_A = current_uA * 1e-6

    soma_distance_m = soma_distance_um * 1e-6
    dend_distance_m = dend_distance_um * 1e-6

    spread = 1.0 / (4.0 * np.pi * conductivity_S_per_m)
    potential_V = current_A * spread * (1.0 / soma_distance_m - 1.0 / dend_distance_m)

    return potential_V * 1e6