# Synapses

Synapses connect neurons and enable network dynamics. Neun Python provides several types of synaptic connections.

## Available Synapse Types

### Electrical Synapse

Direct electrical coupling between neurons through gap junctions.

**Short Name:** `ESyn`

**Description:** Bidirectional current flow proportional to voltage difference.

**Template Parameters:**

- `TNode1` - First neuron type
- `TNode2` - Second neuron type

**Example:**

```python
import neun_py

# Create two HH neurons
neuron_args = neun_py.HHDoubleConstructorArgs()
h1 = neun_py.HHDoubleRK4(neuron_args)
h2 = neun_py.HHDoubleRK4(neuron_args)

# Set parameters for both neurons
for neuron in [h1, h2]:
    neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
    neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
    neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)

# Different initial voltages
h1.set(neun_py.HHDoubleVariable.v, -75)
h2.set(neun_py.HHDoubleVariable.v, -65)

# Create electrical synapse
# Parameters: neuron1, variable1, neuron2, variable2, conductance1, conductance2
synapse = neun_py.ESynHHHHDoubleRK4(
    h1, neun_py.HHDoubleVariable.v,
    h2, neun_py.HHDoubleVariable.v,
    -0.002,  # Conductance from h1 to h2
    -0.002   # Conductance from h2 to h1
)
```

**Characteristics:**

- Fast, instantaneous coupling
- Bidirectional communication
- Synchronizes neuron activity
- No delay or plasticity

### Diffusion Synapse

Synaptic connection based on diffusion dynamics.

**Short Name:** `DSyn`

**Description:** Diffusion-based coupling with time-dependent dynamics.

**Template Parameters:**

- `TNode1` - First neuron type
- `TNode2` - Second neuron type
- `TIntegrator` - Integrator for synapse dynamics
- `precision` - Numeric precision (float/double)

**Example:**

```python
import neun_py

# Create neurons
neuron_args = neun_py.HHDoubleConstructorArgs()
h1 = neun_py.HHDoubleRK4(neuron_args)
h2 = neun_py.HHDoubleRK4(neuron_args)

# ... set parameters as above ...

# Create diffusion synapse
# This synapse has its own state and dynamics
synapse = neun_py.DSynHHHHDoubleRK4(
    h1, neun_py.HHDoubleVariable.v,
    h2, neun_py.HHDoubleVariable.v
)
```

**Characteristics:**

- Slower, time-dependent coupling
- Models chemical diffusion
- Can exhibit delay and filtering
- More biologically realistic for some connections

## Synapse Naming Convention

Synapses follow this naming pattern:

```
{SynapseShortName}{Neuron1ShortName}{Neuron2ShortName}{Precision}{Integrator}
```

**Examples:**

- `ESynHHHHDoubleRK4` - Electrical synapse between two HH neurons, double precision, RK4
- `DSynHRHRDoubleRK6` - Diffusion synapse between two HR neurons, double precision, RK6
- `ESynHHHRFloatRK4` - Electrical synapse from HH to HR neuron, float precision, RK4

## Simulation with Synapses

### Basic Two-Neuron Network

```python
import neun_py
import numpy as np
import matplotlib.pyplot as plt

# Create neurons
neuron_args = neun_py.HHDoubleConstructorArgs()
h1 = neun_py.HHDoubleRK4(neuron_args)
h2 = neun_py.HHDoubleRK4(neuron_args)

# Set parameters
for neuron in [h1, h2]:
    neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
    neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
    neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)

# Different initial conditions
h1.set(neun_py.HHDoubleVariable.v, -75)
h2.set(neun_py.HHDoubleVariable.v, -65)

# Create electrical synapse
synapse = neun_py.ESynHHHHDoubleRK4(
    h1, neun_py.HHDoubleVariable.v,
    h2, neun_py.HHDoubleVariable.v,
    -0.002, -0.002
)

# Simulation parameters
step = 0.001
duration = 100

# Storage
times = []
v1_values = []
v2_values = []

# Simulation loop
time = 0.0
while time < duration:
    # Step the synapse (this updates the coupled neurons)
    synapse.step(step)
    
    # Add external inputs
    h1.add_synaptic_input(0.1)
    h2.add_synaptic_input(0.08)
    
    # Step both neurons
    h1.step(step)
    h2.step(step)
    
    # Record data
    times.append(time)
    v1_values.append(h1.get(neun_py.HHDoubleVariable.v))
    v2_values.append(h2.get(neun_py.HHDoubleVariable.v))
    
    time += step

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(times, v1_values, 'b-', label='Neuron 1', linewidth=1.5)
plt.plot(times, v2_values, 'r-', label='Neuron 2', linewidth=1.5)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.title('Two Coupled Neurons')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('coupled_neurons.pdf')
```

