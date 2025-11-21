# Synapses API Reference

Complete reference for synapse types and their usage in Neun Python.

## Electrical Synapse

### Class Names

Pattern: `ESyn{Neuron1}{Neuron2}{Precision}{Integrator}`

**Common combinations:**
- `neun_py.ESynHHHHDoubleRK4` - HH to HH
- `neun_py.ESynHRHRDoubleRK4` - HR to HR
- `neun_py.ESynHHHRDoubleRK4` - HH to HR

### Constructor

```python
synapse = neun_py.ESynHHHHDoubleRK4(
    neuron1,           # First neuron
    variable1,         # Variable to couple from neuron1
    neuron2,           # Second neuron
    variable2,         # Variable to couple from neuron2
    conductance1,      # Conductance neuron1 → neuron2
    conductance2       # Conductance neuron2 → neuron1
)
```

**Parameters:**
- `neuron1`, `neuron2` - Neuron instances to connect
- `variable1`, `variable2` - Variable enums (typically `.v` for voltage)
- `conductance1`, `conductance2` - Coupling strengths (negative values typical)

### Example

```python
import neun_py

# Create two HH neurons
args = neun_py.HHDoubleConstructorArgs()
n1 = neun_py.HHDoubleRK4(args)
n2 = neun_py.HHDoubleRK4(args)

# Set parameters for both
for n in [n1, n2]:
    n.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    n.set_param(neun_py.HHDoubleParameter.vna, 50)
    n.set_param(neun_py.HHDoubleParameter.vk, -77)
    n.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    n.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    n.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    n.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)

# Different initial voltages
n1.set(neun_py.HHDoubleVariable.v, -75)
n2.set(neun_py.HHDoubleVariable.v, -65)

# Create electrical synapse
syn = neun_py.ESynHHHHDoubleRK4(
    n1, neun_py.HHDoubleVariable.v,
    n2, neun_py.HHDoubleVariable.v,
    -0.002,  # Conductance n1 → n2
    -0.002   # Conductance n2 → n1
)
```

### Methods

#### step(dt)

Advances the synapse by one time step.

```python
syn.step(0.001)
```

**Must be called before stepping the neurons!**

#### get_synaptic_current()

Returns the synaptic current.

```python
current = syn.get_synaptic_current()
```

### Simulation Loop

```python
step = 0.001
duration = 100

time = 0.0
while time < duration:
    # Step synapse FIRST
    syn.step(step)
    
    # Add external inputs
    n1.add_synaptic_input(0.1)
    n2.add_synaptic_input(0.08)
    
    # Then step neurons
    n1.step(step)
    n2.step(step)
    
    time += step
```

### Conductance Values

**Typical ranges:**

| Strength | Conductance | Effect |
|----------|-------------|--------|
| Weak | -0.0001 | Minimal coupling |
| Moderate | -0.001 | Noticeable synchronization |
| Strong | -0.01 | Strong synchronization |
| Very Strong | -0.1 | Nearly identical dynamics |

**Sign convention:** Negative conductances typical for depolarization-driven coupling.

### Asymmetric Coupling

```python
# Unidirectional: n1 → n2
syn = neun_py.ESynHHHHDoubleRK4(
    n1, neun_py.HHDoubleVariable.v,
    n2, neun_py.HHDoubleVariable.v,
    -0.002,  # n1 influences n2
    0.0      # n2 does NOT influence n1
)

# Asymmetric bidirectional
syn = neun_py.ESynHHHHDoubleRK4(
    n1, neun_py.HHDoubleVariable.v,
    n2, neun_py.HHDoubleVariable.v,
    -0.003,  # Stronger n1 → n2
    -0.001   # Weaker n2 → n1
)
```

## Diffusion Synapse

### Class Names

Pattern: `DSyn{Neuron1}{Neuron2}{Precision}{Integrator}`

**Common combinations:**
- `neun_py.DSynHHHHDoubleRK4`
- `neun_py.DSynHRHRDoubleRK4`
- `neun_py.DSynHHHRDoubleRK4`

### Constructor

```python
synapse = neun_py.DSynHHHHDoubleRK4(
    neuron1,
    variable1,
    neuron2,
    variable2
)
```

**Note:** Diffusion synapses have internal state and dynamics.

### Example

```python
import neun_py

# Create neurons
args = neun_py.HHDoubleConstructorArgs()
n1 = neun_py.HHDoubleRK4(args)
n2 = neun_py.HHDoubleRK4(args)

# ... set parameters ...

# Create diffusion synapse
syn = neun_py.DSynHHHHDoubleRK4(
    n1, neun_py.HHDoubleVariable.v,
    n2, neun_py.HHDoubleVariable.v
)
```

### Methods

Same as electrical synapse:

```python
syn.step(dt)
current = syn.get_synaptic_current()
```

### Simulation Loop

Identical to electrical synapse:

```python
step = 0.001
time = 0.0
while time < duration:
    syn.step(step)
    n1.add_synaptic_input(0.1)
    n2.add_synaptic_input(0.08)
    n1.step(step)
    n2.step(step)
    time += step
```

## Multi-Neuron Networks

### Chain Topology

