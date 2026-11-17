from brian2 import *
import matplotlib.pyplot as plt
import scipy.io as mat
import numpy as np

#parameters
pyr_parameters = {
"gLs" : 0.1*mS,
"gLd" : 0.1*mS,
"gNa" : 30.*mS,
"gKdr" : 15.*mS,
"gCa" : 10.*mS,
"gKahp" : 0.8*mS,
"gKC" : 15.*mS,
"VNa" : 60.0*mV,
"VCa" : 80.0*mV,
"VK" : -75.0*mV,
"VL" : -60.0*mV,
"Cm" : 3.0*uF,
"gc" : 2.1*mS,
# "gc" : 2.1mS, #for fig. 7: 3.0*mS, normal: 2.1*mS
"pp" : 0.5,
"alphac": 2.0/ms,
"betac" : 0.1/ms,
"betaqd": 0.001/ms, 
}

pyr_initialvalues = {
    'Vs' : -62.89223689*mV,
    'Vd' : -62.98248752*mV,
    'Cad' :0.21664282,
    'hs' : 0.99806345,
    'ns' :0.00068604,
    'sd' : 0.01086703,
    'cd' :0.00809387,
    'qd' : 0.0811213,
}

#equations for the neuron model using the orignal Pinsky and Rinzel equations and parameter values
eqs_pyr = '''
#membrane potential equations
#for soma
dVs/dt=(-ILs-INa-IK_DR+(gc/pp)*(Vd-Vs)+(Is/pp)-Isyns)/Cm: volt

#for dendrite
dVd/dt=(-ILd-ICad-IK_ahp-IK_C+((gc/(1.0-pp))*(Vs-Vd))+Id_FN/(1.0-pp)-Isynd)/Cm: volt  #-Isynd/(1.0-pp)


ILs   = gLs*(Vs-VL) : amp
INa   = gNa*Minfs*Minfs*hs*(Vs-VNa) :amp
IK_DR = gKdr*ns*(Vs-VK) :amp


ILd    = gLd*(Vd-VL) :amp
ICad   = gCa*sd*sd*(Vd-VCa) :amp
IK_ahp = gKahp*qd*(Vd-VK) :amp
IK_C   = gKC*cd*chid*(Vd-VK) :amp

#calcium concentration
dCad/dt=  (-0.13*ICad/uA-0.075*Cad)/ms: 1

# soma dynamics 
dhs/dt= alphahs-(alphahs+betahs)*hs: 1 
dns/dt= alphans-(alphans+betans)*ns: 1

# dendrite dynamics
dcd/dt= alphacd-(alphacd+betacd)*cd: 1 
dqd/dt= alphaqd-(alphaqd+betaqd)*qd: 1

# calcium dynamics
dsd/dt= alphasd-(alphasd+betasd)*sd: 1

# soma state

# sodium current
alphams=  0.32*(-46.9-Vs/mV)/(exp((-46.9-Vs/mV)/4.0)-1.0)/ms: Hz
betams=  0.28*(Vs/mV+19.9)/(exp((Vs/mV+19.9)/5.0)-1.0)/ms: Hz #orignal one
# betams=  0.28*(Vs/mV+70)/(exp((Vs/mV+70)/5.0)-1.0)/ms: Hz

Minfs=    alphams/(alphams+betams): 1 


alphahs=  0.128*exp((-43.0-Vs/mV)/18.0)/ms: Hz
betahs=   4.0/(1.0+exp((-20.0-Vs/mV)/5.0))/ms: Hz


# Kdr potassium current
alphans=  0.016*(-24.9-Vs/mV)/(exp((-24.9-Vs/mV)/5.0)-1.0)/ms: Hz
betans=   0.25*exp(-1.0-0.025*Vs/mV)/ms: Hz

# dendrite state


# calcium induced potassium current
alphacd=((int(Vd/mV<=-10)*exp(((Vd/mV+50.0)/11) - (Vd/mV + 53.3) / 27))/18.975 + (int(Vd/mV>-10)*2.0*exp((-53.3-Vd/mV)/27.0)))/ms : Hz
betacd=(int(Vd/mV<=-10)*(2.0*exp((-53.3-Vd/mV)/27.0)-alphacd*ms))/ms : Hz

# AHP: calcium induced potassium current
alphaqd=  clip(0.00002*Cad,0.00002*Cad, 0.01)/ms: Hz
betaqd = 0.001/ms: Hz
chid= clip(Cad/250.,Cad/250. , 1. ) : 1 

# calcium current
alphasd=  (1.6/(1.0+exp(-0.072*(Vd/mV-5.0))))/ms: Hz
betasd=   (0.02*(Vd/mV+8.9)/(exp((Vd/mV+8.9)/5.0)-1.0))/ms: Hz
# betasd= (0.02*(Vd/mV+13)/(exp((Vd/mV+13)/5.0)-1.0))/ms: Hz

Id_FN = input_current(t) :amp #input current to the dendrite
# Is_FN = Iapp(t) :amp #input current to the soma : uncomment this for somatic input and change Is to Is_FN in the soma equation and Id_FN to Id in the dendrite equation
Is : amp
Id : amp
Isyns : amp
Isynd : amp
'''
def simulate_pyramidal_cell(input_theory, dt_ms, scale_uA=20.0, baseline_uA=-0.4, calcium_mS=10.0):
    dt = dt_ms * ms
    duration = len(input_theory) * dt

    input_current = TimedArray((scale_uA * input_theory + baseline_uA) * uA, dt=dt)
    
    # namespace = dict(pyr_parameters, input_current=input_current)

    # calcium_mS sets the dendritic calcium conductance (10 mS is the normal value, 0 switches it off)
    namespace = dict(pyr_parameters, input_current=input_current, gCa=calcium_mS * mS)

    cell = NeuronGroup(1, model=eqs_pyr, threshold='Minfs > 0.5', refractory=2 * ms,
                       dt=dt, method='euler', namespace=namespace)
    cell.set_states(pyr_initialvalues)

    state = StateMonitor(cell, ['Vs', 'Vd', 'Id_FN'], record=True)
    spikes = SpikeMonitor(cell)
    run(duration)

    return {
        "time_ms": np.asarray(state.t / ms),
        "v_soma_mV": np.asarray(state.Vs[0] / mV),
        "v_dend_mV": np.asarray(state.Vd[0] / mV),
        "input_uA": np.asarray(state.Id_FN[0] / uA),
        "spike_times_ms": np.asarray(spikes.t / ms),
    }