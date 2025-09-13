using System;
using Platform.RegularExpressions.Transformer.CSharpToCpp;

class Program
{
    static void Main()
    {
        var transformer = new CSharpToCppTransformer();
        
        string input = @"
namespace Platform.Ranges
{
    public struct Range<T>
    {
        public T Minimum;
        public T Maximum;
        
        public override int GetHashCode()
        {
            return {Minimum, Maximum}.GetHashCode();
        }
    }
}";

        string result = transformer.Transform(input);
        Console.WriteLine("===== TRANSFORMED OUTPUT =====");
        Console.WriteLine(result);
        
        // Check if we have the new safe specialization syntax
        if (result.Contains("template <typename T>") && result.Contains("struct std::hash<"))
        {
            Console.WriteLine("\n✅ SUCCESS: Safe specialization pattern detected!");
            if (!result.Contains("namespace std\n{"))
            {
                Console.WriteLine("✅ SUCCESS: No unsafe namespace std usage detected!");
            }
        }
        else
        {
            Console.WriteLine("\n❌ FAILURE: Safe specialization pattern not found!");
        }
    }
}