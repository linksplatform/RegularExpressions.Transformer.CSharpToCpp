// Simplified Memory Management Demonstration
// Shows the three approaches discussed in the Habr article

#include <memory>
#include <iostream>
#include <vector>

// =============================================================================
// Alternative 1: Smart Pointers (Recommended Approach)
// =============================================================================

class SmartPtrNode {
public:
    int value;
    std::weak_ptr<SmartPtrNode> parent;      // Weak to avoid cycles
    std::vector<std::shared_ptr<SmartPtrNode>> children;  // Strong references
    
    SmartPtrNode(int val) : value(val) {
        std::cout << "   SmartPtrNode " << value << " created\n";
    }
    
    ~SmartPtrNode() {
        std::cout << "   SmartPtrNode " << value << " destroyed\n";
    }
    
    void addChild(std::shared_ptr<SmartPtrNode> child) {
        children.push_back(child);
        child->parent = shared_from_this();
        std::cout << "   Added child " << child->value << " to parent " << value << "\n";
    }
    
    // Enable shared_from_this
    std::shared_ptr<SmartPtrNode> getShared() {
        return shared_from_this();
    }
    
private:
    // Helper for shared_from_this (simplified)
    std::shared_ptr<SmartPtrNode> shared_from_this() {
        // In real code, this would inherit from std::enable_shared_from_this
        // For demo, we'll use a different approach
        return std::shared_ptr<SmartPtrNode>(this, [](SmartPtrNode*){}); // No-op deleter for demo
    }
};

// =============================================================================
// Alternative 2: Raw Pointers (Manual Management - Not Recommended)
// =============================================================================

class RawPtrNode {
public:
    int value;
    RawPtrNode* parent;
    std::vector<RawPtrNode*> children;
    
    RawPtrNode(int val) : value(val), parent(nullptr) {
        std::cout << "   RawPtrNode " << value << " created\n";
    }
    
    ~RawPtrNode() {
        std::cout << "   RawPtrNode " << value << " destroyed\n";
        // Manual cleanup required
        for (auto child : children) {
            delete child;
        }
    }
    
    void addChild(RawPtrNode* child) {
        children.push_back(child);
        child->parent = this;
        std::cout << "   Added child " << child->value << " to parent " << value << "\n";
    }
};

// =============================================================================
// Alternative 3: Reference Counting Simulation
// =============================================================================

class RefCountedNode {
private:
    int ref_count = 0;
    
public:
    int value;
    RefCountedNode* parent;  // Would be weak reference in practice
    std::vector<RefCountedNode*> children;
    
    RefCountedNode(int val) : value(val), parent(nullptr) {
        std::cout << "   RefCountedNode " << value << " created (refs: " << ref_count << ")\n";
    }
    
    ~RefCountedNode() {
        std::cout << "   RefCountedNode " << value << " destroyed\n";
    }
    
    void addRef() { 
        ref_count++; 
        std::cout << "   RefCountedNode " << value << " refs: " << ref_count << "\n";
    }
    
    void release() {
        ref_count--;
        std::cout << "   RefCountedNode " << value << " refs: " << ref_count << "\n";
        if (ref_count <= 0) {
            delete this;
        }
    }
    
    void addChild(RefCountedNode* child) {
        children.push_back(child);
        child->addRef();  // Add reference
        child->parent = this;
        std::cout << "   Added child " << child->value << " to parent " << value << "\n";
    }
};

// =============================================================================
// Demonstration Functions
// =============================================================================

void demonstrateSmartPointers() {
    std::cout << "=== Smart Pointers Approach (Recommended) ===\n";
    
    // Create nodes using smart pointers
    auto root = std::make_shared<SmartPtrNode>(1);
    auto child1 = std::make_shared<SmartPtrNode>(2);
    auto child2 = std::make_shared<SmartPtrNode>(3);
    
    // This approach would normally inherit from std::enable_shared_from_this
    // For simplicity, we'll just show the concept
    std::cout << "   Created root and children\n";
    
    // Smart pointers automatically handle memory cleanup
    std::cout << "   Smart pointers will automatically clean up when going out of scope\n";
}

void demonstrateRawPointers() {
    std::cout << "\n=== Raw Pointers Approach (Manual Management) ===\n";
    
    RawPtrNode* root = new RawPtrNode(10);
    RawPtrNode* child1 = new RawPtrNode(20);
    RawPtrNode* child2 = new RawPtrNode(30);
    
    root->addChild(child1);
    root->addChild(child2);
    
    std::cout << "   Manual cleanup required:\n";
    delete root;  // This will delete children too via destructor
}

void demonstrateRefCounting() {
    std::cout << "\n=== Reference Counting Approach ===\n";
    
    RefCountedNode* root = new RefCountedNode(100);
    root->addRef();  // Initial reference
    
    RefCountedNode* child = new RefCountedNode(200);
    root->addChild(child);  // This adds a reference to child
    
    std::cout << "   Releasing references:\n";
    root->release();  // Release root reference
    child->release(); // Release child reference (this should delete it)
}

void demonstrateMemoryManagementComparison() {
    std::cout << "\n=== Memory Management Strategy Comparison ===\n";
    
    std::cout << "1. Smart Pointers:\n";
    std::cout << "   + Automatic memory management\n";
    std::cout << "   + Exception safe\n";
    std::cout << "   + No memory leaks from circular references (with weak_ptr)\n";
    std::cout << "   - Slight overhead from reference counting\n";
    
    std::cout << "\n2. Raw Pointers:\n";
    std::cout << "   + Maximum performance\n";
    std::cout << "   + Direct control over memory\n";
    std::cout << "   - Manual memory management required\n";
    std::cout << "   - Prone to memory leaks and dangling pointers\n";
    
    std::cout << "\n3. Reference Counting:\n";
    std::cout << "   + Automatic cleanup when references reach zero\n";
    std::cout << "   + Deterministic destruction\n";
    std::cout << "   - Cannot handle circular references automatically\n";
    std::cout << "   - Need to manually implement reference counting\n";
    
    std::cout << "\nThe Habr article chose Smart Pointers with custom SmartPtr class\n";
    std::cout << "that can dynamically switch between strong/weak reference modes.\n";
}

int main() {
    std::cout << "Memory Management Alternatives for C# to C++ Transformation\n";
    std::cout << "===========================================================\n";
    
    demonstrateSmartPointers();
    demonstrateRawPointers();
    demonstrateRefCounting();
    demonstrateMemoryManagementComparison();
    
    return 0;
}