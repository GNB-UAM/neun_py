# Adding Custom Models

Neun Python's metaprogramming architecture allows you to easily add custom neuron models without writing C++ binding code manually.

## Overview

The system automatically generates Python bindings from a JSON configuration file (`models.json`). When you add a new model to this file, the build system regenerates the bindings automatically.

## Architecture

### Metaprogramming System

Neun Python uses **code generation** to create Python bindings:

1. **models.json** - Declarative model specifications
2. **generate_pybinds.py** - Code generator that reads models.json
3. **src/pybinds.cpp** - Generated C++ binding code (auto-created)
4. **Makefile** - Orchestrates the generation and compilation

### Build Process

```
models.json → generate_pybinds.py → src/pybinds.cpp → neun_py module
```

The Makefile automatically triggers regeneration when `models.json` changes:

```makefile
src/pybinds.cpp: models.json generate_pybinds.py
	python3 generate_pybinds.py
```

## Adding a New Neuron Model

### Step 1: Create the C++ Header

First, create your neuron model as a C++ header in `include/neun/models/`:

```cpp
// include/neun/models/MyCustomModel.h
#ifndef NEUN_MY_CUSTOM_MODEL_H
#define NEUN_MY_CUSTOM_MODEL_H

#include "NeuronBase.h"

template<typename TIntegrator, typename precision = double>
class MyCustomModel : public NeuronBase<MyCustomModel<TIntegrator, precision>, TIntegrator, precision> {
public:
    // State variables (enum)
    enum Variable { x, y, z };
    
    // Parameters (enum)
    enum Parameter { alpha, beta, gamma };
    
    // Constructor
    MyCustomModel() {
        // Initialize default parameter values
        this->params[Parameter::alpha] = 1.0;
        this->params[Parameter::beta] = 0.5;
        this->params[Parameter::gamma] = 2.0;
        
        // Initialize default state
        this->vars[Variable::x] = 0.0;
        this->vars[Variable::y] = 0.0;
        this->vars[Variable::z] = 0.0;
    }
    
    // System dynamics (required method)
    void operator()(const std::vector<precision>& state,
                   std::vector<precision>& deriv,
                   precision t) {
        // Compute derivatives
        precision x = state[Variable::x];
        precision y = state[Variable::y];
        precision z = state[Variable::z];
        
        precision alpha = this->params[Parameter::alpha];
        precision beta = this->params[Parameter::beta];
        precision gamma = this->params[Parameter::gamma];
        
        // Define your model equations here
        deriv[Variable::x] = alpha * (y - x);
        deriv[Variable::y] = x * (beta - z) - y;
        deriv[Variable::z] = x * y - gamma * z;
    }
};

#endif
```

### Step 2: Update models.json

Add your model to the `neurons` section of `models.json`:

```json
{
  "neurons": {
    "MyCustomModel": {
      "short_name": "MC",
      "description": "My custom neuron model description",
      "header": "MyCustomModel.h",
      "variables": {
        "x": "First state variable",
        "y": "Second state variable",
        "z": "Third state variable"
      },
      "parameters": {
        "alpha": "Alpha parameter description",
        "beta": "Beta parameter description",
        "gamma": "Gamma parameter description"
      }
    },
    ... existing models ...
  }
}
```

### Step 3: Rebuild

The Makefile will automatically regenerate bindings:

```bash
make clean
make
```

Or for development:

```bash
make develop
```

### Step 4: Use Your Model

```python
import neun_py

# Create constructor arguments
args = neun_py.MCDoubleConstructorArgs()

# Create your custom neuron with RK4 integrator
neuron = neun_py.MCDoubleRK4(args)

# Set parameters
neuron.set_param(neun_py.MCDoubleParameter.alpha, 1.5)
neuron.set_param(neun_py.MCDoubleParameter.beta, 0.8)
neuron.set_param(neun_py.MCDoubleParameter.gamma, 2.5)

# Set initial conditions
neuron.set(neun_py.MCDoubleVariable.x, 1.0)
neuron.set(neun_py.MCDoubleVariable.y, 0.0)
neuron.set(neun_py.MCDoubleVariable.z, 0.0)

# Simulate
step = 0.001
for _ in range(10000):
    neuron.step(step)
    x = neuron.get(neun_py.MCDoubleVariable.x)
```

