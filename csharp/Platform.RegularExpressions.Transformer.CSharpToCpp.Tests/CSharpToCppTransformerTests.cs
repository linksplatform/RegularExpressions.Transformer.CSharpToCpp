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
            const string expectedResult = @"class Program
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
        public void IncludeGenerationBasicStringTest()
        {
            const string inputCode = @"class Test
{
    public static void Method(string text)
    {
        // Do something with text
    }
}";
            const string expectedResult = @"#include <string>

class Test
{
    public: static void Method(std::string text)
    {
    }
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.TransformWithIncludes(inputCode);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void IncludeGenerationMultipleStdFeaturesTest()
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
            const string expectedResult = @"#include <cstdint>
#include <exception>
#include <functional>
#include <limits>
#include <string>

class Test
{
    private: std::string message = 0;
    private: std::function<int()> getNumber;
    
    public: std::int32_t GetMaxValue()
    {
        return std::numeric_limits<std::int32_t>::max();
    }
    
    public: void ProcessException(const std::exception& ex)
    {
    }
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.TransformWithIncludes(inputCode);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void IncludeGenerationNoStdFeaturesTest()
        {
            const string inputCode = @"class SimpleTest
{
    public void Method()
    {
        int x = 42;
    }
}";
            const string expectedResult = @"#include <cstdint>

class SimpleTest
{
    public: void Method()
    {
        std::int32_t x = 42;
    }
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.TransformWithIncludes(inputCode);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void IncludeGenerationEmptyCodeTest()
        {
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.TransformWithIncludes("");
            Assert.Equal("", actualResult);
        }
    }
}