### Getting Synaptic Current

```python
# After creating synapse as above...

synaptic_currents = []

time = 0.0
while time < duration:
    synapse.step(step)
    h1.add_synaptic_input(0.1)
    h2.add_synaptic_input(0.08)
    h1.step(step)
    h2.step(step)
    
    # Get the synaptic current
    current = synapse.get_synaptic_current()
    synaptic_currents.append(current)
    
    time += step

# Plot synaptic current over time
plt.figure(figsize=(10, 4))
plt.plot(times, synaptic_currents, 'g-', linewidth=1.5)
plt.xlabel('Time (ms)')
plt.ylabel('Synaptic Current')
plt.title('Electrical Synapse Current')
plt.grid(True, alpha=0.3)
plt.savefig('synaptic_current.pdf')
```

## Network Simulations

### Small Network Example

```python
import neun_py
import numpy as np
import matplotlib.pyplot as plt

def create_hh_neuron(v_init=-65):
    """Helper to create and initialize HH neuron"""
    neuron_args = neun_py.HHDoubleConstructorArgs()
    neuron = neun_py.HHDoubleRK4(neuron_args)
    
    neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
    neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
    neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
    
    neuron.set(neun_py.HHDoubleVariable.v, v_init)
    neuron.set(neun_py.HHDoubleVariable.m, 0.05)
    neuron.set(neun_py.HHDoubleVariable.h, 0.6)
    neuron.set(neun_py.HHDoubleVariable.n, 0.3)
    
    return neuron

# Create a chain of 3 neurons
n1 = create_hh_neuron(-70)
n2 = create_hh_neuron(-65)
n3 = create_hh_neuron(-60)

# Connect them in a chain
s12 = neun_py.ESynHHHHDoubleRK4(
    n1, neun_py.HHDoubleVariable.v,
    n2, neun_py.HHDoubleVariable.v,
    -0.002, -0.002
)

s23 = neun_py.ESynHHHHDoubleRK4(
    n2, neun_py.HHDoubleVariable.v,
    n3, neun_py.HHDoubleVariable.v,
    -0.002, -0.002
)

# Simulation
step = 0.001
duration = 100

times = []
v1_values = []
v2_values = []
v3_values = []

time = 0.0
while time < duration:
    # Step synapses
    s12.step(step)
    s23.step(step)
    
    # Add input to first neuron only
    n1.add_synaptic_input(0.15)
    
    # Step all neurons
    n1.step(step)
    n2.step(step)
    n3.step(step)
    
    # Record
    times.append(time)
    v1_values.append(n1.get(neun_py.HHDoubleVariable.v))
    v2_values.append(n2.get(neun_py.HHDoubleVariable.v))
    v3_values.append(n3.get(neun_py.HHDoubleVariable.v))
    
    time += step

# Plot
plt.figure(figsize=(12, 6))
plt.plot(times, v1_values, 'b-', label='Neuron 1', linewidth=1.5, alpha=0.8)
plt.plot(times, v2_values, 'r-', label='Neuron 2', linewidth=1.5, alpha=0.8)
plt.plot(times, v3_values, 'g-', label='Neuron 3', linewidth=1.5, alpha=0.8)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.title('Chain of 3 Coupled Neurons')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('neuron_chain.pdf')
```

