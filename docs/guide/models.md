# Neuron Models

Neun Python provides several biologically-inspired neuron models, each with different properties and computational characteristics.

## Available Models

### Hodgkin-Huxley Model

The classic conductance-based model with voltage-gated sodium and potassium channels.

**Short Name:** `HH`

**Description:** Captures the generation of action potentials through detailed ionic mechanisms.

**Variables:**

- `v` - Membrane potential (mV)
- `m` - Sodium channel activation gating variable
- `h` - Sodium channel inactivation gating variable  
- `n` - Potassium channel activation gating variable

**Parameters:**

- `cm` - Membrane capacitance (µF/cm²)
- `vna` - Sodium reversal potential (mV)
- `vk` - Potassium reversal potential (mV)
- `vl` - Leak reversal potential (mV)
- `gna` - Maximum sodium conductance (mS/cm²)
- `gk` - Maximum potassium conductance (mS/cm²)
- `gl` - Leak conductance (mS/cm²)

**Example:**

```python
import neun_py

# Create HH neuron with double precision and RK4 integrator
neuron_args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(neuron_args)

# Standard parameters
neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)

# Initial conditions
neuron.set(neun_py.HHDoubleVariable.v, -65)
neuron.set(neun_py.HHDoubleVariable.m, 0.05)
neuron.set(neun_py.HHDoubleVariable.h, 0.6)
neuron.set(neun_py.HHDoubleVariable.n, 0.3)
```

**Characteristics:**

- Biologically realistic
- Computationally expensive (4 coupled differential equations)
- Accurate action potential shape and timing
- Good for detailed biophysical studies

### Hindmarsh-Rose Model

A simplified model that captures bursting behavior with reduced computational cost.

**Short Name:** `HR`

**Description:** Three-variable model of neuronal activity with bursting and chaotic dynamics.

**Variables:**

- `x` - Membrane potential variable
- `y` - Recovery variable
- `z` - Slow adaptation variable

**Parameters:**

- `e` - External current parameter
- `mu` - Time scale parameter
- `S` - Scaling parameter

**Example:**

```python
import neun_py

# Create HR neuron with double precision and RK4 integrator
neuron_args = neun_py.HRDoubleConstructorArgs()
neuron = neun_py.HRDoubleRK4(neuron_args)

# Example parameters for bursting
neuron.set_param(neun_py.HRDoubleParameter.e, 3.0)
neuron.set_param(neun_py.HRDoubleParameter.mu, 0.001)
neuron.set_param(neun_py.HRDoubleParameter.S, 4.0)

# Initial conditions
neuron.set(neun_py.HRDoubleVariable.x, -1.5)
neuron.set(neun_py.HRDoubleVariable.y, 0.0)
neuron.set(neun_py.HRDoubleVariable.z, 0.0)
```

**Characteristics:**

- Fast computation (3 equations)
- Exhibits bursting, spiking, and chaotic behavior
- Phenomenological (less biologically detailed)
- Good for large-scale network simulations

## Model Naming Convention

Neun Python uses a systematic naming scheme for model classes:

```
{ModelShortName}{Precision}{Integrator}
```

**Examples:**

- `HHDoubleRK4` - Hodgkin-Huxley, double precision, 4th-order Runge-Kutta
- `HRFloatRK6` - Hindmarsh-Rose, float precision, 6th-order Runge-Kutta
- `HHDoubleRK6` - Hodgkin-Huxley, double precision, 6th-order Runge-Kutta

## Choosing a Model

### Hodgkin-Huxley

**Use when:**

- You need biologically realistic action potential shapes
- Studying ionic mechanisms
- Membrane properties are important
- Accuracy is more important than speed

**Avoid when:**

- Simulating very large networks (>1000 neurons)
- Real-time performance is critical

### Hindmarsh-Rose

**Use when:**

- Studying bursting dynamics
- Simulating large networks
- Computational efficiency is important
- Qualitative behavior is sufficient

**Avoid when:**

- You need accurate biophysical mechanisms
- Studying specific ionic currents

## Precision and Integrator Selection

### Precision

**Double (recommended):**

- Higher accuracy
- Minimal performance impact on modern CPUs
- Reduces numerical errors in long simulations

**Float:**

- Faster on some hardware (GPUs)
- Smaller memory footprint
- May accumulate errors over long simulations

### Integrators

**RK4 (recommended):**

- Good balance of accuracy and speed
- 4th-order accuracy
- Suitable for most neuroscience applications

**RK6:**

- Higher accuracy (6th-order)
- Better for stiff equations
- Slower than RK4

## Advanced Usage

### Parameter Scanning

