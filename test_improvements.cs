using System;
using Platform.RegularExpressions.Transformer.CSharpToCpp;

class TestProgram
{
    static void Main()
    {
        var transformer = new CSharpToCppTransformer();
        
        // Test 1: Type& val style
        string input1 = "void function(std::string &value) { }";
        string result1 = transformer.Transform(input1);
        Console.WriteLine("Test 1 - Type& val style:");
        Console.WriteLine($"Input:  {input1}");
        Console.WriteLine($"Output: {result1}");
        Console.WriteLine();
        
        // Test 2: Type* val style  
        string input2 = "void function(int *pointer) { }";
        string result2 = transformer.Transform(input2);
        Console.WriteLine("Test 2 - Type* val style:");
        Console.WriteLine($"Input:  {input2}");
        Console.WriteLine($"Output: {result2}");
        Console.WriteLine();
        
        // Test 3: const& for string parameters
        string input3 = "void function(std::string value) { }";
        string result3 = transformer.Transform(input3);
        Console.WriteLine("Test 3 - const& for string parameters:");
        Console.WriteLine($"Input:  {input3}");
        Console.WriteLine($"Output: {result3}");
        Console.WriteLine();
        
        // Test 4: std::move for push_back
        string input4 = "vector.push_back(value);";
        string result4 = transformer.Transform(input4);
        Console.WriteLine("Test 4 - std::move for push_back:");
        Console.WriteLine($"Input:  {input4}");
        Console.WriteLine($"Output: {result4}");
        Console.WriteLine();
    }
}