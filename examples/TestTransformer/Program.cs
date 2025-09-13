using System;
using Platform.RegularExpressions.Transformer.CSharpToCpp;

class TestTransformer 
{
    static void Main(string[] args)
    {
        var transformer = new CSharpToCppTransformer();
        
        // Test pragma once
        string pragmaTest = @"#pragma once
using System;

class Test
{
    public void Method() { }
}";
        
        Console.WriteLine("=== PRAGMA ONCE TEST ===");
        Console.WriteLine("Input:");
        Console.WriteLine(pragmaTest);
        Console.WriteLine("\nOutput:");
        Console.WriteLine(transformer.Transform(pragmaTest));
        
        // Test simple interface
        string simpleInterface = @"
interface ITest
{
    void Method();
}";
        
        Console.WriteLine("\n=== SIMPLE INTERFACE TEST ===");
        Console.WriteLine("Input:");
        Console.WriteLine(simpleInterface);
        Console.WriteLine("\nOutput:");
        var simpleOutput = transformer.Transform(simpleInterface);
        Console.WriteLine(simpleOutput);
        
        // Test templated interface
        string interfaceTest = @"
interface ITest<T>
{
    void Method(T value);
}";
        
        Console.WriteLine("\n=== TEMPLATED INTERFACE TEST ===");
        Console.WriteLine("Input:");
        Console.WriteLine(interfaceTest);
        Console.WriteLine("\nOutput:");
        Console.WriteLine(transformer.Transform(interfaceTest));
        
        // Test struct
        string structTest = @"struct TestStruct<T>
{
    public T Value { get; set; }
    public void Method() { }
}";
        
        Console.WriteLine("\n=== STRUCT TEST ===");
        Console.WriteLine("Input:");
        Console.WriteLine(structTest);
        Console.WriteLine("\nOutput:");
        Console.WriteLine(transformer.Transform(structTest));
    }
}
