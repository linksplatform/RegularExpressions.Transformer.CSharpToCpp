cmake_minimum_required(VERSION 3.10)
project(CSharpToCppTransformer VERSION 1.0.0)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add compiler flags
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    add_compile_options(-Wall -Wextra -O2)
endif()

# Add the library
add_library(CSharpToCppTransformer 
    CSharpToCppTransformer.cpp
)

target_include_directories(CSharpToCppTransformer PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Add the test executable
add_executable(cs2cpp_test
    main.cpp
)

target_link_libraries(cs2cpp_test 
    CSharpToCppTransformer
)

# Add custom target for running tests
add_custom_target(run_test
    COMMAND cs2cpp_test
    DEPENDS cs2cpp_test
    COMMENT "Running C# to C++ transformer tests"
)