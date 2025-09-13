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
        public void BigTypeParametersTest()
        {
            // Test a simple case first - just std::string
            const string code = @"void function(std::string name)";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(code);
            
            // Check that std::string becomes const std::string&
            Assert.Contains("const std::string& name", actualResult);
        }

        [Fact]
        public void UniversalReferenceParametersTest()
        {
            const string code = @"void function(auto&& param)
{
    // body
}";
            const string expectedResult = @"void function(auto&& param)
{
    // body
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(code);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void StdForwardTest()
        {
            const string code = @"void function(auto&& param)
{
    list.push_back(param);
}";
            const string expectedResult = @"void function(auto&& param)
{
    list.push_back(std::forward<decltype(param)>(param));
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(code);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void MixedParameterTypesTest()
        {
            const string code = @"void function(std::vector<big_type> list, big_type case1, const big_type& case2, auto&& case3)
{
    list.push_back(case1);
    list.push_back(case2);
    list.push_back(case3);
}";
            const string expectedResult = @"void function(const std::vector<big_type>& list, const big_type& case1, const big_type& case2, auto&& case3)
{
    list.push_back(std::forward<decltype(case1)>(case1));
    list.push_back(std::forward<decltype(case2)>(case2));
    list.push_back(std::forward<decltype(case3)>(case3));
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(code);
            Assert.Equal(expectedResult, actualResult);
        }
    }
}