### Synchronization Analysis

```python
def analyze_synchronization(v1_values, v2_values):
    """Calculate synchronization between two neurons"""
    v1 = np.array(v1_values)
    v2 = np.array(v2_values)
    
    # Pearson correlation coefficient
    correlation = np.corrcoef(v1, v2)[0, 1]
    
    # Phase difference (simplified)
    phase_diff = np.mean(np.abs(v1 - v2))
    
    return correlation, phase_diff

# After simulation...
corr, phase_diff = analyze_synchronization(v1_values, v2_values)
print(f"Synchronization: {corr:.3f}")
print(f"Mean phase difference: {phase_diff:.3f} mV")
```

## Synaptic Conductance Scanning

```python
def scan_coupling_strength(conductances):
    """Test different coupling strengths"""
    results = []
    
    for g in conductances:
        # Create neurons
        neuron_args = neun_py.HHDoubleConstructorArgs()
        h1 = neun_py.HHDoubleRK4(neuron_args)
        h2 = neun_py.HHDoubleRK4(neuron_args)
        
        # Set parameters...
        for neuron in [h1, h2]:
            neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
            neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
            neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
            neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
            neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
            neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
            neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
        
        h1.set(neun_py.HHDoubleVariable.v, -75)
        h2.set(neun_py.HHDoubleVariable.v, -65)
        
        # Create synapse with varying conductance
        synapse = neun_py.ESynHHHHDoubleRK4(
            h1, neun_py.HHDoubleVariable.v,
            h2, neun_py.HHDoubleVariable.v,
            -g, -g
        )
        
        # Simulate
        v1_vals = []
        v2_vals = []
        
        step = 0.001
        duration = 100
        time = 0.0
        
        while time < duration:
            synapse.step(step)
            h1.add_synaptic_input(0.1)
            h2.add_synaptic_input(0.08)
            h1.step(step)
            h2.step(step)
            
            v1_vals.append(h1.get(neun_py.HHDoubleVariable.v))
            v2_vals.append(h2.get(neun_py.HHDoubleVariable.v))
            
            time += step
        
        # Measure synchronization
        corr, _ = analyze_synchronization(v1_vals, v2_vals)
        results.append(corr)
    
    return np.array(results)

# Scan coupling strengths
conductances = np.linspace(0.0001, 0.01, 20)
sync_values = scan_coupling_strength(conductances)

plt.figure(figsize=(10, 6))
plt.plot(conductances, sync_values, 'o-', linewidth=2)
plt.xlabel('Coupling Conductance')
plt.ylabel('Synchronization (correlation)')
plt.title('Synchronization vs Coupling Strength')
plt.grid(True, alpha=0.3)
plt.savefig('coupling_scan.pdf')
```

## Best Practices

### Synapse Simulation Order

Always step synapses before stepping neurons:

```python
# Correct order
synapse.step(step)
neuron1.step(step)
neuron2.step(step)

# Not recommended - may cause inconsistent coupling
neuron1.step(step)
neuron2.step(step)
synapse.step(step)
```

### Multiple Synapses

When using multiple synapses, step all synapses first:

```python
# Step all synapses
s12.step(step)
s23.step(step)
s13.step(step)

# Then step all neurons
n1.step(step)
n2.step(step)
n3.step(step)
```

### Memory Efficiency

For large networks, pre-allocate storage:

```python
# Pre-allocate arrays
n_steps = int(duration / step)
times = np.zeros(n_steps)
voltages = np.zeros((n_neurons, n_steps))

# Fill during simulation
for i in range(n_steps):
    # ... simulation code ...
    times[i] = i * step
    for j, neuron in enumerate(neurons):
        voltages[j, i] = neuron.get(neun_py.HHDoubleVariable.v)
```

## Next Steps

- Learn about [adding custom models](adding-models.md)
- Explore the [API reference](../api/synapses.md)
- See complete examples in the [examples directory](https://github.com/GNB-UAM/neun_py/tree/main/examples)
