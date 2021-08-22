using Xunit;

namespace Platform.RegularExpressions.Transformer.CSharpToCpp.Tests
{
    /// <summary>
    /// <para>
    /// Represents the sharp to cpp transformer tests.
    /// </para>
    /// <para></para>
    /// </summary>
    public class CSharpToCppTransformerTests
    {
        /// <summary>
        /// <para>
        /// Tests that empty line test.
        /// </para>
        /// <para></para>
        /// </summary>
        [Fact]
        public void EmptyLineTest()
        {
            // This test can help to test basic problems with regular expressions like incorrect syntax
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform("");
            Assert.Equal("", actualResult);
        }

        /// <summary>
        /// <para>
        /// Tests that hello world test.
        /// </para>
        /// <para></para>
        /// </summary>
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
    }
}