```python
import neun_py
import numpy as np
import matplotlib.pyplot as plt

def scan_parameter(param_name, param_values):
    """Scan a parameter and record spiking frequency"""
    results = []
    
    for param_value in param_values:
        neuron_args = neun_py.HHDoubleConstructorArgs()
        neuron = neun_py.HHDoubleRK4(neuron_args)
        
        # Set standard parameters
        neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
        neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
        neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
        neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
        neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
        neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
        neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
        
        # Vary the parameter of interest
        neuron.set_param(param_name, param_value)
        
        # Initial conditions
        neuron.set(neun_py.HHDoubleVariable.v, -65)
        neuron.set(neun_py.HHDoubleVariable.m, 0.05)
        neuron.set(neun_py.HHDoubleVariable.h, 0.6)
        neuron.set(neun_py.HHDoubleVariable.n, 0.3)
        
        # Simulate and count spikes
        spike_count = 0
        prev_v = -65
        step = 0.001
        duration = 100
        
        time = 0.0
        while time < duration:
            neuron.add_synaptic_input(0.1)
            neuron.step(step)
            v = neuron.get(neun_py.HHDoubleVariable.v)
            
            # Detect spike (voltage crosses threshold)
            if prev_v < 0 and v >= 0:
                spike_count += 1
            
            prev_v = v
            time += step
        
        frequency = spike_count / (duration / 1000)  # Convert to Hz
        results.append(frequency)
    
    return np.array(results)

# Example: scan sodium conductance
gna_values = np.linspace(50, 200, 20) * 7.854e-3
frequencies = scan_parameter(neun_py.HHDoubleParameter.gna, gna_values)

plt.plot(gna_values / 7.854e-3, frequencies, 'o-')
plt.xlabel('gNa (mS/cm²)')
plt.ylabel('Firing Frequency (Hz)')
plt.title('Frequency vs Sodium Conductance')
plt.grid(True)
plt.savefig('gna_scan.pdf')
```

### Comparison of Models

```python
import neun_py
import matplotlib.pyplot as plt

def compare_models(duration=50, step=0.001):
    """Compare HH and HR model responses"""
    
    # Create HH neuron
    hh_args = neun_py.HHDoubleConstructorArgs()
    hh = neun_py.HHDoubleRK4(hh_args)
    
    # Standard HH parameters
    hh.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
    hh.set_param(neun_py.HHDoubleParameter.vna, 50)
    hh.set_param(neun_py.HHDoubleParameter.vk, -77)
    hh.set_param(neun_py.HHDoubleParameter.vl, -54.387)
    hh.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
    hh.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
    hh.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)
    
    hh.set(neun_py.HHDoubleVariable.v, -65)
    hh.set(neun_py.HHDoubleVariable.m, 0.05)
    hh.set(neun_py.HHDoubleVariable.h, 0.6)
    hh.set(neun_py.HHDoubleVariable.n, 0.3)
    
    # Create HR neuron
    hr_args = neun_py.HRDoubleConstructorArgs()
    hr = neun_py.HRDoubleRK4(hr_args)
    
    hr.set_param(neun_py.HRDoubleParameter.e, 3.0)
    hr.set_param(neun_py.HRDoubleParameter.mu, 0.001)
    hr.set_param(neun_py.HRDoubleParameter.S, 4.0)
    
    hr.set(neun_py.HRDoubleVariable.x, -1.5)
    hr.set(neun_py.HRDoubleVariable.y, 0.0)
    hr.set(neun_py.HRDoubleVariable.z, 0.0)
    
    # Simulate both
    times = []
    hh_voltages = []
    hr_voltages = []
    
    time = 0.0
    while time < duration:
        hh.add_synaptic_input(0.1)
        hh.step(step)
        hr.add_synaptic_input(0.1)
        hr.step(step)
        
        times.append(time)
        hh_voltages.append(hh.get(neun_py.HHDoubleVariable.v))
        hr_voltages.append(hr.get(neun_py.HRDoubleVariable.x))
        
        time += step
    
    # Plot comparison
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    axes[0].plot(times, hh_voltages, 'b-', linewidth=1.5)
    axes[0].set_ylabel('Membrane Potential (mV)')
    axes[0].set_title('Hodgkin-Huxley Model')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(times, hr_voltages, 'r-', linewidth=1.5)
    axes[1].set_xlabel('Time (ms)')
    axes[1].set_ylabel('x Variable')
    axes[1].set_title('Hindmarsh-Rose Model')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('model_comparison.pdf')

compare_models()
```

## Next Steps

- Learn about [connecting neurons with synapses](synapses.md)
- Explore [adding custom models](adding-models.md)
- See complete examples in the [examples directory](https://github.com/GNB-UAM/neun_py/tree/main/examples)
