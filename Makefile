# Makefile for neun_py
# Replicates and extends build.sh functionality with proper dependencies

SHELL := /bin/bash
PYTHON ?= python3
PIP ?= pip

# Enforce C++20 when compiling extensions via setuptools
CXXFLAGS_STD ?= -std=c++20

# Default target
.PHONY: all
all: develop

# Ensure src directory exists
src:
	mkdir -p src

# Generate pybinds.cpp when models.json or generator changes
src/pybinds.cpp: models.json generate_pybinds.py | src
	@echo "[codegen] Generating $@ from $<"
	$(PYTHON) generate_pybinds.py models.json $@

# Development install (editable)
.PHONY: develop
develop: src/pybinds.cpp
	@echo "[build] Installing module in editable mode"
	CXXFLAGS="$(CXXFLAGS) $(CXXFLAGS_STD)" $(PIP) install -e . -v

# Force regeneration regardless of timestamps
.PHONY: codegen
codegen: | src
	@echo "[codegen] Force regenerating src/pybinds.cpp"
	$(PYTHON) generate_pybinds.py models.json src/pybinds.cpp

# Build distributions
.PHONY: sdist wheel dist
sdist:
	$(PYTHON) -m build --sdist

wheel: src/pybinds.cpp
	CXXFLAGS="$(CXXFLAGS) $(CXXFLAGS_STD)" $(PYTHON) -m build --wheel

dist: sdist wheel

# Quick import test
.PHONY: test
test: develop
	@echo "[test] Importing module and listing available types"
	$(PYTHON) -c "import sys;\
try:\n import neun_py; print('\u2713 Module imported successfully');\
 n = getattr(neun_py, 'get_available_neurons', lambda: [])();\
 print('Available neurons:', len(n) if hasattr(n, '__len__') else 'unknown');\
 s = getattr(neun_py, 'get_available_synapses', lambda: [])();\
 print('Available synapses:', len(s) if hasattr(s, '__len__') else 'unknown')\
except Exception as e:\n print('Import/test failed:', e); sys.exit(1)"

# Serve documentation locally
.PHONY: serve
serve:
	@echo "[docs] Starting MkDocs development server"
	@command -v mkdocs >/dev/null 2>&1 || { echo "Error: mkdocs not found. Install with: pip install mkdocs-material"; exit 1; }
	mkdocs serve

# Clean generated and build artifacts
.PHONY: clean
clean:
	@echo "[clean] Removing build artifacts and generated code"
	rm -rf build/ dist/ *.egg-info
	rm -f src/pybinds.cpp
	find . -type d -name '__pycache__' -exec rm -rf {} +
