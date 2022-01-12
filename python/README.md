<div align="center">

# CSharpToCpp
### Simple C# to C++ translator written in Python

</div>


## Get Started
### Install
```pip install --upgrade cs2cpp```

### Usage
```python
from cs2cpp import CSharpToCpp

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
print(cscpp.translate(sourceCode)) # translate code from C# to C++!
```
