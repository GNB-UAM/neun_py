# Core API

This page documents the core API components available in the Neun Python bindings.

## Module Import

```python
import neun_py
```

All classes, enums, and functions are accessible through the `neun_py` namespace.

## Naming Conventions

Neun Python follows a systematic naming scheme:

### Neuron Classes

```
{ModelShortName}{Precision}{Integrator}
```

- **ModelShortName**: 2-3 letter abbreviation (e.g., `HH`, `HR`)
- **Precision**: `Float` or `Double`
- **Integrator**: `RK4` or `RK6`

**Examples:**
- `HHDoubleRK4` - Hodgkin-Huxley, double precision, 4th-order Runge-Kutta
- `HRFloatRK6` - Hindmarsh-Rose, float precision, 6th-order Runge-Kutta

### Constructor Arguments

```
{ModelShortName}{Precision}ConstructorArgs
```

**Examples:**
- `HHDoubleConstructorArgs()`
- `HRFloatConstructorArgs()`

### Variables and Parameters

```
{ModelShortName}{Precision}Variable.{variable_name}
{ModelShortName}{Precision}Parameter.{parameter_name}
```

**Examples:**
- `HHDoubleVariable.v` - Membrane potential variable
- `HHDoubleParameter.gna` - Sodium conductance parameter

### Synapse Classes

```
{SynapseShortName}{Neuron1Short}{Neuron2Short}{Precision}{Integrator}
```

**Examples:**
- `ESynHHHHDoubleRK4` - Electrical synapse between two HH neurons
- `DSynHRHRDoubleRK6` - Diffusion synapse between two HR neurons

## Common Methods

All neuron classes share these core methods:

### Construction

```python
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)
```

Creates a neuron instance with the specified constructor arguments.

### Setting Parameters

```python
neuron.set_param(parameter_enum, value)
```

Sets a model parameter.

**Parameters:**
- `parameter_enum` - Parameter enum from `{Model}Parameter`
- `value` - Numeric value (float or double matching precision)

**Example:**
```python
neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
```

### Getting Parameters

```python
value = neuron.get_param(parameter_enum)
```

Retrieves a model parameter value.

**Returns:** Numeric value (float or double matching precision)

**Example:**
```python
gna = neuron.get_param(neun_py.HHDoubleParameter.gna)
print(f"Sodium conductance: {gna}")
```

### Setting Variables

```python
neuron.set(variable_enum, value)
```

Sets a state variable to a specific value.

**Parameters:**
- `variable_enum` - Variable enum from `{Model}Variable`
- `value` - Numeric value

**Example:**
```python
neuron.set(neun_py.HHDoubleVariable.v, -65.0)
```

### Getting Variables

```python
value = neuron.get(variable_enum)
```

Retrieves the current value of a state variable.

**Returns:** Numeric value

**Example:**
```python
v = neuron.get(neun_py.HHDoubleVariable.v)
print(f"Membrane potential: {v:.3f} mV")
```

### Adding Input

```python
neuron.add_synaptic_input(current)
```

Adds external current input to the neuron.

**Parameters:**
- `current` - Input current value

**Example:**
```python
neuron.add_synaptic_input(0.1)
```

### Time Stepping

```python
neuron.step(dt)
```

Advances the neuron simulation by one time step.

**Parameters:**
- `dt` - Time step size (typically 0.001 ms)

**Example:**
```python
neuron.step(0.001)
```

## Advanced Methods

### Reset to Initial State

Some models may provide:

```python
neuron.reset()
```

Resets the neuron to its initial state.

### Getting Time

```python
time = neuron.get_time()
```

Returns the current simulation time (if tracked by the model).

### Setting Time

```python
neuron.set_time(t)
```

Sets the current simulation time.

## Data Types

### Precision Types

- **float** - 32-bit floating point
- **double** - 64-bit floating point (recommended)

### Constructor Arguments

Constructor argument objects are lightweight holders for initialization data:

```python
args = neun_py.HHDoubleConstructorArgs()
# Currently empty, but extensible for future parameters
```

## Complete API Example

