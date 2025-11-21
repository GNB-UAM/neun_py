# Contributing

Thank you for your interest in contributing to Neun Python! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.8+
- C++20 compatible compiler (GCC 10+, Clang 11+, MSVC 2019+)
- Git
- Make (Unix/Linux/macOS) or equivalent

### Clone Repository

```bash
git clone https://github.com/GNB-UAM/neun_py.git
cd neun_py
```

### Install Development Dependencies

```bash
# Install in development mode with all extras
pip install -e ".[full]"

# Or install just the development dependencies
pip install pybind11 numpy matplotlib
```

### Build from Source

```bash
# Clean build
make clean
make develop

# Or directly with setup.py
python setup.py develop
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Changes

Follow the coding standards below and commit your changes incrementally.

### 3. Test Your Changes

```bash
# Run examples
python examples/basic.py
python examples/synapsis.py

# Run tests (if available)
make test
```

### 4. Commit

```bash
git add <files>
git commit -m "Description of changes"
```

**Commit message format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

**Example:**

```
feat: add Izhikevich neuron model

Implement Izhikevich model with all parameters and variables.
Update models.json with model specification.
Add example script demonstrating usage.

Closes #42
```

### 5. Push and Create Pull Request

```bash
git push origin feature/my-new-feature
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Code

Follow PEP 8 style guidelines:

```python
# Good
def create_neuron(model_type, precision='double'):
    """Create a neuron instance.
    
    Args:
        model_type: Type of neuron model
        precision: Numeric precision ('float' or 'double')
        
    Returns:
        Neuron instance
    """
    if precision == 'double':
        args = neun_py.HHDoubleConstructorArgs()
        return neun_py.HHDoubleRK4(args)
    # ...
```

**Key points:**
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for functions/classes
- Type hints when appropriate

### C++ Code

Follow modern C++ best practices:

```cpp
// Good
template<typename TIntegrator, typename precision = double>
class MyModel : public NeuronBase<MyModel<TIntegrator, precision>, TIntegrator, precision> {
public:
    enum Variable { x, y, z };
    enum Parameter { alpha, beta };
    
    MyModel() {
        // Initialize with sensible defaults
        this->params[Parameter::alpha] = 1.0;
        this->params[Parameter::beta] = 0.5;
    }
    
    void operator()(const std::vector<precision>& state,
                   std::vector<precision>& deriv,
                   precision t) {
        // Well-commented implementation
        precision x = state[Variable::x];
        precision alpha = this->params[Parameter::alpha];
        
        // dx/dt = ...
        deriv[Variable::x] = alpha * x;
    }
};
```

**Key points:**
- Use C++20 features when appropriate
- Template code should be header-only
- Clear variable names
- Comments for complex logic
- Use `typename` consistently

### JSON Configuration

Keep `models.json` clean and well-organized:

```json
{
  "neurons": {
    "MyModel": {
      "short_name": "MM",
      "description": "Clear, concise description",
      "header": "MyModel.h",
      "variables": {
        "x": "First variable description",
        "y": "Second variable description"
      },
      "parameters": {
        "alpha": "Alpha parameter description"
      }
    }
  }
}
```

**Key points:**
- Alphabetize model entries
- Clear, descriptive names
- Complete descriptions
- Consistent formatting

## Adding New Features

### Adding a Neuron Model

See [Adding Custom Models](../guide/adding-models.md) for detailed instructions.

**Quick checklist:**

1. Create C++ header in `include/neun/models/`
2. Add entry to `models.json`
3. Rebuild with `make clean && make develop`
4. Create example script
5. Update documentation

### Adding a Synapse Type

1. Create C++ header in `include/neun/include/`
2. Add to `models.json` synapses section
3. Rebuild
4. Add tests/examples

### Adding Documentation

Documentation is in `docs/` using MkDocs:

```bash
# Edit markdown files
vim docs/guide/my-new-page.md

# Update navigation in mkdocs.yml
vim mkdocs.yml

# Preview locally (if mkdocs installed)
mkdocs serve
```

## Testing

