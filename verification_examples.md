# C++ Style Improvements Verification

This document shows the transformations our regex patterns should perform:

## 1. Type Reference Style (Type& val instead of Type &val)

**Pattern:** `(?<type>std::[a-zA-Z0-9_]+|[a-zA-Z][a-zA-Z0-9_]*) &(?<var>[a-zA-Z_][a-zA-Z0-9_]*)`
**Replacement:** `${type}& ${var}`

Examples:
- `std::string &value` → `std::string& value`
- `MyType &ref` → `MyType& ref`

## 2. Type Pointer Style (Type* val instead of Type *val)

**Pattern:** `(?<type>std::[a-zA-Z0-9_]+|[a-zA-Z][a-zA-Z0-9_]*) \*(?<var>[a-zA-Z_][a-zA-Z0-9_]*)`
**Replacement:** `${type}* ${var}`

Examples:
- `int *pointer` → `int* pointer`
- `std::string *ptr` → `std::string* ptr`

## 3. Constructor std::move Pattern

**Pattern:** `(?<constructor>[a-zA-Z_][a-zA-Z0-9_]*)\((?<params>[^)]*std::string [a-zA-Z_][a-zA-Z0-9_]*[^)]*)\)(?<init>\s*:\s*[^{]*?)(?<fieldAssignment>(?<field>[a-zA-Z_][a-zA-Z0-9_]*)\((?<param>[a-zA-Z_][a-zA-Z0-9_]*)\))`
**Replacement:** `${constructor}(${params})${init}${field}(std::move(${param}))`

Examples:
- `MyClass(std::string str) : field(str)` → `MyClass(std::string str) : field(std::move(str))`

## 4. Const Reference for std::string Parameters  

**Pattern:** `(?<func>[a-zA-Z_][a-zA-Z0-9_]*)\((?<before>[^)]*?)(?<sep>(^|\(|, ))std::string (?<param>[a-zA-Z_][a-zA-Z0-9_]*)(?<after>[^)]*)\)`
**Replacement:** `${func}(${before}${sep}const std::string& ${param}${after})`

Examples:
- `function(std::string param)` → `function(const std::string& param)`
- `method(int x, std::string str)` → `method(int x, const std::string& str)`

## 5. Const Reference for Container Parameters

**Pattern:** `(?<func>[a-zA-Z_][a-zA-Z0-9_]*)\((?<before>[^)]*?)(?<sep>(^|\(|, ))std::(vector|string|unordered_set|unordered_map|set|map)<[^>]+> (?<param>[a-zA-Z_][a-zA-Z0-9_]*)(?<after>[^)]*)\)`
**Replacement:** `${func}(${before}${sep}const std::${2}<${3}>& ${param}${after})`

Examples:
- `function(std::vector<int> vec)` → `function(const std::vector<int>& vec)`

## 6. std::move for push_back

**Pattern:** `(?<container>[a-zA-Z_][a-zA-Z0-9_]*)\.push_back\((?<value>[a-zA-Z_][a-zA-Z0-9_]*)\)(?!\s*//.*const)`
**Replacement:** `${container}.push_back(std::move(${value}))`

Examples:
- `vector.push_back(value)` → `vector.push_back(std::move(value))`

## 7. Universal Reference for Templates

**Pattern:** `(?<before>template\s*<\s*typename\s+(?<typeParam>[a-zA-Z_][a-zA-Z0-9_]*)\s*>\s*[^(]*\([^)]*?)(?<type>\k<typeParam>) (?<param>[a-zA-Z_][a-zA-Z0-9_]*)(?<after>[^)]*\))`
**Replacement:** `${before}${type}&& ${param}${after}`

Examples:
- `template<typename T> void func(T arg)` → `template<typename T> void func(T&& arg)`

## 8. std::forward for Perfect Forwarding

**Pattern:** `(?<container>[a-zA-Z_][a-zA-Z0-9_]*)\.push_back\((?<param>[a-zA-Z_][a-zA-Z0-9_]*)\)(?=.*template.*\k<param>)`
**Replacement:** `${container}.push_back(std::forward<decltype(${param})>(${param}))`

Examples:
- In template context: `container.push_back(param)` → `container.push_back(std::forward<decltype(param)>(param))`

All these patterns follow modern C++ best practices as requested in the issue.