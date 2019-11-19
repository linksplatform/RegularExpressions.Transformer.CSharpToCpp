import cs2cpp

cpp = cs2cpp.CSharpToCpp(useRegex=1)

print(cpp.Transform("""using System;

// This is hello world program.
class Program
{
    public static void Main(string[] args)
    {
        var myFirstString = "ban";
        char*[] args = {"1", "2"};
        Console.WriteLine("Hello, world!");
    }
}"""))