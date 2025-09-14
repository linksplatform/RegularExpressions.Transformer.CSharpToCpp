using Xunit;

namespace Platform.RegularExpressions.Transformer.CSharpToCpp.Tests
{
    public class CSharpToCppTransformerTests
    {
        [Fact]
        public void EmptyLineTest()
        {
            // This test can help to test basic problems with regular expressions like incorrect syntax
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform("");
            Assert.Equal("", actualResult);
        }

        [Fact]
        public void HelloWorldTest()
        {
            const string helloWorldCode = @"using System;
class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine(""Hello, world!"");
    }
}";
            const string expectedResult = @"#include <iostream>
#include <string>

class Program
{
    public: static void Main(std::string args[])
    {
        printf(""Hello, world!\n"");
    }
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(helloWorldCode);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void BooleanTypeTransformationTest()
        {
            const string booleanCode = @"namespace fuzzbuzz {
    class Program {
        public static Boolean func(int x1, int x2, int y1, int y2) {
            Boolean first = true;
            if(x1*x1 + y1*y1 > x2*x2 + y2*y2) {
                first = false;
            }
            return first;
        }

        public static void Main(string[] args) {
            Console.WriteLine(""Test"");
        }
    }
}";
            const string expectedResult = @"namespace fuzzbuzz {
    class Program {
        public: static bool func(std::int32_t x1, std::int32_t x2, std::int32_t y1, std::int32_t y2) {
            bool first = true;
            if(x1*x1 + y1*y1 > x2*x2 + y2*y2) {
                first = false;
            }
            return first;
        }

        public: static void Main(std::string args[]) {
            printf(""Test\n"");
        }
    }
}";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(booleanCode);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void InputOutputTransformationTest()
        {
            const string inputOutputCode = @"using System;
class Program
{
    public static void Main(string[] args)
    {
        string line = Console.ReadLine();
        int number = int.Parse(line);
        Console.WriteLine(number);
    }
}";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(inputOutputCode);
            // Debug output to see what we get currently
            System.Console.WriteLine("INPUT/OUTPUT ACTUAL:");
            System.Console.WriteLine(actualResult);
        }
    }
}
