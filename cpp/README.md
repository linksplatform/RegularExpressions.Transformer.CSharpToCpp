# C++ Version of CSharpToCppTransformer

This directory contains the C++ implementation of the CSharpToCppTransformer, created as part of solving issue #42 - "Translate itself to C++".

## Overview

The C++ version implements the same core functionality as the original C# version, using a subset of the most important transformation rules. It demonstrates the concept of the transformer translating itself from C# to C++.

## Architecture

The C++ implementation follows the same architecture as the C# version:

- **`SubstitutionRule`**: Represents a single transformation rule with a regex pattern, replacement string, and optional repeat count
- **`TextTransformer`**: Base class that applies a collection of substitution rules to transform text
- **`CSharpToCppTransformer`**: Main transformer class with predefined rules for C# to C++ conversion

## Key Features Implemented

The C++ version includes transformation rules for:

- **Comments removal**: Removes C# single-line comments (`//`)
- **Using statements**: Removes `using` directives
- **Type conversions**: 
  - `string` → `std::string`
  - `null` → `nullptr`
  - `default` → `0`
  - `object` → `void*`
- **Console output**: `Console.WriteLine()` → `printf()`
- **Access modifiers**: `public` → `public:`
- **Namespace separators**: `.` → `::`
- **Exception types**: Various C# exceptions → C++ standard exceptions
- **Language constructs**: `new` keyword removal, `ToString()` conversion

## Building

### Using Make
```bash
make
```

### Using CMake
```bash
mkdir build
cd build
cmake ..
make
```

## Testing

Run the test program:
```bash
./cs2cpp_test
```

The test program demonstrates:
1. Basic transformation rules
2. Hello World program transformation
3. Self-translation concept proof

## Example Usage

```cpp
#include "CSharpToCppTransformer.h"

using namespace Platform::RegularExpressions::Transformer::CSharpToCpp;

int main() {
    CSharpToCppTransformer transformer;
    
    std::string csharpCode = R"(
        using System;
        class Example {
            public void Test() {
                string message = "Hello";
                if (message != null) {
                    Console.WriteLine(message);
                }
            }
        }
    )";
    
    std::string cppCode = transformer.Transform(csharpCode);
    std::cout << cppCode << std::endl;
    
    return 0;
}
```

## Comparison with Original

While the original C# version contains hundreds of sophisticated transformation rules, this C++ version implements the most essential ones to demonstrate the core concept. The simplified approach makes it more maintainable while still showcasing the self-translation capability.

## Future Enhancements

The C++ version can be extended with:
- More comprehensive regex patterns (matching the original C# complexity)
- Generic type transformations
- Advanced language construct conversions
- Better error handling and validation

## Files

- `CSharpToCppTransformer.h` - Header file with class declarations
- `CSharpToCppTransformer.cpp` - Implementation of the transformer
- `main.cpp` - Test program demonstrating functionality
- `Makefile` - Build configuration for Make
- `CMakeLists.txt` - Build configuration for CMake
- `README.md` - This documentation file