"""
Neun Python bindings package.
Provides clean factory interfaces for creating neural network components.
"""

# Make factory functions available at package level
from .factory import (
    create_hh_neuron,
    create_hr_neuron,
    create_neuron,
    create_electrical_synapse,
    create_diffusion_synapse,
    get_variable_enum,
    get_parameter_enum,
    Precision,
    Integrator,
    NeuronModel,
    SynapseType
)

__version__ = "0.1.0"
__all__ = [
    "create_hh_neuron",
    "create_hr_neuron", 
    "create_neuron",
    "create_electrical_synapse",
    "create_diffusion_synapse",
    "get_variable_enum",
    "get_parameter_enum",
    "Precision",
    "Integrator", 
    "NeuronModel",
    "SynapseType"
]
