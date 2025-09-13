#!/usr/bin/env python3
"""
Demonstration of Alternative C# to C++ Transformation Approaches
This script shows different strategies beyond the current regex-based approach.
"""

import re
import ast
from typing import List, Dict, Any
from dataclasses import dataclass

# =============================================================================
# Current Approach: Regex-based Transformation (Existing)
# =============================================================================

class RegexBasedTransformer:
    """Current approach using regex patterns for transformation"""
    
    def __init__(self):
        self.rules = [
            # Basic namespace conversion
            (r'namespace\s+([^{]+)', r'namespace \1'),
            (r'\.', r'::'),
            
            # Access modifiers
            (r'public\s+(?!class|interface|struct)', r'public: '),
            (r'private\s+(?!class|interface|struct)', r'private: '),
            
            # Smart pointer insertion
            (r'(\w+)\s+(\w+)\s*=\s*new\s+\w+\([^)]*\)', r'std::unique_ptr<\1> \2 = std::make_unique<\1>()'),
        ]
    
    def transform(self, csharp_code: str) -> str:
        """Apply regex transformations"""
        cpp_code = csharp_code
        for pattern, replacement in self.rules:
            cpp_code = re.sub(pattern, replacement, cpp_code)
        return cpp_code

# =============================================================================
# Alternative 1: AST-Based Transformation
# =============================================================================

@dataclass
class ClassDeclaration:
    name: str
    members: List[str]
    access_modifiers: Dict[str, str]

@dataclass
class MethodDeclaration:
    name: str
    return_type: str
    parameters: List[str]
    body: str

class ASTBasedTransformer:
    """Enhanced approach using abstract syntax tree analysis"""
    
    def __init__(self):
        self.memory_management_strategy = "smart_pointers"
        self.include_gc_simulation = False
    
    def parse_csharp_class(self, csharp_code: str) -> ClassDeclaration:
        """Simulate parsing C# class into structured representation"""
        # This is a simplified simulation - real implementation would use
        # a proper C# parser like Roslyn
        
        class_match = re.search(r'class\s+(\w+)', csharp_code)
        class_name = class_match.group(1) if class_match else "UnknownClass"
        
        # Extract members (simplified)
        members = re.findall(r'(public|private|protected)\s+\w+\s+(\w+)', csharp_code)
        
        return ClassDeclaration(
            name=class_name,
            members=[member[1] for member in members],
            access_modifiers={member[1]: member[0] for member in members}
        )
    
    def generate_cpp_class(self, class_decl: ClassDeclaration) -> str:
        """Generate C++ class from AST representation"""
        cpp_code = f"class {class_decl.name} {{\n"
        
        # Group by access modifier
        access_sections = {"public": [], "private": [], "protected": []}
        
        for member in class_decl.members:
            access = class_decl.access_modifiers.get(member, "private")
            
            # Apply memory management strategy
            if self.memory_management_strategy == "smart_pointers":
                member_decl = f"    std::unique_ptr<Object> {member};"
            elif self.memory_management_strategy == "raw_pointers":
                member_decl = f"    Object* {member};"
            else:
                member_decl = f"    Object {member};"
            
            access_sections[access].append(member_decl)
        
        # Generate sections
        for access in ["public", "private", "protected"]:
            if access_sections[access]:
                cpp_code += f"{access}:\n"
                cpp_code += "\n".join(access_sections[access]) + "\n"
        
        cpp_code += "};"
        return cpp_code

# =============================================================================
# Alternative 2: Memory Management Strategy Injection
# =============================================================================

class MemoryManagementInjector:
    """Specialized transformer for injecting memory management patterns"""
    
    def __init__(self, strategy: str = "smart_pointers"):
        self.strategy = strategy
        self.circular_ref_detector = CircularReferenceDetector()
    
    def inject_smart_pointers(self, cpp_code: str) -> str:
        """Inject smart pointer usage patterns"""
        transformations = {
            # Convert raw pointer declarations
            r'(\w+)\*\s+(\w+)': r'std::unique_ptr<\1> \2',
            
            # Convert new expressions
            r'new\s+(\w+)\(([^)]*)\)': r'std::make_unique<\1>(\2)',
            
            # Add weak_ptr for potential circular references
            # This would require more sophisticated analysis in practice
        }
        
        result = cpp_code
        for pattern, replacement in transformations.items():
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def inject_gc_simulation(self, cpp_code: str) -> str:
        """Inject garbage collection simulation (not recommended)"""
        header = """
// GC simulation headers (NOT RECOMMENDED)
#include <unordered_set>
#include <memory>

class GCBase {
    static std::unordered_set<GCBase*> live_objects;
public:
    GCBase() { live_objects.insert(this); }
    virtual ~GCBase() { live_objects.erase(this); }
    static void collect() {
        // Simplified mark-and-sweep simulation
        // Real implementation would be much more complex
    }
};
std::unordered_set<GCBase*> GCBase::live_objects;

"""
        return header + cpp_code

# =============================================================================
# Alternative 3: Circular Reference Detection
# =============================================================================

class CircularReferenceDetector:
    """Analyze code for potential circular reference patterns"""
    
    def __init__(self):
        self.dependency_graph = {}
    
    def analyze_dependencies(self, cpp_code: str) -> Dict[str, List[str]]:
        """Build dependency graph from code analysis"""
        # Simplified analysis - real implementation would be more sophisticated
        classes = re.findall(r'class\s+(\w+)', cpp_code)
        
        for class_name in classes:
            # Find member references to other classes
            class_section = self.extract_class_section(cpp_code, class_name)
            references = re.findall(r'std::(?:unique_ptr|shared_ptr)<(\w+)>', class_section)
            self.dependency_graph[class_name] = references
        
        return self.dependency_graph
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def extract_class_section(self, code: str, class_name: str) -> str:
        """Extract the section of code containing a specific class"""
        # Simplified extraction
        pattern = rf'class\s+{class_name}\s*{{[^}}]*}}'
        match = re.search(pattern, code, re.DOTALL)
        return match.group(0) if match else ""

