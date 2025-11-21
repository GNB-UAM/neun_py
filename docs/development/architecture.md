# Architecture

This document explains the metaprogramming architecture that powers Neun Python bindings.

## Overview

Neun Python uses **code generation** to automatically create Python bindings from high-level model specifications. This approach eliminates manual binding code and ensures consistency across all model types.

## System Components

```
┌──────────────┐
│ models.json  │  ← Declarative specifications
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│ generate_pybinds.py│  ← Code generator
└────────┬───────────┘
         │
         ▼
┌─────────────────┐
│ src/pybinds.cpp │  ← Generated C++ bindings
└────────┬────────┘
         │
         ▼
┌───────────────┐
│ neun_py.so    │  ← Compiled Python module
└───────────────┘
```

## models.json Structure

The central configuration file defines all neuron models, synapses, and integrators:

```json
{
  "neurons": {
    "ModelClassName": {
      "short_name": "XX",
      "description": "...",
      "header": "ModelClassName.h",
      "variables": { ... },
      "parameters": { ... }
    }
  },
  "synapses": {
    "SynapseClassName": {
      "short_name": "XSyn",
      "description": "...",
      "header": "SynapseClassName.h",
      "template_params": ["TNode1", "TNode2"]
    }
  },
  "integrators": {
    "IntegratorName": {
      "short_name": "RKX",
      "header": "IntegratorName.h"
    }
  },
  "precisions": ["float", "double"],
  "generation_config": {
    "generate_individual_neurons": true,
    "generate_synaptic_pairs": true
  }
}
```

### Key Sections

**neurons** - Defines neuron model specifications:
- `short_name` - 2-3 letter abbreviation for naming
- `variables` - Dynamic state (e.g., voltage, gating variables)
- `parameters` - Fixed properties (e.g., conductances)
- `header` - C++ header file location

**synapses** - Defines synapse types:
- `template_params` - C++ template parameters
- Supports heterogeneous connections (different neuron types)

**integrators** - Numerical integration methods:
- RungeKutta4 (RK4) - 4th order
- RungeKutta6 (RK6) - 6th order

**precisions** - Numeric types:
- `float` - 32-bit
- `double` - 64-bit

## Code Generator (generate_pybinds.py)

### Generator Class

```python
class PyBindsGenerator:
    def __init__(self, models_file: str):
        self.models_file = models_file
        self.config = self._load_models()
        self.generated_types = set()
        self.syn_pairs_count = 0
```

### Main Generation Pipeline

```python
def generate(self):
    """Main generation pipeline"""
    # 1. Generate headers and boilerplate
    code = self._generate_headers()
    
    # 2. Generate model information map
    code += self._generate_model_info_map()
    
    # 3. Generate neuron bindings
    code += self._generate_all_neuron_bindings()
    
    # 4. Generate synapse bindings
    code += self._generate_all_synapse_bindings()
    
    # 5. Generate module definition
    code += self._generate_module()
    
    return code
```

### Neuron Binding Generation

For each neuron model, the generator creates:

1. **Constructor argument classes**
```cpp
py::class_<HodgkinHuxleyModel<...>::ConstructorArgs>(
    m, "HHDoubleConstructorArgs"
)
```

2. **Variable enums**
```cpp
py::enum_<HodgkinHuxleyModel<...>::Variable>(
    m, "HHDoubleVariable"
)
.value("v", HodgkinHuxleyModel<...>::Variable::v)
.value("m", HodgkinHuxleyModel<...>::Variable::m)
...
```

3. **Parameter enums**
```cpp
py::enum_<HodgkinHuxleyModel<...>::Parameter>(
    m, "HHDoubleParameter"
)
.value("cm", HodgkinHuxleyModel<...>::Parameter::cm)
...
```

4. **Neuron classes**
```cpp
py::class_<HodgkinHuxleyModel<RungeKutta4, double>>(
    m, "HHDoubleRK4"
)
.def(py::init<typename HodgkinHuxleyModel<...>::ConstructorArgs&>())
.def("set", &HodgkinHuxleyModel<...>::set)
.def("get", &HodgkinHuxleyModel<...>::get)
.def("set_param", &HodgkinHuxleyModel<...>::set_param)
.def("get_param", &HodgkinHuxleyModel<...>::get_param)
.def("step", &HodgkinHuxleyModel<...>::step)
.def("add_synaptic_input", &HodgkinHuxleyModel<...>::add_synaptic_input)
```

### Synapse Binding Generation

For each pair of neuron models:

```cpp
py::class_<ElectricalSynapsis<
    HodgkinHuxleyModel<RungeKutta4, double>,
    HodgkinHuxleyModel<RungeKutta4, double>
>>(m, "ESynHHHHDoubleRK4")
.def(py::init<...>())
.def("step", &ElectricalSynapsis<...>::step)
.def("get_synaptic_current", &ElectricalSynapsis<...>::get_synaptic_current)
```

### Combinatorial Explosion Prevention

The generator limits synapse combinations to prevent excessive code generation:

```python
MAX_SYNAPTIC_COMBINATIONS = 200

if self.syn_pairs_count >= MAX_SYNAPTIC_COMBINATIONS:
    print(f"Warning: Reached maximum synapse combinations ({MAX_SYNAPTIC_COMBINATIONS})")
    break
```

## Build System Integration

### Makefile Dependency

```makefile
src/pybinds.cpp: models.json generate_pybinds.py
	python3 generate_pybinds.py
```

Whenever `models.json` or `generate_pybinds.py` changes, `src/pybinds.cpp` is regenerated.

