using System;
using Platform.RegularExpressions.Transformer.CSharpToCpp;

class SimpleTest 
{
    static void Main(string[] args)
    {
        var transformer = new CSharpToCppTransformer();
        
        // Test simple interface
        string simpleInterface = @"interface ISimple
{
    void Method();
}";
        
        Console.WriteLine("=== SIMPLE INTERFACE TEST ===");
        Console.WriteLine("Input:");
        Console.WriteLine(simpleInterface);
        Console.WriteLine("\nOutput:");
        Console.WriteLine(transformer.Transform(simpleInterface));
        
        // Test templated interface
        string templatedInterface = @"interface ITest<T>
{
    void Method(T value);
}";
        
        Console.WriteLine("\n=== TEMPLATED INTERFACE TEST ===");
        Console.WriteLine("Input:");
        Console.WriteLine(templatedInterface);
        Console.WriteLine("\nOutput:");
        Console.WriteLine(transformer.Transform(templatedInterface));
    }
}