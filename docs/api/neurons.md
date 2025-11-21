# Neurons API Reference

Complete reference for all available neuron models in Neun Python.

## Hodgkin-Huxley Model

### Class Names

- `neun_py.HHDoubleRK4`
- `neun_py.HHDoubleRK6`
- `neun_py.HHFloatRK4`
- `neun_py.HHFloatRK6`

### Constructor

```python
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)
```

### Variables

Access via `neun_py.HHDoubleVariable` or `neun_py.HHFloatVariable`:

| Variable | Description | Units | Typical Range |
|----------|-------------|-------|---------------|
| `v` | Membrane potential | mV | -80 to +50 |
| `m` | Sodium activation gating | dimensionless | 0 to 1 |
| `h` | Sodium inactivation gating | dimensionless | 0 to 1 |
| `n` | Potassium activation gating | dimensionless | 0 to 1 |

**Example:**
```python
# Set membrane potential
neuron.set(neun_py.HHDoubleVariable.v, -65.0)

# Get gating variables
m = neuron.get(neun_py.HHDoubleVariable.m)
h = neuron.get(neun_py.HHDoubleVariable.h)
n = neuron.get(neun_py.HHDoubleVariable.n)
```

### Parameters

Access via `neun_py.HHDoubleParameter` or `neun_py.HHFloatParameter`:

| Parameter | Description | Units | Standard Value |
|-----------|-------------|-------|----------------|
| `cm` | Membrane capacitance | µF/cm² | 1.0 * 7.854e-3 |
| `vna` | Sodium reversal potential | mV | 50 |
| `vk` | Potassium reversal potential | mV | -77 |
| `vl` | Leak reversal potential | mV | -54.387 |
| `gna` | Maximum sodium conductance | mS/cm² | 120 * 7.854e-3 |
| `gk` | Maximum potassium conductance | mS/cm² | 36 * 7.854e-3 |
| `gl` | Leak conductance | mS/cm² | 0.3 * 7.854e-3 |

**Example:**
```python
# Standard parameters
neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
```

### Typical Initial Conditions

```python
# Resting state
neuron.set(neun_py.HHDoubleVariable.v, -65)
neuron.set(neun_py.HHDoubleVariable.m, 0.05)
neuron.set(neun_py.HHDoubleVariable.h, 0.6)
neuron.set(neun_py.HHDoubleVariable.n, 0.3)
```

### Dynamics

The Hodgkin-Huxley model equations:

$$
C_m \frac{dV}{dt} = -I_{Na} - I_K - I_L + I_{ext}
$$

where:

$$
I_{Na} = g_{Na} m^3 h (V - V_{Na})
$$

$$
I_K = g_K n^4 (V - V_K)
$$

$$
I_L = g_L (V - V_L)
$$

### Complete Example

```python
import neun_py
import matplotlib.pyplot as plt

# Create HH neuron
args = neun_py.HHDoubleConstructorArgs()
hh = neun_py.HHDoubleRK4(args)

# Set standard squid axon parameters
hh.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
hh.set_param(neun_py.HHDoubleParameter.vna, 50)
hh.set_param(neun_py.HHDoubleParameter.vk, -77)
hh.set_param(neun_py.HHDoubleParameter.vl, -54.387)
hh.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
hh.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
hh.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)

# Resting state
hh.set(neun_py.HHDoubleVariable.v, -65)
hh.set(neun_py.HHDoubleVariable.m, 0.05)
hh.set(neun_py.HHDoubleVariable.h, 0.6)
hh.set(neun_py.HHDoubleVariable.n, 0.3)

# Simulate
times, voltages = [], []
step = 0.001
for i in range(100000):
    hh.add_synaptic_input(0.1)
    hh.step(step)
    if i % 100 == 0:  # Sample every 100 steps
        times.append(i * step)
        voltages.append(hh.get(neun_py.HHDoubleVariable.v))

plt.plot(times, voltages)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Hodgkin-Huxley Action Potential')
plt.savefig('hh_spike.pdf')
```

## Hindmarsh-Rose Model

### Class Names

- `neun_py.HRDoubleRK4`
- `neun_py.HRDoubleRK6`
- `neun_py.HRFloatRK4`
- `neun_py.HRFloatRK6`

### Constructor

```python
args = neun_py.HRDoubleConstructorArgs()
neuron = neun_py.HRDoubleRK4(args)
```

### Variables

Access via `neun_py.HRDoubleVariable` or `neun_py.HRFloatVariable`:

| Variable | Description | Typical Range |
|----------|-------------|---------------|
| `x` | Membrane potential variable | -2 to +2 |
| `y` | Recovery variable | -10 to +10 |
| `z` | Slow adaptation variable | 0 to 5 |

