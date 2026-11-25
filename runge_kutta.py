# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def ode_system(t, u, constants):
    """
    system of first order differential equations
    t: discrete time step value
    y: state vector (vetor das variaveis/populacoes do modelo)
    """
    r1 = constants[0]
    r2 = constants[1]
    w11 = constants[2]
    w12 = constants[3]
    w22 = constants[4]
    w21 = constants[5]

    N1 = u[0]
    N2 = u[1]
    
    dN1dt = r1*N1*(1 - w11*N1 - w21*N2) 
    dN2dt = r2*N2*(1 - w22*N2 - w12*N1) 
    
    return np.array([dN1dt, dN2dt])

def rk4(f, tk, _uk, _dt=0.01, **kwargs):
    """
    single-step fourth-order numerical integration (RK4) method
    f: system of first order ODEs
    tk: current time step
    _uk: current state vector [y1, y2, y3, ...]
    _dt: discrete time step size
    **kwargs: additional parameters for ODE system
    returns: y evaluated at time k+1
    """
    # evaluate derivative at several stages within time interval
    k1 = f(tk, _uk, **kwargs)
    k2 = f(tk + _dt / 2, _uk + (k1 * (_dt / 2)), **kwargs)
    k3 = f(tk + _dt / 2, _uk + (k2 * (_dt / 2)), **kwargs)
    k4 = f(tk + _dt, _uk + (k3 * _dt), **kwargs)

    # return an average of the derivative over tk, tk + dt
    return _uk + (_dt / 6) * (k1 + (2 * k2) + (2 * k3) + k4)

def euler(f, tk, _uk, _dt=0.001, **kwargs):
    """
    single-step explicit method
    func: system of first order ODEs
    tk: current time step
    _uk: current state vector [y1, y2, y3, ...]
    _dt: discrete time step size
    **kwargs: additional parameters for ODE system
    returns: y evaluated at time k+1
    """
    derivada = f(tk, _uk, **kwargs)
    print(derivada)
    return _uk + _dt*derivada

def solveSystem(time, dt, y0, method):
    global parameters
    t = 0
    yk = y0
    state = []

    if method == "euler":
        for t in time:
            state.append(yk)
            yk = euler(ode_system, t, yk, dt, constants=parameters)

    elif method == "rk4":
        for t in time:
            state.append(yk)
            yk = rk4(ode_system, t, yk, dt, constants=parameters)

    return np.array(state)

def save(time, state, names):
    df = pd.DataFrame(state, columns = names)
    df.insert(0, 'time', time)
    df.to_csv('results.csv', float_format='%.5f', sep=',')

def plot(time, state, names):
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6)
    for i in range(len(names)):
        ax.plot(time, state[:, i], label=names[i], linewidth='2')

    ax.set(xlabel='dias', ylabel='populacao')
    plt.legend(loc='best')
    fig.savefig('competicao.png', format='png')
    plt.show()

if __name__ == "__main__":
    global parameters
    names = ['N1', 'N2']
    dt = 0.01
    tfinal = 100
    time = np.arange(0, tfinal + dt, dt)
    initial_condition = np.array([0.2,0.5])     
    #r1, r2, w11, w12, w22, w21
    parameters = [0.4, 0.3, 1., 1.2, 1., 1.]

    result = solveSystem(time, dt, initial_condition, "rk4")
    save(time, result, names)
    plot(time, result, names)