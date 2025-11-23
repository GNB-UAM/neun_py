#!/usr/bin/env python3
"""
Metaprogramming code generator for neun_py bindings.
Generates C++ pybind11 code from models.json configuration.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from itertools import product

MAX_SYNAPTIC_COMBINATIONS = 200  # Limit to avoid code explosion

class PyBindsGenerator:
    def __init__(self, models_file: str):
        self.models_file = models_file
        self.config = self._load_models()
        self.generated_types = set()
        self.syn_pairs_count = 0
        
    def _load_models(self) -> Dict[str, Any]:
        """Load models configuration from JSON file."""
        with open(self.models_file, 'r') as f:
            return json.load(f)
    
    def _get_precision_suffix(self, precision: str) -> str:
        """Get suffix for precision type."""
        return "Float" if precision == "float" else "Double"
    
    def _generate_headers(self) -> str:
        """Generate include headers."""
        headers = []
        headers.append('#include <pybind11/pybind11.h>')
        headers.append('#include <pybind11/stl.h>')
        headers.append('#include <string>')
        headers.append('#include <vector>')
        headers.append('#include <map>')
        headers.append('#include <set>')
        headers.append('#include <typeindex>')
        headers.append('')
        headers.append('#include "NeuronBase.h"')
        headers.append('#include "SystemWrapper.h"')
        headers.append('#include "IzhikevichSystemWrapper.h"')
        headers.append('#include "IntegratedSystemWrapper.h"')
        
        # Model headers
        for model_name, model_info in self.config['neurons'].items():
            headers.append(f'#include "{model_info["header"]}"')
        
        # Synapse headers  
        for synapse_name, synapse_info in self.config['synapses'].items():
            headers.append(f'#include "{synapse_info["header"]}"')
            
        # Integrator headers
        for integrator_name, integrator_info in self.config['integrators'].items():
            headers.append(f'#include "{integrator_info["header"]}"')
        
        headers.append('')
        headers.append('namespace py = pybind11;')
        headers.append('')
        
        return '\n'.join(headers)
    
    def _generate_model_info_map(self) -> str:
        """Generate the static model information map."""
        lines = []
        lines.append('// ============================================================================')
        lines.append('// GENERATED MODEL INFORMATION')
        lines.append('// ============================================================================')
        lines.append('')
        lines.append('struct ModelInfo {')
        lines.append('    std::string class_name;')
        lines.append('    std::string short_name;')
        lines.append('    std::string description;')
        lines.append('    std::vector<std::pair<std::string, std::string>> variables;')
        lines.append('    std::vector<std::pair<std::string, std::string>> parameters;')
        lines.append('};')
        lines.append('')
        lines.append('static const std::map<std::string, ModelInfo> g_models_info = {')
        
        for model_name, model_info in self.config['neurons'].items():
            lines.append(f'    {{"{model_name}", {{')
            lines.append(f'        "{model_name}",')
            lines.append(f'        "{model_info["short_name"]}",')
            lines.append(f'        "{model_info["description"]}",')
            
            # Variables
            lines.append('        {')
            for var_name, var_desc in model_info['variables'].items():
                lines.append(f'            {{"{var_name}", "{var_desc}"}},')
            lines.append('        },')
            
            # Parameters  
            lines.append('        {')
            for param_name, param_desc in model_info['parameters'].items():
                lines.append(f'            {{"{param_name}", "{param_desc}"}},')
            lines.append('        }')
            
            lines.append('    }},')
        
        lines.append('};')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_model_traits(self) -> str:
        """Generate template traits for model name extraction."""
        lines = []
        lines.append('// Template to extract model name at compile time')
        lines.append('template<typename T>')
        lines.append('struct model_name_trait;')
        lines.append('')
        
        # Generate trait specializations
        for model_name in self.config['neurons'].keys():
            lines.append(f'template<typename T>')
            lines.append(f'struct model_name_trait<{model_name}<T>> {{')
            lines.append(f'    static constexpr const char* value = "{model_name}";')
            lines.append('};')
            lines.append('')
        
        # Add wrapper type trait
        lines.append('// Template to determine the appropriate wrapper type for each model')
        lines.append('template<typename Precision, template<typename> class Model>')
        lines.append('struct wrapper_type_trait {')
        lines.append('    using type = SystemWrapper<Model<Precision>>;')
        lines.append('};')
        lines.append('')
        
        # Specialization for IzhikevichModel
        lines.append('// Specialization for IzhikevichModel')
        lines.append('template<typename Precision>')
        lines.append('struct wrapper_type_trait<Precision, IzhikevichModel> {')
        lines.append('    using type = IzhikevichSystemWrapper<Precision>;')
        lines.append('};')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_enum_registration(self) -> str:
        """Generate automatic enum registration system."""
        lines = []
        lines.append('// ============================================================================')
        lines.append('// AUTOMATIC ENUM REGISTRATION')
        lines.append('// ============================================================================')
        lines.append('')
        lines.append('static std::set<std::string> registered_enums;')
        lines.append('')
        lines.append('template<typename ModelType>')
        lines.append('const ModelInfo* get_model_info_by_type() {')
        lines.append('    static_assert(std::is_same_v<ModelType, std::decay_t<ModelType>>, "ModelType should be decayed");')
        lines.append('    ')
        lines.append('    if constexpr (requires { model_name_trait<ModelType>::value; }) {')
        lines.append('        auto it = g_models_info.find(model_name_trait<ModelType>::value);')
        lines.append('        return (it != g_models_info.end()) ? &it->second : nullptr;')
        lines.append('    } else {')
        lines.append('        return nullptr;')
        lines.append('    }')
        lines.append('}')
        lines.append('')
        
        lines.append('template<typename Precision, template<typename> class Model>')
        lines.append('void register_model_enums(py::module_& m) {')
        lines.append('    using ModelType = Model<Precision>;')
        lines.append('    ')
        lines.append('    std::string precision_name = std::is_same_v<Precision, float> ? "Float" : "Double";')
        lines.append('    ')
        lines.append('    const ModelInfo* model_info = get_model_info_by_type<ModelType>();')
        lines.append('    if (!model_info) {')
        lines.append('        throw std::runtime_error("Model info not found for type");')
        lines.append('    }')
        lines.append('    ')
        lines.append('    std::string var_name = model_info->short_name + precision_name + "Variable";')
        lines.append('    std::string param_name = model_info->short_name + precision_name + "Parameter";')
        lines.append('    ')
        lines.append('    // Register variable enum if not already registered')
        lines.append('    if (registered_enums.find(var_name) == registered_enums.end()) {')
        lines.append('        auto var_enum = py::enum_<typename ModelType::variable>(m, var_name.c_str());')
        lines.append('        ')
        lines.append('        for (size_t i = 0; i < model_info->variables.size(); ++i) {')
        lines.append('            const auto& var_info = model_info->variables[i];')
        lines.append('            var_enum.value(var_info.first.c_str(), static_cast<typename ModelType::variable>(i));')
        lines.append('        }')
        lines.append('        ')
        lines.append('        var_enum.export_values();')
        lines.append('        registered_enums.insert(var_name);')
        lines.append('    }')
        lines.append('    ')
        lines.append('    // Register parameter enum if not already registered')
        lines.append('    if (registered_enums.find(param_name) == registered_enums.end()) {')
        lines.append('        auto param_enum = py::enum_<typename ModelType::parameter>(m, param_name.c_str());')
        lines.append('        ')
        lines.append('        for (size_t i = 0; i < model_info->parameters.size(); ++i) {')
        lines.append('            const auto& param_info = model_info->parameters[i];')
        lines.append('            param_enum.value(param_info.first.c_str(), static_cast<typename ModelType::parameter>(i));')
        lines.append('        }')
        lines.append('        ')
        lines.append('        param_enum.export_values();')
        lines.append('        registered_enums.insert(param_name);')
        lines.append('    }')
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_neuron_registration(self) -> str:
        """Generate neuron registration functions."""
        lines = []
        lines.append('// ============================================================================')
        lines.append('// NEURON REGISTRATION FUNCTIONS')
        lines.append('// ============================================================================')
        lines.append('')
        
        lines.append('template<typename Precision, typename Integrator, template<typename> class Model>')
        lines.append('void register_neuron_simple(py::module_& m, const std::string& name) {')
        lines.append('    using ModelType = Model<Precision>;')
        lines.append('    using WrappedModelType = typename wrapper_type_trait<Precision, Model>::type;')
        lines.append('    using NeuronType = IntegratedSystemWrapper<WrappedModelType, Integrator>;')
        lines.append('    ')
        lines.append('    // Register enums based on model type')
        lines.append('    register_model_enums<Precision, Model>(m);')
        lines.append('    ')
        lines.append('    // Register constructor args')
        lines.append('    std::string precision_name = std::is_same_v<Precision, float> ? "Float" : "Double";')
        lines.append('    const ModelInfo* model_info = get_model_info_by_type<Model<Precision>>();')
        lines.append('    ')
        lines.append('    if (model_info) {')
        lines.append('        std::string constructor_name = model_info->short_name + precision_name + "ConstructorArgs";')
        lines.append('        ')
        lines.append('        if (registered_enums.find(constructor_name) == registered_enums.end()) {')
        lines.append('            py::class_<typename NeuronType::ConstructorArgs>(m, constructor_name.c_str())')
        lines.append('                .def(py::init<>());')
        lines.append('            registered_enums.insert(constructor_name);')
        lines.append('        }')
        lines.append('    }')
        lines.append('    ')
        lines.append('    // Register neuron class')
        lines.append('    py::class_<NeuronType>(m, name.c_str())')
        lines.append('        .def(py::init<typename NeuronType::ConstructorArgs&>())')
        lines.append('        .def("set", static_cast<void (NeuronType::*)(typename ModelType::variable, Precision)>(&NeuronType::set))')
        lines.append('        .def("get", static_cast<Precision (NeuronType::*)(typename ModelType::variable) const>(&NeuronType::get))')
        lines.append('        .def("set_param", static_cast<void (NeuronType::*)(typename ModelType::parameter, Precision)>(&NeuronType::set))')
        lines.append('        .def("get_param", static_cast<Precision (NeuronType::*)(typename ModelType::parameter) const>(&NeuronType::get))')
        lines.append('        .def("add_synaptic_input", &NeuronType::add_synaptic_input)')
        lines.append('        .def("get_synaptic_input", &NeuronType::get_synaptic_input)')
        lines.append('        .def("step", &NeuronType::step);')
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_individual_neurons(self) -> str:
        """Generate individual neuron registrations."""
        lines = []
        lines.append('// ============================================================================')
        lines.append('// INDIVIDUAL NEURON REGISTRATIONS')
        lines.append('// ============================================================================')
        lines.append('')
        lines.append('void register_individual_neurons(py::module_& m) {')
        
        for model_name, model_info in self.config['neurons'].items():
            short_name = model_info['short_name']
            for precision in self.config['precisions']:
                precision_suffix = self._get_precision_suffix(precision)
                for integrator_name, integrator_info in self.config['integrators'].items():
                    integrator_suffix = integrator_info['short_name']
                    neuron_name = f"{short_name}{precision_suffix}{integrator_suffix}"
                    
                    lines.append(f'    register_neuron_simple<{precision}, {integrator_name}, {model_name}>(m, "{neuron_name}");')
        
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_synaptic_pairs(self) -> str:
        """Generate synaptic pair registrations (if enabled)."""
        if not self.config['generation_config'].get('generate_synaptic_pairs', False):
            return ''
        
        lines = []
        lines.append('// ============================================================================')
        lines.append('// SYNAPTIC PAIR REGISTRATIONS')
        lines.append('// ============================================================================')
        lines.append('')
        
        # Add synapse enum registration functions
        lines.append('// Register synapse enums based on synapse type and precision only')
        lines.append('template<typename Precision>')
        lines.append('void register_synapse_enums(py::module_& m) {')
        lines.append('    std::string precision_name = std::is_same_v<Precision, float> ? "Float" : "Double";')
        lines.append('    ')
        lines.append('    // Register ElectricalSynapsis enums (independent of neuron models)')
        lines.append('    std::string esyn_var_name = "ESyn" + precision_name + "Variable";')
        lines.append('    std::string esyn_param_name = "ESyn" + precision_name + "Parameter";')
        lines.append('    ')
        lines.append('    if (registered_enums.find(esyn_var_name) == registered_enums.end()) {')
        lines.append('        // Use a dummy type to get the enum structure (all ElectricalSynapsis have same enums)')
        lines.append('        using DummyNeuron = IntegratedSystemWrapper<SystemWrapper<HodgkinHuxleyModel<Precision>>, RungeKutta4>;')
        lines.append('        using ESynapseType = ElectricalSynapsis<DummyNeuron, DummyNeuron, Precision>;')
        lines.append('        ')
        lines.append('        py::enum_<typename ESynapseType::variable>(m, esyn_var_name.c_str())')
        lines.append('            .value("i1", ESynapseType::i1)')
        lines.append('            .value("i2", ESynapseType::i2)')
        lines.append('            .export_values();')
        lines.append('        ')
        lines.append('        registered_enums.insert(esyn_var_name);')
        lines.append('    }')
        lines.append('    ')
        lines.append('    if (registered_enums.find(esyn_param_name) == registered_enums.end()) {')
        lines.append('        using DummyNeuron = IntegratedSystemWrapper<SystemWrapper<HodgkinHuxleyModel<Precision>>, RungeKutta4>;')
        lines.append('        using ESynapseType = ElectricalSynapsis<DummyNeuron, DummyNeuron, Precision>;')
        lines.append('        ')
        lines.append('        py::enum_<typename ESynapseType::parameter>(m, esyn_param_name.c_str())')
        lines.append('            .value("g1", ESynapseType::g1)')
        lines.append('            .value("g2", ESynapseType::g2)')
        lines.append('            .export_values();')
        lines.append('        ')
        lines.append('        registered_enums.insert(esyn_param_name);')
        lines.append('    }')
        lines.append('    ')
        lines.append('    // Register DiffusionSynapsis enums (independent of neuron models)')
        lines.append('    std::string dsyn_var_name = "DSyn" + precision_name + "Variable";')
        lines.append('    std::string dsyn_param_name = "DSyn" + precision_name + "Parameter";')
        lines.append('    ')
        lines.append('    if (registered_enums.find(dsyn_var_name) == registered_enums.end()) {')
        lines.append('        // Note: DiffusionSynapsis enums need to be defined based on actual implementation')
        lines.append('        // For now, we comment this out until we know the actual enum values')
        lines.append('        // using DummyNeuron = IntegratedSystemWrapper<SystemWrapper<HodgkinHuxleyModel<Precision>>, RungeKutta4>;')
        lines.append('        // using DSynapseType = DiffusionSynapsis<DummyNeuron, DummyNeuron, RungeKutta4, Precision>;')
        lines.append('        // py::enum_<typename DSynapseType::variable>(m, dsyn_var_name.c_str());')
        lines.append('        registered_enums.insert(dsyn_var_name);')
        lines.append('    }')
        lines.append('    ')
        lines.append('    if (registered_enums.find(dsyn_param_name) == registered_enums.end()) {')
        lines.append('        // py::enum_<typename DSynapseType::parameter>(m, dsyn_param_name.c_str());')
        lines.append('        registered_enums.insert(dsyn_param_name);')
        lines.append('    }')
        lines.append('}')
        lines.append('')
        
        # Generate separate templates for different synapse types
        lines.append('// Template for ElectricalSynapsis')
        lines.append('template<typename Precision, typename Integrator, template<typename> class Model1, template<typename> class Model2>')
        lines.append('void register_electrical_synapse_pair(py::module_& m, const std::string& name) {')
        lines.append('    using Model1Type = Model1<Precision>;')
        lines.append('    using Model2Type = Model2<Precision>;')
        lines.append('    using WrappedModel1Type = typename wrapper_type_trait<Precision, Model1>::type;')
        lines.append('    using WrappedModel2Type = typename wrapper_type_trait<Precision, Model2>::type;')
        lines.append('    using Neuron1Type = IntegratedSystemWrapper<WrappedModel1Type, Integrator>;')
        lines.append('    using Neuron2Type = IntegratedSystemWrapper<WrappedModel2Type, Integrator>;')
        lines.append('    using SynapseType = ElectricalSynapsis<Neuron1Type, Neuron2Type, Precision>;')
        lines.append('    ')
        lines.append('    py::class_<SynapseType>(m, name.c_str())')
        lines.append('        .def(py::init<Neuron1Type&, typename Model1Type::variable, Neuron2Type&, typename Model2Type::variable, Precision, Precision>())')
        lines.append('        .def("get", static_cast<Precision (SynapseType::*)(typename SynapseType::variable) const>(&SynapseType::get))')
        lines.append('        .def("set", static_cast<void (SynapseType::*)(typename SynapseType::variable, Precision)>(&SynapseType::set))')
        lines.append('        .def("get_param", static_cast<Precision (SynapseType::*)(typename SynapseType::parameter) const>(&SynapseType::get))')
        lines.append('        .def("set_param", static_cast<void (SynapseType::*)(typename SynapseType::parameter, Precision)>(&SynapseType::set))')
        lines.append('        .def("step", &SynapseType::step);')
        lines.append('}')
        lines.append('')
        
        lines.append('// Template for DiffusionSynapsis')
        lines.append('template<typename Precision, typename Integrator, template<typename> class Model1, template<typename> class Model2>')
        lines.append('void register_diffusion_synapse_pair(py::module_& m, const std::string& name) {')
        lines.append('    using Model1Type = Model1<Precision>;')
        lines.append('    using Model2Type = Model2<Precision>;')
        lines.append('    using WrappedModel1Type = typename wrapper_type_trait<Precision, Model1>::type;')
        lines.append('    using WrappedModel2Type = typename wrapper_type_trait<Precision, Model2>::type;')
        lines.append('    using Neuron1Type = IntegratedSystemWrapper<WrappedModel1Type, Integrator>;')
        lines.append('    using Neuron2Type = IntegratedSystemWrapper<WrappedModel2Type, Integrator>;')
        lines.append('    using SynapseType = DiffusionSynapsis<Neuron1Type, Neuron2Type, Integrator, Precision>;')
        lines.append('    using ConstructorArgsType = typename SystemWrapper<DiffusionSynapsisModel<Precision>>::ConstructorArgs;')
        lines.append('    ')
        lines.append('    py::class_<SynapseType>(m, name.c_str())')
        lines.append('        .def(py::init<const Neuron1Type&, typename Model1Type::variable, Neuron2Type&, typename Model2Type::variable, ConstructorArgsType&, int>())')
        lines.append('        .def("step", &SynapseType::step);')
        lines.append('}')
        lines.append('')
        lines.append('void register_synaptic_pairs(py::module_& m) {')
        lines.append('    // Register synapse enums once per precision (independent of specific neuron models)')
        lines.append('    register_synapse_enums<float>(m);')
        lines.append('    register_synapse_enums<double>(m);')
        lines.append('    ')
        
        # Generate limited combinations to avoid explosion
        self.syn_pairs_count = 0
        max_combinations = self.config['generation_config'].get('max_synaptic_combinations', MAX_SYNAPTIC_COMBINATIONS)
        
        for synapse_name, synapse_info in self.config['synapses'].items():
            synapse_short = synapse_info['short_name']
            
            # Generate pairs with same precision and integrator only
            for precision in self.config['precisions']:
                precision_suffix = self._get_precision_suffix(precision)
                        
                for integrator_name, integrator_info in self.config['integrators'].items():
                    integrator_suffix = integrator_info['short_name']

                    for model1_name, model1_info in self.config['neurons'].items():
                        model1_short = model1_info['short_name']
                        
                        for model2_name, model2_info in self.config['neurons'].items():
                            model2_short = model2_info['short_name']
                    
                            if self.syn_pairs_count >= max_combinations:
                                lines.append('    // Additional combinations truncated to avoid code explosion')
                                break
                    
                            # Both neurons use the same precision and integrator
                            pair_name = f"{synapse_short}{model1_short}{model2_short}{precision_suffix}{integrator_suffix}"
                            
                            # Use the appropriate registration function based on synapse type
                            if synapse_name == "ElectricalSynapsis":
                                lines.append(f'    register_electrical_synapse_pair<{precision}, {integrator_name}, {model1_name}, {model2_name}>(m, "{pair_name}");')
                            elif synapse_name == "DiffusionSynapsis":
                                lines.append(f'    register_diffusion_synapse_pair<{precision}, {integrator_name}, {model1_name}, {model2_name}>(m, "{pair_name}");')
                            
                            self.syn_pairs_count += 1
                            
                            if self.syn_pairs_count >= max_combinations:
                                break
                        if self.syn_pairs_count >= max_combinations:
                            break
                    if self.syn_pairs_count >= max_combinations:
                        break
                if self.syn_pairs_count >= max_combinations:
                    break
        
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_utility_functions(self) -> str:
        """Generate utility functions for Python interface."""
        lines = []
        lines.append('// ============================================================================')
        lines.append('// UTILITY FUNCTIONS')
        lines.append('// ============================================================================')
        lines.append('')
        
        # Function to get available NEURON types
        lines.append('std::vector<std::string> get_available_neurons() {')
        lines.append('    std::vector<std::string> neurons;')
        for model_name, model_info in self.config['neurons'].items():
            short_name = model_info['short_name']
            for precision in self.config['precisions']:
                precision_suffix = self._get_precision_suffix(precision)
                for integrator_name, integrator_info in self.config['integrators'].items():
                    integrator_suffix = integrator_info['short_name']
                    neuron_name = f"{short_name}{precision_suffix}{integrator_suffix}"
                    lines.append(f'    neurons.push_back("{neuron_name}");')
        lines.append('    return neurons;')
        lines.append('}')
        lines.append('')

        # Funtion to get available SYNAPSE types
        lines.append('std::vector<std::string> get_available_synapses() {')
        lines.append('    std::vector<std::string> synapses;')
        for synapse_name, synapse_info in self.config['synapses'].items():
            synapse_short = synapse_info['short_name']
            for precision in self.config['precisions']:
                precision_suffix = self._get_precision_suffix(precision)
                for integrator_name, integrator_info in self.config['integrators'].items():
                    integrator_suffix = integrator_info['short_name']
                    for model1_name, model1_info in self.config['neurons'].items():
                        model1_short = model1_info['short_name']
                        for model2_name, model2_info in self.config['neurons'].items():
                            model2_short = model2_info['short_name']
                            pair_name = f"{synapse_short}{model1_short}{model2_short}{precision_suffix}{integrator_suffix}"
                            lines.append(f'    synapses.push_back("{pair_name}");')
        lines.append('    return synapses;')
        lines.append('}')
        lines.append('')


        # Function to get model info by short name
        lines.append('py::dict get_model_info(const std::string& short_name) {')
        lines.append('    for (const auto& pair : g_models_info) {')
        lines.append('        const auto& class_name = pair.first;')
        lines.append('        const auto& model_info = pair.second;')
        lines.append('        if (model_info.short_name == short_name) {')
        lines.append('            py::dict result;')
        lines.append('            result["class_name"] = model_info.class_name;')
        lines.append('            result["short_name"] = model_info.short_name;')
        lines.append('            result["description"] = model_info.description;')
        lines.append('            ')
        lines.append('            py::list vars;')
        lines.append('            for (const auto& var_pair : model_info.variables) {')
        lines.append('                py::dict var_info;')
        lines.append('                var_info["name"] = var_pair.first;')
        lines.append('                var_info["description"] = var_pair.second;')
        lines.append('                vars.append(var_info);')
        lines.append('            }')
        lines.append('            result["variables"] = vars;')
        lines.append('            ')
        lines.append('            py::list params;')
        lines.append('            for (const auto& param_pair : model_info.parameters) {')
        lines.append('                py::dict param_info;')
        lines.append('                param_info["name"] = param_pair.first;')
        lines.append('                param_info["description"] = param_pair.second;')
        lines.append('                params.append(param_info);')
        lines.append('            }')
        lines.append('            result["parameters"] = params;')
        lines.append('            ')
        lines.append('            return result;')
        lines.append('        }')
        lines.append('    }')
        lines.append('    return py::dict();')
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_main_module(self) -> str:
        """Generate the main pybind11 module."""
        lines = []
        lines.append('// ============================================================================')
        lines.append('// MAIN PYBIND11 MODULE')
        lines.append('// ============================================================================')
        lines.append('')
        lines.append('PYBIND11_MODULE(neun_py, m) {')
        lines.append('    m.doc() = "Neun Python Bindings - Neural Simulation Library";')
        lines.append('    m.attr("__version__") = "0.4.0";')
        lines.append('    ')
        lines.append('    // Register individual neurons')
        lines.append('    register_individual_neurons(m);')
        
        if self.config['generation_config'].get('generate_synaptic_pairs', False):
            lines.append('    ')
            lines.append('    // Register synaptic pairs')
            lines.append('    register_synaptic_pairs(m);')
        
        lines.append('    ')
        lines.append('    // Module utility functions')
        lines.append('    m.def("get_available_neurons", &get_available_neurons);')
        if self.config['generation_config'].get('generate_synaptic_pairs', False):
            lines.append('    m.def("get_available_synapses", &get_available_synapses);')
        lines.append('    m.def("get_model_info", &get_model_info);')
        lines.append('}')
        
        return '\n'.join(lines)
    
    def generate(self, output_file: str):
        """Generate the complete pybinds.cpp file."""
        print(f"Generating pybinds code from {self.models_file}...")
        
        sections = []
        sections.append('// ============================================================================')
        sections.append('// AUTOMATICALLY GENERATED FILE - DO NOT EDIT MANUALLY')
        sections.append('// Generated from models.json by generate_pybinds.py')
        sections.append('// ============================================================================')
        sections.append('')
        sections.append(self._generate_headers())
        sections.append(self._generate_model_info_map())
        sections.append(self._generate_model_traits())
        sections.append(self._generate_enum_registration())
        sections.append(self._generate_neuron_registration())
        sections.append(self._generate_individual_neurons())
        sections.append(self._generate_synaptic_pairs())
        sections.append(self._generate_utility_functions())
        sections.append(self._generate_main_module())
        
        full_code = '\n'.join(sections)
        
        # Write to output file
        with open(output_file, 'w') as f:
            f.write(full_code)
        
        print(f"Generated {len(full_code.splitlines())} lines of C++ code in {output_file}")
        
        # Print summary
        total_neurons = len(self.config['neurons']) * len(self.config['precisions']) * len(self.config['integrators'])
        print(f"Total individual neuron types: {total_neurons}")
        
        if self.config['generation_config'].get('generate_synaptic_pairs', False):
            print(f"Synaptic pair types (limited to {MAX_SYNAPTIC_COMBINATIONS}): {self.syn_pairs_count}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_pybinds.py <models.json> <output.cpp>")
        sys.exit(1)
    
    models_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(models_file):
        print(f"Error: Models file {models_file} not found")
        sys.exit(1)
    
    try:
        generator = PyBindsGenerator(models_file)
        generator.generate(output_file)
        print("Code generation completed successfully!")
    except Exception as e:
        print(f"Error during code generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
