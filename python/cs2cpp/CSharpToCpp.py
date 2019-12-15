# -*- coding utf-8 -*-
# authors: Ethosa, Konard

from retranslator import Translator


class CSharpToCpp(Translator):
    def __init__(self, codeString="", extra=[], useRegex=False):
        """initialize class

        Keyword Arguments:
            codeString {str} -- source code on C# (default: {\"})
            extra {list} -- include your own rules (default: {[]})
            useRegex {bool} -- this parameter tells you to use regex (default: {False})
        """
        self.codeString = codeString
        self.Transform = self.compile = self.translate  # callable objects

        #  create little magic ...
        self.rules = CSharpToCpp.FIRST_RULES[:]
        self.rules.extend(extra)
        self.rules.extend(CSharpToCpp.LAST_RULES)
        Translator.__init__(self, codeString, self.rules, useRegex)

    #  Rules for translate code
    FIRST_RULES = [
            # #...
            #
            (r"(\r?\n)?[ \t]+//+.+", r"", None, 0),
            # #pragma warning disable CS1591 #Missing XML comment for publicly visible type or member
            #
            (r"^\s*?\#pragma[\sa-zA-Z0-9]+$", r"", None, 0),
            # {\n\n\n
            # {
            (r"{\s+[\r\n]+", r"{" + "\n", None, 0),
            # Platform.Collections.Methods.Lists
            # Platform::Collections::Methods::Lists
            (r"(namespace[^\r\n]+?)\.([^\r\n]+?)", r"\1::\2", None, 20),
            # out TProduct
            # TProduct
            (r"(?<before>(<|, ))(in|out) (?<typeParameter>[a-zA-Z0-9]+)(?<after>(>|,))", r"\g<before>\g<typeParameter>\g<after>", None, 10),
            # public abstract class
            # class
            (r"(public abstract|static) class", r"class", None, 0),
            # class GenericCollectionMethodsBase {
            # class GenericCollectionMethodsBase { public:
            (r"class ([a-zA-Z0-9]+)(\s+){", r"class \1\2{" + "\n" + "    public:", None, 0),
            # class GenericCollectionMethodsBase<TElement> {
            # template <typename TElement> class GenericCollectionMethodsBase { public:
            (r"class ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>([^{]+){", r"template <typename \2> class \1\3{" + "\n" + "    public:", None, 0),
            # static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
            # template<typename T> static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
            (r"static ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>\(([^\)\r\n]+)\)", r"template <typename \3> static \1 \2(\4)", None, 0),
            # interface IFactory<out TProduct> {
            # template <typename TProduct> class IFactory { public:
            (r"interface (?<interface>[a-zA-Z0-9]+)<(?<typeParameters>[a-zA-Z0-9 ,]+)>(?<whitespace>[^{]+){", r"template <typename...> class \g<interface>; template <typename \g<typeParameters>> class \g<interface><\g<typeParameters>>\g<whitespace>{" + "\n" + "    public:", None, 0),
            # template <typename TObject, TProperty, TValue>
            # template <typename TObject, typename TProperty, TValue>
            (r"(?<before>template <((, )?typename [a-zA-Z0-9]+)+, )(?<typeParameter>[a-zA-Z0-9]+)(?<after>(,|>))", r"\g<before>typename \g<typeParameter>\g<after>", None, 10),
            # (this
            # (
            (r"\(this ", r"(", None, 0),
            # public static readonly EnsureAlwaysExtensionRoot Always = new EnsureAlwaysExtensionRoot();
            # inline static EnsureAlwaysExtensionRoot Always;
            (r"public static readonly (?<type>[a-zA-Z0-9]+) (?<name>[a-zA-Z0-9_]+) = new (?P=type)\(\);", r"inline static \g<type> \g<name>;", None, 0),
            # public static readonly string ExceptionContentsSeparator = "---";
            # inline static const char* ExceptionContentsSeparator = "---";
            (r"public static readonly string (?<name>[a-zA-Z0-9_]+) = \"(?<string>(\"|[^\"\r\n])+)\";", r"inline static const char* \g<name> = \"\g<string>\";", None, 0),
            # private const int MaxPath = 92;
            # static const int MaxPath = 92;
            (r"private (const|static readonly) ([a-zA-Z0-9]+) ([_a-zA-Z0-9]+) = ([^;\r\n]+);", r"static const \2 \3 = \4;", None, 0),
            #  ArgumentNotNone(EnsureAlwaysExtensionRoot root, TArgument argument) where TArgument : class
            #  ArgumentNotNone(EnsureAlwaysExtensionRoot root, TArgument* argument)
            (r"(?<before> [a-zA-Z]+\(([a-zA-Z *,]+, |))(?<type>[a-zA-Z]+)(?<after>(| [a-zA-Z *,]+)\))[ \r\n]+where (?P=type) : class", r"\g<before>\g<type>*\g<after>", None, 0),
            # protected virtual
            # virtual
            (r"protected virtual", r"virtual", None, 0),
            # protected abstract TElement GetFirst();
            # virtual TElement GetFirst() = 0;
            (r"protected abstract ([^;\r\n]+);", r"virtual \1 = 0;", None, 0),
            # TElement GetFirst();
            # virtual TElement GetFirst() = 0;
            (r"([\r\n]+[ ]+)((?!return)[a-zA-Z0-9]+ [a-zA-Z0-9]+\([^\)\r\n]*\))(;[ ]*[\r\n]+)", r"\1virtual \2 = 0\3", None, 1),
            # public virtual
            # virtual
            (r"public virtual", r"virtual", None, 0),
            # protected readonly
            #
            (r"protected readonly ", r"", None, 0),
            # protected readonly TreeElement[] _elements;
            # TreeElement _elements[N];
            (r"(protected|private) readonly ([a-zA-Z<>0-9]+)([\[\]]+) ([_a-zA-Z0-9]+);", r"\2 \4[N];", None, 0),
            # protected readonly TElement Zero;
            # TElement Zero;
            (r"(protected|private) readonly ([a-zA-Z<>0-9]+) ([_a-zA-Z0-9]+);", r"\2 \3;", None, 0),
            # private
            #
            (r"(\W)(private|protected|public|internal) ", r"\1", None, 0),
            # static void NotImplementedException(ThrowExtensionRoot root) => throw new NotImplementedException();
            # static void NotImplementedException(ThrowExtensionRoot root) { return throw new NotImplementedException(); }
            (r"(^\s+)(template \<[^>\r\n]+\> )?(static )?(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+throw([^;\r\n]+);", r"\1\2\3\4\5\6(\7) { throw\8; }", None, 0),
            # SizeBalancedTree(int capacity) => a = b;
            # SizeBalancedTree(int capacity) { a = b; }
            (r"(^\s+)(template \<[^>\r\n]+\> )?(static )?(override )?(void )?([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+([^;\r\n]+);", r"\1\2\3\4\5\6(\7) { \8; }", None, 0),
            # int SizeBalancedTree(int capacity) => a;
            # int SizeBalancedTree(int capacity) { return a; }
            (r"(^\s+)(template \<[^>\r\n]+\> )?(static )?(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(\r\n]*)\)\s+=>\s+([^;\r\n]+);", r"\1\2\3\4\5\6(\7) { return \8; }", None, 0),
            # () => Integer<TElement>.Zero,
            # () { return Integer<TElement>.Zero; },
            (r"\(\)\s+=>\s+([^,;\r\n]+?),", r"() { return \1; },", None, 0),
            # => Integer<TElement>.Zero;
            # { return Integer<TElement>.Zero; }
            (r"\)\s+=>\s+([^;\r\n]+?);", r") { return \1; }", None, 0),
            # () { return avlTree.Count; }
            # [&]()-> auto { return avlTree.Count; }
            (r", \(\) { return ([^;\r\n]+); }", r", [&]()-> auto { return \1; }", None, 0),
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
            (r"(struct|class) ([a-zA-Z0-9]+[^\r\n]*)([\r\n]+(?<indentLevel>[\t ]*)?)\{([\S\s]+?[\r\n]+(?P=indentLevel))\}([^;]|$)", r"\1 \2\3{\4};\5", None, 0),
            # class SizedBinaryTreeMethodsBase : GenericCollectionMethodsBase
            # class SizedBinaryTreeMethodsBase : public GenericCollectionMethodsBase
            (r"class ([a-zA-Z0-9]+) : ([a-zA-Z0-9]+)", r"class \1 : public \2", None, 0),
            # class IProperty : ISetter<TValue, TObject>, IProvider<TValue, TObject>
            # class IProperty : public ISetter<TValue, TObject>, IProvider<TValue, TObject>
            (r"(?<before>class [a-zA-Z0-9]+ : ((public [a-zA-Z0-9]+(<[a-zA-Z0-9 ,]+>)?, )+)?)(?<inheritedType>(?!public)[a-zA-Z0-9]+(<[a-zA-Z0-9 ,]+>)?)(?<after>(, [a-zA-Z0-9]+(?!>)|[ \r\n]+))", r"\g<before>public \g<inheritedType>\g<after>", None, 10),
            # Insert scope borders.
            # ref TElement root
            # ~!root!~ref TElement root
            (r"(?<definition>(?<= |\()(ref [a-zA-Z0-9]+|[a-zA-Z0-9]+(?<!ref)) (?<variable>[a-zA-Z0-9]+)(?=\)|, | =))", r"~!\g<variable>!~\g<definition>", None, 0),
            # Inside the scope of ~!root!~ replace:
            # root
            # *root
            (r"(?<definition>~!(?<pointer>[a-zA-Z0-9]+)!~ref [a-zA-Z0-9]+ (?P=pointer)(?=\)|, | =))(?<before>((?<!~!(?P=pointer)!~)(.|\n))*?)(?<prefix>(\W |\())(?P=pointer)(?<suffix>( |\)|;|,))", r"\g<definition>\g<before>\g<prefix>*\g<pointer>\g<suffix>", None, 70),
            # Remove scope borders.
            # ~!root!~
            #
            (r"~!(?<pointer>[a-zA-Z0-9]+)!~", r"", None, 5),
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
            # [Fact]\npublic static void SizeBalancedTreeMultipleAttachAndDetachTest()
            # TEST_METHOD(SizeBalancedTreeMultipleAttachAndDetachTest)
            (r"\[Fact\][\s\n]+(static )?void ([a-zA-Z0-9]+)\(\)", r"TEST_METHOD(\2)", None, 0),
            # class TreesTests
            # TEST_CLASS(TreesTests)
            (r"class ([a-zA-Z0-9]+)Tests", r"TEST_CLASS(\1)", None, 0),
            # Assert.Equal
            # Assert::AreEqual
            (r"Assert\.Equal", r"Assert::AreEqual", None, 0),
            # $"Argument {argumentName} is None."
            # ((std::string)"Argument ").append(argumentName).append(" is None.").data()
            (r"\$\"(?<left>(\\\"|[^\"\r\n])*){(?<expression>[_a-zA-Z0-9]+)}(?<right>(\\\"|[^\"\r\n])*)\"", r"((std::string)$\"\g<left>\").append(\g<expression>).append(\"\g<right>\").data()", None, 10),
            # $"
            # "
            (r"\$\"", r"\\", None, 0),
            # Console.WriteLine("...")
            # printf("...\n")
            (r"Console\.WriteLine\(\"([^\"\r\n]+)\"\)", r"printf(\"\1\\n\")", None, 0),
            # TElement Root;
            # TElement Root = 0;
            (r"(\r?\n[\t ]+)([a-zA-Z0-9:_]+(?<!return)) ([_a-zA-Z0-9]+);", r"\1\2 \3 = 0;", None, 0),
            # TreeElement _elements[N];
            # TreeElement _elements[N] = { {0} };
            (r"(\r?\n[\t ]+)([a-zA-Z0-9]+) ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\2 \3[\4] = { {0} };", None, 0),
            # auto path = new TElement[MaxPath];
            # TElement path[MaxPath] = { {0} };
            (r"(\r?\n[\t ]+)[a-zA-Z0-9]+ ([a-zA-Z0-9]+) = new ([a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r"\1\3 \2[\4] = { {0} };", None, 0),
            # Insert scope borders.
            # auto added = new StringBuilder();
            # /*~sb~*/std::string added;
            (r"(auto|(System\.Text\.)?StringBuilder) (?<variable>[a-zA-Z0-9]+) = new (System\.Text\.)?StringBuilder\(\);", r"/*~\g<variable>~*/std::string \g<variable>;", None, 0),
            # static void Indent(StringBuilder sb, int level)
            # static void Indent(/*~sb~*/StringBuilder sb, int level)
            (r"(?<start>, |\()(System\.Text\.)?StringBuilder (?<variable>[a-zA-Z0-9]+)(?<end>,|\))", r"\g<start>/*~\g<variable>~*/std::string \g<variable>\g<end>", None, 0),
            # Inside the scope of ~!added!~ replace:
            # sb.ToString()
            # sb.data()
            (r"(?<scope>/\*~(?<variable>[a-zA-Z0-9]+)~\*/)(?<separator>.|\n)(?<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.ToString\(\)", r"\g<scope>\g<separator>\g<before>\g<variable>.data()", None, 10),
            # sb.AppendLine(argument)
            # sb.append(argument).append('\n')
            (r"(?<scope>/\*~(?<variable>[a-zA-Z0-9]+)~\*/)(?<separator>.|\n)(?<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.AppendLine\((?<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<argument>).append('\\n')", None, 10),
            # sb.Append('\t', level);
            # sb.append(level, '\t');
            (r"(?<scope>/\*~(?<variable>[a-zA-Z0-9]+)~\*/)(?<separator>.|\n)(?<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.Append\('(?<character>[^'\r\n]+)', (?<count>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<count>, '\g<character>')", None, 10),
            # sb.Append(argument)
            # sb.append(argument)
            (r"(?<scope>/\*~(?<variable>[a-zA-Z0-9]+)~\*/)(?<separator>.|\n)(?<before>((?<!/\*~(?P=variable)~\*/)(.|\n))*?)(?P=variable)\.Append\((?<argument>[^\),\r\n]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.append(\g<argument>)", None, 10),
            # Remove scope borders.
            # /*~sb~*/
            #
            (r"/\*~(?<pointer>[a-zA-Z0-9]+)~\*/", r"", None, 0),
            # Insert scope borders.
            # auto added = new HashSet<TElement>();
            # ~!added!~std::unordered_set<TElement> added;
            (r"auto (?<variable>[a-zA-Z0-9]+) = new HashSet<(?<element>[a-zA-Z0-9]+)>\(\);", r"~!\g<variable>!~std::unordered_set<\g<element>> \g<variable>;", None, 0),
            # Inside the scope of ~!added!~ replace:
            # added.Add(node)
            # added.insert(node)
            (r"(?<scope>~!(?<variable>[a-zA-Z0-9]+)!~)(?<separator>.|\n)(?<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Add\((?<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.insert(\g<argument>)", None, 10),
            # Inside the scope of ~!added!~ replace:
            # added.Remove(node)
            # added.erase(node)
            (r"(?<scope>~!(?<variable>[a-zA-Z0-9]+)!~)(?<separator>.|\n)(?<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Remove\((?<argument>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>\g<variable>.erase(\g<argument>)", None, 10),
            # if (added.insert(node)) {
            # if (!added.contains(node)) { added.insert(node);
            (r"if \((?<variable>[a-zA-Z0-9]+)\.insert\((?<argument>[a-zA-Z0-9]+)\)\)(?<separator>[\t ]*[\r\n]+)(?<indent>[\t ]*){", r"if (!\g<variable>.contains(\g<argument>))\g<separator>\g<indent>{\n\g<indent>    \g<variable>.insert(\g<argument>);", None, 0),
            # Remove scope borders.
            # ~!added!~
            #
            (r"~!(?<pointer>[a-zA-Z0-9]+)!~", r"", None, 5),
            # Insert scope borders.
            # auto random = new System.Random(0);
            # std::srand(0);
            (r"[a-zA-Z0-9\.]+ ([a-zA-Z0-9]+) = new (System\.)?Random\(([a-zA-Z0-9]+)\);", r"~!\1!~std::srand(\3);", None, 0),
            # Inside the scope of ~!random!~ replace:
            # random.Next(1, N)
            # (std::rand() % N) + 1
            (r"(?<scope>~!(?<variable>[a-zA-Z0-9]+)!~)(?<separator>.|\n)(?<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Next\((?<from>[a-zA-Z0-9]+), (?<to>[a-zA-Z0-9]+)\)", r"\g<scope>\g<separator>\g<before>(std::rand() % \g<to>) + \g<from>", None, 10),
            # Remove scope borders.
            # ~!random!~
            #
            (r"~!(?<pointer>[a-zA-Z0-9]+)!~", r"", None, 5),
            # Insert method body scope starts.
            # void PrintNodes(TElement node, StringBuilder sb, int level) {
            # void PrintNodes(TElement node, StringBuilder sb, int level) {/*method-start*/
            (r"(?<start>\r?\n[\t ]+)(?<prefix>((virtual )?[a-zA-Z0-9:_]+ )?)(?<method>[a-zA-Z][a-zA-Z0-9]*)\((?<arguments>[^\)]*)\)(?<override>( override)?)(?<separator>[ \t\r\n]*)\{(?<end>[^~])", r"\g<start>\g<prefix>\g<method>(\g<arguments>)\g<override>\g<separator>{/*method-start*/\g<end>", None, 0),
            # Insert method body scope ends.
            # {/*method-start*/...}
            # {/*method-start*/.../*method-end*/}
            (r"\{/\*method-start\*/(?<body>((?<bracket>\{)|(?<-bracket>\})|[^\{\}]*)+)\}", r"{/*method-start*/\g<body>/*method-end*/}", None, 0),
            # Inside method bodies replace:
            # GetFirst(
            # this->GetFirst(
            # (r"(?<separator>(\(|, |([\W]) |return ))(?<!(->|\* ))(?<method>(?!sizeof)[a-zA-Z0-9]+)\((?!\) \{)", r"\g<separator>this->\g<method>(", None, 1),
            (r"(?<scope>/\*method-start\*/)(?<before>((?<!/\*method-end\*/)(.|\n))*?)(?<separator>[\W](?<!(::|\.|->)))(?<method>(?!sizeof)[a-zA-Z0-9]+)\((?!\) \{)(?<after>(.|\n)*?)(?<scopeEnd>/\*method-end\*/)", r"\g<scope>\g<before>\g<separator>this->\g<method>(\g<after>\g<scopeEnd>", None, 100),
            # Remove scope borders.
            # /*method-start*/
            #
            (r"/\*method-(start|end)\*/", r"", None, 0),
            # throw new ArgumentNoneException(argumentName, message);
            # throw std::invalid_argument(((std::string)"Argument ").append(argumentName).append(" is None: ").append(message).append("."));
            (r"throw new ArgumentNoneException\((?<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*), (?<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*)\);", r"throw std::invalid_argument(((std::string)\"Argument \").append(\g<argument>).append(\" is None: \").append(\g<message>).append(\".\"));", None, 0),
            # throw new ArgumentException(message, argumentName);
            # throw std::invalid_argument(((std::string)"Invalid ").append(argumentName).append(" argument: ").append(message).append("."));
            (r"throw new ArgumentException\((?<message>[a-zA-Z]*[Mm]essage[a-zA-Z]*), (?<argument>[a-zA-Z]*[Aa]rgument[a-zA-Z]*)\);", r"throw std::invalid_argument(((std::string)\"Invalid \").append(\g<argument>).append(\" argument: \").append(\g<message>).append(\".\"));", None, 0),
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
        (r"(?<firstSeparator>(\(| ))\((?<method>[a-zA-Z0-9_\->\*:]+)\((?<expression>((?<parenthesis>\()|(?<!parenthesis>\))|[a-zA-Z0-9_\->\*:]*)+)(?(parenthesis)(?!))\)\)(?<lastSeparator>(,| |;|\)))", r"\g<firstSeparator>\g<method>(\g<expression>)\g<lastSeparator>", None, 0),
        #  return ref _elements[node];
        #  return &_elements[node];
        (r"return ref ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9\*]+)\];", r"return &\1[\2];", None, 0),
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
        (r"(?<firstNewLine>\r?\n|\A)(?<indent>[\t ]+)\[[a-zA-Z0-9]+(\((?<expression>((?<parenthesis>\()|(?<!parenthesis>\))|[^()]*)+)(?(parenthesis)(?!))\))?\][ \t]*(\r?\n(?P=indent)?", r"\g<firstNewLine>\g<indent>", None, 5),
        #  \n ... namespace
        #  namespace
        (r"(\S[\r\n]{1,2})?[\r\n]+namespace", r"\1namespace", None, 0),
        #  \n ... class
        #  class
        (r"(\S[\r\n]{1,2})?[\r\n]+class", r"\n\1class", None, 0)
    ]
