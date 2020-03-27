# -*- coding utf-8 -*-
# authors: Ethosa, Konard

from retranslator import Translator


class CSharpToCpp(Translator):
    def __init__(self, codeString="", extra=[], useRegex=False, debug=False):
        """initialize class

        Keyword Arguments:
            codeString {str} -- source code on C# (default: {\"})
            extra {list} -- include your own rules (default: {[]})
            useRegex {bool} -- this parameter tells you to use regex (default: {False})
            debug {bool}  (default: {False})
        """
        self.codeString = codeString
        self.Transform = self.compile = self.translate  # callable objects

        #  create little magic ...
        self.rules = CSharpToCpp.FIRST_RULES[:]
        self.rules.extend(extra)
        self.rules.extend(CSharpToCpp.LAST_RULES)
        Translator.__init__(self, codeString, self.rules, useRegex, debug)

    #  Rules for translate code
    FIRST_RULES = [
        # // ...
        # 
        (r"(\r?\n)?[ \t]+//+.+", r"", None, 0),
        # #pragma warning disable CS1591 // Missing XML comment for publicly visible type or member
        # 
        (r"^\s*?\#pragma[\sa-zA-Z0-9]+$", r"", None, 0),
        # {\n\n\n
        # {
        (r"{\s+[\r\n]+", r"{\n", None, 0),
        # Platform.Collections.Methods.Lists
        # Platform::Collections::Methods::Lists
        (r"(namespace[^\r\n]+?)\.([^\r\n]+?)", r"\1::\2", None, 20),
        # nameof(numbers)
        # "numbers"
        (r"(?P<before>\W)nameof\(([^)\n]+\.)?(?P<name>[a-zA-Z0-9_]+)(<[^)\n]+>)?\)", r"\g<before>\"\g<name>\"", None, 0),
        # Insert markers
        # EqualityComparer<T> _equalityComparer = EqualityComparer<T>.Default;
        # EqualityComparer<T> _equalityComparer = EqualityComparer<T>.Default;/*~_comparer~*/
        (r"(?P<declaration>EqualityComparer<(?P<type>[^>\n]+)> (?P<comparer>[a-zA-Z0-9_]+) = EqualityComparer<(?P=type)>\.Default;)", r"\g<declaration>/*~\g<comparer>~*/", None, 0),
        # /*~_equalityComparer~*/..._equalityComparer.Equals(Minimum, value)
        # /*~_equalityComparer~*/...Minimum == value
        (r"(?P<before>/\*~(?P<comparer>[a-zA-Z0-9_]+)~\*/(.|\n)+\W)(?P=comparer)\.Equals\((?P<left>[^,\n]+), (?P<right>[^)\n]+)\)", r"\g<before>\g<left> == \g<right>", None, 50),
        # Remove markers
        # /*~_equalityComparer~*/
        # 
        (r"\r?\n[^\n]+/\*~[a-zA-Z0-9_]+~\*/", r"", None, 10),
        # Insert markers
        # Comparer<T> _comparer = Comparer<T>.Default;
        # Comparer<T> _comparer = Comparer<T>.Default;/*~_comparer~*/
        (r"(?P<declaration>Comparer<(?P<type>[^>\n]+)> (?P<comparer>[a-zA-Z0-9_]+) = Comparer<(?P=type)>\.Default;)", r"\g<declaration>/*~\g<comparer>~*/", None, 0),
        # /*~_comparer~*/..._comparer.Compare(Minimum, value) <= 0
        # /*~_comparer~*/...Minimum <= value
        (r"(?P<before>/\*~(?P<comparer>[a-zA-Z0-9_]+)~\*/(.|\n)+\W)(?P=comparer)\.Compare\((?P<left>[^,\n]+), (?P<right>[^)\n]+)\)\s*(?P<comparison>[<>=]=?)\s*0(?P<after>\D)", r"\g<before>\g<left> \g<comparison> \g<right>\g<after>", None, 50),
        # Remove markers
        # private static readonly Comparer<T> _comparer = Comparer<T>.Default;/*~_comparer~*/
        # 
        (r"\r?\n[^\n]+/\*~[a-zA-Z0-9_]+~\*/", r"", None, 10),
        # Comparer<TArgument>.Default.Compare(maximumArgument, minimumArgument) < 0 
        # maximumArgument < minimumArgument
        (r"Comparer<[^>\n]+>\.Default\.Compare\(\s*(?P<first>[^,)\n]+),\s*(?P<second>[^\)\n]+)\s*\)\s*(?P<comparison>[<>=]=?)\s*0(?P<after>\D)", r"\g<first> \g<comparison> \g<second>\g<after>", None, 0),
        # public static bool operator ==(Range<T> left, Range<T> right) => left.Equals(right);
        # 
        (r"\r?\n[^\n]+bool operator ==\((?P<type>[^\n]+) (?P<left>[a-zA-Z0-9]+), (?P=type) (?P<right>[a-zA-Z0-9]+)\) => ((?P=left)|(?P=right))\.Equals\(((?P=left)|(?P=right))\);", r"", None, 10),
        # public static bool operator !=(Range<T> left, Range<T> right) => !(left == right);
        # 
        (r"\r?\n[^\n]+bool operator !=\((?P<type>[^\n]+) (?P<left>[a-zA-Z0-9]+), (?P=type) (?P<right>[a-zA-Z0-9]+)\) => !\(((?P=left)|(?P=right)) == ((?P=left)|(?P=right))\);", r"", None, 10),
        # public override bool Equals(object obj) => obj is Range<T> range ? Equals(range) : false;
        # 
        (r"\r?\n[^\n]+override bool Equals\((System\.)?[Oo]bject (?P<this>[a-zA-Z0-9]+)\) => (?P=this) is [^\n]+ (?P<other>[a-zA-Z0-9]+) \? Equals\((?P=other)\) : false;", r"", None, 10),
        # out TProduct
        # TProduct
        (r"(?P<before>(<|, ))(in|out) (?P<typeParameter>[a-zA-Z0-9]+)(?P<after>(>|,))", r"\g<before>\g<typeParameter>\g<after>", None, 10),
        # public ...
        # public: ...
        (r"(?P<newLineAndIndent>\r?\n?[ \t]*)(?P<before>[^\{\(\r\n]*)(?P<access>private|protected|public)[ \t]+(?![^\{\(\r\n]*((?<=\s)|\W)(interface|class|struct)(\W)[^\{\(\r\n]*[\{\(\r\n])", r"\g<newLineAndIndent>\g<access>: \g<before>", None, 0),
        # public: static bool CollectExceptions { get; set; }
        # public: inline static bool CollectExceptions;
        (r"(?P<access>(private|protected|public): )(?P<before>(static )?[^\r\n]+ )(?P<name>[a-zA-Z0-9]+) {[^;}]*(?<=\W)get;[^;}]*(?<=\W)set;[^;}]*}", r"\g<access>inline \g<before>\g<name>;", None, 0),
        # public abstract class
        # class
        (r"((public|protected|private|internal|abstract|static) )*(?P<category>interface|class|struct)", r"\g<category>", None, 0),
        # class GenericCollectionMethodsBase<TElement> {
        # template <typename TElement> class GenericCollectionMethodsBase {
        (r"(?P<before>\r?\n)(?P<indent>[ \t]*)(?P<type>class|struct) (?P<typeName>[a-zA-Z0-9]+)<(?P<typeParameters>[a-zA-Z0-9 ,]+)>(?P<typeDefinitionEnding>[^{]+){", r"\g<before>\g<indent>template <typename ...> \g<type> \g<typeName>;\n\g<indent>template <typename \g<typeParameters>> \g<type> \g<typeName><\g<typeParameters>>\g<typeDefinitionEnding>{", None, 0),
        # static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        # template<typename T> static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        (r"static ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>\(([^\)\r\n]+)\)", r"template <typename \3> static \1 \2(\4)", None, 0),
        # interface IFactory<out TProduct> {
        # template <typename...> class IFactory;\ntemplate <typename TProduct> class IFactory<TProduct>
        (r"(?P<before>\r?\n)(?P<indent>[ \t]*)interface (?P<interface>[a-zA-Z0-9]+)<(?P<typeParameters>[a-zA-Z0-9 ,]+)>(?P<typeDefinitionEnding>[^{]+){", r"\g<before>\g<indent>template <typename ...> class \g<interface>;\n\g<indent>template <typename \g<typeParameters>> class \g<interface><\g<typeParameters>>\g<typeDefinitionEnding>{\n    public:", None, 0),
        # template <typename TObject, TProperty, TValue>
        # template <typename TObject, typename TProperty, typename TValue>
        (r"(?P<before>template <((, )?typename [a-zA-Z0-9]+)+, )(?P<typeParameter>[a-zA-Z0-9]+)(?P<after>(,|>))", r"\g<before>typename \g<typeParameter>\g<after>", None, 10),
        # Insert markers
        # private: static void BuildExceptionString(this StringBuilder sb, Exception exception, int level)
        # /*~extensionMethod~BuildExceptionString~*/private: static void BuildExceptionString(this StringBuilder sb, Exception exception, int level)
        (r"private: static [^\r\n]+ (?P<name>[a-zA-Z0-9]+)\(this [^\)\r\n]+\)", r"/*~extensionMethod~\g<name>~*/\0", None, 0),
        # Move all markers to the beginning of the file.
        (r"\A(?P<before>[^\r\n]+\r?\n(.|\n)+)(?P<marker>/\*~extensionMethod~(?P<name>[a-zA-Z0-9]+)~\*/)", r"\g<marker>\g<before>", None, 10),
        # /*~extensionMethod~BuildExceptionString~*/...sb.BuildExceptionString(exception.InnerException, level + 1);
        # /*~extensionMethod~BuildExceptionString~*/...BuildExceptionString(sb, exception.InnerException, level + 1);
        (r"(?P<before>/\*~extensionMethod~(?P<name>[a-zA-Z0-9]+)~\*/(.|\n)+\W)(?P<variable>[_a-zA-Z0-9]+)\.(?P=name)\(", r"\g<before>\g<name>(\g<variable>, ", None, 50),
        # Remove markers
        # /*~extensionMethod~BuildExceptionString~*/
        # 
        (r"/\*~extensionMethod~[a-zA-Z0-9]+~\*/", r"", None, 0),
        # (this 
        # (
        (r"\(this ", r"(", None, 0),
        # public: static readonly EnsureAlwaysExtensionRoot Always = new EnsureAlwaysExtensionRoot();
        # public: inline static EnsureAlwaysExtensionRoot Always;
        (r"(?P<access>(private|protected|public): )?static readonly (?P<type>[a-zA-Z0-9]+(<[a-zA-Z0-9]+>)?) (?P<name>[a-zA-Z0-9_]+) = new (?P=type)\(\);", r"\g<access>inline static \g<type> \g<name>;", None, 0),
        # public: static readonly Range<int> SByte = new Range<int>(std::numeric_limits<int>::min(), std::numeric_limits<int>::max());
        # public: inline static Range<int> SByte = Range<int>(std::numeric_limits<int>::min(), std::numeric_limits<int>::max());
        (r"(?P<access>(private|protected|public): )?static readonly (?P<type>[a-zA-Z0-9]+(<[a-zA-Z0-9]+>)?) (?P<name>[a-zA-Z0-9_]+) = new (?P=type)\((?P<arguments>[^\n]+)\);", r"\g<access>inline static \g<type> \g<name> = \g<type>(\g<arguments>);", None, 0),
        # public: static readonly string ExceptionContentsSeparator = "---";
        # public: inline static std::string ExceptionContentsSeparator = "---";
        (r"(?P<access>(private|protected|public): )?(const|static readonly) string (?P<name>[a-zA-Z0-9_]+) = \"(?P<string>(\\\"|[^\"\r\n])+)\";", r"\g<access>inline static std::string \g<name> = \"\g<string>\";", None, 0),
        # private: const int MaxPath = 92;
        # private: inline static const int MaxPath = 92;
        (r"(?P<access>(private|protected|public): )?(const|static readonly) (?P<type>[a-zA-Z0-9]+) (?P<name>[_a-zA-Z0-9]+) = (?P<value>[^;\r\n]+);", r"\g<access>inline static const \g<type> \g<name> = \g<value>;", None, 0),
        #  ArgumentNotNull(EnsureAlwaysExtensionRoot root, TArgument argument) where TArgument : class
        #  ArgumentNotNull(EnsureAlwaysExtensionRoot root, TArgument* argument)
        (r"(?P<before> [a-zA-Z]+\(([a-zA-Z *,]+, |))(?P<type>[a-zA-Z]+)(?P<after>(| [a-zA-Z *,]+)\))[ \r\n]+where (?P=type) : class", r"\g<before>\g<type>*\g<after>", None, 0),
        # protected: abstract TElement GetFirst();
        # protected: virtual TElement GetFirst() = 0;
        (r"(?P<access>(private|protected|public): )?abstract (?P<method>[^;\r\n]+);", r"\g<access>virtual \g<method> = 0;", None, 0),
        # TElement GetFirst();
        # virtual TElement GetFirst() = 0;
        (r"(?P<before>[\r\n]+[ ]+)(?P<methodDeclaration>(?!return)[a-zA-Z0-9]+ [a-zA-Z0-9]+\([^\)\r\n]*\))(?P<after>;[ ]*[\r\n]+)", r"\g<before>virtual \g<methodDeclaration> = 0\g<after>", None, 1),
        # protected: readonly TreeElement[] _elements;
        # protected: TreeElement _elements[N];
        (r"(?P<access>(private|protected|public): )?readonly (?P<type>[a-zA-Z<>0-9]+)([\[\]]+) (?P<name>[_a-zA-Z0-9]+);", r"\g<access>\g<type> \g<name>[N];", None, 0),
        # protected: readonly TElement Zero;
        # protected: TElement Zero;
        (r"(?P<access>(private|protected|public): )?readonly (?P<type>[a-zA-Z<>0-9]+) (?P<name>[_a-zA-Z0-9]+);", r"\g<access>\g<type> \g<name>;", None, 0),
        # internal
        # 
        (r"(\W)internal\s+", r"\1", None, 0),
        # static void NotImplementedException(ThrowExtensionRoot root) => throw new NotImplementedException();
        # static void NotImplementedException(ThrowExtensionRoot root) { return throw new NotImplementedException(); }
        (r"(^\s+)(private|protected|public)?(: )?(template \<[^>\r\n]+\> )?(static )?(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+throw([^;\r\n]+);", r"\1\2\3\4\5\6\7\8(\9) { throw\10; }", None, 0),
        # SizeBalancedTree(int capacity) => a = b;
        # SizeBalancedTree(int capacity) { a = b; }
        (r"(^\s+)(private|protected|public)?(: )?(template \<[^>\r\n]+\> )?(static )?(override )?(void )?([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+([^;\r\n]+);", r"\1\2\3\4\5\6\7\8(\9) { \10; }", None, 0),
        # int SizeBalancedTree(int capacity) => a;
        # int SizeBalancedTree(int capacity) { return a; }
        (r"(^\s+)(private|protected|public)?(: )?(template \<[^>\r\n]+\> )?(static )?(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+([^;\r\n]+);", r"\1\2\3\4\5\6\7\8(\9) { return \10; }", None, 0),
        # () => Integer<TElement>.Zero,
        # () { return Integer<TElement>.Zero; },
        (r"\(\)\s+=>\s+(?P<expression>[^(),;\r\n]+(\(((([^();\r\n]*?)(?P<parenthesis>\()(?(parenthesis)([^();\r\n]*?)\)))*?([^();\r\n]*?))\))?[^(),;\r\n]*)(?P<after>,|\);)", r"() { return \g<expression>; }\g<after>", None, 0),
        # => Integer<TElement>.Zero;
        # { return Integer<TElement>.Zero; }
        (r"\)\s+=>\s+([^;\r\n]+?);", r") { return \1; }", None, 0),
        # () { return avlTree.Count; }
        # [&]()-> auto { return avlTree.Count; }
        (r"(?P<before>, |\()\(\) { return (?P<expression>[^;\r\n]+); }", r"\g<before>[&]()-> auto { return \g<expression>; }", None, 0),
        # Count => GetSizeOrZero(Root);
        # GetCount() { return GetSizeOrZero(Root); }
        (r"(\W)([A-Z][a-zA-Z]+)\s+=>\s+([^;\r\n]+);", r"\1Get\2() { return \3; }", None, 0),
        # ArgumentInRange(string message) { string messageBuilder() { return message; }
        # ArgumentInRange(string message) { auto messageBuilder = [&]() -> string { return message; };
        (r"(?P<before>\W[_a-zA-Z0-9]+\([^\)\n]*\)[\s\n]*{[\s\n]*([^{}]|\n)*?(\r?\n)?[ \t]*)(?P<returnType>[_a-zA-Z0-9*:]+[_a-zA-Z0-9*: ]*) (?P<methodName>[_a-zA-Z0-9]+)\((?P<arguments>[^\)\n]*)\)\s*{(?P<body>(\"[^\"\n]+\"|[^}]|\n)+?)}", r"\g<before>auto \g<methodName> = [&]() -> \g<returnType> {\g<body>};", None, 10),
        # Func<TElement> treeCount
        # std::function<TElement()> treeCount
        (r"Func<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<\1()> \2", None, 0),
        # Action<TElement> free
        # std::function<void(TElement)> free
        (r"Action<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<void(\1)> \2", None, 0),
        # Predicate<TArgument> predicate
        # std::function<bool(TArgument)> predicate
        (r"Predicate<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<bool(\1)> \2", None, 0),
        # var
        # auto
        (r"(\W)var(\W)", r"\1auto\2", None, 0),
        # unchecked
        # 
        (r"[\r\n]{2}\s*?unchecked\s*?$", r"", None, 0),
        # throw new
        # throw
        (r"(\W)throw new(\W)", r"\1throw\2", None, 0),
        # void RaiseExceptionIgnoredEvent(Exception exception)
        # void RaiseExceptionIgnoredEvent(const std::exception& exception)
        (r"(\(|, )(System\.Exception|Exception)( |\))", r"\1const std::exception&\3", None, 0),
        # EventHandler<Exception>
        # EventHandler<std::exception>
        (r"(\W)(System\.Exception|Exception)(\W)", r"\1std::exception\3", None, 0),
        # override void PrintNode(TElement node, StringBuilder sb, int level)
        # void PrintNode(TElement node, StringBuilder sb, int level) override
        (r"override ([a-zA-Z0-9 \*\+]+)(\([^\)\r\n]+?\))", r"\1\2 override", None, 0),
        # return (range.Minimum, range.Maximum)
        # return {range.Minimum, range.Maximum}
        (r"(?P<before>return\s*)\((?P<values>[^\)\n]+)\)(?!\()(?P<after>\W)", r"\g<before>{\g<values>}\g<after>", None, 0),
        # string
        # std::string
        (r"(?P<before>\W)(?<!::)string(?P<after>\W)", r"\g<before>std::string\g<after>", None, 0),
        # System.ValueTuple
        # std::tuple
        (r"(?P<before>\W)(System\.)?ValueTuple(?!\s*=|\()(?P<after>\W)", r"\g<before>std::tuple\g<after>", None, 0),
        # sbyte
        # std::int8_t
        (r"(?P<before>\W)((System\.)?SB|sb)yte(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int8_t\g<after>", None, 0),
        # short
        # std::int16_t
        (r"(?P<before>\W)((System\.)?Int16|short)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int16_t\g<after>", None, 0),
        # int
        # std::int32_t
        (r"(?P<before>\W)((System\.)?I|i)nt(32)?(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int32_t\g<after>", None, 0),
        # long
        # std::int64_t
        (r"(?P<before>\W)((System\.)?Int64|long)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int64_t\g<after>", None, 0),
        # byte
        # std::uint8_t
        (r"(?P<before>\W)((System\.)?Byte|byte)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint8_t\g<after>", None, 0),
        # ushort
        # std::uint16_t
        (r"(?P<before>\W)((System\.)?UInt16|ushort)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint16_t\g<after>", None, 0),
        # uint
        # std::uint32_t
        (r"(?P<before>\W)((System\.)?UI|ui)nt(32)?(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint32_t\g<after>", None, 0),
        # ulong
        # std::uint64_t
        (r"(?P<before>\W)((System\.)?UInt64|ulong)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint64_t\g<after>", None, 0),
        # char*[] args
        # char* args[]
        (r"([_a-zA-Z0-9:\*]?)\[\] ([a-zA-Z0-9]+)", r"\1 \2[]", None, 0),
        # @object
        # object
        (r"@([_a-zA-Z0-9]+)", r"\1", None, 0),
        # float.MinValue
        # std::numeric_limits<float>::lowest()
        (r"(?P<before>\W)(?P<type>std::[a-z0-9_]+|float|double)\.MinValue(?P<after>\W)", r"\g<before>std::numeric_limits<\g<type>>::lowest()\g<after>", None, 0),
        # double.MaxValue
        # std::numeric_limits<float>::max()
        (r"(?P<before>\W)(?P<type>std::[a-z0-9_]+|float|double)\.MaxValue(?P<after>\W)", r"\g<before>std::numeric_limits<\g<type>>::max()\g<after>", None, 0),
        # using Platform.Numbers;
        # 
        (r"([\r\n]{2}|^)\s*?using [\.a-zA-Z0-9]+;\s*?$", r"", None, 0),
        # struct TreeElement { }
        # struct TreeElement { };
        (r"(struct|class) ([a-zA-Z0-9]+)(\s+){([\sa-zA-Z0-9;:_]+?)}([^;])", r"\1 \2\3{\4};\5", None, 0),
        # class Program { }
        # class Program { };
        (r"(?P<type>struct|class) (?P<name>[a-zA-Z0-9]+[^\r\n]*)(?P<beforeBody>[\r\n]+(?P<indentLevel>[\t ]*)?)\{(?P<body>[\S\s]+?[\r\n]+(?P=indentLevel))\}(?P<afterBody>[^;]|$)", r"\g<type> \g<name>\g<beforeBody>{\g<body>};\g<afterBody>", None, 0),
        # class SizedBinaryTreeMethodsBase : GenericCollectionMethodsBase
        # class SizedBinaryTreeMethodsBase : public GenericCollectionMethodsBase
        (r"(struct|class) ([a-zA-Z0-9]+)(<[a-zA-Z0-9 ,]+>)? : ([a-zA-Z0-9]+)", r"\1 \2\3 : public \4", None, 0),
        # class IProperty : ISetter<TValue, TObject>, IProvider<TValue, TObject>
        # class IProperty : public ISetter<TValue, TObject>, public IProvider<TValue, TObject>
        (r"(?P<before>(struct|class) [a-zA-Z0-9]+ : ((public [a-zA-Z0-9]+(<[a-zA-Z0-9 ,]+>)?, )+)?)(?P<inheritedType>(?!public)[a-zA-Z0-9]+(<[a-zA-Z0-9 ,]+>)?)(?P<after>(, [a-zA-Z0-9]+(?!>)|[ \r\n]+))", r"\g<before>public \g<inheritedType>\g<after>", None, 10),
        # Insert scope borders.
        # ref TElement root
        # ~!root!~ref TElement root
        (r"(?P<definition>(?<= |\()(ref [a-zA-Z0-9]+|[a-zA-Z0-9]+(?<!ref)) (?P<variable>[a-zA-Z0-9]+)(?=\)|, | =))", r"~!\g<variable>!~\g<definition>", None, 0),
        # Inside the scope of ~!root!~ replace:
        # root
        # *root
        (r"(?P<definition>~!(?P<pointer>[a-zA-Z0-9]+)!~ref [a-zA-Z0-9]+ (?P=pointer)(?=\)|, | =))(?P<before>((?<!~!(?P=pointer)!~)(.|\n))*?)(?P<prefix>(\W |\())(?P=pointer)(?P<suffix>( |\)|;|,))", r"\g<definition>\g<before>\g<prefix>*\g<pointer>\g<suffix>", None, 70),
        # Remove scope borders.
        # ~!root!~
        # 
        (r"~!(?P<pointer>[a-zA-Z0-9]+)!~", r"", None, 5),
        # ref auto root = ref
        # ref auto root = 
        (r"ref ([a-zA-Z0-9]+) ([a-zA-Z0-9]+) = ref(\W)", r"\1* \2 =\3", None, 0),
        # *root = ref left;
        # root = left;
        (r"\*([a-zA-Z0-9]+) = ref ([a-zA-Z0-9]+)(\W)", r"\1 = \2\3", None, 0),
        # (ref left)
        # (left)
        (r"\(ref ([a-zA-Z0-9]+)(\)|\(|,)", r"(\1\2", None, 0),
        #  ref TElement 
        #  TElement* 
        (r"( |\()ref ([a-zA-Z0-9]+) ", r"\1\2* ", None, 0),
        # ref sizeBalancedTree.Root
        # &sizeBalancedTree->Root
        (r"ref ([a-zA-Z0-9]+)\.([a-zA-Z0-9\*]+)", r"&\1->\2", None, 0),
        # ref GetElement(node).Right
        # &GetElement(node)->Right
        (r"ref ([a-zA-Z0-9]+)\(([a-zA-Z0-9\*]+)\)\.([a-zA-Z0-9]+)", r"&\1(\2)->\3", None, 0),
        # GetElement(node).Right
        # GetElement(node)->Right
        (r"([a-zA-Z0-9]+)\(([a-zA-Z0-9\*]+)\)\.([a-zA-Z0-9]+)", r"\1(\2)->\3", None, 0),
        # [Fact]\npublic: static void SizeBalancedTreeMultipleAttachAndDetachTest()
        # public: TEST_METHOD(SizeBalancedTreeMultipleAttachAndDetachTest)
        (r"\[Fact\][\s\n]+(public: )?(static )?void ([a-zA-Z0-9]+)\(\)", r"public: TEST_METHOD(\3)", None, 0),
        # class TreesTests
        # TEST_CLASS(TreesTests)
        (r"class ([a-zA-Z0-9]+Tests)", r"TEST_CLASS(\1)", None, 0),
        # Assert.Equal
        # Assert::AreEqual
        (r"(?P<type>Assert)\.(?P<method>(Not)?Equal)", r"\g<type>::Are\g<method>", None, 0),
        # Assert.Throws
        # Assert::ExpectException
        (r"(Assert)\.Throws", r"\1::ExpectException", None, 0),
        # Assert.True
        # Assert::IsTrue
        (r"(Assert)\.(True|False)", r"\1::Is\2", None, 0),
        # $"Argument {argumentName} is null."
        # std::string("Argument ").append(Platform::Converters::To<std::string>(argumentName)).append(" is null.")
        (r"\$\"(?P<left>(\\\"|[^\"\r\n])*){(?P<expression>[_a-zA-Z0-9]+)}(?P<right>(\\\"|[^\"\r\n])*)\"", r"std::string($\"\g<left>\").append(Platform::Converters::To<std::string>(\g<expression>)).append(\"\g<right>\")", None, 10),
        # $"
        # "
        (r"\$\"", r"\"", None, 0),
        # std::string(std::string("[").append(Platform::Converters::To<std::string>(Minimum)).append(", ")).append(Platform::Converters::To<std::string>(Maximum)).append("]")
        # std::string("[").append(Platform::Converters::To<std::string>(Minimum)).append(", ").append(Platform::Converters::To<std::string>(Maximum)).append("]")
        (r"std::string\((?P<begin>std::string\(\"(\\\"|[^\"])*\"\)(\.append\((Platform::Converters::To<std::string>\([^)\n]+\)|[^)\n]+)\))+)\)\.append", r"\g<begin>.append", None, 10),
        # Console.WriteLine("...")
        # printf("...\n")
        (r"Console\.WriteLine\(\"([^\"\r\n]+)\"\)", r"printf(\"\1\\n\")", None, 0),
        # TElement Root;
        # TElement Root = 0;
        (r"(?P<before>\r?\n[\t ]+)(?P<access>(private|protected|public)(: )?)?(?P<type>[a-zA-Z0-9:_]+(?<!return)) (?P<name>[_a-zA-Z0-9]+);", r"\g<before>\g<access>\g<type> \g<name> = 0;", None, 0),
        # TreeElement _elements[N];
        # TreeElement _elements[N] = { {0} };
        (r"(\r?\n[\t ]+)(private|protected|public)?(: )?([a-zA-Z0-9]+) ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\2\3\4 \5[\6] = { {0} };", None, 0),
        # auto path = new TElement[MaxPath];
        # TElement path[MaxPath] = { {0} };
        (r"(\r?\n[\t ]+)[a-zA-Z0-9]+ ([a-zA-Z0-9]+) = new ([a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\3 \2[\4] = { {0} };", None, 0),
        # bool Equals(Range<T> other) { ... }
        # bool operator ==(const Key &other) const { ... }
        (r"(?P<before>\r?\n[^\n]+bool )Equals\((?P<type>[^\n{]+) (?P<variable>[a-zA-Z0-9]+)\)(?P<after>(\s|\n)*{)", r"\g<before>operator ==(const \g<type> &\g<variable>) const\g<after>", None, 0),
        # Insert scope borders.
        # class Range { ... public: override std::string ToString() { return ...; }
        # class Range {/*~Range<T>~*/ ... public: override std::string ToString() { return ...; }
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)template <typename (?P<typeParameter>[^<>\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<(?P=typeParameter)>)(\s*:\s*[^{\n]+)?[\t ]*(\r?\n)?[\t ]*{)(?P<middle>((?!class|struct).|\n)+?)(?P<toStringDeclaration>(?P<access>(private|protected|public): )override std::string ToString\(\))", r"\g<classDeclarationBegin>/*~\g<type>~*/\g<middle>\g<toStringDeclaration>", None, 0),
        # Inside the scope of ~!Range!~ replace:
        # public: override std::string ToString() { return ...; }
        # public: operator std::string() const { return ...; }\n\npublic: friend std::ostream & operator <<(std::ostream &out, const A &obj) { return out << (std::string)obj; }
        (r"(?P<scope>/\*~(?P<type>[_a-zA-Z0-9<>:]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=type)~\*/)(.|\n))*?)(?P<toStringDeclaration>\r?\n(?P<indent>[ \t]*)(?P<access>(private|protected|public): )override std::string ToString\(\) (?P<toStringMethodBody>{[^}\n]+}))", r"\g<scope>\g<separator>\g<before>\n\g<indent>\g<access>operator std::string() const \g<toStringMethodBody>\n\n\g<indent>\g<access>friend std::ostream & operator <<(std::ostream &out, const \g<type> &obj) { return out << (std::string)obj; }", None, 0),
        # Remove scope borders.
        # /*~Range~*/
        # 
        (r"/\*~[_a-zA-Z0-9<>:]+~\*/", r"", None, 0),
        # private: inline static ConcurrentBag<std::exception> _exceptionsBag;
        # private: inline static std::mutex _exceptionsBag_mutex; \n\n private: inline static std::vector<std::exception> _exceptionsBag;
        (r"(?P<begin>\r?\n?(?P<indent>[ \t]+))(?P<access>(private|protected|public): )?inline static ConcurrentBag<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+);", r"\g<begin>private: inline static std::mutex \g<name>_mutex;\n\n\g<indent>\g<access>inline static std::vector<\g<argumentType>> \g<name>;", None, 0),
        # public: static IReadOnlyCollection<std::exception> GetCollectedExceptions() { return _exceptionsBag; }
        # public: static std::vector<std::exception> GetCollectedExceptions() { return std::vector<std::exception>(_exceptionsBag); }
        (r"(?P<access>(private|protected|public): )?static IReadOnlyCollection<(?P<argumentType>[^;\r\n]+)> (?P<methodName>[_a-zA-Z0-9]+)\(\) { return (?P<fieldName>[_a-zA-Z0-9]+); }", r"\g<access>static std::vector<\g<argumentType>> \g<methodName>() { return std::vector<\g<argumentType>>(\g<fieldName>); }", None, 0),
        # public: static event EventHandler<std::exception> ExceptionIgnored = OnExceptionIgnored; ... };
        # ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored; };
        (r"(?P<begin>\r?\n(\r?\n)?(?P<halfIndent>[ \t]+)(?P=halfIndent))(?P<access>(private|protected|public): )?static event EventHandler<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+) = (?P<defaultDelegate>[_a-zA-Z0-9]+);(?P<middle>(.|\n)+?)(?P<end>\r?\n(?P=halfIndent)};)", r"\g<middle>\n\n\g<halfIndent>\g<halfIndent>\g<access>static inline Platform::Delegates::MulticastDelegate<void(void*, const \g<argumentType>&)> \g<name> = \g<defaultDelegate>;\g<end>", None, 0),
        # Insert scope borders.
        # class IgnoredExceptions { ... private: inline static std::vector<std::exception> _exceptionsBag;
        # class IgnoredExceptions {/*~_exceptionsBag~*/ ... private: inline static std::vector<std::exception> _exceptionsBag;
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<vectorFieldDeclaration>(?P<access>(private|protected|public): )inline static std::vector<(?P<argumentType>[^;\r\n]+)> (?P<fieldName>[_a-zA-Z0-9]+);)", r"\g<classDeclarationBegin>/*~\g<fieldName>~*/\g<middle>\g<vectorFieldDeclaration>", None, 0),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # _exceptionsBag.Add(exception);
        # _exceptionsBag.push_back(exception);
        (r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=fieldName)~\*/)(.|\n))*?)(?P=fieldName)\.Add", r"\g<scope>\g<separator>\g<before>\g<fieldName>.push_back", None, 10),
        # Remove scope borders.
        # /*~_exceptionsBag~*/
        # 
        (r"/\*~[_a-zA-Z0-9]+~\*/", r"", None, 0),
        # Insert scope borders.
        # class IgnoredExceptions { ... private: static std::mutex _exceptionsBag_mutex;
        # class IgnoredExceptions {/*~_exceptionsBag~*/ ... private: static std::mutex _exceptionsBag_mutex;
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<mutexDeclaration>private: inline static std::mutex (?P<fieldName>[_a-zA-Z0-9]+)_mutex;)", r"\g<classDeclarationBegin>/*~\g<fieldName>~*/\g<middle>\g<mutexDeclaration>", None, 0),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # return std::vector<std::exception>(_exceptionsBag);
        # std::lock_guard<std::mutex> guard(_exceptionsBag_mutex); return std::vector<std::exception>(_exceptionsBag);
        (r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=fieldName)~\*/)(.|\n))*?){(?P<after>((?!lock_guard)[^{};\r\n])*(?P=fieldName)[^;}\r\n]*;)", r"\g<scope>\g<separator>\g<before>{ std::lock_guard<std::mutex> guard(\g<fieldName>_mutex);\g<after>", None, 10),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # _exceptionsBag.Add(exception);
        # std::lock_guard<std::mutex> guard(_exceptionsBag_mutex); \r\n _exceptionsBag.Add(exception);
        (r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=fieldName)~\*/)(.|\n))*?){(?P<after>((?!lock_guard)([^{};]|\n))*?\r?\n(?P<indent>[ \t]*)(?P=fieldName)[^;}\r\n]*;)", r"\g<scope>\g<separator>\g<before>{\n\g<indent>std::lock_guard<std::mutex> guard(\g<fieldName>_mutex);\g<after>", None, 10),
        # Remove scope borders.
        # /*~_exceptionsBag~*/
        # 
        (r"/\*~[_a-zA-Z0-9]+~\*/", r"", None, 0),
        # Insert scope borders.
        # class IgnoredExceptions { ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored;
        # class IgnoredExceptions {/*~ExceptionIgnored~*/ ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored;
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<eventDeclaration>(?P<access>(private|protected|public): )static inline Platform::Delegates::MulticastDelegate<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+) = (?P<defaultDelegate>[_a-zA-Z0-9]+);)", r"\g<classDeclarationBegin>/*~\g<name>~*/\g<middle>\g<eventDeclaration>", None, 0),
        # Inside the scope of ~!ExceptionIgnored!~ replace:
        # ExceptionIgnored.Invoke(NULL, exception);
        # ExceptionIgnored(NULL, exception);
        (r"(?P<scope>/\*~(?P<eventName>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=eventName)~\*/)(.|\n))*?)(?P=eventName)\.Invoke", r"\g<scope>\g<separator>\g<before>\g<eventName>", None, 10),
        # Remove scope borders.
        # /*~ExceptionIgnored~*/
        # 
        (r"/\*~[a-zA-Z0-9]+~\*/", r"", None, 0),
        # Insert scope borders.
        # auto added = new StringBuilder();
        # /*~sb~*/std::string added;
        (r"(auto|(System\.Text\.)?StringBuilder) (?P<variable>[a-zA-Z0-9]+) = new (System\.Text\.)?StringBuilder\(\);", r"/*~\g<variable>~*/std::string \g<variable>;", None, 0),
        # static void Indent(StringBuilder sb, int level)
        # static void Indent(/*~sb~*/StringBuilder sb, int level)
        (r"(?P<start>, |\()(System\.Text\.)?StringBuilder (?P<variable>[a-zA-Z0-9]+)(?P<end>,|\))", r"\g<start>/*~\g<variable>~*/std::string& \g<variable>\g<end>", None, 0),
        # Inside the scope of ~!added!~ replace:
        # sb.ToString()
        # sb
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.ToString\(\)", r"\g<scope>\g<separator>\g<before>\g<variable>", None, 10),
        # sb.AppendLine(argument)
        # sb.append(Platform::Converters::To<std::string>(argument)).append(1, '\n')
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.AppendLine\((?P<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(Platform::Converters::To<std::string>(\g<argument>)).append(1, '\\n')", None, 10),
        # sb.Append('\t', level);
        # sb.append(level, '\t');
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.Append\('(?P<character>[^'\r\n]+)', (?P<count>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<count>, '\g<character>')", None, 10),
        # sb.Append(argument)
        # sb.append(Platform::Converters::To<std::string>(argument))
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.Append\((?P<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(Platform::Converters::To<std::string>(\g<argument>))", None, 10),
        # Remove scope borders.
        # /*~sb~*/
        # 
        (r"/\*~[a-zA-Z0-9]+~\*/", r"", None, 0),
        # Insert scope borders.
        # auto added = new HashSet<TElement>();
        # ~!added!~std::unordered_set<TElement> added;
        (r"auto (?P<variable>[a-zA-Z0-9]+) = new HashSet<(?P<element>[a-zA-Z0-9]+)>\(\);", r"~!\g<variable>!~std::unordered_set<\g<element>> \g<variable>;", None, 0),
        # Inside the scope of ~!added!~ replace:
        # added.Add(node)
        # added.insert(node)
        (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Add\((?P<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.insert(\g<argument>)", None, 10),
        # Inside the scope of ~!added!~ replace:
        # added.Remove(node)
        # added.erase(node)
        (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Remove\((?P<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.erase(\g<argument>)", None, 10),
        # if (added.insert(node)) {
        # if (!added.contains(node)) { added.insert(node);
        (r"if \((?P<variable>[a-zA-Z0-9]+)\.insert\((?P<argument>[a-zA-Z0-9]+)\)\)(?P<separator>[\t ]*[\r\n]+)(?P<indent>[\t ]*){", r"if (!\g<variable>.contains(\g<argument>))\g<separator>\g<indent>{\n\g<indent>    \g<variable>.insert(\g<argument>);", None, 0),
        # Remove scope borders.
        # ~!added!~
        # 
        (r"~![a-zA-Z0-9]+!~", r"", None, 5),
        # Insert scope borders.
        # auto random = new System.Random(0);
        # std::srand(0);
        (r"[a-zA-Z0-9\.]+ ([a-zA-Z0-9]+) = new (System\.)?Random\(([a-zA-Z0-9]+)\);", r"~!\1!~std::srand(\3);", None, 0),
        # Inside the scope of ~!random!~ replace:
        # random.Next(1, N)
        # (std::rand() % N) + 1
        (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Next\((?P<from>[a-zA-Z0-9]+), (?P<to>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>(std::rand() % \g<to>) + \g<from>", None, 10),
        # Remove scope borders.
        # ~!random!~
        # 
        (r"~![a-zA-Z0-9]+!~", r"", None, 5),
        # Insert method body scope starts.
        # void PrintNodes(TElement node, StringBuilder sb, int level) {
        # void PrintNodes(TElement node, StringBuilder sb, int level) {/*method-start*/
        (r"(?P<start>\r?\n[\t ]+)(?P<prefix>((private|protected|public): )?(virtual )?[a-zA-Z0-9:_]+ )?(?P<method>[a-zA-Z][a-zA-Z0-9]*)\((?P<arguments>[^\)]*)\)(?P<override>( override)?)(?P<separator>[ \t\r\n]*)\{(?P<end>[^~])", r"\g<start>\g<prefix>\g<method>(\g<arguments>)\g<override>\g<separator>{/*method-start*/\g<end>", None, 0),
        # Insert method body scope ends.
        # {/*method-start*/...}
        # {/*method-start*/.../*method-end*/}
        (r"\{/\*method-start\*/(?P<body>((([^\{\}]*)(?P<bracket>\{)(?(bracket)([^\{\}]*)\}))+([^\{\}]*)))\}", r"{/*method-start*/\g<body>/*method-end*/}", None, 0),
        # Inside method bodies replace:
        # GetFirst(
        # this->GetFirst(
        (r"(?P<scope>/\*method-start\*/)(?P<before>((?<!/\*method-end\*/)(.|\n))*?)(?P<separator>[\W](?<!(::|\.|->|throw\s+)))(?P<method>(?!sizeof)[a-zA-Z0-9]+)\((?!\) \{)(?P<after>(.|\n)*?)(?P<scopeEnd>/\*method-end\*/)", r"\g<scope>\g<before>\g<separator>this->\g<method>(\g<after>\g<scopeEnd>", None, 100),
        # Remove scope borders.
        # /*method-start*/
        # 
        (r"/\*method-(start|end)\*/", r"", None, 0),
        # Insert scope borders.
        # const std::exception& ex
        # const std::exception& ex/*~ex~*/
        (r"(?P<before>\(| )(?P<variableDefinition>(const )?(std::)?exception&? (?P<variable>[_a-zA-Z0-9]+))(?P<after>\W)", r"\g<before>\g<variableDefinition>/*~\g<variable>~*/\g<after>", None, 0),
        # Inside the scope of ~!ex!~ replace:
        # ex.Message
        # ex.what()
        (r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(Platform::Converters::To<std::string>\((?P=variable)\.Message\)|(?P=variable)\.Message)", r"\g<scope>\g<separator>\g<before>\g<variable>.what()", None, 10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        (r"/\*~[_a-zA-Z0-9]+~\*/", r"", None, 0),
        # throw ArgumentNullException(argumentName, message);
        # throw std::invalid_argument(std::string("Argument ").append(argumentName).append(" is null: ").append(message).append("."));
        (r"throw ArgumentNullException\((?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*), (?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*(\(\))?)\);", r"throw std::invalid_argument(std::string(\"Argument \").append(\g<argument>).append(\" is null: \").append(\g<message>).append(\".\"));", None, 0),
        # throw ArgumentException(message, argumentName);
        # throw std::invalid_argument(std::string("Invalid ").append(argumentName).append(" argument: ").append(message).append("."));
        (r"throw ArgumentException\((?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*(\(\))?), (?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*)\);", r"throw std::invalid_argument(std::string(\"Invalid \").append(\g<argument>).append(\" argument: \").append(\g<message>).append(\".\"));", None, 0),
        # throw ArgumentOutOfRangeException(argumentName, argumentValue, messageBuilder());
        # throw std::invalid_argument(std::string("Value [").append(Platform::Converters::To<std::string>(argumentValue)).append("] of argument [").append(argumentName).append("] is out of range: ").append(messageBuilder()).append("."));
        (r"throw ArgumentOutOfRangeException\((?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*([Nn]ame[a-zA-Z]*)?), (?P<argumentValue>[a-zA-Z]*[Aa]rgument[a-zA-Z]*([Vv]alue[a-zA-Z]*)?), (?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*(\(\))?)\);", r"throw std::invalid_argument(std::string(\"Value [\").append(Platform::Converters::To<std::string>(\g<argumentValue>)).append(\"] of argument [\").append(\g<argument>).append(\"] is out of range: \").append(\g<message>).append(\".\"));", None, 0),
        # throw NotSupportedException();
        # throw std::logic_error("Not supported exception.");
        (r"throw NotSupportedException\(\);", r"throw std::logic_error(\"Not supported exception.\");", None, 0),
        # throw NotImplementedException();
        # throw std::logic_error("Not implemented exception.");
        (r"throw NotImplementedException\(\);", r"throw std::logic_error(\"Not implemented exception.\");", None, 0),
        # Insert scope borders.
        # const std::string& message
        # const std::string& message/*~message~*/
        (r"(?P<before>\(| )(?P<variableDefinition>(const )?((std::)?string&?|char\*) (?P<variable>[_a-zA-Z0-9]+))(?P<after>\W)", r"\g<before>\g<variableDefinition>/*~\g<variable>~*/\g<after>", None, 0),
        # Inside the scope of /*~message~*/ replace:
        # Platform::Converters::To<std::string>(message)
        # message
        (r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)Platform::Converters::To<std::string>\((?P=variable)\)", r"\g<scope>\g<separator>\g<before>\g<variable>", None, 10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        (r"/\*~[_a-zA-Z0-9]+~\*/", r"", None, 0),
        # Insert scope borders.
        # std::tuple<T, T> tuple
        # std::tuple<T, T> tuple/*~tuple~*/
        (r"(?P<before>\(| )(?P<variableDefinition>(const )?(std::)?tuple<[^\n]+>&? (?P<variable>[_a-zA-Z0-9]+))(?P<after>\W)", r"\g<before>\g<variableDefinition>/*~\g<variable>~*/\g<after>", None, 0),
        # Inside the scope of ~!ex!~ replace:
        # tuple.Item1
        # std::get<1-1>(tuple)
        (r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.Item(?P<itemNumber>\d+)(?P<after>\W)", r"\g<scope>\g<separator>\g<before>std::get<\g<itemNumber>-1>(\g<variable>)\g<after>", None, 10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        (r"/\*~[_a-zA-Z0-9]+~\*/", r"", None, 0),
        # Insert scope borders.
        # class Range<T> {
        # class Range<T> {/*~type~Range<T>~*/
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)template <typename (?P<typeParameter>[^\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<(?P=typeParameter)>)(\s*:\s*[^{\n]+)?[\t ]*(\r?\n)?[\t ]*{)", r"\g<classDeclarationBegin>/*~type~\g<type>~*/", None, 0),
        # Inside the scope of /*~type~Range<T>~*/ insert inner scope and replace:
        # public: static implicit operator std::tuple<T, T>(Range<T> range)
        # public: operator std::tuple<T, T>() const {/*~variable~Range<T>~*/
        (r"(?P<scope>/\*~type~(?P<type>[^~\n\*]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~type~(?P=type)~\*/)(.|\n))*?)(?P<access>(private|protected|public): )static implicit operator (?P<targetType>[^\(\n]+)\((?P<argumentDeclaration>(?P=type) (?P<variable>[a-zA-Z0-9]+))\)(?P<after>\s*\n?\s*{)", r"\g<scope>\g<separator>\g<before>\g<access>operator \g<targetType>() const\g<after>/*~variable~\g<variable>~*/", None, 10),
        # Inside the scope of /*~type~Range<T>~*/ replace:
        # public: static implicit operator Range<T>(std::tuple<T, T> tuple) { return new Range<T>(std::get<1-1>(tuple), std::get<2-1>(tuple)); }
        # public: Range(std::tuple<T, T> tuple) : Range(std::get<1-1>(tuple), std::get<2-1>(tuple)) { }
        (r"(?P<scope>/\*~type~(?P<type>(?P<typeName>[_a-zA-Z0-9]+)[^~\n\*]*)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~type~(?P=type)~\*/)(.|\n))*?)(?P<access>(private|protected|public): )static implicit operator (?P=type)\((?P<arguments>[^{}\n]+)\)(\s|\n)*{(\s|\n)*return (new )?(?P=type)\((?P<passedArguments>[^\n]+)\);(\s|\n)*}", r"\g<scope>\g<separator>\g<before>\g<access>\g<typeName>(\g<arguments>) : \g<typeName>(\g<passedArguments>) { }", None, 10),
        # Inside the scope of /*~variable~range~*/ replace:
        # range.Minimum
        # this->Minimum
        (r"(?P<scope>{/\*~variable~(?P<variable>[^~\n]+)~\*/)(?P<separator>.|\n)(?P<before>(?P<beforeExpression>(([^{}]|\n)(?P<bracket>{)(?(bracket)([^{}]|\n)}))*?([^{}]|\n)))(?P=variable)\.(?P<field>[_a-zA-Z0-9]+)(?P<after>(,|;|}| |\))(?P<afterExpression>(([^{}]|\n)(?P<bracket>{)(?(bracket)([^{}]|\n)}))*?([^{}]|\n))})", r"\g<scope>\g<separator>\g<before>this->\g<field>\g<after>", None, 10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        (r"/\*~[^~\n]+~[^~\n]+~\*/", r"", None, 0),
        # Insert scope borders.
        # namespace Platform::Ranges { ... }
        # namespace Platform::Ranges {/*~start~namespace~Platform::Ranges~*/ ... /*~end~namespace~Platform::Ranges~*/} 
        (r"(?P<namespaceDeclarationBegin>\r?\n(?P<indent>[\t ]*)namespace (?P<namespaceName>(?P<namePart>[a-zA-Z][a-zA-Z0-9]+)(?P<nextNamePart>::[a-zA-Z][a-zA-Z0-9]+)+)(\s|\n)*{)(?P<middle>(.|\n)*)(?P<end>(?<=\r?\n)(?P=indent)}(?!;))", r"\g<namespaceDeclarationBegin>/*~start~namespace~\g<namespaceName>~*/\g<middle>/*~end~namespace~\g<namespaceName>~*/\g<end>", None, 0),
        # Insert scope borders.
        # class Range<T> { ... };
        # class Range<T> {/*~start~type~Range<T>~T~*/ ... /*~start~type~Range<T>~T~*/};
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)template <typename (?P<typeParameter>[^\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<(?P=typeParameter)>)(\s*:\s*[^{\n]+)?[\t ]*(\r?\n)?[\t ]*{)(?P<middle>(.|\n)*)(?P<endIndent>(?<=\r?\n)(?P=indent))(?P<end>};)", r"\g<classDeclarationBegin>/*~start~type~\g<type>~\g<typeParameter>~*/\g<middle>\g<endIndent>/*~end~type~\g<type>~\g<typeParameter>~*/\g<end>", None, 0),
        # Inside scopes replace:
        # /*~start~namespace~Platform::Ranges~*/ ... /*~start~type~Range<T>~T~*/ ... public: override std::int32_t GetHashCode() { return {Minimum, Maximum}.GetHashCode(); } ... /*~start~type~Range<T>~T~*/ ... /*~end~namespace~Platform::Ranges~*/
        # /*~start~namespace~Platform::Ranges~*/ ... /*~start~type~Range<T>~T~*/ ... /*~start~type~Range<T>~T~*/ ... /*~end~namespace~Platform::Ranges~*/ namespace std { template <typename T> struct hash<Platform::Ranges::Range<T>> { std::size_t operator()(const Platform::Ranges::Range<T> &obj) const { return {Minimum, Maximum}.GetHashCode(); } }; }
        (r"(?P<namespaceScopeStart>/\*~start~namespace~(?P<namespace>[^~\n\*]+)~\*/)(?P<betweenStartScopes>(.|\n)+)(?P<typeScopeStart>/\*~start~type~(?P<type>[^~\n\*]+)~(?P<typeParameter>[^~\n\*]+)~\*/)(?P<before>(.|\n)+?)(?P<hashMethodDeclaration>\r?\n[ \t]*(?P<access>(private|protected|public): )override std::int32_t GetHashCode\(\)(\s|\n)*{\s*(?P<methodBody>[^\s][^\n]+[^\s])\s*}\s*)(?P<after>(.|\n)+?)(?P<typeScopeEnd>/\*~end~type~(?P=type)~(?P=typeParameter)~\*/)(?P<betweenEndScopes>(.|\n)+)(?P<namespaceScopeEnd>/\*~end~namespace~(?P=namespace)~\*/)}\r?\n", r"\g<namespaceScopeStart>\g<betweenStartScopes>\g<typeScopeStart>\g<before>\g<after>\g<typeScopeEnd>\g<betweenEndScopes>\g<namespaceScopeEnd>}\n\nnamespace std\n{\n    template <typename \g<typeParameter>>\n    struct hash<\g<namespace>::\g<type>>\n    {\n        std::size_t operator()(const \g<namespace>::\g<type> &obj) const\n        {\n            /*~start~method~*/\g<methodBody>/*~end~method~*/\n        }\n    };\n}\n", None, 10),
        # Inside scope of /*~start~method~*/ replace:
        # /*~start~method~*/ ... Minimum ... /*~end~method~*/
        # /*~start~method~*/ ... obj.Minimum ... /*~end~method~*/
        (r"(?P<methodScopeStart>/\*~start~method~\*/)(?P<before>.+({|, ))(?P<name>[a-zA-Z][a-zA-Z0-9]+)(?P<after>[^\n\.\(a-zA-Z0-9]((?!/\*~end~method~\*/)[^\n])+)(?P<methodScopeEnd>/\*~end~method~\*/)", r"\g<methodScopeStart>\g<before>obj.\g<name>\g<after>\g<methodScopeEnd>", None, 10),
        # Remove scope borders.
        # /*~start~type~Range<T>~*/
        # 
        (r"/\*~[^~\*\n]+(~[^~\*\n]+)*~\*/", r"", None, 0),
    ]

    LAST_RULES = [
        # ICounter<int, int> c1;
        # ICounter<int, int>* c1;
        (r"(?P<abstractType>I[A-Z][a-zA-Z0-9]+(<[^>\r\n]+>)?) (?P<variable>[_a-zA-Z0-9]+)(?P<after> = null)?;", r"\g<abstractType>* \g<variable>\g<after>;", None, 0),
        # (expression)
        # expression
        (r"(\(| )\(([a-zA-Z0-9_\*:]+)\)(,| |;|\))", r"\1\2\3", None, 0),
        # (method(expression))
        # method(expression)
        (r"(?P<firstSeparator>(\(| ))\((?P<method>[a-zA-Z0-9_\->\*:]+)\((?P<expression>((([a-zA-Z0-9_\->\*:]*)(?P<parenthesis>\()(?(parenthesis)([a-zA-Z0-9_\->\*:]*)\)))+([a-zA-Z0-9_\->\*:]*)))(?(parenthesis)(?!))\)\)(?P<lastSeparator>(,| |;|\)))", r"\g<firstSeparator>\g<method>(\g<expression>)\g<lastSeparator>", None, 0),
        # .append(".")
        # .append(1, '.');
        (r"\.append\(\"([^\\\"]|\\[^\"])\"\)", r".append(1, '\1')", None, 0),
        # return ref _elements[node];
        # return &_elements[node];
        (r"return ref ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9\*]+)\];", r"return &\1[\2];", None, 0),
        # ((1, 2))
        # ({1, 2})
        (r"(?P<before>\(|, )\((?P<first>[^\n()]+), (?P<second>[^\n()]+)\)(?P<after>\)|, )", r"\g<before>{\g<first>, \g<second>}\g<after>", None, 10),
        # {1, 2}.GetHashCode()
        # Platform::Hashing::Hash(1, 2)
        (r"{(?P<first>[^\n{}]+), (?P<second>[^\n{}]+)}\.GetHashCode\(\)", r"Platform::Hashing::Hash(\g<first>, \g<second>)", None, 10),
        # range.ToString()
        # Platform::Converters::To<std::string>(range).data()
        (r"(?P<before>\W)(?P<variable>[_a-zA-Z][_a-zA-Z0-9]+)\.ToString\(\)", r"\g<before>Platform::Converters::To<std::string>(\g<variable>).data()", None, 10),
        # new
        # 
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)new\s+", r"\g<before>", None, 10),
        # x == null
        # x == nullptr
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)(?P<variable>[_a-zA-Z][_a-zA-Z0-9]+)(?P<operator>\s*(==|!=)\s*)null(?P<after>\W)", r"\g<before>\g<variable>\g<operator>nullptr\g<after>", None, 10),
        # null
        # {}
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)null(?P<after>\W)", r"\g<before>{}\g<after>", None, 10),
        # default
        # 0
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)default(?P<after>\W)", r"\g<before>0\g<after>", None, 10),
        # object x
        # void *x
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)([O|o]bject|System\.Object) (?P<after>\w)", r"\g<before>void *\g<after>", None, 10),
        # <object>
        # <void*>
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)(?<!\w )([O|o]bject|System\.Object)(?P<after>\W)", r"\g<before>void*\g<after>", None, 10),
        # ArgumentNullException
        # std::invalid_argument
        (r"(?P<before>\r?\n[^\"\r\n]*(\"(\\\"|[^\"\r\n])*\"[^\"\r\n]*)*)(?<=\W)(System\.)?ArgumentNullException(?P<after>\W)", r"\g<before>std::invalid_argument\g<after>", None, 10),
        # InvalidOperationException
        # std::runtime_error
        (r"(\W)(InvalidOperationException|Exception)(\W)", r"\1std::runtime_error\3", None, 0),
        # ArgumentException
        # std::invalid_argument
        (r"(\W)(ArgumentException|ArgumentOutOfRangeException)(\W)", r"\1std::invalid_argument\3", None, 0),
        # template <typename T> struct Range : IEquatable<Range<T>>
        # template <typename T> struct Range {
        (r"(?P<before>template <typename (?P<typeParameter>[^\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<[^\n]+>)) : (public )?IEquatable<(?P=type)>(?P<after>(\s|\n)*{)", r"\g<before>\g<after>", None, 0),
        # #region Always
        # 
        (r"(^|\r?\n)[ \t]*\#(region|endregion)[^\r\n]*(\r?\n|$)", r"", None, 0),
        # //#define ENABLE_TREE_AUTO_DEBUG_AND_VALIDATION
        # 
        (r"\/\/[ \t]*\#define[ \t]+[_a-zA-Z0-9]+[ \t]*", r"", None, 0),
        # #if USEARRAYPOOL\r\n#endif
        # 
        (r"#if [a-zA-Z0-9]+\s+#endif", r"", None, 0),
        # [Fact]
        # 
        (r"(?P<firstNewLine>\r?\n|\A)(?P<indent>[\t ]+)\[[a-zA-Z0-9]+(\((?P<expression>((([^()\r\n]*)(?P<parenthesis>\()(?(parenthesis)([^()\r\n]*)\)))+([^()\r\n]*)))(?(parenthesis)(?!))\))?\][ \t]*(\r?\n(?P=indent))?", r"\g<firstNewLine>\g<indent>", None, 5),
        # \A \n ... namespace
        # \Anamespace
        (r"(\A)(\r?\n)+namespace", r"\1namespace", None, 0),
        # \A \n ... class
        # \Aclass
        (r"(\A)(\r?\n)+class", r"\1class", None, 0),
        # \n\n\n
        # \n\n
        (r"\r?\n[ \t]*\r?\n[ \t]*\r?\n", r"\n\n", None, 50),
        # {\n\n
        # {\n
        (r"{[ \t]*\r?\n[ \t]*\r?\n", r"{\n", None, 10),
        # \n\n}
        # \n}
        (r"\r?\n[ \t]*\r?\n(?P<end>[ \t]*})", r"\n\g<end>", None, 10),
    ]
