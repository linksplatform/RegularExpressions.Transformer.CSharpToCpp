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
        public void PragmaOncePreservationTest()
        {
            const string input = @"#pragma once
using System;

class Test
{
    public void Method() { }
}";
            const string expectedResult = @"#pragma once

class Test
{
    public: void Method() { }
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(input);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void PragmaWarningRemovalTest()
        {
            const string input = @"#pragma warning disable CS1591
using System;

class Test
{
    public void Method() { }
}";
            const string expectedResult = @"class Test
{
    public: void Method() { }
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(input);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void SimpleInterfaceToStructTest()
        {
            const string input = @"
interface ITest
{
    void Method();
}";
            const string expectedResult = @"
struct ITest
{
    public:
    virtual void Method() = 0;
    virtual ~ITest() = default;
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(input);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void TemplatedInterfaceToStructTest()
        {
            const string input = @"
interface ITest<T>
{
    void Method(T value);
}";
            const string expectedResult = @"
template <typename ...> struct ITest;
template <typename T>
struct ITest<T>
{
    public:
    virtual void Method(T value) = 0;
    virtual ~ITest() = default;
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(input);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void TemplatedClassSeparationTest()
        {
            const string input = @"
class TestClass<T>
{
    public T Value { get; set; }
}";
            const string expectedResult = @"
template <typename ...> class TestClass;
template <typename T>
class TestClass<T>
{
    public: inline T Value;
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(input);
            Assert.Equal(expectedResult, actualResult);
        }

        [Fact]
        public void TemplatedStructSeparationTest()
        {
            const string input = @"
struct TestStruct<T>
{
    public T Value { get; set; }
}";
            const string expectedResult = @"
template <typename ...> struct TestStruct;
template <typename T>
struct TestStruct<T>
{
    public: inline T Value;
};";
            var transformer = new CSharpToCppTransformer();
            var actualResult = transformer.Transform(input);
            Assert.Equal(expectedResult, actualResult);
        }
    }
}