# =============================================================================
# Alternative 4: Runtime Library Generator
# =============================================================================

class RuntimeLibraryGenerator:
    """Generate C++ runtime library equivalent to C# BCL classes"""
    
    def generate_string_class(self) -> str:
        """Generate System.String equivalent"""
        return """
// C# System.String equivalent
class String {
private:
    std::string data_;
    
public:
    String(const std::string& str) : data_(str) {}
    String(const char* str) : data_(str) {}
    
    // C# String methods
    int Length() const { return data_.length(); }
    String Substring(int start) const { return String(data_.substr(start)); }
    String Substring(int start, int length) const { 
        return String(data_.substr(start, length)); 
    }
    bool Contains(const String& other) const {
        return data_.find(other.data_) != std::string::npos;
    }
    String ToUpper() const {
        std::string result = data_;
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return String(result);
    }
    
    // Operators
    String operator+(const String& other) const {
        return String(data_ + other.data_);
    }
    bool operator==(const String& other) const {
        return data_ == other.data_;
    }
    
    // Conversion
    const std::string& toCppString() const { return data_; }
};
"""
    
    def generate_list_class(self) -> str:
        """Generate System.Collections.Generic.List<T> equivalent"""
        return """
// C# List<T> equivalent
template<typename T>
class List {
private:
    std::vector<T> data_;
    
public:
    List() = default;
    List(std::initializer_list<T> init) : data_(init) {}
    
    // C# List<T> methods
    void Add(const T& item) { data_.push_back(item); }
    void Remove(const T& item) {
        auto it = std::find(data_.begin(), data_.end(), item);
        if (it != data_.end()) data_.erase(it);
    }
    int Count() const { return data_.size(); }
    bool Contains(const T& item) const {
        return std::find(data_.begin(), data_.end(), item) != data_.end();
    }
    void Clear() { data_.clear(); }
    
    // Indexer
    T& operator[](int index) { return data_[index]; }
    const T& operator[](int index) const { return data_[index]; }
    
    // Iterators for range-based for loops
    auto begin() { return data_.begin(); }
    auto end() { return data_.end(); }
    auto begin() const { return data_.begin(); }
    auto end() const { return data_.end(); }
};
"""

# =============================================================================
# Demonstration and Testing
# =============================================================================

def demonstrate_alternatives():
    """Demonstrate all alternative approaches"""
    
    # Sample C# code for transformation
    sample_csharp = """
public class MyClass {
    public string Name { get; set; }
    private List<int> numbers;
    public MyClass reference;
    
    public MyClass(string name) {
        Name = name;
        numbers = new List<int>();
    }
    
    public void AddNumber(int num) {
        numbers.Add(num);
    }
}
"""
    
    print("=== C# to C++ Transformation Alternatives Demo ===\n")
    
    # 1. Current Regex Approach
    print("1. Current Regex-based Approach:")
    regex_transformer = RegexBasedTransformer()
    regex_result = regex_transformer.transform(sample_csharp)
    print(regex_result[:200] + "..." if len(regex_result) > 200 else regex_result)
    print()
    
    # 2. AST-based Approach
    print("2. AST-based Approach:")
    ast_transformer = ASTBasedTransformer()
    class_decl = ast_transformer.parse_csharp_class(sample_csharp)
    ast_result = ast_transformer.generate_cpp_class(class_decl)
    print(ast_result)
    print()
    
    # 3. Memory Management Injection
    print("3. Memory Management Strategy Injection:")
    mm_injector = MemoryManagementInjector("smart_pointers")
    cpp_with_smart_ptrs = mm_injector.inject_smart_pointers("""
    MyClass* obj = new MyClass("test");
    AnotherClass* ref = obj;
    """)
    print(cpp_with_smart_ptrs)
    print()
    
    # 4. Circular Reference Detection
    print("4. Circular Reference Detection:")
    detector = CircularReferenceDetector()
    sample_cpp_with_refs = """
    class A {
        std::shared_ptr<B> b_ref;
    };
    class B {
        std::shared_ptr<A> a_ref;
    };
    """
    dependencies = detector.analyze_dependencies(sample_cpp_with_refs)
    cycles = detector.detect_cycles()
    print(f"Dependencies: {dependencies}")
    print(f"Detected cycles: {cycles}")
    print()
    
    # 5. Runtime Library Generation
    print("5. Runtime Library Generation:")
    runtime_gen = RuntimeLibraryGenerator()
    string_class = runtime_gen.generate_string_class()
    print(string_class[:300] + "..." if len(string_class) > 300 else string_class)
    
    print("\n=== Demo completed ===")
    
    print("""
Summary of Alternative Approaches:

1. Current Regex Approach:
   - Fast and simple
   - Limited semantic understanding
   - Good for syntax transformations

2. AST-based Approach:
   - Better semantic understanding
   - More accurate transformations
   - Slower but more reliable

3. Memory Management Injection:
   - Specialized for memory safety
   - Can handle smart pointer insertion
   - Addresses C#/C++ memory model differences

4. Circular Reference Detection:
   - Prevents memory leaks
   - Enables weak pointer optimization
   - Essential for complex object graphs

5. Runtime Library:
   - Provides C#-like APIs in C++
   - Eases migration burden
   - Maintains familiar programming model

These approaches can be combined for a comprehensive transformation solution.
""")

if __name__ == "__main__":
    demonstrate_alternatives()