```python
import neun_py

def create_hh_neuron(v_init=-65):
    args = neun_py.HHDoubleConstructorArgs()
    n = neun_py.HHDoubleRK4(args)
    # ... set parameters ...
    n.set(neun_py.HHDoubleVariable.v, v_init)
    return n

# Create chain: n1 → n2 → n3
n1 = create_hh_neuron(-70)
n2 = create_hh_neuron(-65)
n3 = create_hh_neuron(-60)

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
time = 0.0
while time < duration:
    # Step all synapses
    s12.step(step)
    s23.step(step)
    
    # External input to first neuron only
    n1.add_synaptic_input(0.15)
    
    # Step all neurons
    n1.step(step)
    n2.step(step)
    n3.step(step)
    
    time += step
```

### Ring Topology

```python
# Create ring: n1 ↔ n2 ↔ n3 ↔ n1
n1 = create_hh_neuron(-70)
n2 = create_hh_neuron(-65)
n3 = create_hh_neuron(-60)

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

s31 = neun_py.ESynHHHHDoubleRK4(
    n3, neun_py.HHDoubleVariable.v,
    n1, neun_py.HHDoubleVariable.v,
    -0.002, -0.002
)

# Simulation
time = 0.0
while time < duration:
    s12.step(step)
    s23.step(step)
    s31.step(step)
    
    n1.step(step)
    n2.step(step)
    n3.step(step)
    
    time += step
```

### All-to-All Topology

```python
import neun_py

n_neurons = 4
neurons = [create_hh_neuron(-65 + i*5) for i in range(n_neurons)]

# Create all-to-all synapses
synapses = []
for i in range(n_neurons):
    for j in range(i+1, n_neurons):
        syn = neun_py.ESynHHHHDoubleRK4(
            neurons[i], neun_py.HHDoubleVariable.v,
            neurons[j], neun_py.HHDoubleVariable.v,
            -0.001, -0.001
        )
        synapses.append(syn)

# Simulation
step = 0.001
time = 0.0
while time < duration:
    # Step all synapses
    for syn in synapses:
        syn.step(step)
    
    # Step all neurons
    for neuron in neurons:
        neuron.add_synaptic_input(0.1)
        neuron.step(step)
    
    time += step
```

## Heterogeneous Networks

### Mixing Neuron Types

```python
import neun_py

# Create different neuron types
hh_args = neun_py.HHDoubleConstructorArgs()
hr_args = neun_py.HRDoubleConstructorArgs()

hh_neuron = neun_py.HHDoubleRK4(hh_args)
hr_neuron = neun_py.HRDoubleRK4(hr_args)

# ... set parameters ...

# Connect different types
syn = neun_py.ESynHHHRDoubleRK4(
    hh_neuron, neun_py.HHDoubleVariable.v,
    hr_neuron, neun_py.HRDoubleVariable.x,
    -0.002, -0.002
)
```

## Analysis Tools

### Synchronization Measurement

```python
import numpy as np

def measure_synchronization(v1_values, v2_values):
    """Measure correlation between two neurons"""
    v1 = np.array(v1_values)
    v2 = np.array(v2_values)
    correlation = np.corrcoef(v1, v2)[0, 1]
    return correlation

# After simulation
sync = measure_synchronization(n1_voltages, n2_voltages)
print(f"Synchronization: {sync:.3f}")
```

### Phase Difference

```python
def phase_difference(v1_values, v2_values):
    """Compute mean phase difference"""
    v1 = np.array(v1_values)
    v2 = np.array(v2_values)
    return np.mean(np.abs(v1 - v2))

# After simulation
phase_diff = phase_difference(n1_voltages, n2_voltages)
print(f"Mean phase difference: {phase_diff:.3f} mV")
```

## Best Practices

### Simulation Order

**Always follow this order:**

1. Step all synapses
2. Add external inputs
3. Step all neurons

```python
# Correct
syn1.step(step)
syn2.step(step)
n1.add_synaptic_input(0.1)
n2.add_synaptic_input(0.1)
n1.step(step)
n2.step(step)
```

### Memory Efficiency

For large networks, use NumPy arrays:

```python
import numpy as np

n_neurons = 100
n_steps = 100000

# Pre-allocate
voltages = np.zeros((n_neurons, n_steps))

for i in range(n_steps):
    # ... step synapses and neurons ...
    for j, neuron in enumerate(neurons):
        voltages[j, i] = neuron.get(neun_py.HHDoubleVariable.v)
```

### Conductance Tuning

Start with weak coupling and increase:

```python
conductances = [0.0001, 0.0005, 0.001, 0.005, 0.01]

for g in conductances:
    syn = neun_py.ESynHHHHDoubleRK4(
        n1, neun_py.HHDoubleVariable.v,
        n2, neun_py.HHDoubleVariable.v,
        -g, -g
    )
    # ... simulate and measure synchronization ...
```

## See Also

- [Core API Reference](core.md) - Basic methods
- [Neurons API Reference](neurons.md) - Neuron models
- [Synapses Guide](../guide/synapses.md) - Usage examples
- [Basic Usage](../guide/basic-usage.md) - Getting started
