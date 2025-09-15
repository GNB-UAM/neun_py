cmake_minimum_required(VERSION 3.15)

project(neun_py LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

# Find nlohmann/json for JSON model definitions
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    # If not found as a package, try to find the header manually
    find_path(NLOHMANN_JSON_INCLUDE_DIR NAMES 
      nlohmann/json.hpp
      HINTS "/usr/include" 
            "/usr/local/include"
            "/opt/homebrew/include"
      PATH_SUFFIXES nlohmann)
    
    if(NLOHMANN_JSON_INCLUDE_DIR)
        message(STATUS "Found nlohmann/json headers: ${NLOHMANN_JSON_INCLUDE_DIR}")
    else()
        message(WARNING "nlohmann/json not found. Install with: sudo apt install nlohmann-json3-dev (Ubuntu) or brew install nlohmann-json (macOS)")
    endif()
endif()

# Find Neun library headers
find_path(NEUN_INCLUDE_DIR NAMES 
  NeuronBase.h SystemWrapper.h
  HINTS "/usr/local/Neun/0.4.0" 
        "/usr/local/include/neun"
        "/usr/include/neun"
  PATH_SUFFIXES include)

if(NOT NEUN_INCLUDE_DIR)
  message(FATAL_ERROR "Could not find Neun headers. Set NEUN_INCLUDE_DIR manually or install Neun.")
endif()

# Find Neun library (optional - if it's header-only, this won't be needed)
find_library(NEUN_LIBRARY NAMES neun libneun
  HINTS "/usr/local/Neun/0.4.0"
        "/usr/local/lib"
        "/usr/lib"
  PATH_SUFFIXES lib lib64)

# Code generation for pybinds.cpp
set(MODELS_JSON "${CMAKE_CURRENT_SOURCE_DIR}/models.json")
set(PYBINDS_CPP "${CMAKE_CURRENT_SOURCE_DIR}/src/pybinds.cpp")
set(GENERATOR_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/generate_pybinds.py")

# Custom command to generate pybinds.cpp from models.json
add_custom_command(
    OUTPUT "${PYBINDS_CPP}"
    COMMAND python3 "${GENERATOR_SCRIPT}" "${MODELS_JSON}" "${PYBINDS_CPP}"
    DEPENDS "${MODELS_JSON}" "${GENERATOR_SCRIPT}"
    COMMENT "Generating pybinds.cpp from models.json"
    VERBATIM
)

# Create the Python module
pybind11_add_module(neun_py MODULE "${PYBINDS_CPP}")

# Include directories
target_include_directories(neun_py PRIVATE "${NEUN_INCLUDE_DIR}")

# Add nlohmann/json if found
if(nlohmann_json_FOUND)
    target_link_libraries(neun_py PRIVATE nlohmann_json::nlohmann_json)
elseif(NLOHMANN_JSON_INCLUDE_DIR)
    target_include_directories(neun_py PRIVATE "${NLOHMANN_JSON_INCLUDE_DIR}")
endif()

# Link libraries (only if NEUN_LIBRARY was found)
if(NEUN_LIBRARY)
    target_link_libraries(neun_py PRIVATE "${NEUN_LIBRARY}")
    message(STATUS "Found Neun library: ${NEUN_LIBRARY}")
else()
    message(STATUS "Neun library not found - assuming header-only library")
endif()

# Set module properties correctly for pybind11
set_target_properties(neun_py PROPERTIES 
    PREFIX ""
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
)

# Installation
install(TARGETS neun_py
        DESTINATION ${CMAKE_INSTALL_PREFIX})

# Print configuration summary
message(STATUS "=== Neun Python Bindings Configuration ===")
message(STATUS "Neun include directory: ${NEUN_INCLUDE_DIR}")
message(STATUS "Python executable: ${PYTHON_EXECUTABLE}")
message(STATUS "Python version: ${PYTHON_VERSION}")
message(STATUS "pybind11 version: ${pybind11_VERSION}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "===========================================")