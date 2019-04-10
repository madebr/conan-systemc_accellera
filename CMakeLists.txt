cmake_minimum_required(VERSION 3.0)
project(conan_systemc)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_subdirectory(source_subfolder)
