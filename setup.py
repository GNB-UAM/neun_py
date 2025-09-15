import os
import re
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from pybind11.setup_helpers import Pybind11Extension
import pybind11

def find_neun_include():
    """Find the system-wide installed Neun include directory"""
    # Common system include paths
    possible_paths = [
        "/usr/local/Neun/0.4.0"
    ]
    
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "NeuronBase.h")):
            print(f"Found Neun headers at: {path}")
            return path
    
    # Try pkg-config if available
    try:
        result = subprocess.run(['pkg-config', '--cflags-only-I', 'neun'], 
                              capture_output=True, text=True, check=True)
        include_flags = result.stdout.strip()
        if include_flags:
            # Extract path from -I/path/to/include
            include_path = include_flags.replace('-I', '').strip()
            if os.path.exists(os.path.join(include_path, "NeuronBase.h")):
                print(f"Found Neun headers via pkg-config at: {include_path}")
                return include_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Check if user specified NEUN_INCLUDE_DIR environment variable
    env_path = os.environ.get('NEUN_INCLUDE_DIR')
    if env_path and os.path.exists(os.path.join(env_path, "NeuronBase.h")):
        print(f"Found Neun headers via NEUN_INCLUDE_DIR at: {env_path}")
        return env_path
    
    print("ERROR: Could not find Neun library headers!")
    print("Please install Neun headers system-wide or set NEUN_INCLUDE_DIR environment variable")
    print("Example: export NEUN_INCLUDE_DIR=/path/to/neun/include")
    sys.exit(1)

# Find system-wide Neun installation
neun_include_dir = find_neun_include()

# Build include directories (no libraries needed for header-only library)
include_dirs = [
    pybind11.get_include(),
    neun_include_dir,
]

ext_modules = [
    Pybind11Extension(
        "neun_py",
        ["src/pybinds.cpp"],
        include_dirs=include_dirs,
        cmake=True,
        language='c++',
        cxx_std=20,
        define_macros=[('VERSION_INFO', '"dev"')],
    ),
]

setup(
    name="neun_py",
    version="0.4.0",
    author="Angel Lareo",
    author_email="angel.lareo@uam.es",
    description="Python bindings for Neun neural simulation library",
    long_description="Python bindings for the Neun C++ neural simulation library using pybind11",
    long_description_content_type="text/plain",
    packages=[],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "full": [
            "numpy>=1.20.0",
            "matplotlib>=3.0.0",
        ],
    }
)