## Using the Interactive Tool

For convenience, use the `add_model.py` script:

```bash
python3 add_model.py
```

The script will interactively prompt you for:

- Model class name
- Short name
- Description
- Header file
- Variables (name and description)
- Parameters (name and description)

It automatically updates `models.json` and validates the JSON syntax.

### Example Session

```
$ python3 add_model.py
🧠 Adding New Neuron Model to models.json
==================================================
Model class name (e.g., IzhikevichModel): MyCustomModel
Short name (e.g., IZ): MC
Description: My custom neuron model for testing
Header file (default: MyCustomModel.h): 

📊 Adding State Variables (press Enter on empty name to finish):
Variable name: x
Description for 'x': First state variable
Variable name: y
Description for 'y': Second state variable
Variable name: z
Description for 'z': Third state variable
Variable name: 

⚙️  Adding Parameters (press Enter on empty name to finish):
Parameter name: alpha
Description for 'alpha': Alpha parameter
Parameter name: beta
Description for 'beta': Beta parameter
Parameter name: gamma
Description for 'gamma': Gamma parameter
Parameter name: 

✅ Model 'MyCustomModel' added successfully!
```

## models.json Schema

### Neuron Model Entry

```json
{
  "neurons": {
    "ModelClassName": {
      "short_name": "XX",                    // 2-3 letter abbreviation
      "description": "Model description",    // Brief description
      "header": "ModelClassName.h",          // C++ header file
      "variables": {                         // State variables
        "var1": "Variable 1 description",
        "var2": "Variable 2 description"
      },
      "parameters": {                        // Model parameters
        "param1": "Parameter 1 description",
        "param2": "Parameter 2 description"
      }
    }
  }
}
```

### Synapse Entry

```json
{
  "synapses": {
    "SynapseClassName": {
      "short_name": "XSyn",                  // Synapse abbreviation
      "description": "Synapse description",  // Brief description
      "header": "SynapseClassName.h",        // C++ header file
      "template_params": ["TNode1", "TNode2"] // Template parameters
    }
  }
}
```

### Integrator Entry

```json
{
  "integrators": {
    "IntegratorName": {
      "short_name": "RKX",                   // Integrator abbreviation
      "header": "IntegratorName.h"           // C++ header file
    }
  }
}
```

## Generated Python API

For each neuron model, the generator creates:

### Constructor Arguments Class

```python
neun_py.{ShortName}{Precision}ConstructorArgs()
```

Example: `neun_py.MCDoubleConstructorArgs()`

### Neuron Classes

```python
neun_py.{ShortName}{Precision}{Integrator}(args)
```

Examples:
- `neun_py.MCDoubleRK4(args)`
- `neun_py.MCFloatRK6(args)`

### Variable Enums

```python
neun_py.{ShortName}{Precision}Variable.{var_name}
```

Example: `neun_py.MCDoubleVariable.x`

### Parameter Enums

```python
neun_py.{ShortName}{Precision}Parameter.{param_name}
```

Example: `neun_py.MCDoubleParameter.alpha`

### Synapse Classes

For each pair of neuron models:

```python
neun_py.{SynShortName}{Neuron1Short}{Neuron2Short}{Precision}{Integrator}
```

Example: `neun_py.ESynMCMCDoubleRK4` (electrical synapse between two MyCustomModel neurons)

## Advanced: Code Generator Internals

### Generator Structure

The `generate_pybinds.py` script contains several key classes and methods:

```python
class PyBindsGenerator:
    def _generate_neuron_bindings(self, neuron_name, neuron_info, precision, integrator):
        """Generate bindings for a specific neuron model"""
        
    def _generate_synapse_bindings(self, synapse_name, neuron1, neuron2, precision, integrator):
        """Generate bindings for synaptic connections"""
        
    def generate(self):
        """Main generation method"""
```

