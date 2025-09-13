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
        public void SafeHashSpecializationTest()
        {
            const string inputCode = @"
namespace Platform.Ranges
{
    template <typename T> struct Range
    {
        T Minimum;
        T Maximum;
        
        public: override std::int32_t GetHashCode()
        {
            return {Minimum, Maximum}.GetHashCode();
        }
    };
}";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(inputCode);
            
            // Should generate safe specialization syntax
            Assert.Contains("template <typename T>", actualResult);
            Assert.Contains("struct std::hash<Platform::Ranges::Range<T>>", actualResult);
            
            // Should NOT contain unsafe namespace std opening
            Assert.DoesNotContain("namespace std\n{", actualResult);
            Assert.DoesNotContain("namespace std {", actualResult);
        }
    }
}
