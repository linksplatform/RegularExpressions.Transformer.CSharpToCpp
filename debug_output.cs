using System;
using Platform.RegularExpressions.Transformer.CSharpToCpp;

class Program
{
    static void Main()
    {
        var transformer = new CSharpToCppTransformer();
        
        const string csharpCode1 = @"class Range<T>
{
    public Range(T value) => { _value = value; };
    public static implicit operator Range<T>(T value) { return new Range<T>(value); }
}";
        
        const string csharpCode2 = @"class Range<T>
{
    public static implicit operator std::tuple<T, T>(Range<T> range) { return (range.Min, range.Max); }
}";
        
        Console.WriteLine("=== Test 1: Constructor ===");
        Console.WriteLine(transformer.Transform(csharpCode1));
        Console.WriteLine("\n=== Test 2: Operator ===");
        Console.WriteLine(transformer.Transform(csharpCode2));
    }
}