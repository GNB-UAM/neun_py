# filepath: /home/alareo/workspace/Research/neun_py/neun_py/build.sh
#!/bin/bash
#
# Build script for neun_py with automatic code generation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== neun_py Build Script ===${NC}"


# Show usage options
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo -e "${BLUE}Build options:${NC}"
    echo -e "  ./build.sh          - Normal build (regenerate only if needed)"
    echo -e "  ./build.sh --help   - Show build options"
    echo -e "  ./build.sh --test   - Run tests after building the library"
    echo -e "  ./build.sh --force   - Force regeneration of pybinds.cpp"
    exit 0
fi

# Check if required files exist
if [ ! -f "models.json" ]; then
    echo -e "${RED}Error: models.json not found${NC}"
    exit 1
fi

if [ ! -f "generate_pybinds.py" ]; then
    echo -e "${RED}Error: generate_pybinds.py not found${NC}"
    exit 1
fi

# Create directories if they don't exist
mkdir -p src

# Check if pybinds.cpp needs regeneration
NEEDS_REGEN=false

if [ ! -f "src/pybinds.cpp" ]; then
    echo -e "${YELLOW}pybinds.cpp does not exist, will generate${NC}"
    NEEDS_REGEN=true
elif [ "models.json" -nt "src/pybinds.cpp" ]; then
    echo -e "${YELLOW}models.json is newer than pybinds.cpp, will regenerate${NC}"
    NEEDS_REGEN=true
elif [ "generate_pybinds.py" -nt "src/pybinds.cpp" ]; then
    echo -e "${YELLOW}generate_pybinds.py is newer than pybinds.cpp, will regenerate${NC}"
    NEEDS_REGEN=true
else
    echo -e "${GREEN}pybinds.cpp is up to date${NC}"
fi

# Force regeneration if --force flag is provided
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    echo -e "${YELLOW}Force regeneration requested${NC}"
    NEEDS_REGEN=true
fi

# Regenerate pybinds.cpp if needed
if [ "$NEEDS_REGEN" = true ]; then
    echo -e "${BLUE}Step 1: Regenerating pybinds.cpp from models.json...${NC}"
    python3 generate_pybinds.py models.json src/pybinds.cpp
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to generate pybinds.cpp${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ pybinds.cpp generated successfully${NC}"
else
    echo -e "${BLUE}Step 1: Skipping regeneration (pybinds.cpp is up to date)${NC}"
fi

# Build and install Python module using setuptools (no CMake needed)
echo -e "${BLUE}Step 2: Building and installing Python module...${NC}"

# Install in development mode for easy testing
pip install -e . -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Python module installation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python module installed successfully${NC}"

# Test if --test flag is provided
if [ "$1" = "--test" ] || [ "$1" = "-f" ]; then
    echo -e "${YELLOW}Force regeneration requested${NC}"
    DO_TEST=true
fi

if [ "$DO_TEST" = true ]; then
    # Test the installation
    echo -e "${BLUE}Step 3: Testing installation...${NC}"
    python3 -c "import neun_py; print('✓ Module imported successfully'); print('Available neurons:', len(neun_py.get_available_neurons())); print('Available synapses:', len(neun_py.get_available_synapses()))"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Installation test failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Installation test passed${NC}"

    echo -e "${GREEN}=== Build completed successfully! ===${NC}"
    echo -e "${BLUE}Usage:${NC}"
    echo -e "  import neun_py"
    echo -e "  neuron = neun_py.HHDoubleRK4()"
    echo -e "  python3 examples/basic.py --output basic.dat"
fi