**Example:**
```python
# Set initial state
neuron.set(neun_py.HRDoubleVariable.x, -1.5)
neuron.set(neun_py.HRDoubleVariable.y, 0.0)
neuron.set(neun_py.HRDoubleVariable.z, 0.0)

# Read state
x = neuron.get(neun_py.HRDoubleVariable.x)
y = neuron.get(neun_py.HRDoubleVariable.y)
z = neuron.get(neun_py.HRDoubleVariable.z)
```

### Parameters

Access via `neun_py.HRDoubleParameter` or `neun_py.HRFloatParameter`:

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `e` | External current parameter | 2.0 to 4.0 |
| `mu` | Time scale parameter | 0.0001 to 0.01 |
| `S` | Scaling parameter | 2.0 to 6.0 |

**Example:**
```python
# Bursting regime
neuron.set_param(neun_py.HRDoubleParameter.e, 3.0)
neuron.set_param(neun_py.HRDoubleParameter.mu, 0.001)
neuron.set_param(neun_py.HRDoubleParameter.S, 4.0)

# Spiking regime
neuron.set_param(neun_py.HRDoubleParameter.e, 2.5)
neuron.set_param(neun_py.HRDoubleParameter.mu, 0.005)
neuron.set_param(neun_py.HRDoubleParameter.S, 2.0)

# Chaotic regime
neuron.set_param(neun_py.HRDoubleParameter.e, 3.2)
neuron.set_param(neun_py.HRDoubleParameter.mu, 0.002)
neuron.set_param(neun_py.HRDoubleParameter.S, 4.5)
```

### Typical Initial Conditions

```python
# Standard initial state
neuron.set(neun_py.HRDoubleVariable.x, -1.5)
neuron.set(neun_py.HRDoubleVariable.y, 0.0)
neuron.set(neun_py.HRDoubleVariable.z, 0.0)
```

### Dynamics

The Hindmarsh-Rose model equations:

$$
\frac{dx}{dt} = y - ax^3 + bx^2 - z + I
$$

$$
\frac{dy}{dt} = c - dx^2 - y
$$

$$
\frac{dz}{dt} = \mu(S(x - x_0) - z)
$$

### Complete Example

```python
import neun_py
import matplotlib.pyplot as plt

# Create HR neuron
args = neun_py.HRDoubleConstructorArgs()
hr = neun_py.HRDoubleRK4(args)

# Bursting parameters
hr.set_param(neun_py.HRDoubleParameter.e, 3.0)
hr.set_param(neun_py.HRDoubleParameter.mu, 0.001)
hr.set_param(neun_py.HRDoubleParameter.S, 4.0)

# Initial state
hr.set(neun_py.HRDoubleVariable.x, -1.5)
hr.set(neun_py.HRDoubleVariable.y, 0.0)
hr.set(neun_py.HRDoubleVariable.z, 0.0)

# Simulate bursting
times, x_values = [], []
step = 0.01
for i in range(50000):
    hr.add_synaptic_input(0.1)
    hr.step(step)
    if i % 10 == 0:
        times.append(i * step)
        x_values.append(hr.get(neun_py.HRDoubleVariable.x))

plt.plot(times, x_values)
plt.xlabel('Time')
plt.ylabel('x')
plt.title('Hindmarsh-Rose Bursting')
plt.savefig('hr_burst.pdf')
```

## Model Comparison

| Feature | Hodgkin-Huxley | Hindmarsh-Rose |
|---------|----------------|----------------|
| **Variables** | 4 (v, m, h, n) | 3 (x, y, z) |
| **Biological Detail** | High | Medium |
| **Computational Cost** | High | Medium |
| **Bursting** | No | Yes |
| **Chaos** | No | Yes |
| **Best For** | Biophysical studies | Network dynamics |
| **Time Step** | ~0.001 ms | ~0.01 ms |

## Choosing Precision

### Double Precision (Recommended)

```python
neuron = neun_py.HHDoubleRK4(args)
```

**Advantages:**
- Better numerical stability
- Minimal performance cost
- Recommended for production

### Float Precision

```python
neuron = neun_py.HHFloatRK4(args)
```

**Advantages:**
- Smaller memory footprint
- Faster on some GPUs
- Use only if memory constrained

## Choosing Integrator

### RK4 (Recommended)

```python
neuron = neun_py.HHDoubleRK4(args)
```

**Advantages:**
- 4th-order accuracy
- Good balance of speed and accuracy
- Suitable for most applications

### RK6

```python
neuron = neun_py.HHDoubleRK6(args)
```

**Advantages:**
- 6th-order accuracy
- Better for stiff equations
- Use for high-precision requirements

**Performance comparison** (approximate):
- RK4: 1.0× baseline
- RK6: 1.5× slower

## See Also

- [Core API Reference](core.md) - Common methods and patterns
- [Synapses API Reference](synapses.md) - Connecting neurons
- [Models Guide](../guide/models.md) - Detailed model information
- [Basic Usage](../guide/basic-usage.md) - Getting started
