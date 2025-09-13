#include "CSharpToCppTransformer.h"
#include <algorithm>

namespace Platform::RegularExpressions::Transformer::CSharpToCpp
{
    // SubstitutionRule implementation
    SubstitutionRule::SubstitutionRule(const std::string& pattern, const std::string& replacement, int maxRepeat)
        : _pattern(pattern), _replacement(replacement), _maxRepeat(maxRepeat)
    {
    }

    std::string SubstitutionRule::Apply(const std::string& text) const
    {
        std::string result = text;
        int repeatCount = 0;
        
        if (_maxRepeat == 0)
        {
            // Apply once
            result = std::regex_replace(result, _pattern, _replacement);
        }
        else
        {
            // Apply up to maxRepeat times
            while (repeatCount < _maxRepeat && std::regex_search(result, _pattern))
            {
                result = std::regex_replace(result, _pattern, _replacement);
                repeatCount++;
            }
        }
        
        return result;
    }

    // TextTransformer implementation
    TextTransformer::TextTransformer(const std::vector<SubstitutionRule>& rules)
        : _rules(rules)
    {
    }

    std::string TextTransformer::Transform(const std::string& text)
    {
        std::string result = text;
        
        for (const auto& rule : _rules)
        {
            result = rule.Apply(result);
        }
        
        return result;
    }

    // CSharpToCppTransformer implementation
    std::vector<SubstitutionRule> CSharpToCppTransformer::CreateFirstStageRules()
    {
        return {
            // Remove single-line comments
            SubstitutionRule(R"(//.*)", "", 0),
            
            // Remove pragma directives
            SubstitutionRule(R"(#pragma.*)", "", 0),
            
            // Using statement removal
            SubstitutionRule(R"(using [^;]+;)", "", 0),
            
            // String type conversion
            SubstitutionRule(R"(\bstring\b)", "std::string", 0),
            
            // String array conversion
            SubstitutionRule(R"(std::string\[\] ([a-zA-Z0-9]+))", "std::string $1[]", 0),
            
            // Console.WriteLine conversion  
            SubstitutionRule(R"(Console\.WriteLine\(\"([^"]*)\"\);)", "printf(\"$1\\n\");", 0),
            
            // Access modifier conversion - simplified
            SubstitutionRule(R"((public|private|protected) ([a-zA-Z]))", "$1: $2", 0),
            
            // Class/interface/struct declaration cleanup
            SubstitutionRule(R"((public|protected|private|internal|abstract|static) +(interface|class|struct))", "$2", 0),
            
            // Namespace separator conversion
            SubstitutionRule(R"(namespace ([a-zA-Z0-9]+)\.([a-zA-Z0-9\.]+))", "namespace $1::$2", 0),
            
            // nameof conversion - simplified
            SubstitutionRule(R"(nameof\(([a-zA-Z0-9_]+)\))", "\"$1\"", 0)
        };
    }

    std::vector<SubstitutionRule> CSharpToCppTransformer::CreateLastStageRules()
    {
        return {
            // null conversion
            SubstitutionRule(R"(\bnull\b)", "nullptr", 0),
            
            // default conversion
            SubstitutionRule(R"(\bdefault\b)", "0", 0),
            
            // object type conversion
            SubstitutionRule(R"(\bobject\b)", "void*", 0),
            SubstitutionRule(R"(System\.Object)", "void*", 0),
            
            // new keyword removal
            SubstitutionRule(R"(\bnew\s+)", "", 0),
            
            // ToString conversion
            SubstitutionRule(R"(([a-zA-Z0-9_]+)\.ToString\(\))", "Platform::Converters::To<std::string>($1).data()", 0),
            
            // Exception type conversions
            SubstitutionRule(R"(ArgumentNullException)", "std::invalid_argument", 0),
            SubstitutionRule(R"(System\.ArgumentNullException)", "std::invalid_argument", 0),
            SubstitutionRule(R"(InvalidOperationException)", "std::runtime_error", 0),
            SubstitutionRule(R"(ArgumentException)", "std::invalid_argument", 0),
            SubstitutionRule(R"(ArgumentOutOfRangeException)", "std::invalid_argument", 0),
            SubstitutionRule(R"(\bException\b)", "std::runtime_error", 0)
        };
    }

    const std::vector<SubstitutionRule> CSharpToCppTransformer::FirstStage = CreateFirstStageRules();
    const std::vector<SubstitutionRule> CSharpToCppTransformer::LastStage = CreateLastStageRules();

    CSharpToCppTransformer::CSharpToCppTransformer()
        : TextTransformer([&]() {
            std::vector<SubstitutionRule> allRules;
            allRules.insert(allRules.end(), FirstStage.begin(), FirstStage.end());
            allRules.insert(allRules.end(), LastStage.begin(), LastStage.end());
            return allRules;
        }())
    {
    }

    CSharpToCppTransformer::CSharpToCppTransformer(const std::vector<SubstitutionRule>& extraRules)
        : TextTransformer([&]() {
            std::vector<SubstitutionRule> allRules;
            allRules.insert(allRules.end(), FirstStage.begin(), FirstStage.end());
            allRules.insert(allRules.end(), extraRules.begin(), extraRules.end());
            allRules.insert(allRules.end(), LastStage.begin(), LastStage.end());
            return allRules;
        }())
    {
    }
}