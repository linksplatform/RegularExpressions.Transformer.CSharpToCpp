// Test cases for readonly transformations
public class TestClass
{
    // Test string readonly
    public static readonly string ExceptionContentsSeparator = "---";
    private static readonly string PrivateMessage = "error";
    
    // Test other types readonly
    public static readonly int MaxPath = 92;
    private static readonly bool IsEnabled = true;
    
    // Test const (should already work)
    private const int ConstValue = 42;
    public const string ConstString = "test";
}