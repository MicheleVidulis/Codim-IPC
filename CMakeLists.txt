cmake_minimum_required(VERSION 3.2 FATAL_ERROR)

if (NOT APPLE)
set(CMAKE_C_COMPILER /usr/bin/gcc)
set(CMAKE_CXX_COMPILER /usr/bin/g++)
endif()
project(JGSL CXX)


set(LINEAR_SOLVER "CHOLMOD" CACHE STRING "Direct linear system solver to use (options: EIGEN, CHOLMOD)")
set_property(CACHE LINEAR_SOLVER PROPERTY STRINGS "EIGEN" "CHOLMOD")

set(ENABLE_FEM_SHELL ON)

add_definitions(-DSTORAGE_ENABLED_OPENMP )
if (ENABLE_FEM_SHELL)
  add_definitions(-DENABLE_FEM_SHELL)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -mfma -mbmi2 -mavx2 -fPIC -Wno-unused-variable -Wno-sign-compare -Wno-reorder")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/build")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/build")
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/CMake)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/Library)

if(NOT CMAKE_BUILD_TYPE)
    message(STATUS "No build type selected, default to RelWithAssert")
    set(CMAKE_BUILD_TYPE "RelWithAssert")
endif()

set(CMAKE_BUILD_TYPE "${CMAKE_BUILD_TYPE}" CACHE STRING "Choose the type of build. Options are: None Debug Release RelWithDebInfo MinSizeRel RelWithAssert" FORCE)


# Color output
include(UseColors)

# Make sure warnings/errors are still colorized when using Ninja for building.
if(NOT CMAKE_CXX_COMPILER_ID STREQUAL "Intel")
    add_definitions(-fdiagnostics-color=always)
endif()

# Make sure warnings/errors are still colorized when using Ninja for building.
add_definitions(-fdiagnostics-color=always)

# Export compile flags(used for autocompletion of the C++ code)
set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

# CMake plugin for vscode
include(CMakeToolsHelpers OPTIONAL)



find_package(PythonInterp 3 REQUIRED)
add_subdirectory(Externals)

set(PYBIND11_CPP_STANDARD -std=c++1z)
add_subdirectory(Externals/pybind11-master)
include_directories(Externals/flat_hash_map)
include_directories(Externals/meta/include)

pybind11_add_module(JGSL Library/EXPORTER.cpp
  Library/Math/Distance/EVCTCD/CTCD.cpp)

find_package(Eigen3 REQUIRED)
add_library(eigen INTERFACE IMPORTED)

find_package(Boost REQUIRED)

if(LINEAR_SOLVER STREQUAL "CHOLMOD")
  message("Linear solver: use CHOLMOD")
  include(onetbb)
  include(suitesparse)
  target_compile_definitions(JGSL PUBLIC CHOLMOD_DIRECT_SOLVER)
else()
  message("Linear solver: use Eigen (default)")
endif()

if(LINEAR_SOLVER STREQUAL "CHOLMOD")
  set(JGSL_DEPS partio Kokkos::kokkos cabanacore eigen amgcl TBB::tbb SuiteSparse::SuiteSparse)
else()
  set(JGSL_DEPS partio Kokkos::kokkos cabanacore eigen amgcl)
endif()

target_include_directories(JGSL SYSTEM PUBLIC ${EIGEN3_INCLUDE_DIR} ${Boost_INCLUDE_DIRS})
target_link_libraries(JGSL PUBLIC ${JGSL_DEPS})