### Customizing Generation

To modify the code generation behavior, edit `generate_pybinds.py`. Key sections:

**Adding new enum types:**

```python
def _generate_parameter_enum(self, neuron_name, params):
    # Add custom parameter enum generation
    pass
```

**Modifying class templates:**

```python
def _generate_neuron_class(self, class_name, base_class):
    # Customize neuron class generation
    pass
```

**Limiting combinations:**

The generator limits synapse combinations to prevent code explosion:

```python
MAX_SYNAPTIC_COMBINATIONS = 200
```

## Testing Your Model

### Unit Test

Create a simple test:

```python
import neun_py
import numpy as np

def test_my_custom_model():
    """Test MyCustomModel basics"""
    # Create neuron
    args = neun_py.MCDoubleConstructorArgs()
    neuron = neun_py.MCDoubleRK4(args)
    
    # Set parameters
    neuron.set_param(neun_py.MCDoubleParameter.alpha, 1.0)
    
    # Set initial state
    neuron.set(neun_py.MCDoubleVariable.x, 1.0)
    
    # Step
    neuron.step(0.001)
    
    # Check state changed
    x = neuron.get(neun_py.MCDoubleVariable.x)
    assert x != 1.0, "State should change after step"
    
    print("✓ MyCustomModel test passed")

if __name__ == "__main__":
    test_my_custom_model()
```

### Integration Test

Test with synapses:

```python
def test_my_custom_model_synapse():
    """Test MyCustomModel with electrical synapse"""
    args = neun_py.MCDoubleConstructorArgs()
    n1 = neun_py.MCDoubleRK4(args)
    n2 = neun_py.MCDoubleRK4(args)
    
    # Different initial conditions
    n1.set(neun_py.MCDoubleVariable.x, 1.0)
    n2.set(neun_py.MCDoubleVariable.x, -1.0)
    
    # Create synapse
    syn = neun_py.ESynMCMCDoubleRK4(
        n1, neun_py.MCDoubleVariable.x,
        n2, neun_py.MCDoubleVariable.x,
        -0.001, -0.001
    )
    
    # Simulate
    for _ in range(1000):
        syn.step(0.001)
        n1.step(0.001)
        n2.step(0.001)
    
    x1 = n1.get(neun_py.MCDoubleVariable.x)
    x2 = n2.get(neun_py.MCDoubleVariable.x)
    
    print(f"After coupling: x1={x1:.3f}, x2={x2:.3f}")
    print("✓ Synapse test passed")

if __name__ == "__main__":
    test_my_custom_model_synapse()
```

## Troubleshooting

### Common Issues

**Build fails after adding model:**

- Check `models.json` syntax with `python3 -m json.tool models.json`
- Ensure header file exists in `include/neun/models/`
- Verify C++ class name matches JSON entry

**Import error in Python:**

- Rebuild with `make clean && make develop`
- Check that short name doesn't conflict with existing models

**Segmentation fault when using model:**

- Ensure your C++ model properly initializes all variables
- Check array bounds in `operator()` method
- Verify parameter and variable enums match class definition

### Debugging Generated Code

To inspect generated bindings:

```bash
# Generate bindings
python3 generate_pybinds.py

# View generated code
less src/pybinds.cpp

# Search for your model
grep -n "MyCustomModel" src/pybinds.cpp
```

## Best Practices

1. **Clear naming** - Use descriptive variable and parameter names
2. **Documentation** - Add comments in your C++ header
3. **Default values** - Provide sensible parameter defaults in constructor
4. **Testing** - Create unit tests for your model
5. **Validation** - Check parameter ranges in C++ code if needed

## Next Steps

- Study existing models in `include/neun/models/`
- Read the [architecture documentation](../development/architecture.md)
- Learn about [contributing](../development/contributing.md)
- Explore the full [API reference](../api/core.md)
