using System;
using Platform.RegularExpressions.Transformer.CSharpToCpp;

public class Debug2
{
    public static void Main()
    {
        const string inputCode = @"using System;

class Test
{
    private string message;
    private Func<int> getNumber;
    
    public int GetMaxValue()
    {
        return int.MaxValue;
    }
    
    public void ProcessException(Exception ex)
    {
        // Handle exception
    }
}";
        var transformer = new CSharpToCppTransformer();
        var actualResult = transformer.TransformWithIncludes(inputCode);
        Console.WriteLine("ACTUAL OUTPUT:");
        Console.WriteLine("==============");
        Console.WriteLine(actualResult);
        Console.WriteLine("==============");
    }
}