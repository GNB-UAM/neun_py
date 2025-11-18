# Neun Python Bindings

Python bindings for the [Neun](https://github.com/GNB-UAM/neun) neural simulation library, automatically generated using pybind11 and metaprogramming.

## Overview

Neun-py provides Python access to the high-performance C++ Neun neural simulation library. The bindings are automatically generated from a JSON configuration file, making it easy to add new neuron models and maintain consistency between C++ and Python interfaces.

**Key Features:**
- **Automatic code generation** from JSON model specifications
- **Type-safe bindings** with proper enum support
- **Multiple precision types** (float, double) and integrators (RK4, RK6)
- **Synaptic coupling** between different neuron types
- **Header-only library** - no linking required
- **Easy model addition** through JSON configuration

## Installation

### Prerequisites

- **C++ compiler** with C++20 support (GCC 10+, Clang 10+)
- **Python 3.7+** with development headers
- **pybind11** (automatically installed during build)
- **Neun library** installed system-wide

### Building from Source

1. **Clone and build the Python bindings**:
```bash
git clone git@github.com/GNB-UAM/neun_py
cd neun_py
# Recommended: use Makefile
make            # generates code (if needed) and installs in editable mode

# Or explicitly
make codegen    # force-regenerate src/pybinds.cpp
make develop    # pip install -e .
```

3. **Optional dependencies for examples**:
```bash
pip install neun_py[examples]  # Includes matplotlib and numpy
```

### Make targets

```bash
make              # Default: codegen (if needed) + install editable
make codegen      # Force regenerate src/pybinds.cpp
make develop      # Install editable (-e .)
make test         # Import module and print available types
make sdist        # Build a source distribution
make wheel        # Build a wheel (compiles extension)
make dist         # Build both sdist and wheel
make clean        # Remove build/ dist/ *.egg-info __pycache__ and generated src/pybinds.cpp
```

The Makefile automatically:
- Regenerates C++ bindings when models.json or generator changes
- Installs in editable mode for fast iteration
- Provides clean/test/dist helpers

## Usage

### Basic Simulation

```python
import neun_py
import matplotlib.pyplot as plt

# Create a Hodgkin-Huxley neuron
args = neun_py_core.HHDoubleConstructorArgs()
neuron = neun_py_core.HHDoubleRK4(args)

# Set parameters
neuron.set_param(neun_py_core.HHDoubleParameter.cm, 1e-3)
neuron.set_param(neun_py_core.HHDoubleParameter.gna, 120e-3)

# Set initial conditions
neuron.set_var(neun_py_core.HHDoubleVariable.v, -80.0)

# Simulate
times, voltages = [], []
for i in range(10000):
    neuron.step(0.001)
    times.append(i * 0.001)
    voltages.append(neuron.get_var(neun_py_core.HHDoubleVariable.v))

# Plot
plt.plot(times, voltages)
plt.show()
```

### Available Models and Types

The bindings generate classes for all combinations of:
- **Models**: `HH` (Hodgkin-Huxley), `HR` (Hindmarsh-Rose), etc.
- **Precisions**: `Float`, `Double`  
- **Integrators**: `RK4`, `RK6`

Examples: `HHDoubleRK4`, `HRFloatRK6`, etc.

### Synaptic Coupling

```python
# Create two neurons
h1 = neun_py_core.HHDoubleRK4(args)
h2 = neun_py_core.HHDoubleRK4(args)

# Create electrical synapse
synapse = neun_py_core.ESynHHHHDoubleRK4(
    h1, neun_py_core.HHDoubleVariable.v,
    h2, neun_py_core.HHDoubleVariable.v,
    -0.002, -0.002  # Conductances
)

# Access synapse variables
current = synapse.get(neun_py_core.ESynDoubleVariable.i1)
conductance = synapse.get_param(neun_py_core.ESynDoubleParameter.g1)
```

## Adding New Models

### 1. Update models.json

Add your model to the configuration file:

```json
{
  "neurons": {
    "MyCustomModel": {
      "short_name": "MCM",
      "header": "MyCustomModel.h",
      "description": "Description of my custom model",
      "variables": {
        "v": "Membrane potential (mV)",
        "n": "Gating variable"
      },
      "parameters": {
        "g": "Conductance (mS/cm²)",
        "tau": "Time constant (ms)"
      }
    }
  }
}
```

### 2. Implement C++ Model

Create `MyCustomModel.h` following Neun conventions:

```cpp
template<typename Precision>
class MyCustomModel {
public:
    enum variable { v, n, n_variables };
    enum parameter { g, tau, n_parameters };
    
    // ... implementation details
};
```

### 3. Regenerate and Build

```bash
make codegen && make
```

The new model will be automatically available as:
- `MCMFloatRK4`, `MCMDoubleRK4`, etc.
- `MCMFloatVariable.v`, `MCMDoubleParameter.g`, etc.

## Project Structure

```
neun_py/
├── models.json             # Model configuration file
├── generate_pybinds.py     # Automatic code generator
├── Makefile                # Build orchestration (codegen, install, test, clean)
├── setup.py                # Python packaging
├── src/                    # Generated C++ code
│   └── pybinds.cpp        # Auto-generated bindings
└── examples/               # Usage examples
  ├── basic.py           # Single neuron simulation
  ├── synapsis.py        # Coupled neurons
  └── test_examples.py   # Test suite
```

## Build System

The build system uses a multi-stage approach:

1. **Configuration**: `models.json` defines available models, integrators, and precision types
2. **Code Generation**: `generate_pybinds.py` creates C++ pybind11 code from the JSON configuration
3. **Compilation**: `setup.py` compiles the generated C++ code into a Python module
4. **Installation**: Module is installed in development mode for easy testing

### Smart Regeneration

The build script only regenerates C++ code when needed:
- When `models.json` is newer than `src/pybinds.cpp`
- When `generate_pybinds.py` is modified
- When forced with `--force` flag

This saves significant compilation time during development.

## Installation Options

### Development Installation
```bash
git clone [repository]
cd neun_py
make
```
Installs in editable mode with automatic path detection.

### Production Installation  
```bash
pip install neun-py                    # Core library only
pip install neun-py[examples]          # With matplotlib/numpy
pip install neun-py[full]              # All optional dependencies
```

### Environment Variables
If automatic detection fails, use:
```bash
export NEUN_INCLUDE_DIR=/path/to/neun/include
make
```

## API Reference

### Available Functions
```python
# Get available types
neurons = neun_py_core.get_available_neurons()
synapses = neun_py_core.get_available_synapses()

# Get model information  
info = neun_py_core.get_model_info("HH")
```

### Neuron Interface
```python
# Creation
args = neun_py_core.HHDoubleConstructorArgs()
neuron = neun_py_core.HHDoubleRK4(args)

# Variables and parameters
neuron.set_var(neun_py_core.HHDoubleVariable.v, value)
neuron.set_param(neun_py_core.HHDoubleParameter.cm, value)
voltage = neuron.get_var(neun_py_core.HHDoubleVariable.v)

# Simulation
neuron.add_synaptic_input(current)
neuron.step(dt)
```

### Synapse Interface  
```python
# Electrical synapses
synapse.get(neun_py_core.ESynDoubleVariable.i1)
synapse.set_param(neun_py_core.ESynDoubleParameter.g1, value)
synapse.step(dt)
```

## Architecture

The project uses **metaprogramming** to automatically generate Python bindings:

1. **`models.json`** - Configuration defining available models
2. **`generate_pybinds.py`** - Code generator script  
3. **`Makefile`** - Smart build orchestration
4. **`setup.py`** - Python packaging

This approach ensures:
- **Type safety** - Enums prevent variable/parameter mistakes
- **Maintainability** - Single source of truth in JSON
- **Scalability** - Easy to add new models without manual coding
- **Consistency** - Automatic C++/Python interface alignment

## Troubleshooting

**Import Error**: Ensure Neun is installed system-wide and build completed successfully

**Compilation Error**: Check that your C++ compiler supports C++20

**Missing Synapses**: Verify `generate_synaptic_pairs: true` in models.json

**Path Issues**: Use `NEUN_INCLUDE_DIR` environment variable if headers aren't found automatically

## Contributing

1. Add your model to `models.json`
2. Implement the C++ model following Neun conventions
3. Test with `make codegen && make`
4. Submit pull request with both JSON and header files