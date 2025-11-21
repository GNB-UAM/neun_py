# Neun Python Bindings

<div align="center">

**High-performance Python bindings for neural simulation**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

</div>

## Overview

Neun-py provides Python access to the high-performance C++ [Neun](https://github.com/GNB-UAM/neun) neural simulation library. The bindings are automatically generated from a JSON configuration file, making it easy to add new neuron models and maintain consistency between C++ and Python interfaces.

### Key Features

- **Easy neuron modelling** - Simple API for complex neural dynamics
- **Multiple precision types** - Float and double precision support
- **Flexible integration** - RK4, RK6 numerical integrators
- **Type-safe bindings** - Compile-time type checking via enums
- **Synaptic coupling** - Connect neurons with electrical and chemical synapses
- **Extensible** - Add new models through JSON configuration

## Quick Example

```python
import neun_py
import matplotlib.pyplot as plt

# Create a Hodgkin-Huxley neuron
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)

# Set parameters
neuron.set_param(neun_py.HHDoubleParameter.cm, 1e-3)
neuron.set(neun_py.HHDoubleVariable.v, -80.0)

# Simulate
times, voltages = [], []
for i in range(10000):
    neuron.step(0.001)
    times.append(i * 0.001)
    voltages.append(neuron.get(neun_py.HHDoubleVariable.v))

plt.plot(times, voltages)
plt.show()
```

## Installation

### Quick Install

```bash
pip install neun-py
```

### From Source

```bash
git clone https://github.com/GNB-UAM/neun_py
cd neun_py
python3 -m venv venv
source venv/bin/activate
make
```

See [Installation Guide](getting-started/installation.md) for detailed instructions.

## Documentation

- **[Getting Started](getting-started/installation.md)** - Installation and first steps
- **[User Guide](guide/basic-usage.md)** - Detailed usage examples
- **[API Reference](api/core.md)** - Complete API documentation
- **[Development](development/architecture.md)** - Architecture and contributing

## Available Models

The library includes implementations of:

- **Hodgkin-Huxley (HH)** - Classic conductance-based model
- **Hindmarsh-Rose (HR)** - Simplified bursting neuron model
- And more...

Each model is available with:
- **Precision**: Float, Double
- **Integrators**: RungeKutta4 (RK4), RungeKutta6 (RK6)

Examples: `HHDoubleRK4`, `HRFloatRK6`, etc.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](license.md) file for details.

## Citation

If you use Neun-py in your research, please cite:

```bibtex
@software{neun_py,
  title = {Neun Python Bindings},
  author = {Lareo, Angel},
  year = {2024},
  url = {https://github.com/GNB-UAM/neun_py}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/GNB-UAM/neun_py/issues)
- **Discussions**: [GitHub Discussions](https://github.com/GNB-UAM/neun_py/discussions)
