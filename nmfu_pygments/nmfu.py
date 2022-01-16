from pygments.lexer import RegexLexer, words, bygroups, using
from pygments.token import *

def kwds(joined):
    return words(joined.split(), prefix="\\b", suffix="\\b")

nmfu_kwds = kwds("case loop optional try catch wait finish break foreach do match expr else yield prio end")
nmfu_conds = kwds("if elif")
nmfu_defwords = kwds("parser macro hook finishcode yieldcode")
nmfu_bool = kwds("true false")
nmfu_catch = kwds("nomatch outofspace")
nmfu_outtype = kwds("int str raw bool enum")

nmfu_num_exprs = [
    (r"\b[+\-]?\d+", Number.Integer),
    (r"\b[+\-]?0x[0-9a-fA-F]+", Number.Hex),
    (r"\b0b[01]+", Number.Bin),
    (r"'(\.|[^'])'", String.Char)
]

# common groups
nmfu_math_exprs = [
    (r"\*", Operator),
    (r"\+", Operator),
    (r"-", Operator),
    (r"/", Operator),
    (r"%", Operator),
    (r"[!=]=", Operator),
    (r"[<>]=?", Operator),
    (r"&", Operator),
    (r"\|", Operator),
    (r"\^", Operator),
    (r"\!", Operator),

    (r"\b\$\w+", Name.Variable.Magic),
    (r"(?<=\w)\.len", Name.Builtin),

    *nmfu_num_exprs,

    (r'\(|\)', Punctuation),
    (r'[A-Z0-9_]+', Name.Constant),
    (r'\w+', Name),
]

class NmfuLexer(RegexLexer):
    name = "NMFU"
    aliases = ['nmfu']
    filenames = ['*.nmfu']

    tokens = {
        # main definitions
        'root': [
            (r'\s+', Text),   # ignore whitespace
            (r'//.*$', Comment),
            (nmfu_kwds, Keyword),
            (nmfu_defwords, Keyword.Declaration),
            (nmfu_bool, Keyword.Constant),
            (nmfu_catch, Name.Exception),
            (r"^\s*out\b", Keyword.Declaration, "out"),

            # greedy case
            (r"\bgreedy(?=\s+case\b)", Keyword),

            # macro defn
            (r"(?<=^\bmacro\b)\w+(?=\s*\()", Name.Function),

            # macro call
            (r"\b\w+(?=\s*\()", Name.Function),

            (r'\+?=', Operator),
            *nmfu_num_exprs,

            # regex
            (r"(b?)(/(?:[^/\\]|\\.)+/)", bygroups(String.Affix, String.Regex)),

            # match
            (r'("(?:[^"\\]|\\.)*")([bi]?)', bygroups(String, String.Affix)),

            # if/elif
            (nmfu_conds, Keyword, "if_elif"),

            # math
            (r"\[", Punctuation, "math_expr"),
            
            # fallback (names + text)
            (r'[A-Z0-9_]+', Name.Constant),
            (r'\w+', Name),
            (r'\{|\}', Punctuation),
            ('.', Text)
        ],
        "if_elif": [
            (r'\s+', Text),
            *nmfu_math_exprs,
            (r'\{', Punctuation, "#pop"),
            ('.', Text)
        ],
        "math_expr": [
            (r'\s+', Text),
            *nmfu_math_exprs,
            (r'\]', Punctuation, "#pop"),
            ('.', Text)
        ],
        # output declaration
        'out': [
            (r'\s+', Text),
            # we've already read an "out", now we want type stuff
            (nmfu_outtype, Keyword.Type),
            ("unterminated", Name.Decorator),
            (r'(?<=int)\b{', Text, 'out_int'),
            (r'(?<=str)\b(\[)(\d+)(\])', bygroups(Punctuation, Number, Punctuation)),
            (r'=', Operator, "#pop"),
            (r';', Punctuation, "#pop"),
            (r'[A-Z0-9_]+', Name.Constant),
            (r'\w+', Name.Variable),
            (r'\{\|}', Punctuation),
            ('.', Text)
        ],
        'out_int': [
            (r'\s+', Text),
            (r'}', Punctuation, "#pop"),
            (r'(size)(\s+)(\d+)', bygroups(Name.Decorator, Text, Number)),
            (r'(un)?signed', Name.Decorator),
            (r',', Punctuation),
            ('.', Text)
        ],
    }