```python
import neun_py
import numpy as np

# Create neuron
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)

# Set all parameters
neuron.set_param(neun_py.HHDoubleParameter.cm, 1 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.vna, 50)
neuron.set_param(neun_py.HHDoubleParameter.vk, -77)
neuron.set_param(neun_py.HHDoubleParameter.vl, -54.387)
neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gl, 0.3 * 7.854e-3)

# Set initial conditions
neuron.set(neun_py.HHDoubleVariable.v, -65)
neuron.set(neun_py.HHDoubleVariable.m, 0.05)
neuron.set(neun_py.HHDoubleVariable.h, 0.6)
neuron.set(neun_py.HHDoubleVariable.n, 0.3)

# Simulate
step = 0.001
duration = 100
n_steps = int(duration / step)

times = np.zeros(n_steps)
voltages = np.zeros(n_steps)

for i in range(n_steps):
    neuron.add_synaptic_input(0.1)
    neuron.step(step)
    
    times[i] = i * step
    voltages[i] = neuron.get(neun_py.HHDoubleVariable.v)

# Get final state
final_v = neuron.get(neun_py.HHDoubleVariable.v)
final_m = neuron.get(neun_py.HHDoubleVariable.m)
final_n = neuron.get(neun_py.HHDoubleVariable.n)
final_h = neuron.get(neun_py.HHDoubleVariable.h)

print(f"Final state:")
print(f"  v = {final_v:.3f} mV")
print(f"  m = {final_m:.3f}")
print(f"  n = {final_n:.3f}")
print(f"  h = {final_h:.3f}")
```

## Error Handling

### Common Exceptions

**AttributeError:**
```python
# Wrong method name
neuron.set_var(...)  # AttributeError: 'HHDoubleRK4' object has no attribute 'set_var'

# Correct:
neuron.set(...)
```

**TypeError:**
```python
# Wrong type for enum
neuron.set("v", -65)  # TypeError: incompatible function arguments

# Correct:
neuron.set(neun_py.HHDoubleVariable.v, -65)
```

**ValueError:**
```python
# Invalid enum value
neuron.get(neun_py.HRDoubleVariable.x)  # ValueError if used with HH neuron

# Correct:
neuron.get(neun_py.HHDoubleVariable.v)
```

### Safe Access Pattern

```python
def safe_get_variable(neuron, variable_enum, default=0.0):
    """Safely get a variable with fallback"""
    try:
        return neuron.get(variable_enum)
    except (AttributeError, ValueError):
        return default

# Usage
v = safe_get_variable(neuron, neun_py.HHDoubleVariable.v, -65.0)
```

## Performance Tips

### Pre-allocate Arrays

```python
# Efficient: pre-allocate
n_steps = 100000
voltages = np.zeros(n_steps)
for i in range(n_steps):
    neuron.step(0.001)
    voltages[i] = neuron.get(neun_py.HHDoubleVariable.v)

# Inefficient: append
voltages = []
for i in range(n_steps):
    neuron.step(0.001)
    voltages.append(neuron.get(neun_py.HHDoubleVariable.v))
```

### Minimize Python Calls

```python
# Less efficient: call get() every iteration
for i in range(n_steps):
    neuron.step(0.001)
    v = neuron.get(neun_py.HHDoubleVariable.v)
    m = neuron.get(neun_py.HHDoubleVariable.m)
    n = neuron.get(neun_py.HHDoubleVariable.n)
    h = neuron.get(neun_py.HHDoubleVariable.h)
    process(v, m, n, h)

# More efficient: store only when needed
for i in range(n_steps):
    neuron.step(0.001)
    if i % 10 == 0:  # Sample every 10 steps
        v = neuron.get(neun_py.HHDoubleVariable.v)
        store(v)
```

### Use Double Precision

Double precision has minimal performance cost on modern CPUs but provides better numerical stability:

```python
# Recommended
neuron = neun_py.HHDoubleRK4(args)

# Use float only if memory is critical
neuron = neun_py.HHFloatRK4(args)
```

## See Also

- [Neurons API Reference](neurons.md) - Detailed neuron model documentation
- [Synapses API Reference](synapses.md) - Synapse types and usage
- [Basic Usage Guide](../guide/basic-usage.md) - Getting started
- [Examples](https://github.com/GNB-UAM/neun_py/tree/main/examples) - Complete code examples
