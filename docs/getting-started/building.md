# Building from Source

Advanced guide for building Neun-py from source with custom configurations.

## Build System

Neun-py uses a multi-stage build process:

1. **Code Generation** - `generate_pybinds.py` creates C++ bindings from `models.json`
2. **Compilation** - C++ code is compiled into a Python extension module
3. **Installation** - Module installed in development or production mode

## Makefile Targets

```bash
make              # Default: codegen + install editable
make codegen      # Force regenerate src/pybinds.cpp
make develop      # Install in editable mode (pip install -e .)
make test         # Import module and list available types
make sdist        # Build source distribution
make wheel        # Build binary wheel
make dist         # Build both sdist and wheel
make clean        # Remove build artifacts
```

## Smart Regeneration

The build system automatically regenerates C++ bindings when:

- `models.json` is modified
- `generate_pybinds.py` is updated
- Manual regeneration via `make codegen`

This saves compilation time during development.

## Build Configuration

### Compiler Flags

The Makefile enforces C++20 via the `CXXFLAGS` environment variable:

```bash
CXXFLAGS="-std=c++20 -O3" make
```

### Custom Compiler

```bash
CXX=clang++ make
```

### Custom Python

```bash
PYTHON=python3.11 make
```

## Development Workflow

### 1. Setup Development Environment

```bash
git clone https://github.com/GNB-UAM/neun_py
cd neun_py
python3 -m venv venv
source venv/bin/activate
```

### 2. Initial Build

```bash
make  # Generates code and installs
```

### 3. Iterative Development

After modifying `models.json` or generator:

```bash
make codegen && make  # Regenerate and reinstall
```

### 4. Testing Changes

```bash
make test
python examples/basic.py
```

### 5. Clean Rebuild

```bash
make clean && make
```

## Building Distributions

### Source Distribution

```bash
make sdist
# Creates dist/neun_py-*.tar.gz
```

Includes:
- All source files
- Headers from `include/neun/`
- `models.json` and generator
- LICENSE, README, etc.

### Binary Wheel

```bash
make wheel
# Creates dist/neun_py-*-cp3*-*.whl
```

Platform-specific compiled extension.

### Both

```bash
make dist
```

## Advanced Configuration

### Custom Include Directories

If Neun headers are in a non-standard location:

```bash
export NEUN_INCLUDE_DIR=/custom/path/to/neun/include
make
```

### Build Options in setup.py

Edit `setup.py` to customize:

- Compiler flags in `get_compile_args()`
- Include directories in `get_neun_include_dirs()`
- Extension configuration in `ext_modules`

### Modifying Code Generation

Edit `generate_pybinds.py` to:

- Add new model types
- Customize binding generation
- Add utility functions
- Modify enum registration

Then regenerate:

```bash
make codegen && make
```

## Troubleshooting Build Issues

### Missing pybind11

```bash
pip install pybind11
```

### Compiler Errors

Check compiler version:

```bash
g++ --version  # Should be 10+
```

Verify C++20 support:

```bash
echo 'int main() {}' | g++ -std=c++20 -x c++ -
```

### Header Not Found

Ensure headers are in the expected location:

```bash
find include/neun -name "*.h" -o -name "*.hpp"
```

### Build Cache Issues

Clear all build artifacts:

```bash
make clean
rm -rf build/ dist/ *.egg-info
find . -name __pycache__ -exec rm -rf {} +
```

## Next Steps

- [Adding New Models](../guide/adding-models.md) - Extend the library
- [Architecture](../development/architecture.md) - Understand the design
- [Contributing](../development/contributing.md) - Submit improvements
