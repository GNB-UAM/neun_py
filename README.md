# Neun Python Bindings

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://gnb-uam.github.io/neun_py/)

Python bindings for the [Neun](https://github.com/GNB-UAM/neun) neural simulation library. High-performance computational neuroscience with an intuitive Python interface.

## Features

- **Multiple neuron models** - Hodgkin-Huxley, Hindmarsh-Rose, and more  
- **High performance** - C++ speed with Python convenience  
- **Synaptic coupling** - Electrical and diffusion synapses  
- **Type safe** - Strongly typed bindings prevent errors  
- **Extensible** - Add custom models through JSON configuration  
- **NumPy integration** - Seamless array operations

## Quick start

### Installation

Download the wheel matching your Python version and platform from the
[GitHub releases](https://github.com/GNB-UAM/neun_py/releases) page, then install it:

```bash
python -m pip install /path/to/neun_py-<version>-<python>-<abi>-<platform>.whl
```

Release wheels are built for CPython 3.9-3.13 on x86-64 Linux (manylinux 2.28),
Windows, and macOS. A matching wheel contains the compiled extension and needs
neither a compiler nor a separate Neun installation. On other platforms, the
release source archive can be installed with `python -m pip install
/path/to/neun_py-<version>.tar.gz`; this builds the extension and requires a
C++20 compiler and Python development headers, but not a separate Neun install.

### From source

```bash
git clone https://github.com/GNB-UAM/neun_py.git
cd neun_py
make
```

The source tree bundles the header-only Neun library under `include/neun`;
the build generates the bindings from `models.json` and compiles them using
those headers. The `examples` extra installs plotting dependencies:

```bash
python -m pip install -e '.[examples]'
```

### First simulation

```python
import neun_py
import matplotlib.pyplot as plt

# Create Hodgkin-Huxley neuron
args = neun_py.HHDoubleConstructorArgs()
neuron = neun_py.HHDoubleRK4(args)

# Set parameters
neuron.set_param(neun_py.HHDoubleParameter.gna, 120 * 7.854e-3)
neuron.set_param(neun_py.HHDoubleParameter.gk, 36 * 7.854e-3)

# Initialize
neuron.set(neun_py.HHDoubleVariable.v, -65)

# Simulate
times, voltages = [], []
for i in range(100000):
    neuron.add_synaptic_input(0.1)
    neuron.step(0.001)
    if i % 100 == 0:
        times.append(i * 0.001)
        voltages.append(neuron.get(neun_py.HHDoubleVariable.v))

plt.plot(times, voltages)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.savefig('spike.pdf')
```

## Documentation

**[Full Documentation](https://gnb-uam.github.io/neun_py/)** - Complete guides and API reference

**Quick Links:**
- [Installation Guide](https://gnb-uam.github.io/neun_py/getting-started/installation/)
- [Quick Start Tutorial](https://gnb-uam.github.io/neun_py/getting-started/quickstart/)
- [User Guide](https://gnb-uam.github.io/neun_py/guide/basic-usage/)
- [API Reference](https://gnb-uam.github.io/neun_py/api/core/)
- [Adding Models](https://gnb-uam.github.io/neun_py/guide/adding-models/)

## Examples

See the [`examples/`](examples/) directory:

- [`basic.py`](examples/basic.py) - Single neuron simulation
- [`synapsis.py`](examples/synapsis.py) - Coupled neurons with electrical synapse

Run with:
```bash
python examples/basic.py --plot output.pdf
python examples/synapsis.py --plot coupled.pdf
```

## Available models

| Model | Short Name | Description |
|-------|------------|-------------|
| **Hodgkin-Huxley** | `HH` | Classic conductance-based model |
| **Hindmarsh-Rose** | `HR` | Simplified bursting model |
| **Izhikevich**     | `Iz` | simplified model of neuronal activity |

Each model supports:
- **Precisions:** `Float`, `Double`
- **Integrators:** `RK4` (4th order), `RK6` (6th order)

Example class names: `HHDoubleRK4`, `HRFloatRK6`

## Development

### Creating a release

After pushing the workflow to GitHub, use **Actions > Release > Run workflow**
to test its source and wheel builds without creating a release. The manual run
does not check the tag or publish artifacts to a GitHub release.

1. Update `VERSION` in `setup.py`, commit the change, and push it to GitHub.
2. Tag that commit with the same version and push the tag:

  ```bash
  git tag v0.4.0
  git push origin v0.4.0
  ```

  Replace `0.4.0` with the new version; tags must match `v` plus `VERSION`.
3. The Release workflow builds an sdist and platform wheels, tests the wheels,
  and creates a GitHub release with those files and generated notes. Check the
  Actions run and the release page before sharing it. This does not publish to
  PyPI.

### Build system

```bash
make              # Build and install in development mode
make clean        # Remove build artifacts
make test         # Run tests
make dist         # Build distributions
```

### Adding models

1. Create C++ header in `include/neun/models/`
2. Add entry to `models.json`
3. Rebuild with `make clean && make`

See [Adding Models Guide](https://gnb-uam.github.io/neun_py/guide/adding-models/) for details.

## Contributing

Contributions welcome! See [Contributing Guide](https://gnb-uam.github.io/neun_py/development/contributing/).

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

- ✅ Free to use and modify
- ✅ Open source required for derivatives
- ✅ Network use requires source availability

See [LICENSE](LICENSE) for full text.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{lareo2025neun,
  title = {Neun},
  author = {Angel Lareo},
  year = {2025},
  url = {https://github.com/GNB-UAM/Neun}
}
```

## Links

- **Documentation:** https://gnb-uam.github.io/neun_py/
- **Neun library:** https://github.com/GNB-UAM/neun
- **Source code:** https://github.com/GNB-UAM/neun_py
- **Issue tracker:** https://github.com/GNB-UAM/neun_py/issues

---

Made with ❤️ by [Angel Lareo](https://github.com/angellareo)
