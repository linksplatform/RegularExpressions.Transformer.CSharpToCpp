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
        # out TProduct
        # TProduct
        (r"(?P<before>(<|, ))(in|out) (?P<typeParameter>[a-zA-Z0-9]+)(?P<after>(>|,))", r"\g<before>\g<typeParameter>\g<after>", None, 10),
        # public ...
        # public: ...
        (r"(?P<newLineAndIndent>\r?\n?[ \t]*)(?P<before>[^\{\(\r\n]*)(?P<access>private|protected|public)[ \t]+(?![^\{\(\r\n]*(interface|class|struct)[^\{\(\r\n]*[\{\(\r\n])", r"\g<newLineAndIndent>\g<access>: \g<before>", None, 0),
        # public: static bool CollectExceptions { get; set; }
        # public: inline static bool CollectExceptions;
        (r"(?P<access>(private|protected|public): )(?P<before>(static )?[^\r\n]+ )(?P<name>[a-zA-Z0-9]+) {[^;}]*(?<=\W)get;[^;}]*(?<=\W)set;[^;}]*}", r"\g<access>inline \g<before>\g<name>;", None, 0),
        # public abstract class
        # class
        (r"((public|protected|private|internal|abstract|static) )*(?P<category>interface|class|struct)", r"\g<category>", None, 0),
        # class GenericCollectionMethodsBase<TElement> {
        # template <typename TElement> class GenericCollectionMethodsBase {
        (r"class ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>([^{]+){", r"template <typename \2> class \1\3{", None, 0),
        # static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        # template<typename T> static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        (r"static ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>\(([^\)\r\n]+)\)", r"template <typename \3> static \1 \2(\4)", None, 0),
        # interface IFactory<out TProduct> {
        # template <typename TProduct> class IFactory { public:
        (r"interface (?P<interface>[a-zA-Z0-9]+)<(?P<typeParameters>[a-zA-Z0-9 ,]+)>(?P<whitespace>[^{]+){", r"template <typename...> class \g<interface>; template <typename \g<typeParameters>> class \g<interface><\g<typeParameters>>\g<whitespace>{\n    public:", None, 0),
        # template <typename TObject, TProperty, TValue>
        # template <typename TObject, typename TProperty, TValue>
        (r"(?P<before>template <((, )?typename [a-zA-Z0-9]+)+, )(?P<typeParameter>[a-zA-Z0-9]+)(?P<after>(,|>))", r"\g<before>typename \g<typeParameter>\g<after>", None, 10),
        # Insert markers
        # private: static void BuildExceptionString(this StringBuilder sb, Exception exception, int level)
        # /*~extensionMethod~BuildExceptionString~*/private: static void BuildExceptionString(this StringBuilder sb, Exception exception, int level)
        (r"private: static [^\r\n]+ (?P<name>[a-zA-Z0-9]+)\(this [^\)\r\n]+\)", r"/*~extensionMethod~\g<name>~*/$0", None, 0),
        # Move all markers to the beginning of the file.
        (r"\A(?P<before>[^\r\n]+\r?\n(.|\n)+)(?P<marker>/\*~extensionMethod~(?P<name>[a-zA-Z0-9]+)~\*/)", r"\g<marker>\g<before>", None, 10),
        # /*~extensionMethod~BuildExceptionString~*/...sb.BuildExceptionString(exception.InnerException, level + 1);
        # /*~extensionMethod~BuildExceptionString~*/...BuildExceptionString(sb, exception.InnerException, level + 1);
        (r"(?P<before>/\*~extensionMethod~(?P<name>[a-zA-Z0-9]+)~\*/(.|\n)+\W)(?P<variable>[_a-zA-Z0-9]+)\.\k<name>\(", r"\g<before>\g<name>(\g<variable>, ", None, 50),
        # Remove markers
        # /*~extensionMethod~BuildExceptionString~*/
        #
        (r"/\*~extensionMethod~[a-zA-Z0-9]+~\*/", r"", None, 0),
        # (this
        # (
        (r"\(this ", r"(", None, 0),
        # public: static readonly EnsureAlwaysExtensionRoot Always = new EnsureAlwaysExtensionRoot();
        # public:inline static EnsureAlwaysExtensionRoot Always;
        (r"(?P<access>(private|protected|public): )?static readonly (?P<type>[a-zA-Z0-9]+) (?P<name>[a-zA-Z0-9_]+) = new \k<type>\(\);", r"\g<access>inline static \g<type> \g<name>;", None, 0),
        # public: static readonly string ExceptionContentsSeparator = "---";
        # public: inline static const char* ExceptionContentsSeparator = "---";
        (r"(?P<access>(private|protected|public): )?static readonly string (?P<name>[a-zA-Z0-9_]+) = ""(?P<string>(\"|[^\"\r\n])+)"";", r"\g<access>inline static const char* \g<name> = \"\g<string>\";", None, 0),
        # private: const int MaxPath = 92;
        # private: static const int MaxPath = 92;
        (r"(?P<access>(private|protected|public): )?(const|static readonly) (?P<type>[a-zA-Z0-9]+) (?P<name>[_a-zA-Z0-9]+) = (?P<value>[^;\r\n]+);", r"\g<access>static const \g<type> \g<name> = \g<value>;", None, 0),
        #  ArgumentNotNull(EnsureAlwaysExtensionRoot root, TArgument argument) where TArgument : class
        #  ArgumentNotNull(EnsureAlwaysExtensionRoot root, TArgument* argument)
        (r"(?P<before> [a-zA-Z]+\(([a-zA-Z *,]+, |))(?P<type>[a-zA-Z]+)(?P<after>(| [a-zA-Z *,]+)\))[ \r\n]+where \k<type> : class", r"\g<before>\g<type>*\g<after>", None, 0),
        # protected: abstract TElement GetFirst();
        # protected: virtual TElement GetFirst() = 0;
        (r"(?P<access>(private|protected|public): )?abstract (?P<method>[^;\r\n]+);", r"\g<access>virtual \g<method> = 0;", None, 0),
        # TElement GetFirst();
        # virtual TElement GetFirst() = 0;
        (r"([\r\n]+[ ]+)((?!return)[a-zA-Z0-9]+ [a-zA-Z0-9]+\([^\)\r\n]*\))(;[ ]*[\r\n]+)", r"\1virtual \2 = 0\3", None, 1),
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
        (r"\(\)\s+=>\s+(?P<expression>[^\(\),;\r\n]+(\(((?P<parenthesis>\()|(?P<parenthesis>\))|[^\(\);\r\n]*?)*?\))?[^\(\),;\r\n]*)(?P<after>,|\);)", r"() { return \g<expression>; }\g<after>", None, 0),
        # => Integer<TElement>.Zero;
        # { return Integer<TElement>.Zero; }
        (r"\)\s+=>\s+([^;\r\n]+?);", r") { return \1; }", None, 0),
        # () { return avlTree.Count; }
        # [&]()-> auto { return avlTree.Count; }
        (r"(?P<before>, |\()\(\) { return (?P<expression>[^;\r\n]+); }", r"\g<before>[&]()-> auto { return \g<expression>; }", None, 0),
        # Count => GetSizeOrZero(Root);
        # GetCount() { return GetSizeOrZero(Root); }
        (r"(\W)([A-Z][a-zA-Z]+)\s+=>\s+([^;\r\n]+);", r"\1Get\2() { return \3; }", None, 0),
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
        # throw new InvalidOperationException
        # throw std::runtime_error
        (r"throw new (InvalidOperationException|Exception)", r"throw std::runtime_error", None, 0),
        # void RaiseExceptionIgnoredEvent(Exception exception)
        # void RaiseExceptionIgnoredEvent(const std::exception& exception)
        (r"(\(|, )(System\.Exception|Exception)( |\))", r"\1const std::exception&\3", None, 0),
        # EventHandler<Exception>
        # EventHandler<std::exception>
        (r"(\W)(System\.Exception|Exception)(\W)", r"\1std::exception\3", None, 0),
        # override void PrintNode(TElement node, StringBuilder sb, int level)
        # void PrintNode(TElement node, StringBuilder sb, int level) override
        (r"override ([a-zA-Z0-9 \*\+]+)(\([^\)\r\n]+?\))", r"\1\2 override", None, 0),
        # string
        # const char*
        (r"(\W)string(\W)", r"\1const char*\2", None, 0),
        # sbyte
        # std::int8_t
        (r"(\W)sbyte(\W)", r"\1std::int8_t\2", None, 0),
        # uint
        # std::uint32_t
        (r"(\W)uint(\W)", r"\1std::uint32_t\2", None, 0),
        # char*[] args
        # char* args[]
        (r"([_a-zA-Z0-9:\*]?)\[\] ([a-zA-Z0-9]+)", r"\1 \2[]", None, 0),
        # @object
        # object
        (r"@([_a-zA-Z0-9]+)", r"\1", None, 0),
        # using Platform.Numbers;
        #
        (r"([\r\n]{2}|^)\s*?using [\.a-zA-Z0-9]+;\s*?$", r"", None, 0),
        # struct TreeElement { }
        # struct TreeElement { };
        (r"(struct|class) ([a-zA-Z0-9]+)(\s+){([\sa-zA-Z0-9;:_]+?)}([^;])", r"\1 \2\3{\4};\5", None, 0),
        # class Program { }
        # class Program { };
        (r"(struct|class) ([a-zA-Z0-9]+[^\r\n]*)([\r\n]+(?P<indentLevel>[\t ]*)?)\{([\S\s]+?[\r\n]+\k<indentLevel>)\}([^;]|$)", r"\1 \2\3{\4};\5", None, 0),
        # class SizedBinaryTreeMethodsBase : GenericCollectionMethodsBase
        # class SizedBinaryTreeMethodsBase : public GenericCollectionMethodsBase
        (r"class ([a-zA-Z0-9]+) : ([a-zA-Z0-9]+)", r"class \1 : public \2", None, 0),
        # class IProperty : ISetter<TValue, TObject>, IProvider<TValue, TObject>
        # class IProperty : public ISetter<TValue, TObject>, IProvider<TValue, TObject>
        (r"(?P<before>class [a-zA-Z0-9]+ : ((public [a-zA-Z0-9]+(<[a-zA-Z0-9 ,]+>)?, )+)?)(?P<inheritedType>(?!public)[a-zA-Z0-9]+(<[a-zA-Z0-9 ,]+>)?)(?P<after>(, [a-zA-Z0-9]+(?!>)|[ \r\n]+))", r"\g<before>public \g<inheritedType>\g<after>", None, 10),
        # Insert scope borders.
        # ref TElement root
        # ~!root!~ref TElement root
        (r"(?P<definition>(?<= |\()(ref [a-zA-Z0-9]+|[a-zA-Z0-9]+(?<!ref)) (?P<variable>[a-zA-Z0-9]+)(?=\)|, | =))", r"~!\g<variable>!~\g<definition>", None, 0),
        # Inside the scope of ~!root!~ replace:
        # root
        # *root
        (r"(?P<definition>~!(?P<pointer>[a-zA-Z0-9]+)!~ref [a-zA-Z0-9]+ \k<pointer>(?=\)|, | =))(?P<before>((?<!~!\k<pointer>!~)(.|\n))*?)(?P<prefix>(\W |\())\k<pointer>(?P<suffix>( |\)|;|,))", r"\g<definition>\g<before>\g<prefix>*\g<pointer>\g<suffix>", None, 70),
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
        (r"class ([a-zA-Z0-9]+)Tests", r"TEST_CLASS(\1)", None, 0),
        # Assert.Equal
        # Assert::AreEqual
        (r"(Assert)\.Equal", r"\1::AreEqual", None, 0),
        # Assert.Throws
        # Assert::ExpectException
        (r"(Assert)\.Throws", r"\1::ExpectException", None, 0),
        # $"Argument {argumentName} is null."
        # ((std::string)"Argument ").append(argumentName).append(" is null.").data()
        (r"\$""(?P<left>(\\\"|[^\"\r\n])*){(?P<expression>[_a-zA-Z0-9]+)}(?P<right>(\\\"|[^\"\r\n])*)\"", r"((std::string)$\"\g<left>\").append(\g<expression>).append(\"\g<right>\").data()", None, 10),
        # $"
        # "
        (r"\$""", r"\"", None, 0),
        # Console.WriteLine("...")
        # printf("...\n")
        (r"Console\.WriteLine\(\"([^\"\r\n]+)\"\)", r"printf(\"\1\\n\")", None, 0),
        # TElement Root;
        # TElement Root = 0;
        (r"(\r?\n[\t ]+)(private|protected|public)?(: )?([a-zA-Z0-9:_]+(?<!return)) ([_a-zA-Z0-9]+);", r"\1\2\3\4 \5 = 0;", None, 0),
        # TreeElement _elements[N];
        # TreeElement _elements[N] = { {0} };
        (r"(\r?\n[\t ]+)(private|protected|public)?(: )?([a-zA-Z0-9]+) ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\2\3\4 \5[\6] = { {0} };", None, 0),
        # auto path = new TElement[MaxPath];
        # TElement path[MaxPath] = { {0} };
        (r"(\r?\n[\t ]+)[a-zA-Z0-9]+ ([a-zA-Z0-9]+) = new ([a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\3 \2[\4] = { {0} };", None, 0),
        # private: static readonly ConcurrentBag<std::exception> _exceptionsBag = new ConcurrentBag<std::exception>();
        # private: inline static std::mutex _exceptionsBag_mutex; \n\n private: inline static std::vector<std::exception> _exceptionsBag;
        (r"(?P<begin>\r?\n?(?P<indent>[ \t]+))(?P<access>(private|protected|public): )?static readonly ConcurrentBag<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+) = new ConcurrentBag<\k<argumentType>>\(\);", r"\g<begin>private: inline static std::mutex \g<name>_mutex;\n\n\g<indent>\g<access>inline static std::vector<\g<argumentType>> \g<name>;", None, 0),
        # public: static IReadOnlyCollection<std::exception> GetCollectedExceptions() { return _exceptionsBag; }
        # public: static std::vector<std::exception> GetCollectedExceptions() { return std::vector<std::exception>(_exceptionsBag); }
        (r"(?P<access>(private|protected|public): )?static IReadOnlyCollection<(?P<argumentType>[^;\r\n]+)> (?P<methodName>[_a-zA-Z0-9]+)\(\) { return (?P<fieldName>[_a-zA-Z0-9]+); }", r"\g<access>static std::vector<\g<argumentType>> \g<methodName>() { return std::vector<\g<argumentType>>(\g<fieldName>); }", None, 0),
        # public: static event EventHandler<std::exception> ExceptionIgnored = OnExceptionIgnored; ... };
        # ... public: static inline Platform::Delegates::MulticastDelegate<void(void*, const std::exception&)> ExceptionIgnored = OnExceptionIgnored; };
        (r"(?P<begin>\r?\n(\r?\n)?(?P<halfIndent>[ \t]+)\k<halfIndent>)(?P<access>(private|protected|public): )?static event EventHandler<(?P<argumentType>[^;\r\n]+)> (?P<name>[_a-zA-Z0-9]+) = (?P<defaultDelegate>[_a-zA-Z0-9]+);(?P<middle>(.|\n)+?)(?P<end>\r?\n\k<halfIndent>};)", r"\g<middle>\n\n\g<halfIndent>\g<halfIndent>\g<access>static inline Platform::Delegates::MulticastDelegate<void(void*, const \g<argumentType>&)> \g<name> = \g<defaultDelegate>;\g<end>", None, 0),
        # Insert scope borders.
        # class IgnoredExceptions { ... private: inline static std::vector<std::exception> _exceptionsBag;
        # class IgnoredExceptions {/*~_exceptionsBag~*/ ... private: inline static std::vector<std::exception> _exceptionsBag;
        (r"(?P<classDeclarationBegin>\r?\n(?P<indent>[\t ]*)class [^{\r\n]+\r\n[\t ]*{)(?P<middle>((?!class).|\n)+?)(?P<vectorFieldDeclaration>(?P<access>(private|protected|public): )inline static std::vector<(?P<argumentType>[^;\r\n]+)> (?P<fieldName>[_a-zA-Z0-9]+);)", r"\g<classDeclarationBegin>/*~\g<fieldName>~*/\g<middle>\g<vectorFieldDeclaration>", None, 0),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # _exceptionsBag.Add(exception);
        # _exceptionsBag.push_back(exception);
        (r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<fieldName>~\*/)(.|\n))*?)\k<fieldName>\.Add", r"\g<scope>\g<separator>\g<before>\g<fieldName>.push_back", None, 10),
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
        (r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<fieldName>~\*/)(.|\n))*?){(?P<after>((?!lock_guard)[^{};\r\n])*\k<fieldName>[^;}\r\n]*;)", r"\g<scope>\g<separator>\g<before>{ std::lock_guard<std::mutex> guard(\g<fieldName>_mutex);\g<after>", None, 10),
        # Inside the scope of ~!_exceptionsBag!~ replace:
        # _exceptionsBag.Add(exception);
        # std::lock_guard<std::mutex> guard(_exceptionsBag_mutex); \r\n _exceptionsBag.Add(exception);
        (r"(?P<scope>/\*~(?P<fieldName>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<fieldName>~\*/)(.|\n))*?){(?P<after>((?!lock_guard)([^{};]|\n))*?\r?\n(?P<indent>[ \t]*)\k<fieldName>[^;}\r\n]*;)", r"\g<scope>\g<separator>\g<before>{\n\g<indent>std::lock_guard<std::mutex> guard(\g<fieldName>_mutex);\g<after>", None, 10),
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
        (r"(?P<scope>/\*~(?P<eventName>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<eventName>~\*/)(.|\n))*?)\k<eventName>\.Invoke", r"\g<scope>\g<separator>\g<before>\g<eventName>", None, 10),
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
        # sb.data()
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.ToString\(\)", r"\g<scope>\g<separator>\g<before>\g<variable>.data()", None, 10),
        # sb.AppendLine(argument)
        # sb.append(argument).append('\n')
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.AppendLine\((?P<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<argument>).append(1, '\\n')", None, 10),
        # sb.Append('\t', level);
        # sb.append(level, '\t');
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.Append\('(?P<character>[^'\r\n]+)', (?P<count>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<count>, '\g<character>')", None, 10),
        # sb.Append(argument)
        # sb.append(argument)
        (r"(?P<scope>/\*~(?P<variable>[a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.Append\((?P<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<argument>)", None, 10),
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
        (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!\k<variable>!~)(.|\n))*?)\k<variable>\.Add\((?P<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.insert(\g<argument>)", None, 10),
        # Inside the scope of ~!added!~ replace:
        # added.Remove(node)
        # added.erase(node)
        (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!\k<variable>!~)(.|\n))*?)\k<variable>\.Remove\((?P<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.erase(\g<argument>)", None, 10),
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
        (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!\k<variable>!~)(.|\n))*?)\k<variable>\.Next\((?P<from>[a-zA-Z0-9]+), (?P<to>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>(std::rand() % \g<to>) + \g<from>", None, 10),
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
        (r"\{/\*method-start\*/(?P<body>((?P<bracket>\{)|(?P<bracket>\})|[^\{\}]*)+)\}", r"{/*method-start*/\g<body>/*method-end*/}", None, 0),
        # Inside method bodies replace:
        # GetFirst(
        # this->GetFirst(
        # (r"(?P<separator>(\(|, |([\W]) |return ))(?<!(->|\* ))(?P<method>(?!sizeof)[a-zA-Z0-9]+)\((?!\) \{)", r"\g<separator>this->\g<method>(", None, 1),
        (r"(?P<scope>/\*method-start\*/)(?P<before>((?<!/\*method-end\*/)(.|\n))*?)(?P<separator>[\W](?<!(::|\.|->)))(?P<method>(?!sizeof)[a-zA-Z0-9]+)\((?!\) \{)(?P<after>(.|\n)*?)(?P<scopeEnd>/\*method-end\*/)", r"\g<scope>\g<before>\g<separator>this->\g<method>(\g<after>\g<scopeEnd>", None, 100),
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
        (r"(?P<scope>/\*~(?P<variable>[_a-zA-Z0-9]+)~\*/)(?P<separator>.|\n)(?P<before>((?<!/\*~\k<variable>~\*/)(.|\n))*?)\k<variable>\.Message", r"\g<scope>\g<separator>\g<before>\g<variable>.what()", None, 10),
        # Remove scope borders.
        # /*~ex~*/
        #
        (r"/\*~[_a-zA-Z0-9]+~\*/", r"", None, 0),
        # throw new ArgumentNullException(argumentName, message);
        # throw std::invalid_argument(((std::string)"Argument ").append(argumentName).append(" is null: ").append(message).append("."));
        (r"throw new ArgumentNullException\((?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*), (?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*)\);", r"throw std::invalid_argument(((std::string)\"Argument \").append(\g<argument>).append(\" is null: \").append(\g<message>).append(\".\"));", None, 0),
        # throw new ArgumentException(message, argumentName);
        # throw std::invalid_argument(((std::string)"Invalid ").append(argumentName).append(" argument: ").append(message).append("."));
        (r"throw new ArgumentException\((?P<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*), (?P<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*)\);", r"throw std::invalid_argument(((std::string)\"Invalid \").append(\g<argument>).append(\" argument: \").append(\g<message>).append(\".\"));", None, 0),
        # throw new NotSupportedException();
        # throw std::logic_error("Not supported exception.");
        (r"throw new NotSupportedException\(\);", r"throw std::logic_error(\"Not supported exception.\");", None, 0),
        # throw new NotImplementedException();
        # throw std::logic_error("Not implemented exception.");
        (r"throw new NotImplementedException\(\);", r"throw std::logic_error(\"Not implemented exception.\");", None, 0),
    ]

    LAST_RULES = [
        # (expression)
        # expression
        (r"(\(| )\(([a-zA-Z0-9_\*:]+)\)(,| |;|\))", r"\1\2\3", None, 0),
        #  (method(expression))
        #  method(expression)
        (r"(?P<firstSeparator>(\(| ))\((?P<method>[a-zA-Z0-9_\->\*:]+)\((?P<expression>((?P<parenthesis>\()|(?<!parenthesis>\))|[a-zA-Z0-9_\->\*:]*)+)(?(parenthesis)(?!))\)\)(?P<lastSeparator>(,| |;|\)))",
         r"\g<firstSeparator>\g<method>(\g<expression>)\g<lastSeparator>", None, 0),
        #  return ref _elements[node];
        #  return &_elements[node];
        (r"return ref ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9\*]+)\];",
         r"return &\1[\2];", None, 0),
        #  default
        #  0
        (r"(\W)default(\W)", r"{\1}0\2", None, 0),
        #  //#define ENABLE_TREE_AUTO_DEBUG_AND_VALIDATION
        #
        (r"\/\/[ \t]*\#define[ \t]+[_a-zA-Z0-9]+[ \t]*", r"", None, 0),
        #  #if USEARRAYPOOL\r\n#endif
        #
        (r"#if [a-zA-Z0-9]+\s+#endif", r"", None, 0),
        #  [Fact]
        #
        (r"(?P<firstNewLine>\r?\n|\A)(?P<indent>[\t ]+)\[[a-zA-Z0-9]+(\((?P<expression>((?P<parenthesis>\()|(?<!parenthesis>\))|[^\(\)]*)+)(?(parenthesis)(?!))\))?\][ \t]*(\r?\n(?P=indent))?",
         r"\g<firstNewLine>\g<indent>", None, 5),
        #  \n ... namespace
        #  namespace
        (r"(\S[\r\n]{1,2})?[\r\n]+namespace", r"\1namespace", None, 0),
        #  \n ... class
        #  class
        (r"(\S[\r\n]{1,2})?[\r\n]+class", r"\n\1class", None, 0)
    ]