### setup.py Integration

```python
class build_ext_with_codegen(build_ext):
    """Custom build_ext that runs code generator first"""
    
    def run(self):
        # Generate bindings before compilation
        subprocess.check_call([sys.executable, 'generate_pybinds.py'])
        super().run()
```

## C++ Base Classes

### NeuronBase Template

Neuron models inherit from `NeuronBase`:

```cpp
template<typename TIntegrator, typename precision = double>
class HodgkinHuxleyModel : public NeuronBase<
    HodgkinHuxleyModel<TIntegrator, precision>,
    TIntegrator,
    precision
> {
    // Model implementation
};
```

**NeuronBase provides:**
- `set(variable, value)` - Set state variable
- `get(variable)` - Get state variable
- `set_param(parameter, value)` - Set parameter
- `get_param(parameter)` - Get parameter
- `step(dt)` - Time integration
- `add_synaptic_input(current)` - External input

### Synapse Base Classes

Synapses connect two neurons:

```cpp
template<typename TNode1, typename TNode2>
class ElectricalSynapsis {
    TNode1& node1;
    TNode2& node2;
    // Synapse implementation
};
```

## Type Safety

The metaprogramming system ensures type safety:

1. **Compile-time checking** - Invalid combinations won't compile
2. **Enum types** - Variables and parameters are strongly typed
3. **Template instantiation** - Only valid combinations generated

### Example Type Safety

```python
# Type-safe: correct variable enum
neuron.set(neun_py.HHDoubleVariable.v, -65)

# Runtime error: wrong variable enum for this neuron type
neuron.set(neun_py.HRDoubleVariable.x, -65)  # Error!
```

## Naming Conventions

### Systematic Naming

All generated names follow patterns:

**Neurons:**
```
{ShortName}{Precision}{Integrator}
```

**Enums:**
```
{ShortName}{Precision}Variable
{ShortName}{Precision}Parameter
```

**Synapses:**
```
{SynShortName}{Neuron1Short}{Neuron2Short}{Precision}{Integrator}
```

### Why This Matters

1. **Predictable** - Users can infer names
2. **Consistent** - Same pattern everywhere
3. **Scalable** - Adding models doesn't break patterns
4. **Discoverable** - Tab completion in IDEs works well

## Memory Management

### C++ Ownership

- Neurons created in Python are owned by Python (via pybind11 smart pointers)
- Synapses hold references, not copies
- No manual memory management needed

### Python Integration

```cpp
// Pybind11 handles reference counting automatically
py::class_<HodgkinHuxleyModel<...>>(m, "HHDoubleRK4")
    .def(py::init<...>())  // Automatic lifetime management
```

## Performance Considerations

### Generated Code Size

- Each neuron × precision × integrator = 1 class
- Each synapse × neuron pair × precision × integrator = 1 class
- With 2 neurons, 2 precisions, 2 integrators:
  - 2 × 2 × 2 = 8 neuron classes
  - 2 × (2 × 2) × 2 × 2 = 32 synapse classes

### Compilation Time

- More combinations = longer compilation
- `MAX_SYNAPTIC_COMBINATIONS` limits explosion
- Typical build time: 30-60 seconds

### Runtime Performance

- Zero overhead from code generation
- Inline-friendly template instantiation
- Direct C++ performance in Python

## Extensibility

### Adding New Components

1. **New neuron model:**
   - Create C++ header
   - Add entry to `models.json`
   - Rebuild

2. **New synapse type:**
   - Create C++ header
   - Add to `models.json`
   - Bindings generated automatically

3. **New integrator:**
   - Create C++ header
   - Add to `models.json`
   - All models get new integrator option

### Generator Customization

Modify `generate_pybinds.py` to:

- Add new binding methods
- Change naming conventions
- Customize enum generation
- Add documentation strings

## Error Handling

### Generation Errors

```python
try:
    config = self._load_models()
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {self.models_file}")
    sys.exit(1)
```

### Compilation Errors

- Missing headers → Check `models.json` paths
- Template errors → Verify C++ model matches specification
- Linking errors → Ensure all headers accessible

## Debugging

### Inspect Generated Code

```bash
# View generated bindings
cat src/pybinds.cpp | less

# Search for specific model
grep "HHDoubleRK4" src/pybinds.cpp

# Count generated classes
grep "py::class_" src/pybinds.cpp | wc -l
```

### Verbose Generation

Add debug output to `generate_pybinds.py`:

```python
print(f"Generating neuron: {neuron_name}")
print(f"  Precision: {precision}")
print(f"  Integrator: {integrator}")
```

## Best Practices

1. **Keep models.json clean** - Use clear names and descriptions
2. **Document C++ headers** - Comments help users understand models
3. **Test incrementally** - Add one model at a time
4. **Validate JSON** - Use `python3 -m json.tool models.json`
5. **Version control** - Track `models.json` changes carefully

## Future Enhancements

Potential improvements to the architecture:

- **Parallel compilation** - Speed up builds with ccache
- **Incremental generation** - Only regenerate changed bindings
- **Documentation generation** - Auto-generate API docs from JSON
- **Type stubs** - Generate `.pyi` files for better IDE support
- **Validation** - Check C++ headers match JSON specifications

## See Also

- [Adding Models Guide](../guide/adding-models.md) - How to add new models
- [Contributing](contributing.md) - Development workflow
- [Code Generator Source](https://github.com/GNB-UAM/neun_py/blob/main/generate_pybinds.py)
