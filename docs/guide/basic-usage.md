# Basic Usage

This guide covers the fundamental concepts and workflows for using Neun Python bindings.

## Core Concepts

### Neurons

Neurons are the primary computational units. Each neuron model has:

- **Variables** - Dynamic state (e.g., membrane potential, gating variables)
- **Parameters** - Fixed properties (e.g., conductances, reversal potentials)
- **Integrator** - Numerical method for solving differential equations

### Integrators

Integrators solve the differential equations that govern neuron dynamics:

- **RK4** - 4th-order Runge-Kutta (good balance of accuracy and speed)
- **RK6** - 6th-order Runge-Kutta (higher accuracy, slower)

### Precision

Models support different numeric precisions:

- **float** - Single precision (32-bit)
- **double** - Double precision (64-bit, recommended)

## Creating a Neuron

### Basic Neuron Creation

```python
import neun_py

# Create constructor arguments
neuron_args = neun_py.HHDoubleConstructorArgs()

# Create a Hodgkin-Huxley neuron with double precision and RK4 integrator
neuron = neun_py.HHDoubleRK4(neuron_args)
```

### Setting Parameters

Parameters define the physical properties of the neuron:

```python
# Set membrane capacitance
neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)

# Set reversal potentials (mV)
neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)

# Set conductances (mS/cm²)
neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
```

### Setting Initial Conditions

Variables define the dynamic state:

```python
# Set membrane potential
neuron.set(neun_py.HHDoubleVariable.v, -80)

# Set gating variables
neuron.set(neun_py.HHDoubleVariable.m, 0.1)
neuron.set(neun_py.HHDoubleVariable.n, 0.7)
neuron.set(neun_py.HHDoubleVariable.h, 0.01)
```

## Running a Simulation

### Basic Simulation Loop

```python
# Simulation parameters
step = 0.001  # Integration time step (ms)
simulation_time = 100  # Total time (ms)

# Storage for results
times = []
voltages = []

# Simulation loop
time = 0.0
while time < simulation_time:
    # Add external input (optional)
    neuron.add_synaptic_input(0.1)
    
    # Step the neuron forward in time
    neuron.step(step)
    
    # Read the current voltage
    voltage = neuron.get(neun_py.HHDoubleVariable.v)
    
    # Store results
    times.append(time)
    voltages.append(voltage)
    
    time += step
```

### Adding External Inputs

```python
# Add constant current
neuron.add_synaptic_input(0.1)  # Current in appropriate units

# Add time-varying current
import math
time = 0.0
while time < simulation_time:
    # Sinusoidal input
    current = 0.1 * math.sin(2 * math.pi * time / 20)
    neuron.add_synaptic_input(current)
    neuron.step(step)
    time += step
```

## Reading Neuron State

### Getting Variables

```python
# Get membrane potential
v = neuron.get(neun_py.HHDoubleVariable.v)

# Get gating variables
m = neuron.get(neun_py.HHDoubleVariable.m)
n = neuron.get(neun_py.HHDoubleVariable.n)
h = neuron.get(neun_py.HHDoubleVariable.h)

print(f"Membrane potential: {v:.3f} mV")
print(f"Gating variables: m={m:.3f}, n={n:.3f}, h={h:.3f}")
```

### Getting Parameters

```python
# Get parameters
cm = neuron.get_param(neun_py.HHDoubleParameter.cm)
gna = neuron.get_param(neun_py.HHDoubleParameter.gna)

print(f"Membrane capacitance: {cm:.6f}")
print(f"Sodium conductance: {gna:.6f}")
```

## Visualization

### Plotting with Matplotlib

```python
import matplotlib.pyplot as plt

# Plot membrane potential over time
plt.figure(figsize=(10, 4))
plt.plot(times, voltages, linewidth=1.5)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.title('Hodgkin-Huxley Neuron Simulation')
plt.grid(True, alpha=0.3)
plt.savefig('neuron_simulation.pdf')
plt.close()
```

### Multiple Variables

```python
# Store multiple variables
import numpy as np

times = []
v_values = []
m_values = []
n_values = []
h_values = []

time = 0.0
while time < simulation_time:
    neuron.add_synaptic_input(0.1)
    neuron.step(step)
    
    times.append(time)
    v_values.append(neuron.get(neun_py.HHDoubleVariable.v))
    m_values.append(neuron.get(neun_py.HHDoubleVariable.m))
    n_values.append(neuron.get(neun_py.HHDoubleVariable.n))
    h_values.append(neuron.get(neun_py.HHDoubleVariable.h))
    
    time += step

# Create subplots
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Plot voltage
axes[0].plot(times, v_values, 'b-', linewidth=1.5)
axes[0].set_ylabel('Voltage (mV)')
axes[0].set_title('Membrane Potential')
axes[0].grid(True, alpha=0.3)

# Plot gating variables
axes[1].plot(times, m_values, 'r-', label='m', linewidth=1.5)
axes[1].plot(times, n_values, 'g-', label='n', linewidth=1.5)
axes[1].plot(times, h_values, 'b-', label='h', linewidth=1.5)
axes[1].set_xlabel('Time (ms)')
axes[1].set_ylabel('Gating Variable')
axes[1].set_title('Gating Variables')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('hh_detailed.pdf')
plt.close()
```

## Saving Data

### Writing to Text Files

```python
# Save data to file
with open('simulation_data.dat', 'w') as f:
    f.write("# Time(ms) Voltage(mV)\n")
    for t, v in zip(times, voltages):
        f.write(f"{t:.6f} {v:.6f}\n")
```

### Using NumPy Arrays

```python
import numpy as np

# Convert to numpy arrays
times_array = np.array(times)
voltages_array = np.array(voltages)

# Save as NumPy binary format
np.savez('simulation.npz', times=times_array, voltages=voltages_array)

# Load later
data = np.load('simulation.npz')
times_loaded = data['times']
voltages_loaded = data['voltages']
```

## Common Patterns

### Initialization Helper

```python
def create_hh_neuron(v_init=-80, external_current=0.1):
    """Create and initialize a Hodgkin-Huxley neuron"""
    neuron_args = neun_py.HHDoubleConstructorArgs()
    neuron = neun_py.HHDoubleRK4(neuron_args)
    
    # Set parameters
    neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
    neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
    neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
    
    # Set initial conditions
    neuron.set(neun_py.HHDoubleVariable.v, v_init)
    neuron.set(neun_py.HHDoubleVariable.m, 0.1)
    neuron.set(neun_py.HHDoubleVariable.n, 0.7)
    neuron.set(neun_py.HHDoubleVariable.h, 0.01)
    
    return neuron

# Usage
neuron = create_hh_neuron(v_init=-75)
```

### Simulation Wrapper

```python
def simulate_neuron(neuron, duration, step, external_input=0.1):
    """Run a neuron simulation and return results"""
    times = []
    voltages = []
    
    time = 0.0
    while time < duration:
        neuron.add_synaptic_input(external_input)
        neuron.step(step)
        
        times.append(time)
        voltages.append(neuron.get(neun_py.HHDoubleVariable.v))
        
        time += step
    
    return np.array(times), np.array(voltages)

# Usage
neuron = create_hh_neuron()
times, voltages = simulate_neuron(neuron, duration=100, step=0.001)
```

## Next Steps

- Learn about different [neuron models](models.md)
- Connect neurons with [synapses](synapses.md)
- Add your own [custom models](adding-models.md)
