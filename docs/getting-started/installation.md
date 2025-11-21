# Installation

## Prerequisites

- **C++ compiler** with C++20 support (GCC 10+, Clang 10+, MSVC 2019+)
- **Python 3.7+** with development headers
- **pybind11** (automatically installed during build)

## Installation Methods

### Via pip (Recommended)

```bash
pip install neun-py
```

### From Source

#### 1. Clone the repository

```bash
git clone https://github.com/GNB-UAM/neun_py
cd neun_py
```

#### 2. Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Build and install

```bash
make  # Generates code and installs in editable mode
```

Or manually:

```bash
make codegen  # Generate C++ bindings
make develop  # Install in editable mode
```

### Optional Dependencies

Install extra dependencies for examples and plotting:

```bash
pip install neun-py[examples]  # Includes matplotlib
pip install neun-py[full]      # All optional dependencies
```

Or if building from source:

```bash
pip install -e .[examples]
```

## Platform-Specific Notes

### Linux

Install development headers:

```bash
# Debian/Ubuntu
sudo apt install python3-dev g++

# Fedora/RHEL
sudo dnf install python3-devel gcc-c++
```

### macOS

Install Xcode Command Line Tools:

```bash
xcode-select --install
```

### Windows

Install Visual Studio 2019 or later with C++ support, or use MinGW-w64.

## Verifying Installation

Test the installation:

```bash
python -c "import neun_py; print(f'Neun-py imported successfully')"
```

Run example:

```bash
python examples/basic.py --plot test.pdf
```

## Troubleshooting

### Import Error

If you get `ImportError: No module named 'neun_py'`:

- Ensure the virtual environment is activated
- Verify installation: `pip list | grep neun`

### Compilation Error

If C++ compilation fails:

- Check compiler version: `g++ --version` (should be 10+)
- Ensure C++20 support is available
- Check Python dev headers: `python3-config --includes`

### Missing Headers

If the build can't find Neun headers:

```bash
export NEUN_INCLUDE_DIR=/path/to/neun/include
make
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Your first simulation
- [Building from Source](building.md) - Advanced build options
