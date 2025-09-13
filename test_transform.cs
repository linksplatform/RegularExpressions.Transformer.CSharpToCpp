using System;

namespace TestApp 
{
    class Program
    {
        static void Main()
        {
            var transformer = new Platform.RegularExpressions.Transformer.CSharpToCpp.CSharpToCppTransformer();
            
            const string csharpCode1 = @"class Range<T>
{
    public Range(T value) => { _value = value; };
    public static implicit operator Range<T>(T value) { return new Range<T>(value); }
}";
            
            Console.WriteLine("=== Test 1: Constructor ===");
            string result1 = transformer.Transform(csharpCode1);
            Console.WriteLine(result1);
        }
    }
}