### Manual Testing

```bash
# Test basic functionality
python examples/basic.py

# Test synapses
python examples/synapsis.py

# Test with plotting (requires matplotlib)
python examples/basic.py --plot output.pdf
```

### Creating Tests

Add test scripts in `examples/test_examples.py` or create new test files:

```python
#!/usr/bin/env python3
"""Test new model"""
import neun_py

def test_my_model():
    """Test MyModel basic functionality"""
    args = neun_py.MMDoubleConstructorArgs()
    neuron = neun_py.MMDoubleRK4(args)
    
    # Set parameters
    neuron.set_param(neun_py.MMDoubleParameter.alpha, 1.0)
    
    # Set initial state
    neuron.set(neun_py.MMDoubleVariable.x, 0.5)
    
    # Step
    neuron.step(0.001)
    
    # Verify state changed
    x = neuron.get(neun_py.MMDoubleVariable.x)
    assert x != 0.5, "State should change"
    
    print("✓ MyModel test passed")

if __name__ == "__main__":
    test_my_model()
```

## Documentation

### Docstrings

Use NumPy-style docstrings for Python:

```python
def simulate_network(neurons, synapses, duration, step):
    """Simulate a network of coupled neurons.
    
    Parameters
    ----------
    neurons : list
        List of neuron instances
    synapses : list
        List of synapse instances
    duration : float
        Simulation duration in milliseconds
    step : float
        Time step in milliseconds
        
    Returns
    -------
    times : ndarray
        Array of time points
    voltages : ndarray
        Array of voltages (neurons × time)
        
    Examples
    --------
    >>> neurons = [create_hh_neuron() for _ in range(3)]
    >>> times, voltages = simulate_network(neurons, [], 100, 0.001)
    """
    # Implementation
```

### Comments

```cpp
// Single-line comments for brief explanations

/*
 * Multi-line comments for complex sections:
 * - Explain algorithm
 * - Note assumptions
 * - Cite references if applicable
 */

/**
 * Function documentation
 * 
 * @param x Input value
 * @return Output value
 */
```

## Code Review

Pull requests will be reviewed for:

1. **Correctness** - Does it work as intended?
2. **Tests** - Are there adequate tests?
3. **Documentation** - Is it well-documented?
4. **Style** - Does it follow coding standards?
5. **Performance** - Are there obvious inefficiencies?

## Common Issues

### Build Fails After Changes

```bash
# Clean rebuild
make clean
make develop

# Check for syntax errors
python3 -m py_compile generate_pybinds.py

# Validate JSON
python3 -m json.tool models.json
```

### Import Errors

```bash
# Reinstall in development mode
pip uninstall neun-py
pip install -e .
```

### Compiler Errors

- Check C++ header syntax
- Ensure all includes are correct
- Verify template parameters match `models.json`

## Getting Help

- **Issues** - Open an issue on GitHub
- **Discussions** - Use GitHub Discussions for questions
- **Email** - Contact maintainers (see README)

## License

By contributing, you agree that your contributions will be licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Accepting constructive criticism gracefully
- Focusing on what's best for the community

**Unacceptable behavior:**
- Harassment, trolling, or discriminatory comments
- Publishing others' private information
- Unprofessional conduct

### Enforcement

Instances of unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## Recognition

Contributors will be acknowledged in:

- README.md contributors section
- Release notes
- CONTRIBUTORS file (if created)

## Release Process

For maintainers releasing new versions:

1. Update version in `pyproject.toml`
2. Update CHANGELOG (if exists)
3. Tag release: `git tag v0.5.0`
4. Push tags: `git push --tags`
5. Build distributions: `make dist`
6. Upload to PyPI: `twine upload dist/*`

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues/PRs
3. Open a new discussion on GitHub
4. Contact maintainers

Thank you for contributing to Neun Python! 🧠

## See Also

- [Architecture Documentation](architecture.md) - System design
- [Adding Models Guide](../guide/adding-models.md) - How to add new models
- [GitHub Repository](https://github.com/GNB-UAM/neun_py)
