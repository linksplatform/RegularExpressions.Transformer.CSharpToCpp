#!/usr/bin/env python3
import sys
sys.path.append('../python')

from cs2cpp.cs2cpp import CSharpToCpp

def test_include_generation():
    print("Testing Python include generation...")
    
    transformer = CSharpToCpp()
    
    # Simple test with just std::string
    test_code = "class Test { string name; }"
    
    try:
        result = transformer.translate(test_code)
        print(f"Input: {test_code}")
        print(f"Output: {result}")
        
        if "#include <string>" in result:
            print("✓ Include generation working!")
        else:
            print("✗ Include generation not working")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_include_generation()