using Platform.RegularExpressions.Transformer.CSharpToCpp;

var transformer = new CSharpToCppTransformer();
var input = @"class TestClass
{
    private string field;
    
    public TestClass(string stringParam)
    {
        field = stringParam;
    }
}";

Console.WriteLine("Input:");
Console.WriteLine(input);
Console.WriteLine("\nOutput:");
var result = transformer.Transform(input);
Console.WriteLine(result);