<h1 align="center">CSharpToCpp</h1>

Installation: ```pip install --upgrade cs2cpp```
Import:
```python
from cs2cpp import CSharpToCppTranslator
```

 translate code :eyes: :
```python
cscpp = CSharpToCpp()
sourceCode = """using System;
 // This is hello world program.
class Program
{
    public static void Main(string[] args)
    {
        var myFirstString = "ban";
        char*[] args = {"1", "2"};
        Console.WriteLine("Hello, world!");
    }
}"""
 print(cscpp.Transform(sourceCode)) # translate code from C# to C++!
```
