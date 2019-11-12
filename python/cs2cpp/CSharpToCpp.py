# -*- coding utf-8 -*-
# authors: Ethosa, Konard

from retranslator import Translator

class CSharpToCpp(Translator):
    def __init__(self, codeString="", extra=[], useRegex=False):
        """initialize class
        
        Keyword Arguments:
            codeString {str} -- source code on C# (default: {""})
            extra {list} -- include your own rules (default: {[]})
            useRegex {bool} -- this parameter tells you to use regex (default: {False})
        """
        self.codeString = codeString
        self.extra = extra
        self.Transform = self.compile = self.translate # callable objects

        # create little magic ...
        self.rules = CSharpToCppTranslator.FIRST_RULES[:]
        for rule in self.extra:
            self.rules.append(rule)
        for i in CSharpToCppTranslator.LAST_RULES:
            self.rules.append(i)
        Translator.__init__(self, codeString, self.rules, useRegex)

    # Rules for translate code
    FIRST_RULES = [
        # // ...
        #
        (r'(\r?\n)?[ \t]+//+.+"', r"", None, 0),
        # #pragma warning disable CS1591 // Missing XML comment for publicly visible type or member
        # 
        (r"^\s*?\#pragma[\sa-zA-Z0-9]+$", r"", None, 0),
        # {\n\n\n
        # {
        (r"{\s+[\r\n]+", r"{", None, 0),
        # Platform.Collections.Methods.Lists
        # Platform::Collections::Methods::Lists
        (r"(namespace[^\r\n]+?)\.([^\r\n]+?)", r"\1::\2", None, 20),
        # public abstract class
        # class
        (r"(public abstract|static) class", r"class", None, 0),
        # class GenericCollectionMethodsBase {
        # class GenericCollectionMethodsBase { public:
        (r"class ([a-zA-Z0-9]+)(\s+){", r"class \1\2{\n    public:", None, 0),
        # class GenericCollectionMethodsBase<TElement> {
        # template <typename TElement> class GenericCollectionMethodsBase { public:
        (r"class ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>([^{]+){", r"template <typename \2> class \1\3{\n    public:", None, 0),
        # static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        # template<typename T> static void TestMultipleCreationsAndDeletions<TElement>(SizedBinaryTreeMethodsBase<TElement> tree, TElement* root)
        (r"static ([a-zA-Z0-9]+) ([a-zA-Z0-9]+)<([a-zA-Z0-9]+)>\(([^\)]+)\)", r"template <typename \3> static \1 \2(\4)", None, 0),
        # (this
        # (
        (r"\(this ", r"\(", None, 0),
        # Func<TElement> treeCount
        # std::function<TElement()> treeCount
        (r"Func<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<\1()> \2", None, 0),
        # Action<TElement> free
        # std::function<void(TElement)> free
        (r"Action<([a-zA-Z0-9]+)> ([a-zA-Z0-9]+)", r"std::function<void(\1)> \2", None, 0),
        # private const int MaxPath = 92;
        # static const int MaxPath = 92;
        (r"private (const|static readonly) ([a-zA-Z0-9]+) ([_a-zA-Z0-9]+) = ([^;]+);", r"static const \2 \3 = \4;", None, 0),
        # protected virtual
        # virtual
        (r"protected virtual", r"virtual", None, 0),
        # protected readonly
        # 
        (r"protected readonly", r"", None, 0),
        # protected readonly TreeElement[] _elements;
        # TreeElement _elements[N];
        (r"(protected|private) readonly ([a-zA-Z<>0-9]+)([\[\]]+) ([_a-zA-Z0-9]+);", r"\2 \4[N];", None, 0),
        # protected readonly TElement Zero;
        # TElement Zero;
        (r"(protected|private) readonly ([a-zA-Z<>0-9]+) ([_a-zA-Z0-9]+);", r"\2 \3;", None, 0),
        # private
        # 
        (r"(\W)(private|protected|public|internal) ", r"\1", None, 0),
        # SizeBalancedTree(int capacity) => a = b;
        # SizeBalancedTree(int capacity) { a = b; }
        (r"(^\s+)(override )?(void )?([a-zA-Z0-9]+)\(([^\(]*)\)\s+=>\s+([^;]+);", r"\1\2\3\4(\5) { \6; }", None, 0),
        # int SizeBalancedTree(int capacity) => a;
        # int SizeBalancedTree(int capacity) { return a; }
        (r"(^\s+)(override )?([a-zA-Z0-9]+ )([a-zA-Z0-9]+)\(([^\(]*)\)\s+=>\s+([^;]+);", r"\1\2\3\4(\5) { return \6; }", None, 0),
        # () => Integer<TElement>.Zero,
        # () { return Integer<TElement>.Zero; },
        (r"\(\)\s+=>\s+([^\r\n,;]+?),", r"() { return \1; },", None, 0),
        # => Integer<TElement>.Zero;
        # { return Integer<TElement>.Zero; }
        (r"\)\s+=>\s+([^\r\n;]+?);", r") { return \1; }", None, 0),
        # () { return avlTree.Count; }
        # [&]()-> auto { return avlTree.Count; }
        (r", \(\) { return ([^;]+); }", r", [&]()-> auto { return \1; }", None, 0),
        # Count => GetSizeOrZero(Root);
        # GetCount() { return GetSizeOrZero(Root); }
        (r"([A-Z][a-z]+)\s+=>\s+([^;]+);", r"Get\1() { return \2; }", None, 0),
        # var
        # auto
        (r"(\W)var(\W)", r"\1auto\2", None, 0),
        # unchecked
        # 
        (r"[\r\n]{2}\s*?unchecked\s*?$", r"", None, 0),
        # $"
        # "
        (r"\$\"", r"\"", None, 0),
        # Console.WriteLine("...")
        # printf("...\n")
        (r"Console\.WriteLine\(\"([^\"]+)\"\)", r'printf("\1\\n")', None, 0),
        # Console.Write("...")
        # printf("...")
        (r"Console\.Write\(\"([^\"]+)\"\)", r'printf("\1")', None, 0),
        # throw new InvalidOperationException
        # throw std::exception
        (r"throw new (InvalidOperationException|Exception)", r'throw std::exception', None, 0),
        # override void PrintNode(TElement node, StringBuilder sb, int level)
        # void PrintNode(TElement node, StringBuilder sb, int level) override
        (r"override ([a-zA-Z0-9 \*\+]+)(\([^\)]+?\))", r'\1\2 override', None, 0),
        # string
        # char*
        (r"(\W)string(\W)", r'\1char\*\2', None, 0),
        # char*[] args
        # char* args[]
        (r"([_a-zA-Z0-9:\*]?)\[\] ([a-zA-Z0-9]+)", r'\1 \2[]', None, 0),
        # using Platform.Numbers;
        # 
        (r"([\r\n]{2}|^)\s*?using [\.a-zA-Z0-9]+;\s*?$", r'', None, 0),
        # struct TreeElement { }
        # struct TreeElement { };
        (r"(struct|class) ([a-zA-Z0-9]+)(\s+){([\sa-zA-Z0-9;:_]+?)}([^;])", r'\1 \2\3{\4};\5', None, 0),
        # class Program { }
        # class Program { };
        # !WARNING! (r"(struct|class) ([a-zA-Z0-9]+[^\r\n]*)([\r\n]+(?P<indentLevel>[\t ]*)?)\{([\S\s]+?[\r\n]+(?P=indentLevel))\}([^;]|$)", r'\1 \2\3{\4};\5', None, 0),
        # class SizedBinaryTreeMethodsBase : GenericCollectionMethodsBase
        # class SizedBinaryTreeMethodsBase : public GenericCollectionMethodsBase
        (r"class ([a-zA-Z0-9]+) : ([a-zA-Z0-9]+)", r'class \1 : public \2', None, 0),
        # Insert scope borders.
        # ref TElement root
        # ~!root!~ref TElement root
        # !WARNING! (r"(?P<definition>(?<= |\()(ref [a-zA-Z0-9]+|[a-zA-Z0-9]+(?<!ref)) (?P<variable>[a-zA-Z0-9]+)(?=\)|, | =))", r'~!\{variable}!~\{definition}', None, 0),
        # Inside the scope of ~!root!~ replace:
        # root
        # *root
        (r"(?P<definition>~!(?P<pointer>[a-zA-Z0-9]+)!~ref [a-zA-Z0-9]+ (?P=pointer)(?=\)|, | =))(?P<before>((?<!~!)(.|\n))*?)(?P<prefix>(\W |\())(?P=pointer)(?P<suffix>( |\)|;|,))", r'\{definition}\{before}\{prefix}*\{pointer}\{suffix}', None, 70),
        # Remove scope borders.
        # ~!root!~
        # 
        (r"~!(?P<pointer>[a-zA-Z0-9]+)!~", r'', None, 5),
        # ref auto root = ref
        # ref auto root = 
        (r"ref ([a-zA-Z0-9]+) ([a-zA-Z0-9]+) = ref(\W)", r'\1* \2 =\3', None, 0),
        # *root = ref left;
        # root = left;
        (r"\*([a-zA-Z0-9]+) = ref ([a-zA-Z0-9]+)(\W)", r'\1 = \2\3', None, 0),
        # (ref left)
        # (left)
        (r"\(ref ([a-zA-Z0-9]+)(\)|\(|,)", r'(\1\2', None, 0),
        # ref TElement 
        # TElement*
        (r"( |\()ref ([a-zA-Z0-9]+) ", r'\1\2* ', None, 0),
        # ref sizeBalancedTree.Root
        # &sizeBalancedTree->Root
        (r"ref ([a-zA-Z0-9]+)\.([a-zA-Z0-9\*]+)", r'&\1->\2', None, 0),
        # ref GetElement(node).Right
        # &GetElement(node)->Right
        (r"ref ([a-zA-Z0-9]+)\(([a-zA-Z0-9\*]+)\)\.([a-zA-Z0-9]+)", r'&\1(\2)->\3', None, 0),
        # GetElement(node).Right
        # GetElement(node)->Right
        (r"([a-zA-Z0-9]+)\(([a-zA-Z0-9\*]+)\)\.([a-zA-Z0-9]+)", r'\1(\2)->\3', None, 0),
        # [Fact]\npublic static void SizeBalancedTreeMultipleAttachAndDetachTest()
        # TEST_METHOD(SizeBalancedTreeMultipleAttachAndDetachTest)
        (r"\[Fact\][\s\n]+(static )?void ([a-zA-Z0-9]+)\(\)", r'TEST_METHOD(\2)', None, 0),
        # class TreesTests
        # TEST_CLASS(TreesTests)
        (r"class ([a-zA-Z0-9]+)Tests", r'TEST_CLASS(\1)', None, 0),
        # Assert.Equal
        # Assert::AreEqual
        (r"Assert\.Equal", r'Assert::AreEqual', None, 0),
        # TElement Root;
        # TElement Root = 0;
        (r"(\r?\n[\t ]+)([a-zA-Z0-9:_]+(?<!return)) ([_a-zA-Z0-9]+);", r'\1\2 \3 = 0;', None, 0),
        # TreeElement _elements[N];
        # TreeElement _elements[N] = { {0} };
        (r"(\r?\n[\t ]+)([a-zA-Z0-9]+) ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r'\1\2 \3[\4] = { {0} };', None, 0),
        # auto path = new TElement[MaxPath];
        # TElement path[MaxPath] = { {0} };
        (r"(\r?\n[\t ]+)[a-zA-Z0-9]+ ([a-zA-Z0-9]+) = new ([a-zA-Z0-9]+)\[([_a-zA-Z0-9]+)\];", r'\1\3 \2[\4] = { {0} };', None, 0),
        # Insert scope borders.
        # auto added = new HashSet<TElement>();
        # ~!added!~std::unordered_set<TElement> added;
        (r"auto (?P<variable>[a-zA-Z0-9]+) = new HashSet<(?P<element>[a-zA-Z0-9]+)>\(\);", r'~!\{variable}!~std::unordered_set<\{element}> \{variable};', None, 0),
        # Inside the scope of ~!added!~ replace:
        # added.Add(node)
        # added.insert(node)
        # !!ERROR!! (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Add\((?P<argument>[a-zA-Z0-9]+)\)", r'\{scope}\{separator}\{before}\{variable}.insert(\{argument})', None, 10),
        # Inside the scope of ~!added!~ replace:
        # added.Remove(node)
        # added.erase(node)
        # !!ERROR!! (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Remove\((?P<argument>[a-zA-Z0-9]+)\)", r'\{scope}\{separator}\{before}\{variable}.erase(\{argument})', None, 10),
        # if (added.insert(node)) {
        # if (!added.contains(node)) { added.insert(node);
        (r"if \((?P<variable>[a-zA-Z0-9]+)\.insert\((?P<argument>[a-zA-Z0-9]+)\)\)(?P<separator>[\t ]*[\r\n]+)(?P<indent>[\t ]*){", r'if (!\{variable}.contains(\{argument}))\{separator}\{indent}{\n\{indent}    \{variable}.insert(\{argument});', None, 0),
        # Remove scope borders.
        # ~!added!~
        # 
        (r"~!(?P<pointer>[a-zA-Z0-9]+)!~", r'', None, 5),
        # Insert scope borders.
        # auto random = new System.Random(0);
        # std::srand(0);
        (r"[a-zA-Z0-9\.]+ ([a-zA-Z0-9]+) = new (System\.)?Random\(([a-zA-Z0-9]+)\);", r'~!\1!~std::srand(\3);', None, 0),
        # Inside the scope of ~!random!~ replace:
        # random.Next(1, N)
        # s(std::rand() % N) + 1
        # !!ERROR!! (r"(?P<scope>~!(?P<variable>[a-zA-Z0-9]+)!~)(?P<separator>.|\n)(?P<before>((?<!~!(?P=variable)!~)(.|\n))*?)(?P=variable)\.Next\((?P<from>[a-zA-Z0-9]+), (?P<to>[a-zA-Z0-9]+)\)", r'\{scope}${separator}\{before}(std::rand() % ${to}) + \{from}', None, 210),
        # Remove scope borders.
        # ~!random!~
        # 
        (r"~!(?P<pointer>[a-zA-Z0-9]+)!~", r'', None, 5),
        # Insert method body scope starts.
        # void PrintNodes(TElement node, StringBuilder sb, int level) {
        # void PrintNodes(TElement node, StringBuilder sb, int level) {/*method-start*/
        (r"(?P<start>\r?\n[\t ]+)(?P<prefix>((virtual )?[a-zA-Z0-9:_]+ )?)(?P<method>[a-zA-Z][a-zA-Z0-9]*)\((?P<arguments>[^\)]*)\)(?P<override>( override)?)(?P<separator>[ \t\r\n]*)\{(?P<end>[^~])", r'\{start}\{prefix}\{method}(\{arguments})\{override}\{separator}{/*method-start*/\{end}', None, 5),
        # Insert method body scope ends.
        # {/*method-start*/...}
        # {/*method-start*/.../*method-end*/}
        # !!ERROR!! (r"\{/\*method-start\*/(?P<body>((?P<bracket>\{)|(?<-bracket>\})|[^\{\}]*)+)\}", r'{/*method-start*/\{body}/*method-end*/}', None, 0),
        # Remove scope borders.
        # /*method-start*/
        # 
        (r"/\*method-(start|end)\*/", r'', None, 0)
    ]

    LAST_RULES = [
        # (expression)
        # expression
        (r"(\(| )\(([a-zA-Z0-9_\*:]+)\)(,| |;|\))", r"\1\2\3", None, 0),
        # (method(expression))
        # method(expression)
        # !!ERROR!! (r"(?P<firstSeparator>(\(| ))\((?P<method>[a-zA-Z0-9_\->\*:]+)\((?P<expression>((?P<parenthesis>\()|(?<-parenthesis>\))|[a-zA-Z0-9_\->\*:]*)+)(?(parenthesis)(?!))\)\)(?P<lastSeparator>(,| |;|\)))", r"\{firstSeparator}\{method}(\{expression})\{lastSeparator}", None, 0),
        # return ref _elements[node];
        # return &_elements[node];
        (r"return ref ([_a-zA-Z0-9]+)\[([_a-zA-Z0-9\*]+)\];", r"return &\1[\2];", None, 0),
        # default
        # 0
        (r"(\W)default(\W)", r"\{1}0\2", None, 0),
        # //#define ENABLE_TREE_AUTO_DEBUG_AND_VALIDATION
        #
        (r"\/\/[ \t]*\#define[ \t]+[_a-zA-Z0-9]+[ \t]*", r"", None, 0),
        # #if USEARRAYPOOL\r\n#endif
        #
        (r"#if [a-zA-Z0-9]+\s+#endif", r"", None, 0),
        # [Fact]
        # 
        # !!ERROR!! (r"(?P<firstNewLine>\r?\n|\A)(?P<indent>[\t ]+)\[[a-zA-Z0-9]+(\((?P<expression>((?P<parenthesis>\()|(?<-parenthesis>\))|[^()]*)+)(?(parenthesis)(?!))\))?\][ \t]*(\r?\n(?P=indent))?", r"\{firstNewLine}\{indent}", None, 5),
        # \n ... namespace
        # namespace
        (r"(\S[\r\n]{1,2})?[\r\n]+namespace", r"\1namespace", None, 0),
        # \n ... class
        # class
        (r"(\S[\r\n]{1,2})?[\r\n]+class", r"\1class", None, 0)
    ]
