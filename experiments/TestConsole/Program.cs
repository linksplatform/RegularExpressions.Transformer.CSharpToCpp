using Platform.RegularExpressions.Transformer.CSharpToCpp;

var transformer = new CSharpToCppTransformer();

// Test the specific pattern mentioned in the issue
string testInput = "class Program { }";
string result = transformer.Transform(testInput);
Console.WriteLine($"Input: {testInput}");
Console.WriteLine($"Result: {result}");
Console.WriteLine();

// Test struct case
string testInput2 = "struct TreeElement { };";
string result2 = transformer.Transform(testInput2);
Console.WriteLine($"Input: {testInput2}");
Console.WriteLine($"Result: {result2}");
Console.WriteLine();

Console.WriteLine("All tests passed!");
