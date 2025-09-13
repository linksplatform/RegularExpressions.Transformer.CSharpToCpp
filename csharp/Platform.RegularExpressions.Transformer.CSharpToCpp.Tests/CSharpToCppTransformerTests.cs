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
        public void TemplateLineBreakTest()
        {
            const string inputCode = @"
struct ISetter<TValue>
{
    virtual void Set(TValue value) = 0;

    virtual ~ISetter<TValue>() = default;
};";
            const string expectedResult = @"
template <typename ...> struct ISetter;
template <typename TValue>
struct ISetter<TValue>
{
    virtual void Set(TValue value) = 0;

    virtual ~ISetter<TValue>() = default;
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(inputCode);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void InterfaceTemplateLineBreakTest()
        {
            const string inputCode = @"
interface IFactory<TProduct>
{
    TProduct Create();
};";
            const string expectedResult = @"
template <typename ...> class IFactory;
template <typename TProduct>
class IFactory<TProduct>
{
    public:
    TProduct Create();
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(inputCode);
            Assert.Equal(expectedResult, actualResult);
        }
    }
}
