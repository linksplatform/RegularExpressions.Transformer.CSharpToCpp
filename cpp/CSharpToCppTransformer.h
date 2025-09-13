#pragma once

#include <string>
#include <vector>
#include <regex>
#include <memory>
#include <iostream>

namespace Platform::RegularExpressions::Transformer::CSharpToCpp
{
    /// <summary>
    /// Represents a substitution rule that can be applied to transform text.
    /// </summary>
    class SubstitutionRule
    {
    private:
        std::regex _pattern;
        std::string _replacement;
        int _maxRepeat;

    public:
        /// <summary>
        /// Initializes a new SubstitutionRule instance.
        /// </summary>
        /// <param name="pattern">The regular expression pattern to match.</param>
        /// <param name="replacement">The replacement string.</param>
        /// <param name="maxRepeat">Maximum number of times to apply this rule.</param>
        SubstitutionRule(const std::string& pattern, const std::string& replacement, int maxRepeat = 0);
        
        /// <summary>
        /// Applies the substitution rule to the input text.
        /// </summary>
        /// <param name="text">The text to transform.</param>
        /// <returns>The transformed text.</returns>
        std::string Apply(const std::string& text) const;
        
        /// <summary>
        /// Gets the maximum repeat count for this rule.
        /// </summary>
        int GetMaxRepeat() const { return _maxRepeat; }
    };

    /// <summary>
    /// Base class for text transformers.
    /// </summary>
    class TextTransformer
    {
    protected:
        std::vector<SubstitutionRule> _rules;
        
    public:
        /// <summary>
        /// Initializes a new TextTransformer instance.
        /// </summary>
        /// <param name="rules">The substitution rules to apply.</param>
        TextTransformer(const std::vector<SubstitutionRule>& rules);
        
        /// <summary>
        /// Transforms the input text using all substitution rules.
        /// </summary>
        /// <param name="text">The text to transform.</param>
        /// <returns>The transformed text.</returns>
        virtual std::string Transform(const std::string& text);
    };

    /// <summary>
    /// Represents the C# to C++ transformer.
    /// </summary>
    class CSharpToCppTransformer : public TextTransformer
    {
    private:
        static std::vector<SubstitutionRule> CreateFirstStageRules();
        static std::vector<SubstitutionRule> CreateLastStageRules();
        
    public:
        /// <summary>
        /// The first stage transformation rules.
        /// </summary>
        static const std::vector<SubstitutionRule> FirstStage;
        
        /// <summary>
        /// The last stage transformation rules.
        /// </summary>
        static const std::vector<SubstitutionRule> LastStage;
        
        /// <summary>
        /// Initializes a new CSharpToCppTransformer instance.
        /// </summary>
        CSharpToCppTransformer();
        
        /// <summary>
        /// Initializes a new CSharpToCppTransformer instance with extra rules.
        /// </summary>
        /// <param name="extraRules">Additional transformation rules to include.</param>
        CSharpToCppTransformer(const std::vector<SubstitutionRule>& extraRules);
    };
}