import os
import sys
import subprocess
import setuptools
from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension

# Platform flag used by compile arg helper
is_windows = sys.platform.startswith('win')

def get_neun_headers():
    """Return a list of all Neun header files under include/neun/**.

    These can be used for packaging (e.g. MANIFEST.in) or for IDE indexers.
    """
    neun_dir = os.path.join("include", "neun")
    headers = []
    for root, _, files in os.walk(neun_dir):
        for file in files:
            if file.endswith((".h", ".hpp")):
                headers.append(os.path.join(root, file))
    return headers

def get_neun_include_dirs():
    """Collect all unique include directories inside include/neun/** that contain headers.

    This ensures the extension can #include <...> from any subdirectory without relying
    on relative paths. The pybind11 include directory is appended separately.
    """
    neun_dir = os.path.join("include", "neun")
    include_dirs = set()
    for root, _, files in os.walk(neun_dir):
        if any(f.endswith((".h", ".hpp")) for f in files):
            include_dirs.add(root)
    # Always ensure top-level neun include directory is present
    include_dirs.add(neun_dir)
    return sorted(include_dirs)

def get_include_dirs():
    """Return project header include directories (pybind11 include is added at build time)."""
    return get_neun_include_dirs()

def get_compile_args():
    """Return platform-specific extra compile arguments."""
    if is_windows:
        return ["/O2", "/std:c++20"]
    return ["-O3", "-std=c++20", "-fvisibility=hidden"]

# Build include directories dynamically from header tree
include_dirs = get_include_dirs()

# Capture headers (not strictly required for build, but may help packaging)
NEUN_HEADERS = get_neun_headers()

ext_modules = [
    Extension(
        "neun_py",
        ["src/pybinds.cpp"],  # generated before compilation
        include_dirs=include_dirs,
        extra_compile_args=get_compile_args(),
        define_macros=[('VERSION_INFO', '"dev"')],
        language='c++',
    ),
]


class build_ext_with_codegen(build_ext):
    """Run code generator before building and inject pybind11 includes."""

    def _run_codegen(self):
        project_root = os.path.abspath(os.path.dirname(__file__))
        src_dir = os.path.join(project_root, "src")
        os.makedirs(src_dir, exist_ok=True)
        models_json = os.path.join(project_root, "models.json")
        output_cpp = os.path.join(src_dir, "pybinds.cpp")

        gen_script = os.path.join(project_root, "generate_pybinds.py")
        if not os.path.exists(gen_script):
            raise RuntimeError(f"Code generator not found: {gen_script}")
        if not os.path.exists(models_json):
            raise RuntimeError(f"Models file not found: {models_json}")

        cmd = [sys.executable, gen_script, models_json, output_cpp]
        self.announce("Running code generator: " + " ".join(cmd), level=3)
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Code generation failed with exit code {e.returncode}") from e

    def build_extensions(self):
        # Ensure pybind11 includes are present at build time
        try:
            import pybind11  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "pybind11 is required to build the extension. Install it (PEP 517 builds will do this automatically)."
            ) from e

        for ext in self.extensions:
            incs = list(set((ext.include_dirs or []) + [pybind11.get_include()]))
            ext.include_dirs = incs

        super().build_extensions()

    def run(self):
        # Generate code first
        self._run_codegen()
        # Then proceed with normal build
        super().run()

setup(
    name="neun_py",
    version="0.4.0",
    author="Angel Lareo",
    author_email="angel.lareo@uam.es",
    description="Python bindings for Neun neural simulation library",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext_with_codegen},
    # Packages: For adding Python packages under a src/ layout
    packages=find_packages(),
    # If you decide to ship headers inside the wheel, you can add MANIFEST.in entries.
    # Example (create MANIFEST.in): recursive-include include/neun *.h *.hpp
    include_package_data=True,
    package_data={"neun_py": []},  # placeholder
    install_requires=[
        "numpy>=1.20.0",
    ],
    python_requires=">=3.7",
    extras_require={
        "examples": [
            "matplotlib>=3.0.0",
        ],
        "full": [
            "matplotlib>=3.0.0",
        ],
    },
    zip_safe=False
)
