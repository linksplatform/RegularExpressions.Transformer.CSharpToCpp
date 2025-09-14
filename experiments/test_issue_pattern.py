#!/usr/bin/env python3
"""
Test script to verify the issue #28 patterns work correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from cs2cpp import CSharpToCpp

def test_issue_pattern():
    translator = CSharpToCpp()
    
    # Test the specific pattern mentioned in the issue
    test_input = """class Program { }"""
    
    result = translator.translate(test_input)
    print("Input:", test_input)
    print("Result:", result)
    print()
    
    # Test with a more complex example
    test_input2 = """struct TreeElement { };"""
    result2 = translator.translate(test_input2)
    print("Input:", test_input2)
    print("Result:", result2)
    print()
    
    # Test the multiline case
    test_input3 = """
class Program 
{
    public static void Main(string[] args)
    {
        Console.WriteLine("Hello, world!");
    }
}"""
    result3 = translator.translate(test_input3)
    print("Input:", test_input3)
    print("Result:", result3)
    print()

if __name__ == "__main__":
    test_issue_pattern()