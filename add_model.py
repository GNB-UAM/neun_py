#!/usr/bin/env python3
"""
Script to easily add new neuron models to models.json
"""

import json
import sys
from pathlib import Path

def add_model_interactive():
    """Interactive model addition."""
    print("🧠 Adding New Neuron Model to models.json")
    print("=" * 50)
    
    # Get model information
    class_name = input("Model class name (e.g., IzhikevichModel): ").strip()
    if not class_name:
        print("❌ Class name is required")
        return False
    
    short_name = input("Short name (e.g., IZ): ").strip()
    if not short_name:
        print("❌ Short name is required")
        return False
    
    description = input("Description: ").strip()
    if not description:
        description = f"{class_name} neuron model"
    
    header = input(f"Header file (default: {class_name}.h): ").strip()
    if not header:
        header = f"{class_name}.h"
    
    # Get variables
    print("\n📊 Adding State Variables (press Enter on empty name to finish):")
    variables = {}
    while True:
        var_name = input("Variable name: ").strip()
        if not var_name:
            break
        var_desc = input(f"Description for '{var_name}': ").strip()
        if not var_desc:
            var_desc = f"State variable {var_name}"
        variables[var_name] = var_desc
    
    if not variables:
        print("❌ At least one variable is required")
        return False
    
    # Get parameters
    print("\n⚙️  Adding Parameters (press Enter on empty name to finish):")
    parameters = {}
    while True:
        param_name = input("Parameter name: ").strip()
        if not param_name:
            break
        param_desc = input(f"Description for '{param_name}': ").strip()
        if not param_desc:
            param_desc = f"Model parameter {param_name}"
        parameters[param_name] = param_desc
    
    if not parameters:
        print("❌ At least one parameter is required")
        return False
    
    # Create model entry
    model_entry = {
        "short_name": short_name,
        "description": description,
        "header": header,
        "variables": variables,
        "parameters": parameters
    }
    
    return class_name, model_entry

def add_model_from_args():
    """Add model from command line arguments."""
    if len(sys.argv) < 4:
        print("Usage: python3 add_model.py <class_name> <short_name> <description>")
        return False
    
    class_name = sys.argv[1]
    short_name = sys.argv[2]
    description = sys.argv[3]
    header = f"{class_name}.h"
    
    # Default minimal example (user needs to edit models.json manually for full details)
    model_entry = {
        "short_name": short_name,
        "description": description,
        "header": header,
        "variables": {
            "x": "State variable x"
        },
        "parameters": {
            "a": "Parameter a"
        }
    }
    
    return class_name, model_entry

def main():
    """Main function."""
    models_file = Path(__file__).parent / "models.json"
    
    if not models_file.exists():
        print(f"❌ models.json not found at {models_file}")
        return False
    
    # Load existing models
    try:
        with open(models_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load models.json: {e}")
        return False
    
    # Get new model info
    if len(sys.argv) > 1:
        result = add_model_from_args()
    else:
        result = add_model_interactive()
    
    if not result:
        return False
    
    class_name, model_entry = result
    
    # Check if model already exists
    if class_name in config['models']:
        overwrite = input(f"⚠️  Model '{class_name}' already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Cancelled")
            return False
    
    # Add the model
    config['models'][class_name] = model_entry
    
    # Save updated config
    try:
        with open(models_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Added model '{class_name}' to models.json")
        
        # Calculate new totals
        total_neurons = len(config['models']) * len(config['precisions']) * len(config['integrators'])
        print(f"📊 New total neuron type combinations: {total_neurons}")
        
        print(f"\n🔄 To apply changes:")
        print(f"   1. Run: python3 generate_pybinds.py models.json src/pybinds.cpp")
        print(f"   2. Run: ./build.sh --install")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save models.json: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
