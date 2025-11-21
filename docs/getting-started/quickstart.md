# Quick Start

This guide will walk you through your first neural simulation using Neun-py.

## Your First Neuron

Let's simulate a single Hodgkin-Huxley neuron:

```python
import neun_py

# Create neuron with constructor arguments
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)

# Set physiological parameters
neuron.set_param(neun_py.HHDoubleParameter.cm, 1e-3)   # Membrane capacitance
neuron.set_param(neun_py.HHDoubleParameter.gna, 120e-3) # Na+ conductance
neuron.set_param(neun_py.HHDoubleParameter.gk, 36e-3)   # K+ conductance

# Set initial conditions
neuron.set(neun_py.HHDoubleVariable.v, -65.0)  # Resting potential
neuron.set(neun_py.HHDoubleVariable.m, 0.05)
neuron.set(neun_py.HHDoubleVariable.h, 0.6)
neuron.set(neun_py.HHDoubleVariable.n, 0.32)

# Simulate for 100ms with 0.01ms steps
dt = 0.01
for step in range(10000):
    neuron.step(dt)
    v = neuron.get(neun_py.HHDoubleVariable.v)
    print(f"{step * dt:.2f}\t{v:.3f}")
```

## Visualizing Results

Add plotting to see the membrane potential:

```python
import neun_py
import matplotlib.pyplot as plt

# Setup
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)

neuron.set_param(neun_py.HHDoubleParameter.cm, 1e-3)
neuron.set(neun_py.HHDoubleVariable.v, -65.0)

# Simulate and record
times, voltages = [], []
dt = 0.01
for step in range(10000):
    neuron.step(dt)
    times.append(step * dt)
    voltages.append(neuron.get(neun_py.HHDoubleVariable.v))

# Plot
plt.figure(figsize=(10, 4))
plt.plot(times, voltages)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.title('Hodgkin-Huxley Neuron')
plt.grid(True)
plt.show()
```

## Understanding the Code

### Neuron Creation

```python
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)
```

- `HH` = Hodgkin-Huxley model
- `Double` = Double precision floating point
- `RK4` = 4th-order Runge-Kutta integrator

### Setting Parameters

Parameters are constants that define the neuron's properties:

```python
neuron.set_param(neun_py.HHDoubleParameter.cm, 1e-3)
```

Use `set_param()` with the appropriate parameter enum.

### Setting Variables

Variables are the neuron's dynamic state:

```python
neuron.set(neun_py.HHDoubleVariable.v, -65.0)
```

Use `set()` with the appropriate variable enum.

### Simulation

```python
neuron.step(dt)  # Advance simulation by dt milliseconds
v = neuron.get(neun_py.HHDoubleVariable.v)  # Read current voltage
```

## Available Model Combinations

All models are available in these combinations:

- **Precision**: `Float`, `Double`
- **Integrators**: `RK4` (4th order), `RK6` (6th order)

Examples:
- `HHDoubleRK4` - Hodgkin-Huxley, double precision, RK4
- `HRFloatRK6` - Hindmarsh-Rose, single precision, RK6

## Next Steps

- [Basic Usage Guide](../guide/basic-usage.md) - More detailed examples
- [Neuron Models](../guide/models.md) - Available models and their parameters
- [Synaptic Coupling](../guide/synapses.md) - Connecting neurons
