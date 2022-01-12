# -*- coding utf-8 -*-
# authors: Ethosa, Konard
from typing import NoReturn, Optional, List

from retranslator import Translator, SubRule, SteppedTranslator
from regex import search, sub


class CSharpToCpp(Translator):
    def __init__(
        self,
        extra: List[SubRule] = []
    ) -> NoReturn:
        """Initializes class

        :param extra: include your own rules
        """
        #  create little magic ...
        self.rules = CSharpToCpp.FIRST_RULES[:]
        self.rules.extend(extra)
        self.rules.extend(CSharpToCpp.LAST_RULES)
        Translator.__init__(self, self.rules)

    #  Rules for translate code
    FIRST_RULES = [
        # // ...
        # 
        SubRule(r"(\r?\n)?[ \t]+//+.+", r"", max_repeat=0),
        # #pragma warning disable CS1591 // Missing XML comment for publicly visible type or member
        # 
        SubRule(r"^\s*?\#pragma[\sa-zA-Z0-9]+$", r"", max_repeat=0),
        # {\n\n\n
        # {
        SubRule(r"{\s+[\r\n]+", r"{\n", max_repeat=0),
        # Platform.Collections.Methods.Lists
        # Platform::Collections::Methods::Lists
        SubRule(r"(namespace[^\r\n]+?)\.([^\r\n]+?)", r"\1::\2", max_repeat=20),
        # nameof(numbers)
        # "numbers"
        SubRule(r"(?P<before>\W)nameof\(([^)\n]+\.)?(?P<name>[a-zA-Z0-9_]+)(<[^)\n]+>)?\)", r"\g<before>\"\g<name>\"", max_repeat=0),
        # Insert markers
        # EqualityComparer<T> _equalityComparer = EqualityComparer<T>.Default;
        # EqualityComparer<T> _equalityComparer = EqualityComparer<T>.Default;/*~_comparer~*/
        SubRule(r"(?P<declaration>EqualityComparer<(?P<type>[^>\n]+)> (?P<comparer>[a-zA-Z0-9_]+) = EqualityComparer<\k<type>>\.Default;)", r"\g<declaration>/*~\g<comparer>~*/", max_repeat=0),
        # /*~_equalityComparer~*/..._equalityComparer.Equals(Minimum, value)
        # /*~_equalityComparer~*/...Minimum == value
        SubRule(r"(?P<before>/\*~(?P<comparer>[a-zA-Z0-9_]+)~\*/(.|\n)+\W)\k<comparer>\.Equals\((?P<left>[^,\n]+), (?P<right>[^)\n]+)\)", r"\g<before>\g<left> == \g<right>", max_repeat=50),
        # Remove markers
        # /*~_equalityComparer~*/
        # 
        SubRule(r"\r?\n[^\n]+/\*~[a-zA-Z0-9_]+~\*/", r"", max_repeat=10),
        # Insert markers
        # Comparer<T> _comparer = Comparer<T>.Default;
        # Comparer<T> _comparer = Comparer<T>.Default;/*~_comparer~*/
        SubRule(r"(?P<declaration>Comparer<(?P<type>[^>\n]+)> (?P<comparer>[a-zA-Z0-9_]+) = Comparer<\k<type>>\.Default;)", r"\g<declaration>/*~\g<comparer>~*/", max_repeat=0),
        # /*~_comparer~*/..._comparer.Compare(Minimum, value) <= 0
        # /*~_comparer~*/...Minimum <= value
        SubRule(r"(?P<before>/\*~(?P<comparer>[a-zA-Z0-9_]+)~\*/(.|\n)+\W)\k<comparer>\.Compare\((?P<left>[^,\n]+), (?P<right>[^)\n]+)\)\s*(?P<comparison>[<>=]=?)\s*0(?P<after>\D)", r"\g<before>\g<left> \g<comparison> \g<right>\g<after>", max_repeat=50),
        # Remove markers
        # private static readonly Comparer<T> _comparer = Comparer<T>.Default;/*~_comparer~*/
        # 
        SubRule(r"\r?\n[^\n]+/\*~[a-zA-Z0-9_]+~\*/", r"", max_repeat=10),
        # Comparer<TArgument>.Default.Compare(maximumArgument, minimumArgument) < 0 
        # maximumArgument < minimumArgument
        SubRule(r"Comparer<[^>\n]+>\.Default\.Compare\(\s*(?P<first>[^,)\n]+),\s*(?P<second>[^\)\n]+)\s*\)\s*(?P<comparison>[<>=]=?)\s*0(?P<after>\D)", r"\g<first> \g<comparison> \g<second>\g<after>", max_repeat=0),
        # public static bool operator ==(Range<T> left, Range<T> right) => left.Equals(right);
        # 
        SubRule(r"\r?\n[^\n]+bool operator ==\((?P<type>[^\n]+) (?P<left>[a-zA-Z0-9]+), \k<type> (?P<right>[a-zA-Z0-9]+)\) => (\k<left>|\k<right>)\.Equals\((\k<left>|\k<right>)\);", r"", max_repeat=10),
        # public static bool operator !=(Range<T> left, Range<T> right) => !(left == right);
        # 
        SubRule(r"\r?\n[^\n]+bool operator !=\((?P<type>[^\n]+) (?P<left>[a-zA-Z0-9]+), \k<type> (?P<right>[a-zA-Z0-9]+)\) => !\((\k<left>|\k<right>) == (\k<left>|\k<right>)\);", r"", max_repeat=10),
        # public override bool Equals(object obj) => obj is Range<T> range ? Equals(range) : false;
        # 
        SubRule(r"\r?\n[^\n]+override bool Equals\((System\.)?[Oo]bject (?P<this>[a-zA-Z0-9]+)\) => \k<this> is [^\n]+ (?P<other>[a-zA-Z0-9]+) \? Equals\(\k<other>\) : false;", r"", max_repeat=10),
        # out TProduct
        # TProduct
        SubRule(r"(?P<before>(<|, ))(in|out) (?P<typeParameter>[a-zA-Z0-9]+)(?P<after>(>|,))", r"\g<before>\g<typeParameter>\g<after>", max_repeat=10),
        # public ...
        # public: ...
        SubRule(r"(?P<newLineAndIndent>\r?\n?[ \t]*)(?P<before>[^\{\(\r\n]*)(?P<access>private|protected|public)[ \t]+(?![^\{\(\r\n]*((?<=\s)|\W)(interface|class|struct)(\W)[^\{\(\r\n]*[\{\(\r\n])", r"\g<newLineAndIndent>\g<access>: \g<before>", max_repeat=0),
        # public: static bool CollectExceptions { get; set; }
        # public: inline static bool CollectExceptions;
        SubRule(r"(?P<access>(private|protected|public): )(?P<before>(static )?[^\r\n]+ )(?P<name>[a-zA-Z0-9]+) {[^;}]*(?<=\W)get;[^;}]*(?<=\W)set;[^;}]*}", r"\g<access>inline \g<before>\g<name>;", max_repeat=0),
        # public abstract class
        # class
        SubRule(r"((public|protected|private|internal|abstract|static) )*(?P<category>interface|class|struct)", r"\g<category>", max_repeat=0),
        # class GenericCollectionMethodsBase<TElement> {
        # template <typename TElement> class GenericCollectionMethodsBase {
        SubRule(r"(?P<before>\r?\n)(?P<indent>[ \t]*)(?P<type>class|struct) (?P<typeName>[a-zA-Z0-9]+)<(?P<typeParameters>[a-zA-Z0-9 ,]+)>(?P<typeDefinitionEnding>[^{]+){", r"\g<before>\g<indent>template <typename ...> \g<type> \g<typeName>;\n" + "\g<indent>template <typename \g<typeParameters>> \g<type> \g<typeName><\g<typeParameters>>\g<typeDefinitionEnding>{", max_repeat=0),
        # static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        # template<typename T> static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        SubRule(r"static ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>\(([^\)\r\n]+)\)", r"template <typename \3> static \1 \2(\4)", max_repeat=0),
        # interface IFactory<out TProduct> {
        # template <typename...> class IFactory;\ntemplate <typename TProduct> class IFactory<TProduct>
        SubRule(r"(?P<before>\r?\n)(?P<indent>[ \t]*)interface (?P<interface>[a-zA-Z0-9]+)<(?P<typeParameters>[a-zA-Z0-9 ,]+)>(?P<typeDefinitionEnding>[^{]+){", r"\g<before>\g<indent>template <typename ...> class \g<interface>;\n" + "\g<indent>template <typename \g<typeParameters>> class \g<interface><\g<typeParameters>>\g<typeDefinitionEnding>{\n" + "    public:", max_repeat=0),
        # template <typename TObject, TProperty, TValue>
        # template <typename TObject, typename TProperty, typename TValue>
        SubRule(r"(?P<before>template <((, )?typename [a-zA-Z0-9]+)+, )(?P<typeParameter>[a-zA-Z0-9]+)(?P<after>(,|>))", r"\g<before>typename \g<typeParameter>\g<after>", max_repeat=10),
        # Insert markers
        # private: static void BuildExceptionString(this StringBuilder sb, Exception exception, int level)
        # /*~extensionMethod~BuildExceptionString~*/private: static void BuildExceptionString(this StringBuilder sb, Exception exception, int level)
        SubRule(r"private: static [^\r\n]+ (?P<name>[a-zA-Z0-9]+)\(this [^\)\r\n]+\)", r"/*~extensionMethod~\g<name>~*/\0", max_repeat=0),
        # Move all markers to the beginning of the file.
        SubRule(r"\A(?P<before>[^\r\n]+\r?\n(.|\n)+)(?P<marker>/\*~extensionMethod~(?P<name>[a-zA-Z0-9]+)~\*/)", r"\g<marker>\g<before>", max_repeat=10),
        # /*~extensionMethod~BuildExceptionString~*/...sb.BuildExceptionString(exception.InnerException, level + 1);
        # /*~extensionMethod~BuildExceptionString~*/...BuildExceptionString(sb, exception.InnerException, level + 1);
        SubRule(r"(?P<before>/\*~extensionMethod~(?P<name>[a-zA-Z0-9]+)~\*/(.|\n)+\W)(?P<variable>[_a-zA-Z0-9]+)\.\k<name>\(", r"\g<before>\g<name>(\g<variable>, ", max_repeat=50),
        # Remove markers
        # /*~extensionMethod~BuildExceptionString~*/
        # 
        SubRule(r"/\*~extensionMethod~[a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # (this 
        # (
        SubRule(r"\(this ", r"(", max_repeat=0),
        # private: static readonly Disposal _emptyDelegate = (manual, wasDisposed) => { };
        # private: inline static std::function<Disposal> _emptyDelegate = [](auto manual, auto wasDisposed) { };
        SubRule(r"(?P<access>(private|protected|public): )?static readonly (?P<type>[a-zA-Z][a-zA-Z0-9]*) (?P<name>[a-zA-Z_][a-zA-Z0-9_]*) = \((?P<firstArgument>[a-zA-Z_][a-zA-Z0-9_]*), (?P<secondArgument>[a-zA-Z_][a-zA-Z0-9_]*)\) => {\s*};", r"\g<access>inline static std::function<\g<type>> \g<name> = [](auto \g<firstArgument>, auto \g<secondArgument>) { };", max_repeat=0),
        # public: static readonly EnsureAlwaysExtensionRoot Always = new EnsureAlwaysExtensionRoot();
        # public: inline static EnsureAlwaysExtensionRoot Always;
        SubRule(r"(?P<access>(private|protected|public): )?static readonly (?P<type>[a-zA-Z0-9]+(<[a-zA-Z0-9]+>)?) (?P<name>[a-zA-Z0-9_]+) = new \k<type>\(\);", r"\g<access>inline static \g<type> \g<name>;", max_repeat=0),
        # public: static readonly Range<int> SByte = new Range<int>(std::numeric_limits<int>::min(), std::numeric_limits<int>::max());
        # public: inline static Range<int> SByte = Range<int>(std::numeric_limits<int>::min(), std::numeric_limits<int>::max());
        SubRule(r"(?P<access>(private|protected|public): )?static readonly (?P<type>[a-zA-Z0-9]+(<[a-zA-Z0-9]+>)?) (?P<name>[a-zA-Z0-9_]+) = new \k<type>\((?P<arguments>[^\n]+)\);", r"\g<access>inline static \g<type> \g<name> = \g<type>(\g<arguments>);", max_repeat=0),
        # public: static readonly string ExceptionContentsSeparator = "---";
        # public: inline static std::string ExceptionContentsSeparator = "---";
        SubRule(r"(?P<access>(private|protected|public): )?(const|static readonly) string (?P<name>[a-zA-Z0-9_]+) = \"\"(?P<string>(\\\"\"|[^\"\"\r\n])+)\"\";", r"\g<access>inline static std::string \g<name> = \"\g<string>\";", max_repeat=0),
        # private: const int MaxPath = 92;
        # private: inline static const int MaxPath = 92;
        SubRule(r"(?P<access>(private|protected|public): )?(const|static readonly) (?P<type>[a-zA-Z0-9]+) (?P<name>[_a-zA-Z0-9]+) = (?P<value>[^;\r\n]+);", r"\g<access>inline static const \g<type> \g<name> = \g<value>;", max_repeat=0),
        #  ArgumentNotNull(EnsureAlwaysExtensionRoot root, TArgument argument) where TArgument : class
        #  ArgumentNotNull(EnsureAlwaysExtensionRoot root, TArgument* argument)
        SubRule(r"(?P<before> [a-zA-Z]+\(([a-zA-Z *,]+, |))(?P<type>[a-zA-Z]+)(?P<after>(| [a-zA-Z *,]+)\))[ \r\n]+where \k<type> : class", r"\g<before>\g<type>*\g<after>", max_repeat=0),
        # protected: abstract TElement GetFirst();
        # protected: virtual TElement GetFirst() = 0;
        SubRule(r"(?P<access>(private|protected|public): )?abstract (?P<method>[^;\r\n]+);", r"\g<access>virtual \g<method> = 0;", max_repeat=0),
        # TElement GetFirst();
        # virtual TElement GetFirst() = 0;
        SubRule(r"(?P<before>[\r\n]+[ ]+)(?P<methodDeclaration>(?!return)[a-zA-Z0-9]+ [a-zA-Z0-9]+\([^\)\r\n]*\))(?P<after>;[ ]*[\r\n]+)", r"\g<before>virtual \g<methodDeclaration> = 0\g<after>", max_repeat=1),
        # protected: readonly TreeElement[] _elements;
        # protected: TreeElement _elements[N];
        SubRule(r"(?P<access>(private|protected|public): )?readonly (?P<type>[a-zA-Z<>0-9]+)([\[\]]+) (?P<name>[_a-zA-Z0-9]+);", r"\g<access>\g<type> \g<name>[N];", max_repeat=0),
        # protected: readonly TElement Zero;
        # protected: TElement Zero;
        SubRule(r"(?P<access>(private|protected|public): )?readonly (?P<type>[a-zA-Z<>0-9]+) (?P<name>[_a-zA-Z0-9]+);", r"\g<access>\g<type> \g<name>;", max_repeat=0),
        # internal
        # 
        SubRule(r"(\W)internal\s+", r"\1", max_repeat=0),
        # static void NotImplementedException(ThrowExtensionRoot root) => throw new NotImplementedException();
        # static void NotImplementedException(ThrowExtensionRoot root) { return throw new NotImplementedException(); }
        SubRule(r"(^\s+)(private|protected|public)?(: )?(template \<[^>\r\n]+\> )?(static )?(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+throw([^;\r\n]+);", r"\1\2\3\4\5\6\7\8(\9) { throw\10; }", max_repeat=0),
        # SizeBalancedTree(int capacity) => a = b;
        # SizeBalancedTree(int capacity) { a = b; }
        SubRule(r"(^\s+)(private|protected|public)?(: )?(template \<[^>\r\n]+\> )?(static )?(override )?(void )?([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+([^;\r\n]+);", r"\1\2\3\4\5\6\7\8(\9) { \10; }", max_repeat=0),
        # int SizeBalancedTree(int capacity) => a;
        # int SizeBalancedTree(int capacity) { return a; }
        SubRule(r"(^\s+)(private|protected|public)?(: )?(template \<[^>\r\n]+\> )?(static )?(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+([^;\r\n]+);", r"\1\2\3\4\5\6\7\8(\9) { return \10; }", max_repeat=0),
        # OnDispose = (manual, wasDisposed) =>
        # OnDispose = [&](auto manual, auto wasDisposed)
        SubRule(r"(?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)(?P<operator>\s*\+?=\s*)\((?P<firstArgument>[a-zA-Z_][a-zA-Z0-9_]*), (?P<secondArgument>[a-zA-Z_][a-zA-Z0-9_]*)\)\s*=>", r"\g<variable>\g<operator>[&](auto \g<firstArgument>, auto \g<secondArgument>)", max_repeat=0),
        # () => Integer<TElement>.Zero,
        # () { return Integer<TElement>.Zero; },
        SubRule(r"\(\)\s+=>\s+(?P<expression>[^(),;\r\n]+(\(((?P<parenthesis>\()|(?(parenthesis)\))|[^();\r\n]*?)*?\))?[^(),;\r\n]*)(?P<after>,|\);)", r"() { return \g<expression>; }\g<after>", max_repeat=0),
        # ~DisposableBase() => Destruct();
        # ~DisposableBase() { Destruct(); }
        SubRule(r"~(?P<class>[a-zA-Z_][a-zA-Z0-9_]*)\(\)\s+=>\s+([^;\r\n]+?);", r"~\g<class>() { \1; }", max_repeat=0),
        # => Integer<TElement>.Zero;
        # { return Integer<TElement>.Zero; }
        SubRule(r"\)\s+=>\s+([^;\r\n]+?);", r") { return \1; }", max_repeat=0),
        # () { return avlTree.Count; }
        # [&]()-> auto { return avlTree.Count; }
        SubRule(r"(?P<before>, |\()\(\) { return (?P<expression>[^;\r\n]+); }", r"\g<before>[&]()-> auto { return \g<expression>; }", max_repeat=0),
        # Count => GetSizeOrZero(Root);
        # Count() { return GetSizeOrZero(Root); }
        SubRule(r"(\W)([A-Z][a-zA-Z]+)\s+=>\s+([^;\r\n]+);", r"\1\2() { return \3; }", max_repeat=0),
        # Insert scope borders.
        # interface IDisposable { ... }
        # interface IDisposable {/*~start~interface~IDisposable~*/ ... /*~end~interface~IDisposable~*/}
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)interface[\t ]*(?P<type>[a-zA-Z][a-zA-Z0-9]*(<[^<>\n]*>)?)[^{}]*{)(?P<middle>(.|\n)*)(?P<beforeEnd>(?<=\r?\n)\k<indent>)(?P<end>})", r"\g<classDeclarationBegin>/*~start~interface~\g<type>~*/\g<middle>\g<beforeEnd>/*~end~interface~\g<type>~*/\g<end>", max_repeat=0),
        # Inside the scope replace:
        # /*~start~interface~IDisposable~*/ ... bool IsDisposed { get; } ... /*~end~interface~IDisposable~*/
        # /*~start~interface~IDisposable~*/ ... virtual bool IsDisposed() = 0; /*~end~interface~IDisposable~*/
        SubRule(r"(?P<before>(?P<typeScopeStart>/\*~start~interface~(?P<type>[^~\n\*]+)~\*/)(.|\n)+?)(?P<propertyDeclaration>(?P<access>(private|protected|public): )?(?P<propertyType>[a-zA-Z_][a-zA-Z0-9_:<>]*) (?P<property>[a-zA-Z_][a-zA-Z0-9_]*)(?P<blockOpen>[\n\s]*{[\n\s]*)(\[[^\n]+\][\n\s]*)?get;(?P<blockClose>[\n\s]*}))(?P<after>(.|\n)+?(?P<typeScopeEnd>/\*~end~interface~\k<type>~\*/))", r"\g<before>virtual \g<propertyType> \g<property>() = 0;\g<after>", max_repeat=20),
        # Remove scope borders.
        # /*~start~interface~IDisposable~*/
        # 
        SubRule(r"/\*~[^~\*\n]+(~[^~\*\n]+)*~\*/", r"", max_repeat=0),
        # public: T Object { get; }
        # public: const T Object;
        SubRule(r"(?P<before>[^\r]\r?\n[ \t]*)(?P<access>(private|protected|public): )?(?P<type>[a-zA-Z_][a-zA-Z0-9_:<>]*) (?P<property>[a-zA-Z_][a-zA-Z0-9_]*)(?P<blockOpen>[\n\s]*{[\n\s]*)(\[[^\n]+\][\n\s]*)?get;(?P<blockClose>[\n\s]*})(?P<after>[\n\s]*)", r"\g<before>\g<access>const \g<type> \g<property>;\g<after>", max_repeat=2),
        # public: bool IsDisposed { get => _disposed > 0; }
        # public: bool IsDisposed() { return _disposed > 0; }
        SubRule(r"(?P<before>[^\r]\r?\n[ \t]*)(?P<access>(private|protected|public): )?(?P<virtual>virtual )?bool (?P<property>[a-zA-Z_][a-zA-Z0-9_]*)(?P<blockOpen>[\n\s]*{[\n\s]*)(\[[^\n]+\][\n\s]*)?get\s*=>\s*(?P<expression>[^\n]+);(?P<blockClose>[\n\s]*}[\n\s]*)", r"\g<before>\g<access>\g<virtual>bool \g<property>()\g<blockOpen>return \g<expression>;\g<blockClose>", max_repeat=2),
        # protected: virtual std::string ObjectName { get => GetType().Name; }
        # protected: virtual std::string ObjectName() { return GetType().Name; }
        SubRule(r"(?P<before>[^\r]\r?\n[ \t]*)(?P<access>(private|protected|public): )?(?P<virtual>virtual )?(?P<type>[a-zA-Z_][a-zA-Z0-9_:<>]*) (?P<property>[a-zA-Z_][a-zA-Z0-9_]*)(?P<blockOpen>[\n\s]*{[\n\s]*)(\[[^\n]+\][\n\s]*)?get\s*=>\s*(?P<expression>[^\n]+);(?P<blockClose>[\n\s]*}[\n\s]*)", r"\g<before>\g<access>\g<virtual>\g<type> \g<property>()\g<blockOpen>return \g<expression>;\g<blockClose>", max_repeat=2),
        # ArgumentInRange(string message) { string messageBuilder() { return message; }
        # ArgumentInRange(string message) { auto messageBuilder = [&]() -> string { return message; };
        SubRule(r"(?P<before>\W[_a-zA-Z0-9]+\([^\)\n]*\)[\s\n]*{[\s\n]*([^{}]|\n)*?(\r?\n)?[ \t]*)(?P<returnType>[_a-zA-Z0-9*:]+[_a-zA-Z0-9*: ]*) (?P<methodName>[_a-zA-Z0-9]+)\((?P<arguments>[^\)\n]*)\)\s*{(?P<body>(""[^""\n]+""|[^}]|\n)+?)}", r"\g<before>auto \g<methodName> = [&]() -> \g<returnType> {\g<body>};", max_repeat=10),
        # Func<TElement> treeCount
        # std::function<TElement()> treeCount
        SubRule(r"Func<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<\1()> \2", max_repeat=0),
        # Action<TElement> free
        # std::function<void(TElement)> free
        SubRule(r"Action(<(?P<typeParameters>[a-zA-Z0-9]+(, ([a-zA-Z0-9]+))*)>)?(?P<after>>| (?P<variable>[a-zA-Z0-9]+))", r"std::function<void(\g<typeParameters>)>\g<after>", max_repeat=0),
        # Predicate<TArgument> predicate
        # std::function<bool(TArgument)> predicate
        SubRule(r"Predicate<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<bool(\1)> \2", max_repeat=0),
        # var
        # auto
        SubRule(r"(\W)var(\W)", r"\1auto\2", max_repeat=0),
        # unchecked
        # 
        SubRule(r"[\r\n]{2}\s*?unchecked\s*?$", r"", max_repeat=0),
        # throw new
        # throw
        SubRule(r"(\W)throw new(\W)", r"\1throw\2", max_repeat=0),
        # void RaiseExceptionIgnoredEvent(Exception exception)
        # void RaiseExceptionIgnoredEvent(const std::exception& exception)
        SubRule(r"(\(|, )(System\.Exception|Exception)( |\))", r"\1const std::exception&\3", max_repeat=0),
        # EventHandler<Exception>
        # EventHandler<std::exception>
        SubRule(r"(\W)(System\.Exception|Exception)(\W)", r"\1std::exception\3", max_repeat=0),
        # override void PrintNode(TElement node, StringBuilder sb, int level)
        # void PrintNode(TElement node, StringBuilder sb, int level) override
        SubRule(r"override ([a-zA-Z0-9 \*\+]+)(\([^\)\r\n]+?\))", r"\1\2 override", max_repeat=0),
        # return (range.Minimum, range.Maximum)
        # return {range.Minimum, range.Maximum}
        SubRule(r"(?P<before>return\s*)\((?P<values>[^\)\n]+)\)(?!\()(?P<after>\W)", r"\g<before>{\g<values>}\g<after>", max_repeat=0),
        # string
        # std::string
        SubRule(r"(?P<before>\W)(?<!::)string(?P<after>\W)", r"\g<before>std::string\g<after>", max_repeat=0),
        # System.ValueTuple
        # std::tuple
        SubRule(r"(?P<before>\W)(System\.)?ValueTuple(?!\s*=|\()(?P<after>\W)", r"\g<before>std::tuple\g<after>", max_repeat=0),
        # sbyte
        # std::int8_t
        SubRule(r"(?P<before>\W)((System\.)?SB|sb)yte(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int8_t\g<after>", max_repeat=0),
        # short
        # std::int16_t
        SubRule(r"(?P<before>\W)((System\.)?Int16|short)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int16_t\g<after>", max_repeat=0),
        # int
        # std::int32_t
        SubRule(r"(?P<before>\W)((System\.)?I|i)nt(32)?(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int32_t\g<after>", max_repeat=0),
        # long
        # std::int64_t
        SubRule(r"(?P<before>\W)((System\.)?Int64|long)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::int64_t\g<after>", max_repeat=0),
        # byte
        # std::uint8_t
        SubRule(r"(?P<before>\W)((System\.)?Byte|byte)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint8_t\g<after>", max_repeat=0),
        # ushort
        # std::uint16_t
        SubRule(r"(?P<before>\W)((System\.)?UInt16|ushort)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint16_t\g<after>", max_repeat=0),
        # uint
        # std::uint32_t
        SubRule(r"(?P<before>\W)((System\.)?UI|ui)nt(32)?(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint32_t\g<after>", max_repeat=0),
        # ulong
        # std::uint64_t
        SubRule(r"(?P<before>\W)((System\.)?UInt64|ulong)(?!\s*=|\()(?P<after>\W)", r"\g<before>std::uint64_t\g<after>", max_repeat=0),
        # char*[] args
        # char* args[]
        SubRule(r"([_a-zA-Z0-9:\*]?)\[\] ([a-zA-Z0-9]+)", r"\1 \2[]", max_repeat=0),
        # float.MinValue
        # std::numeric_limits<float>::lowest()
        SubRule(r"(?P<before>\W)(?P<type>std::[a-z0-9_]+|float|double)\.MinValue(?P<after>\W)", r"\g<before>std::numeric_limits<\g<type>>::lowest()\g<after>", max_repeat=0),
        # double.MaxValue
        # std::numeric_limits<float>::max()
        SubRule(r"(?P<before>\W)(?P<type>std::[a-z0-9_]+|float|double)\.MaxValue(?P<after>\W)", r"\g<before>std::numeric_limits<\g<type>>::max()\g<after>", max_repeat=0),
        # using Platform.Numbers;
        # 
        SubRule(r"([\r\n]{2}|^)\s*?using [\.a-zA-Z0-9]+;\s*?$", r"", max_repeat=0),
        # class SizedBinaryTreeMethodsBase : GenericCollectionMethodsBase
        # class SizedBinaryTreeMethodsBase : public GenericCollectionMethodsBase
        SubRule(r"(struct|class) ([a-zA-Z0-9]+)(<[a-zA-Z0-9 ,]+>)? : ([a-zA-Z0-9]+)", r"\1 \2\3 : public \4", max_repeat=0),
        # System.IDisposable
        # System::IDisposable
        SubRule(r"(?P<before>System(::[a-zA-Z_]\w*)*)\.(?P<after>[a-zA-Z_]\w*)", r"\g<before>::\g<after>", max_repeat=20),
        # class IProperty : ISetter<TValue, TObject>, IProvider<TValue, TObject>
        # class IProperty : public ISetter<TValue, TObject>, public IProvider<TValue, TObject>
        SubRule(r"(?P<before>(interface|struct|class) [a-zA-Z_]\w* : ((public [a-zA-Z_][\w:]*(<[a-zA-Z0-9 ,]+>)?, )+)?)(?P<inheritedType>(?!public)[a-zA-Z_][\w:]*(<[a-zA-Z0-9 ,]+>)?)(?P<after>(, [a-zA-Z_][\w:]*(?!>)|[ \r\n]+))", r"\g<before>public \g<inheritedType>\g<after>", max_repeat=10),
        # interface IDisposable {
        # class IDisposable { public:
        SubRule(r"(?P<before>\r?\n)(?P<indent>[ \t]*)interface (?P<interface>[a-zA-Z_]\w*)(?P<typeDefinitionEnding>[^{]+){", r"\g<before>\g<indent>class \g<interface>\g<typeDefinitionEnding>{\n" + "    public:", max_repeat=0),
        # struct TreeElement { }
        # struct TreeElement { };
        SubRule(r"(struct|class) ([a-zA-Z0-9]+)(\s+){([\sa-zA-Z0-9;:_]+?)}([^;])", r"\1 \2\3{\4};\5", max_repeat=0),
        # class Program { }
        # class Program { };
        SubRule(r"(?P<type>struct|class) (?P<name>[a-zA-Z0-9]+[^\r\n]*)(?P<beforeBody>[\r\n]+(?P<indentLevel>[\t ]*)?)\{(?P<body>[\S\s]+?[\r\n]+\k<indentLevel>)\}(?P<afterBody>[^;]|$)", r"\g<type> \g<name>\g<beforeBody>{\g<body>};\g<afterBody>", max_repeat=0),
        # Insert scope borders.
        # ref TElement root
        # ~!root!~ref TElement root
        SubRule(r"(?P<definition>(?<= |\()(ref [a-zA-Z0-9]+|[a-zA-Z0-9]+(?<!ref)) (?P<variable>[a-zA-Z0-9]+)(?=\)|, | =))", r"~!\g<variable>!~\g<definition>", max_repeat=0),
        # Inside the scope of ~!root!~ replace:
        # root
        # *root
        SubRule(r"(?P<definition>~!(?P<pointer>[a-zA-Z0-9]+)!~ref [a-zA-Z0-9]+ \k<pointer>(?=\)|, | =))(?P<before>((?<!~!\k<pointer>!~)(.|\n))*?)(?P<prefix>(\W |\())\k<pointer>(?P<suffix>( |\)|;|,))", r"\g<definition>\g<before>\g<prefix>*\g<pointer>\g<suffix>", max_repeat=70),
        # Remove scope borders.
        # ~!root!~
        # 
        SubRule(r"~!(?P<pointer>[a-zA-Z0-9]+)!~", r"", max_repeat=5),
        # ref auto root = ref
        # ref auto root = 
        SubRule(r"ref ([a-zA-Z0-9]+) ([a-zA-Z0-9]+) = ref(\W)", r"\1* \2 =\3", max_repeat=0),
        # *root = ref left;
        # root = left;
        SubRule(r"\*([a-zA-Z0-9]+) = ref ([a-zA-Z0-9]+)(\W)", r"\1 = \2\3", max_repeat=0),
        # (ref left)
        # (left)
        SubRule(r"\(ref ([a-zA-Z0-9]+)(\)|\(|,)", r"(\1\2", max_repeat=0),
        #  ref TElement 
        #  TElement* 
        SubRule(r"( |\()ref ([a-zA-Z0-9]+) ", r"\1\2* ", max_repeat=0),
        # ref sizeBalancedTree.Root
        # &sizeBalancedTree->Root
        SubRule(r"ref ([a-zA-Z0-9]+)\.([a-zA-Z0-9\*]+)", r"&\1->\2", max_repeat=0),
        # ref GetElement(node).Right
        # &GetElement(node)->Right
        SubRule(r"ref ([a-zA-Z0-9]+)\(([a-zA-Z0-9\*]+)\)\.([a-zA-Z0-9]+)", r"&\1(\2)->\3", max_repeat=0),
        # GetElement(node).Right
        # GetElement(node)->Right
        SubRule(r"([a-zA-Z0-9]+)\(([a-zA-Z0-9\*]+)\)\.([a-zA-Z0-9]+)", r"\1(\2)->\3", max_repeat=0),
        # [Fact]\npublic: static void SizeBalancedTreeMultipleAttachAndDetachTest()
        # public: TEST_METHOD(SizeBalancedTreeMultipleAttachAndDetachTest)
        SubRule(r"\[Fact\][\s\n]+(public: )?(static )?void ([a-zA-Z0-9]+)\(\)", r"public: TEST_METHOD(\3)", max_repeat=0),
        # class TreesTests
        # TEST_CLASS(TreesTests)
        SubRule(r"class ([a-zA-Z0-9]+Tests)", r"TEST_CLASS(\1)", max_repeat=0),
        # Assert.Equal
        # Assert::AreEqual
        SubRule(r"(?P<type>Assert)\.(?P<method>(Not)?Equal)", r"\g<type>::Are\g<method>", max_repeat=0),
        # Assert.Throws
        # Assert::ExpectException
        SubRule(r"(Assert)\.Throws", r"\1::ExpectException", max_repeat=0),
        # Assert.True
        # Assert::IsTrue
        SubRule(r"(Assert)\.(True|False)", r"\1::Is\2", max_repeat=0),
        # $"Argument {argumentName} is null."
        # std::string("Argument ").append(Platform::Converters::To<std::string>(argumentName)).append(" is null.")
        SubRule(r"\$\"\"(?P<left>(\\\"\"|[^\"\"\r\n])*){(?P<expression>[_a-zA-Z0-9]+)}(?P<right>(\\\"\"|[^\"\"\r\n])*)\"\"", r"std::string($\"\g<left>\").append(Platform::Converters::To<std::string>(\g<expression>)).append(\"\g<right>\")", max_repeat=10),
        # $"
        # "
        SubRule(r"\$""", r"\"", max_repeat=0),
        # std::string(std::string("[").append(Platform::Converters::To<std::string>(Minimum)).append(", ")).append(Platform::Converters::To<std::string>(Maximum)).append("]")
        # std::string("[").append(Platform::Converters::To<std::string>(Minimum)).append(", ").append(Platform::Converters::To<std::string>(Maximum)).append("]")
        SubRule(r"std::string\((?P<begin>std::string\(\"\"(\\\"\"|[^\"\"])*\"\"\)(\.append\((Platform::Converters::To<std::string>\([^)\n]+\)|[^)\n]+)\))+)\)\.append", r"\g<begin>.append", max_repeat=10),
        # Console.WriteLine("...")
        # printf("...\n")
        SubRule(r"Console\.WriteLine\(\"\"([^\"\"\r\n]+)\"\"\)", r"printf(\"\1\\n\")", max_repeat=0),
        # TElement Root;
        # TElement Root = 0;
        SubRule(r"(?P<before>\r?\n[\t ]+)(?P<access>(private|protected|public)(: )?)?(?P<type>[a-zA-Z0-9:_]+(?<!return)) (?P<name>[_a-zA-Z0-9]+);", r"\g<before>\g<access>\g<type> \g<name> = 0;", max_repeat=0),
        # TreeElement _elements[N];
        # TreeElement _elements[N] = { {0} };
        SubRule(r"(\r?\n[\t ]+)(private|protected|public)?(: )?([a-zA-Z0-9]+) ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\2\3\4 \5[\6] = { {0} };", max_repeat=0),
        # auto path = new TElement[MaxPath];
        # TElement path[MaxPath] = { {0} };
        SubRule(r"(\r?\n[\t ]+)[a-zA-Z0-9]+ ([a-zA-Z0-9]+) = new ([a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\3 \2[\4] = { {0} };", max_repeat=0),
        # bool Equals(Range<T> other) { ... }
        # bool operator ==(const Key &other) const { ... }
        SubRule(r"(?P<before>\r?\n[^\n]+bool )Equals\((?P<type>[^\n{]+) (?P<variable>[a-zA-Z0-9]+)\)(?P<after>(\s|\n)*{)", r"\g<before>operator ==(const \g<type> &\g<variable>) const\g<after>", max_repeat=0),
        # Insert scope borders.
        # class Range { ... public: override std::string ToString() { return ...; }
        # class Range {/*~Range<T>~*/ ... public: override std::string ToString() { return ...; }
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)template <typename (?P<typeParameter>[^<>\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<\k<typeParameter>>)(\s*:\s*[^{\n]+)?[\t ]*(\r?\n)?[\t ]*{)(?P<middle>((?!class|struct).|\n)+?)(?P<toStringDeclaration>(?P<access>(private|protected|public): )override std::string ToString\(\))", r"\g<classDeclarationBegin>/*~\g<type>~*/\g<middle>\g<toStringDeclaration>", max_repeat=0),
        # Inside the scope of ~!Range!~ replace:
        # public: override std::string ToString() { return ...; }
        # public: operator std::string() const { return ...; }\n\npublic: friend std::ostream & operator <<(std::ostream &out, const A &obj) { return out << (std::string)obj; }
        SubRule(r"(?P<scope>/\*~(?P<type>[_a-zA-Z0-9<>:]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<type>~\*/)(.|\n))*?)(?P<toStringDeclaration>\r?\n(?P<indent>[ \t]*)(?P<access>(private|protected|public): )override std::string ToString\(\) (?P<toStringMethodBody>{[^}\n]+}))", r"\g<scope>\g<separator>\g<before>\n\g<indent>\g<access>operator std::string() const \g<toStringMethodBody>\n\n\g<indent>\g<access>friend std::ostream & operator <<(std::ostream &out, const \g<type> &obj) { return out << (std::string)obj; }", max_repeat=0),
        # Remove scope borders.
        # /*~Range~*/
        # 
        SubRule(r"/\*~[_a-zA-Z0-9<>:]+~\*/", r"", max_repeat=0),
        # private: inline static ConcurrentBag<std::exception> _exceptionsBag;
        # private: inline static std::mutex _exceptionsBag_mutex; \n\n private: inline static std::vector<std::exception> _exceptionsBag;
        SubRule(r"(?P<begin>\r?\n?(?P<indent>[ \t]+))(?P<access>(private|protected|public): )?inline static ConcurrentBag<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+);", r"\g<begin>private: inline static std::mutex \g<name>_mutex;\n\n\g<indent>\g<access>inline static std::vector<\g<argumentType>> \g<name>;", max_repeat=0),
        # public: static IReadOnlyCollection<std::exception> GetCollectedExceptions() { return _exceptionsBag; }
        # public: static std::vector<std::exception> GetCollectedExceptions() { return std::vector<std::exception>(_exceptionsBag); }
        SubRule(r"(?P<access>(private|protected|public): )?static IReadOnlyCollection<(?P<argumentType>[^;\r\n]+)> (?P<methodName>[_a-zA-Z0-9]+)\(\) { return (?P<fieldName>[_a-zA-Z0-9]+); }", r"\g<access>static std::vector<\g<argumentType>> \g<methodName>() { return std::vector<\g<argumentType>>(\g<fieldName>); }", max_repeat=0),
        # public: static event EventHandler<std::exception> ExceptionIgnored = OnExceptionIgnored; ... };
        # ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored; };
        SubRule(r"(?P<begin>\r?\n(\r?\n)?(?P<halfIndent>[ \t]+)\k<halfIndent>)(?P<access>(private|protected|public): )?static event EventHandler<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+) = (?P<defaultDelegate>[_a-zA-Z0-9]+);(?P<middle>(.|\n)+?)(?P<end>\r?\n\k<halfIndent>};)", r"\g<middle>\n\n\g<halfIndent>\g<halfIndent>\g<access>static inline Platform::Delegates::MulticastDelegate<void(void*, const \g<argumentType>&)> \g<name> = \g<defaultDelegate>;\g<end>", max_repeat=0),
        # public: event Disposal OnDispose;
        # public: Platform::Delegates::MulticastDelegate<Disposal> OnDispose;
        SubRule(r"(?P<begin>(?P<access>(private|protected|public): )?(static )?)event (?P<type>[a-zA-Z][:_a-zA-Z0-9]+) (?P<name>[a-zA-Z][_a-zA-Z0-9]+);", r"\g<begin>Platform::Delegates::MulticastDelegate<\g<type>> \g<name>;", max_repeat=0),
        # Insert scope borders.
        # class IgnoredExceptions { ... private: inline static std::vector<std::exception> _exceptionsBag;
        # class IgnoredExceptions {/*~_exceptionsBag~*/ ... private: inline static std::vector<std::exception> _exceptionsBag;
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<vectorFieldDeclaration>(?P<access>(private|protected|public): )inline static std::vector<(?P<argumentType>[^;\r\n]+)> (?P<fieldName>[_a-zA-Z0-9]+);)", r"\g<classDeclarationBegin>/*~\g<fieldName>~*/\g<middle>\g<vectorFieldDeclaration>", max_repeat=0),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # _exceptionsBag.Add(exception);
        # _exceptionsBag.push_back(exception);
        SubRule(r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<fieldName>~\*/)(.|\n))*?)\k<fieldName>\.Add", r"\g<scope>\g<separator>\g<before>\g<fieldName>.push_back", max_repeat=10),
        # Remove scope borders.
        # /*~_exceptionsBag~*/
        # 
        SubRule(r"/\*~[_a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # class IgnoredExceptions { ... private: static std::mutex _exceptionsBag_mutex;
        # class IgnoredExceptions {/*~_exceptionsBag~*/ ... private: static std::mutex _exceptionsBag_mutex;
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<mutexDeclaration>private: inline static std::mutex (?P<fieldName>[_a-zA-Z0-9]+)_mutex;)", r"\g<classDeclarationBegin>/*~\g<fieldName>~*/\g<middle>\g<mutexDeclaration>", max_repeat=0),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # return std::vector<std::exception>(_exceptionsBag);
        # std::lock_guard<std::mutex> guard(_exceptionsBag_mutex); return std::vector<std::exception>(_exceptionsBag);
        SubRule(r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<fieldName>~\*/)(.|\n))*?){(?P<after>((?!lock_guard)[^{};\r\n])*\k<fieldName>[^;}\r\n]*;)", r"\g<scope>\g<separator>\g<before>{ std::lock_guard<std::mutex> guard(\g<fieldName>_mutex);\g<after>", max_repeat=10),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # _exceptionsBag.Add(exception);
        # std::lock_guard<std::mutex> guard(_exceptionsBag_mutex); \r\n _exceptionsBag.Add(exception);
        SubRule(r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<fieldName>~\*/)(.|\n))*?){(?P<after>((?!lock_guard)([^{};]|\n))*?\r?\n(?P<indent>[ \t]*)\k<fieldName>[^;}\r\n]*;)", r"\g<scope>\g<separator>\g<before>{\n" + "\g<indent>std::lock_guard<std::mutex> guard(\g<fieldName>_mutex);\g<after>", max_repeat=10),
        # Remove scope borders.
        # /*~_exceptionsBag~*/
        # 
        SubRule(r"/\*~[_a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # class IgnoredExceptions { ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored;
        # class IgnoredExceptions {/*~ExceptionIgnored~*/ ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored;
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<eventDeclaration>(?P<access>(private|protected|public): )static inline Platform::Delegates::MulticastDelegate<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+) = (?P<defaultDelegate>[_a-zA-Z0-9]+);)", r"\g<classDeclarationBegin>/*~\g<name>~*/\g<middle>\g<eventDeclaration>", max_repeat=0),
        # Inside the scope of ~!ExceptionIgnored!~ replace:
        # ExceptionIgnored.Invoke(NULL, exception);
        # ExceptionIgnored(NULL, exception);
        SubRule(r"(?P<scope>/\*~(?P<eventName>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<eventName>~\*/)(.|\n))*?)\k<eventName>\.Invoke", r"\g<scope>\g<separator>\g<before>\g<eventName>", max_repeat=10),
        # Remove scope borders.
        # /*~ExceptionIgnored~*/
        # 
        SubRule(r"/\*~[a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # auto added = new StringBuilder();
        # /*~sb~*/std::string added;
        SubRule(r"(auto|(System\.Text\.)?StringBuilder) (?P<variable>[a-zA-Z0-9]+) = new (System\.Text\.)?StringBuilder\(\);", r"/*~\g<variable>~*/std::string \g<variable>;", max_repeat=0),
        # static void Indent(StringBuilder sb, int level)
        # static void Indent(/*~sb~*/StringBuilder sb, int level)
        SubRule(r"(?P<start>, |\()(System\.Text\.)?StringBuilder (?P<variable>[a-zA-Z0-9]+)(?P<end>,|\))", r"\g<start>/*~\g<variable>~*/std::string& \g<variable>\g<end>", max_repeat=0),
        # Inside the scope of ~!added!~ replace:
        # sb.ToString()
        # sb
        SubRule(r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.ToString\(\)", r"\g<scope>\g<separator>\g<before>\g<variable>", max_repeat=10),
        # sb.AppendLine(argument)
        # sb.append(Platform::Converters::To<std::string>(argument)).append(1, '\n')
        SubRule(r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.AppendLine\((?P<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(Platform::Converters::To<std::string>(\g<argument>)).append(1, '\\n')", max_repeat=10),
        # sb.Append('\t', level);
        # sb.append(level, '\t');
        SubRule(r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.Append\('(?P<character>[^'\r\n]+)', (?P<count>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<count>, '\g<character>')", max_repeat=10),
        # sb.Append(argument)
        # sb.append(Platform::Converters::To<std::string>(argument))
        SubRule(r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.Append\((?P<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(Platform::Converters::To<std::string>(\g<argument>))", max_repeat=10),
        # Remove scope borders.
        # /*~sb~*/
        # 
        SubRule(r"/\*~[a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # auto added = new HashSet<TElement>();
        # ~!added!~std::unordered_set<TElement> added;
        SubRule(r"auto (?P<variable>[a-zA-Z0-9]+) = new HashSet<(?P<element>[a-zA-Z0-9]+)>\(\);", r"~!\g<variable>!~std::unordered_set<\g<element>> \g<variable>;", max_repeat=0),
        # Inside the scope of ~!added!~ replace:
        # added.Add(node)
        # added.insert(node)
        SubRule(r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!\k<variable>!~)(.|\n))*?)\k<variable>\.Add\((?P<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.insert(\g<argument>)", max_repeat=10),
        # Inside the scope of ~!added!~ replace:
        # added.Remove(node)
        # added.erase(node)
        SubRule(r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!\k<variable>!~)(.|\n))*?)\k<variable>\.Remove\((?P<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.erase(\g<argument>)", max_repeat=10),
        # if (added.insert(node)) {
        # if (!added.contains(node)) { added.insert(node);
        SubRule(r"if \((?P<variable>[a-zA-Z0-9]+)\.insert\((?P<argument>[a-zA-Z0-9]+)\)\)(?P<separator>[\t ]*[\r\n]+)(?P<indent>[\t ]*){", r"if (!\g<variable>.contains(\g<argument>))\g<separator>\g<indent>{\n" + "\g<indent>    \g<variable>.insert(\g<argument>);", max_repeat=0),
        # Remove scope borders.
        # ~!added!~
        # 
        SubRule(r"~![a-zA-Z0-9]+!~", r"", max_repeat=5),
        # Insert scope borders.
        # auto random = new System::Random(0);
        # std::srand(0);
        SubRule(r"[a-zA-Z0-9\.]+ ([a-zA-Z0-9]+) = new (System::)?Random\(([a-zA-Z0-9]+)\);", r"~!\1!~std::srand(\3);", max_repeat=0),
        # Inside the scope of ~!random!~ replace:
        # random.Next(1, N)
        # (std::rand() % N) + 1
        SubRule(r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!\k<variable>!~)(.|\n))*?)\k<variable>\.Next\((?P<from>[a-zA-Z0-9]+), (?P<to>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>(std::rand() % \g<to>) + \g<from>", max_repeat=10),
        # Remove scope borders.
        # ~!random!~
        # 
        SubRule(r"~![a-zA-Z0-9]+!~", r"", max_repeat=5),
        # Insert method body scope starts.
        # void PrintNodes(TElement node, StringBuilder sb, int level) {
        # void PrintNodes(TElement node, StringBuilder sb, int level) {/*method-start*/
        SubRule(r"(?P<start>\r?\n[\t ]+)(?P<prefix>((private|protected|public): )?(virtual )?[a-zA-Z0-9:_]+ )?(?P<method>[a-zA-Z][a-zA-Z0-9]*)\((?P<arguments>[^\)]*)\)(?P<override>( override)?)(?P<separator>[ \t\r\n]*)\{(?P<end>[^~])", r"\g<start>\g<prefix>\g<method>(\g<arguments>)\g<override>\g<separator>{/*method-start*/\g<end>", max_repeat=0),
        # Insert method body scope ends.
        # {/*method-start*/...}
        # {/*method-start*/.../*method-end*/}
        SubRule(r"\{/\*method-start\*/(?P<body>((?P<bracket>\{)|(?(bracket)\})|[^\{\}]*)+)\}", r"{/*method-start*/\g<body>/*method-end*/}", max_repeat=0),
        # Inside method bodies replace:
        # GetFirst(
        # this->GetFirst(
        SubRule(r"(?P<scope>/\*method-start\*/)(?P<before>((?<!/\*method-end\*/)(.|\n))*?)(?P<separator>[\W](?<!(::|\.|->|throw\s+)))(?P<method>(?!sizeof)[a-zA-Z0-9]+)\((?!\) \{)(?P<after>(.|\n)*?)(?P<scopeEnd>/\*method-end\*/)", r"\g<scope>\g<before>\g<separator>this->\g<method>(\g<after>\g<scopeEnd>", max_repeat=100),
        # Remove scope borders.
        # /*method-start*/
        # 
        SubRule(r"/\*method-(start|end)\*/", r"", max_repeat=0),
        # Insert scope borders.
        # const std::exception& ex
        # const std::exception& ex/*~ex~*/
        SubRule(r"(?P<before>\(| )(?P<variableDefinition>(const )?(std::)?exception&? (?P<variable>[_a-zA-Z0-9]+))(?P<after>\W)", r"\g<before>\g<variableDefinition>/*~\g<variable>~*/\g<after>", max_repeat=0),
        # Inside the scope of ~!ex!~ replace:
        # ex.Message
        # ex.what()
        SubRule(r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)(Platform::Converters::To<std::string>\(\k<variable>\.Message\)|\k<variable>\.Message)", r"\g<scope>\g<separator>\g<before>\g<variable>.what()", max_repeat=10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        SubRule(r"/\*~[_a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # throw ObjectDisposedException(objectName, message);
        # throw std::runtime_error(std::string("Attempt to access disposed object [").append(objectName).append("]: ").append(message).append("."));
        SubRule(r"throw ObjectDisposedException\((?P<objectName>[a-zA-Z_][a-zA-Z0-9_]*), (?P<message>[a-zA-Z0-9_]*[Mm]essage[a-zA-Z0-9_]*(\(\))?|[a-zA-Z_][a-zA-Z0-9_]*)\);", r"throw std::runtime_error(std::string(\"Attempt to access disposed object [\").append(\g<objectName>).append(\"]: \").append(\g<message>).append(\".\"));", max_repeat=0),
        # throw ArgumentNullException(argumentName, message);
        # throw std::invalid_argument(std::string("Argument ").append(argumentName).append(" is null: ").append(message).append("."));
        SubRule(r"throw ArgumentNullException\((?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*), (?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*(\(\))?)\);", r"throw std::invalid_argument(std::string(\"Argument \").append(\g<argument>).append(\" is null: \").append(\g<message>).append(\".\"));", max_repeat=0),
        # throw ArgumentException(message, argumentName);
        # throw std::invalid_argument(std::string("Invalid ").append(argumentName).append(" argument: ").append(message).append("."));
        SubRule(r"throw ArgumentException\((?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*(\(\))?), (?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*)\);", r"throw std::invalid_argument(std::string(\"Invalid \").append(\g<argument>).append(\" argument: \").append(\g<message>).append(\".\"));", max_repeat=0),
        # throw ArgumentOutOfRangeException(argumentName, argumentValue, messageBuilder());
        # throw std::invalid_argument(std::string("Value [").append(Platform::Converters::To<std::string>(argumentValue)).append("] of argument [").append(argumentName).append("] is out of range: ").append(messageBuilder()).append("."));
        SubRule(r"throw ArgumentOutOfRangeException\((?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*([Nn]ame[a-zA-Z]*)?), (?P<argumentValue>[a-zA-Z]*[Aa]rgument[a-zA-Z]*([Vv]alue[a-zA-Z]*)?), (?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*(\(\))?)\);", r"throw std::invalid_argument(std::string(\"Value [\").append(Platform::Converters::To<std::string>(\g<argumentValue>)).append(\"] of argument [\").append(\g<argument>).append(\"] is out of range: \").append(\g<message>).append(\".\"));", max_repeat=0),
        # throw NotSupportedException();
        # throw std::logic_error("Not supported exception.");
        SubRule(r"throw NotSupportedException\(\);", r"throw std::logic_error(\"Not supported exception.\");", max_repeat=0),
        # throw NotImplementedException();
        # throw std::logic_error("Not implemented exception.");
        SubRule(r"throw NotImplementedException\(\);", r"throw std::logic_error(\"Not implemented exception.\");", max_repeat=0),
        # Insert scope borders.
        # const std::string& message
        # const std::string& message/*~message~*/
        SubRule(r"(?P<before>\(| )(?P<variableDefinition>(const )?((std::)?string&?|char\*) (?P<variable>[_a-zA-Z0-9]+))(?P<after>\W)", r"\g<before>\g<variableDefinition>/*~\g<variable>~*/\g<after>", max_repeat=0),
        # Inside the scope of /*~message~*/ replace:
        # Platform::Converters::To<std::string>(message)
        # message
        SubRule(r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)Platform::Converters::To<std::string>\(\k<variable>\)", r"\g<scope>\g<separator>\g<before>\g<variable>", max_repeat=10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        SubRule(r"/\*~[_a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # std::tuple<T, T> tuple
        # std::tuple<T, T> tuple/*~tuple~*/
        SubRule(r"(?P<before>\(| )(?P<variableDefinition>(const )?(std::)?tuple<[^\n]+>&? (?P<variable>[_a-zA-Z0-9]+))(?P<after>\W)", r"\g<before>\g<variableDefinition>/*~\g<variable>~*/\g<after>", max_repeat=0),
        # Inside the scope of ~!ex!~ replace:
        # tuple.Item1
        # std::get<1-1>(tuple)
        SubRule(r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.Item(?P<itemNumber>\d+)(?P<after>\W)", r"\g<scope>\g<separator>\g<before>std::get<\g<itemNumber>-1>(\g<variable>)\g<after>", max_repeat=10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        SubRule(r"/\*~[_a-zA-Z0-9]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # class Range<T> {
        # class Range<T> {/*~type~Range<T>~*/
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)(template\s*<[^<>\n]*> )?(struct|class) (?P<fullType>(?P<typeName>[a-zA-Z0-9]+)(<[^:\n]*>)?)(\s*:\s*[^{\n]+)?[\t ]*(\r?\n)?[\t ]*{)", r"\g<classDeclarationBegin>/*~type~\g<typeName>~\g<fullType>~*/", max_repeat=0),
        # Inside the scope of /*~type~Range<T>~*/ insert inner scope and replace:
        # public: static implicit operator std::tuple<T, T>(Range<T> range)
        # public: operator std::tuple<T, T>() const {/*~variable~Range<T>~*/
        SubRule(r"(?P<scope>/\*~type~(?P<typeName>[^~\n\*]+)~(?P<fullType>[^~\n\*]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~type~\k<typeName>~\k<fullType>~\*/)(.|\n))*?)(?P<access>(private|protected|public): )static implicit operator (?P<targetType>[^\(\n]+)\((?P<argumentDeclaration>\k<fullType> (?P<variable>[a-zA-Z0-9]+))\)(?P<after>\s*\n?\s*{)", r"\g<scope>\g<separator>\g<before>\g<access>operator \g<targetType>() const\g<after>/*~variable~\g<variable>~*/", max_repeat=10),
        # Inside the scope of /*~type~Range<T>~*/ replace:
        # public: static implicit operator Range<T>(std::tuple<T, T> tuple) { return new Range<T>(std::get<1-1>(tuple), std::get<2-1>(tuple)); }
        # public: Range(std::tuple<T, T> tuple) : Range(std::get<1-1>(tuple), std::get<2-1>(tuple)) { }
        SubRule(r"(?P<scope>/\*~type~(?P<typeName>[^~\n\*]+)~(?P<fullType>[^~\n\*]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~type~\k<typeName>~\k<fullType>~\*/)(.|\n))*?)(?P<access>(private|protected|public): )static implicit operator (\k<fullType>|\k<typeName>)\((?P<arguments>[^{}\n]+)\)(\s|\n)*{(\s|\n)*return (new )?(\k<fullType>|\k<typeName>)\((?P<passedArguments>[^\n]+)\);(\s|\n)*}", r"\g<scope>\g<separator>\g<before>\g<access>\g<typeName>(\g<arguments>) : \g<typeName>(\g<passedArguments>) { }", max_repeat=10),
        # Inside the scope of /*~variable~range~*/ replace:
        # range.Minimum
        # this->Minimum
        SubRule(r"(?P<scope>{/\*~variable~(?P<variable>[^~\n]+)~\*/)(?P<separator>.|\n)(?P<before>(?P<beforeExpression>(?P<bracket>{)|(?(bracket)})|[^{}]|\n)*?)\k<variable>\.(?P<field>[_a-zA-Z0-9]+)(?P<after>(,|;|}| |\))(?P<afterExpression>(?P<bracket>{)|(?(bracket)})|[^{}]|\n)*?})", r"\g<scope>\g<separator>\g<before>this->\g<field>\g<after>", max_repeat=10),
        # Remove scope borders.
        # /*~ex~*/
        # 
        SubRule(r"/\*~[^~\n]+~[^~\n]+~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # namespace Platform::Ranges { ... }
        # namespace Platform::Ranges {/*~start~namespace~Platform::Ranges~*/ ... /*~end~namespace~Platform::Ranges~*/} 
        SubRule(r"(?P<namespaceDeclarationBegin>\r?\n(?P<indent>[\t ]*)namespace (?P<namespaceName>(?P<namePart>[a-zA-Z][a-zA-Z0-9]+)(?P<nextNamePart>::[a-zA-Z][a-zA-Z0-9]+)+)(\s|\n)*{)(?P<middle>(.|\n)*)(?P<end>(?<=\r?\n)\k<indent>}(?!;))", r"\g<namespaceDeclarationBegin>/*~start~namespace~\g<namespaceName>~*/\g<middle>/*~end~namespace~\g<namespaceName>~*/\g<end>", max_repeat=0),
        # Insert scope borders.
        # class Range<T> { ... };
        # class Range<T> {/*~start~type~Range<T>~T~*/ ... /*~end~type~Range<T>~T~*/};
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)template <typename (?P<typeParameter>[^\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<\k<typeParameter>>)(\s*:\s*[^{\n]+)?[\t ]*(\r?\n)?[\t ]*{)(?P<middle>(.|\n)*)(?P<endIndent>(?<=\r?\n)\k<indent>)(?P<end>};)", r"\g<classDeclarationBegin>/*~start~type~\g<type>~\g<typeParameter>~*/\g<middle>\g<endIndent>/*~end~type~\g<type>~\g<typeParameter>~*/\g<end>", max_repeat=0),
        # Inside the scope replace:
        # /*~start~namespace~Platform::Ranges~*/ ... /*~start~type~Range<T>~T~*/ ... public: override std::int32_t GetHashCode() { return {Minimum, Maximum}.GetHashCode(); } ... /*~end~type~Range<T>~T~*/ ... /*~end~namespace~Platform::Ranges~*/
        # /*~start~namespace~Platform::Ranges~*/ ... /*~start~type~Range<T>~T~*/ ... /*~end~type~Range<T>~T~*/ ... /*~end~namespace~Platform::Ranges~*/ namespace std { template <typename T> struct hash<Platform::Ranges::Range<T>> { std::size_t operator()(const Platform::Ranges::Range<T> &obj) const { return {Minimum, Maximum}.GetHashCode(); } }; }
        SubRule(r"(?P<namespaceScopeStart>/\*~start~namespace~(?P<namespace>[^~\n\*]+)~\*/)(?P<betweenStartScopes>(.|\n)+)(?P<typeScopeStart>/\*~start~type~(?P<type>[^~\n\*]+)~(?P<typeParameter>[^~\n\*]+)~\*/)(?P<before>(.|\n)+?)(?P<hashMethodDeclaration>\r?\n[ \t]*(?P<access>(private|protected|public): )override std::int32_t GetHashCode\(\)(\s|\n)*{\s*(?P<methodBody>[^\s][^\n]+[^\s])\s*}\s*)(?P<after>(.|\n)+?)(?P<typeScopeEnd>/\*~end~type~\k<type>~\k<typeParameter>~\*/)(?P<betweenEndScopes>(.|\n)+)(?P<namespaceScopeEnd>/\*~end~namespace~\k<namespace>~\*/)}\r?\n", r"\g<namespaceScopeStart>\g<betweenStartScopes>\g<typeScopeStart>\g<before>\g<after>\g<typeScopeEnd>\g<betweenEndScopes>\g<namespaceScopeEnd>}\n" + "\nnamespace std\n" + "{\n" + "    template <typename \g<typeParameter>>\n" + "    struct hash<\g<namespace>::\g<type>>\n" + "    {\n" + "        std::size_t operator()(const \g<namespace>::\g<type> &obj) const\n" + "        {\n" + "            /*~start~method~*/\g<methodBody>/*~end~method~*/\n" + "        }\n" + "    };\n" + "}\n", max_repeat=10),
        # Inside scope of /*~start~method~*/ replace:
        # /*~start~method~*/ ... Minimum ... /*~end~method~*/
        # /*~start~method~*/ ... obj.Minimum ... /*~end~method~*/
        SubRule(r"(?P<methodScopeStart>/\*~start~method~\*/)(?P<before>.+({|, ))(?P<name>[a-zA-Z][a-zA-Z0-9]+)(?P<after>[^\n\.\(a-zA-Z0-9]((?!/\*~end~method~\*/)[^\n])+)(?P<methodScopeEnd>/\*~end~method~\*/)", r"\g<methodScopeStart>\g<before>obj.\g<name>\g<after>\g<methodScopeEnd>", max_repeat=10),
        # Remove scope borders.
        # /*~start~type~Range<T>~*/
        # 
        SubRule(r"/\*~[^~\*\n]+(~[^~\*\n]+)*~\*/", r"", max_repeat=0),
        # class Disposable<T> : public Disposable
        # class Disposable<T> : public Disposable<>
        SubRule(r"(?P<before>(struct|class) (?P<type>[a-zA-Z][a-zA-Z0-9]*)<[^<>\n]+> : (?P<access>(private|protected|public) )?\k<type>)(?P<after>\b(?!<))", r"\g<before><>\g<after>", max_repeat=0),
        # Insert scope borders.
        # class Disposable<T> : public Disposable<> { ... };
        # class Disposable<T> : public Disposable<> {/*~start~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/ ... /*~end~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/};
        SubRule(r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)template[\t ]*<(?P<typeParameters>[^\n]*)>[\t ]*(struct|class)[\t ]+(?P<fullType>(?P<type>[a-zA-Z][a-zA-Z0-9]*)(<[^<>\n]*>)?)[\t ]*:[\t ]*(?P<access>(private|protected|public)[\t ]+)?(?P<fullBaseType>(?P<baseType>[a-zA-Z][a-zA-Z0-9]*)(<[^<>\n]*>)?)[\t ]*(\r?\n)?[\t ]*{)(?P<middle>(.|\n)*)(?P<beforeEnd>(?<=\r?\n)\k<indent>)(?P<end>};)", r"\g<classDeclarationBegin>/*~start~type~\g<type>~\g<fullType>~\g<baseType>~\g<fullBaseType>~*/\g<middle>\g<beforeEnd>/*~end~type~\g<type>~\g<fullType>~\g<baseType>~\g<fullBaseType>~*/\g<end>", max_repeat=0),
        # Inside the scope replace:
        # /*~start~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/ ... ) : base( ... /*~end~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/
        # /*~start~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/ ... ) : Disposable<>( /*~end~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/
        SubRule(r"(?P<before>(?P<typeScopeStart>/\*~start~type~(?P<types>(?P<type>[^~\n\*]+)~(?P<fullType>[^~\n\*]+)~\k<type>~(?P<fullBaseType>[^~\n\*]+))~\*/)(.|\n)+?\)\s*:\s)base(?P<after>\((.|\n)+?(?P<typeScopeEnd>/\*~end~type~\k<types>~\*/))", r"\g<before>\g<fullBaseType>\g<after>", max_repeat=20),
        # Inside the scope replace:
        # /*~start~type~Disposable~Disposable<T>~X~X<>~*/ ... ) : base( ... /*~end~type~Disposable~Disposable<T>~X~X<>~*/
        # /*~start~type~Disposable~Disposable<T>~X~X<>~*/ ... ) : X( /*~end~type~Disposable~Disposable<T>~X~X<>~*/
        SubRule(r"(?P<before>(?P<typeScopeStart>/\*~start~type~(?P<types>(?P<type>[^~\n\*]+)~(?P<fullType>[^~\n\*]+)~(?P<baseType>[^~\n\*]+)~(?P<fullBaseType>[^~\n\*]+))~\*/)(.|\n)+?\)\s*:\s)base(?P<after>\((.|\n)+?(?P<typeScopeEnd>/\*~end~type~\k<types>~\*/))", r"\g<before>\g<baseType>\g<after>", max_repeat=20),
        # Inside the scope replace:
        # /*~start~type~Disposable~Disposable<T>~X~X<>~*/ ... public: Disposable(T object) { Object = object; } ... public: Disposable(T object) : Disposable(object) { } ... /*~end~type~Disposable~Disposable<T>~X~X<>~*/
        # /*~start~type~Disposable~Disposable<T>~X~X<>~*/ ... public: Disposable(T object) { Object = object; } /*~end~type~Disposable~Disposable<T>~X~X<>~*/
        SubRule(r"(?P<before>(?P<typeScopeStart>/\*~start~type~(?P<types>(?P<type>[^~\n\*]+)~(?P<fullType>[^~\n\*]+)~(?P<baseType>[^~\n\*]+)~(?P<fullBaseType>[^~\n\*]+))~\*/)(.|\n)+?(?P<constructor>(?P<access>(private|protected|public):[\t ]*)?\k<type>\((?P<arguments>[^()\n]+)\)\s*{[^{}\n]+})(.|\n)+?)(?P<duplicateConstructor>(?P<access>(private|protected|public):[\t ]*)?\k<type>\(\k<arguments>\)\s*:[^{}\n]+\s*{[^{}\n]+})(?P<after>(.|\n)+?(?P<typeScopeEnd>/\*~end~type~\k<types>~\*/))", r"\g<before>\g<after>", max_repeat=20),
        # Remove scope borders.
        # /*~start~type~Disposable~Disposable<T>~Disposable~Disposable<>~*/
        # 
        SubRule(r"/\*~[^~\*\n]+(~[^~\*\n]+)*~\*/", r"", max_repeat=0),
        # Insert scope borders.
        # private: inline static const AppDomain _currentDomain = AppDomain.CurrentDomain;
        # private: inline static const AppDomain _currentDomain = AppDomain.CurrentDomain;/*~app-domain~_currentDomain~*/
        SubRule(r"(?P<declaration>(?P<access>(private|protected|public):[\t ]*)?(inline[\t ]+)?(static[\t ]+)?(const[\t ]+)?AppDomain[\t ]+(?P<field>[a-zA-Z_][a-zA-Z0-9_]*)[\t ]*=[\t ]*AppDomain\.CurrentDomain;)", r"\g<declaration>/*~app-domain~\g<field>~*/", max_repeat=0),
        # Inside the scope replace:
        # /*~app-domain~_currentDomain~*/ ... _currentDomain.ProcessExit += OnProcessExit;
        # /*~app-domain~_currentDomain~*/ ... std::atexit(OnProcessExit);
        SubRule(r"(?P<before>(?P<fieldScopeStart>/\*~app-domain~(?P<field>[^~\n\*]+)~\*/)(.|\n)+?)\k<field>\.ProcessExit[\t ]*\+=[\t ]*(?P<eventHandler>[a-zA-Z_][a-zA-Z0-9_]*);", r"\g<before>std::atexit(\g<eventHandler>);/*~process-exit-handler~\g<eventHandler>~*/", max_repeat=20),
        # Inside the scope replace:
        # /*~app-domain~_currentDomain~*/ ... _currentDomain.ProcessExit -= OnProcessExit;
        # /*~app-domain~_currentDomain~*/ ... /* No translation. It is not possible to unsubscribe from std::atexit. */
        SubRule(r"(?P<before>(?P<fieldScopeStart>/\*~app-domain~(?P<field>[^~\n\*]+)~\*/)(.|\n)+?\r?\n[\t ]*)\k<field>\.ProcessExit[\t ]*\-=[\t ]*(?P<eventHandler>[a-zA-Z_][a-zA-Z0-9_]*);", r"\g<before>/* No translation. It is not possible to unsubscribe from std::atexit. */", max_repeat=20),
        # Inside the scope replace:
        # /*~process-exit-handler~OnProcessExit~*/ ... static void OnProcessExit(void *sender, EventArgs e)
        # /*~process-exit-handler~OnProcessExit~*/ ... static void OnProcessExit()
        SubRule(r"(?P<before>(?P<fieldScopeStart>/\*~process-exit-handler~(?P<handler>[^~\n\*]+)~\*/)(.|\n)+?static[\t ]+void[\t ]+\k<handler>\()[^()\n]+\)", r"\g<before>)", max_repeat=20),
        # Remove scope borders.
        # /*~app-domain~_currentDomain~*/
        # 
        SubRule(r"/\*~[^~\*\n]+(~[^~\*\n]+)*~\*/", r"", max_repeat=0),
        # AppDomain.CurrentDomain.ProcessExit -= OnProcessExit;
        # /* No translation. It is not possible to unsubscribe from std::atexit. */
        SubRule(r"AppDomain\.CurrentDomain\.ProcessExit -= ([a-zA-Z_][a-zA-Z0-9_]*);", r"/* No translation. It is not possible to unsubscribe from std::atexit. */", max_repeat=0),
    ]


    LAST_RULES = [
        # IDisposable disposable)
        # IDisposable &disposable)
        SubRule(r"(?P<argumentAbstractType>I[A-Z][a-zA-Z0-9]+(<[^>\r\n]+>)?) (?P<argument>[_a-zA-Z0-9]+)(?P<after>,|\))", r"\g<argumentAbstractType> &\g<argument>\g<after>", max_repeat=0),
        # ICounter<int, int> c1;
        # ICounter<int, int>* c1;
        SubRule(r"(?P<abstractType>I[A-Z][a-zA-Z0-9]+(<[^>\r\n]+>)?) (?P<variable>[_a-zA-Z0-9]+)(?P<after> = null)?;", r"\g<abstractType> *\g<variable>\g<after>;", max_repeat=0),
        # (expression)
        # expression
        SubRule(r"(\(| )\(([a-zA-Z0-9_\*:]+)\)(,| |;|\))", r"\1\2\3", max_repeat=0),
        # (method(expression))
        # method(expression)
        SubRule(r"(?P<firstSeparator>(\(| ))\((?P<method>[a-zA-Z0-9_\->\*:]+)\((?P<expression>((?P<parenthesis>\()|(?(parenthesis)\))|[a-zA-Z0-9_\->\*:]*)+)(?(parenthesis)(?!))\)\)(?P<lastSeparator>(,| |;|\)))", r"\g<firstSeparator>\g<method>(\g<expression>)\g<lastSeparator>", max_repeat=0),
        # .append(".")
        # .append(1, '.');
        SubRule(r"\.append\(""([^\\""]|\\[^""])""\)", r".append(1, '\1')", max_repeat=0),
        # return ref _elements[node];
        # return &_elements[node];
        SubRule(r"return ref ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9\*]+)\];", r"return &\1[\2];", max_repeat=0),
        # ((1, 2))
        # ({1, 2})
        SubRule(r"(?P<before>\(|, )\((?P<first>[^\n()]+), (?P<second>[^\n()]+)\)(?P<after>\)|, )", r"\g<before>{\g<first>, \g<second>}\g<after>", max_repeat=10),
        # {1, 2}.GetHashCode()
        # Platform::Hashing::Hash(1, 2)
        SubRule(r"{(?P<first>[^\n{}]+), (?P<second>[^\n{}]+)}\.GetHashCode\(\)", r"Platform::Hashing::Hash(\g<first>, \g<second>)", max_repeat=10),
        # range.ToString()
        # Platform::Converters::To<std::string>(range).data()
        SubRule(r"(?P<before>\W)(?P<variable>[_a-zA-Z][_a-zA-Z0-9]+)\.ToString\(\)", r"\g<before>Platform::Converters::To<std::string>(\g<variable>).data()", max_repeat=10),
        # new
        # 
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)new\s+", r"\g<before>", max_repeat=10),
        # x == null
        # x == nullptr
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)(?P<variable>[_a-zA-Z][_a-zA-Z0-9]+)(?P<operator>\s*(==|!=)\s*)null(?P<after>\W)", r"\g<before>\g<variable>\g<operator>nullptr\g<after>", max_repeat=10),
        # null
        # {}
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)null(?P<after>\W)", r"\g<before>{}\g<after>", max_repeat=10),
        # default
        # 0
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)default(?P<after>\W)", r"\g<before>0\g<after>", max_repeat=10),
        # object x
        # void *x
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)(?<!@)(object|System\.Object) (?P<after>\w)", r"\g<before>void *\g<after>", max_repeat=10),
        # <object>
        # <void*>
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)(?<!@)(object|System\.Object)(?P<after>\W)", r"\g<before>void*\g<after>", max_repeat=10),
        # @object
        # object
        SubRule(r"@([_a-zA-Z0-9]+)", r"\1", max_repeat=0),
        # this->GetType().Name
        # typeid(this).name()
        SubRule(r"(this)->GetType\(\)\.Name", r"typeid(\1).name()", max_repeat=0),
        # ArgumentNullException
        # std::invalid_argument
        SubRule(r"(?P<before>\r?\n[^\"\"\r\n]*(\"\"(\\\"\"|[^\"\"\r\n])*\"\"[^\"\"\r\n]*)*)(?<=\W)(System\.)?ArgumentNullException(?P<after>\W)", r"\g<before>std::invalid_argument\g<after>", max_repeat=10),
        # InvalidOperationException
        # std::runtime_error
        SubRule(r"(\W)(InvalidOperationException|Exception)(\W)", r"\1std::runtime_error\3", max_repeat=0),
        # ArgumentException
        # std::invalid_argument
        SubRule(r"(\W)(ArgumentException|ArgumentOutOfRangeException)(\W)", r"\1std::invalid_argument\3", max_repeat=0),
        # template <typename T> struct Range : IEquatable<Range<T>>
        # template <typename T> struct Range {
        SubRule(r"(?P<before>template <typename (?P<typeParameter>[^\n]+)> (struct|class) (?P<type>[a-zA-Z0-9]+<[^\n]+>)) : (public )?IEquatable<\k<type>>(?P<after>(\s|\n)*{)", r"\g<before>\g<after>", max_repeat=0),
        # public: delegate void Disposal(bool manual, bool wasDisposed);
        # public: delegate void Disposal(bool, bool);
        SubRule(r"(?P<before>(?P<access>(private|protected|public): )delegate (?P<returnType>[a-zA-Z][a-zA-Z0-9:]+) (?P<delegate>[a-zA-Z][a-zA-Z0-9]+)\(((?P<leftArgumentType>[a-zA-Z][a-zA-Z0-9:]+), )*)(?P<argumentType>[a-zA-Z][a-zA-Z0-9:]+) (?P<argumentName>[a-zA-Z][a-zA-Z0-9]+)(?P<after>(, (?P<rightArgumentType>[a-zA-Z][a-zA-Z0-9:]+) (?P<rightArgumentName>[a-zA-Z][a-zA-Z0-9]+))*\);)", r"\g<before>\g<argumentType>\g<after>", max_repeat=20),
        # public: delegate void Disposal(bool, bool);
        # using Disposal = void(bool, bool);
        SubRule(r"(?P<access>(private|protected|public): )delegate (?P<returnType>[a-zA-Z][a-zA-Z0-9:]+) (?P<delegate>[a-zA-Z][a-zA-Z0-9]+)\((?P<argumentTypes>[^\(\)\n]*)\);", r"using \g<delegate> = \g<returnType>(\g<argumentTypes>);", max_repeat=20),
        # <4-1>
        # <3>
        SubRule(r"(?P<before><)4-1(?P<after>>)", r"\g<before>3\g<after>", max_repeat=0),
        # <3-1>
        # <2>
        SubRule(r"(?P<before><)3-1(?P<after>>)", r"\g<before>2\g<after>", max_repeat=0),
        # <2-1>
        # <1>
        SubRule(r"(?P<before><)2-1(?P<after>>)", r"\g<before>1\g<after>", max_repeat=0),
        # <1-1>
        # <0>
        SubRule(r"(?P<before><)1-1(?P<after>>)", r"\g<before>0\g<after>", max_repeat=0),
        # #region Always
        # 
        SubRule(r"(^|\r?\n)[ \t]*\#(region|endregion)[^\r\n]*(\r?\n|$)", r"", max_repeat=0),
        # //#define ENABLE_TREE_AUTO_DEBUG_AND_VALIDATION
        # 
        SubRule(r"\/\/[ \t]*\#define[ \t]+[_a-zA-Z0-9]+[ \t]*", r"", max_repeat=0),
        # #if USEARRAYPOOL\r\n#endif
        # 
        SubRule(r"#if [a-zA-Z0-9]+\s+#endif", r"", max_repeat=0),
        # [Fact]
        # 
        SubRule(r"(?P<firstNewLine>\r?\n|\A)(?P<indent>[\t ]+)\[[a-zA-Z0-9]+(\((?P<expression>((?P<parenthesis>\()|(?(parenthesis)\))|[^()\r\n]*)+)(?(parenthesis)(?!))\))?\][ \t]*(\r?\n\k<indent>)?", r"\g<firstNewLine>\g<indent>", max_repeat=5),
        # \A \n ... namespace
        # \Anamespace
        SubRule(r"(\A)(\r?\n)+namespace", r"\1namespace", max_repeat=0),
        # \A \n ... class
        # \Aclass
        SubRule(r"(\A)(\r?\n)+class", r"\1class", max_repeat=0),
        # \n\n\n
        # \n\n
        SubRule(r"\r?\n[ \t]*\r?\n[ \t]*\r?\n", r"\n\n", max_repeat=50),
        # {\n\n
        # {\n
        SubRule(r"{[ \t]*\r?\n[ \t]*\r?\n", r"{\n", max_repeat=10),
        # \n\n}
        # \n}
        SubRule(r"\r?\n[ \t]*\r?\n(?P<end>[ \t]*})", "\n\g<end>", max_repeat=10),
    ]
