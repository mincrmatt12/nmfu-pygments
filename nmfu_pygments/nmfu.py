from pygments.lexer import RegexLexer, words, bygroups, using
from pygments.token import *

def kwds(joined):
    return words(joined.split(), prefix="\\b", suffix="\\b")

nmfu_kwds = kwds("case loop optional try catch wait finish break foreach do match expr else yield prio end")
nmfu_conds = kwds("if elif")
nmfu_defwords = kwds("parser macro hook finishcode yieldcode")
nmfu_bool = kwds("true false")
nmfu_catch = kwds("nomatch outofspace")
nmfu_outtype = kwds("int str raw bool enum unterminated")

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
    (r"(?<=\w)\.len", Name.Variable.Magic),

    *nmfu_num_exprs
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
            (r"^\s*out\b", Keyword.Declaration, "out"),

            # greedy case
            (r"\bgreedy(?=\s+case\b)", Keyword),

            # macro defn
            (r"(?<=^\bmacro\b)\w+(?=\s*\()", Name.Function),

            # macro call
            (r"\b\w+(?=\s*\()", Name.Function),

            *nmfu_num_exprs,

            # regex
            (r"(b?)(/(?:[^/\\]|\\.)+/)", bygroups(String.Affix, String.Regex)),

            # match
            (r'("(?:[^"\\]|\\.)*")([bi]?)', bygroups(String, String.Affix)),

            # if/elif
            (nmfu_conds, Keyword, "if_elif"),

            # math
            (r"\[", Text, "math_expr"),
            
            # fallback
            ('.', Text)
        ],
        "if_elif": [
            (r'\s+', Text),
            *nmfu_math_exprs,
            (r'\{', Text, "#pop"),
            ('.', Text)
        ],
        "math_expr": [
            (r'\s+', Text),
            *nmfu_math_exprs,
            (r'\]', Text, "#pop"),
            ('.', Text)
        ],
        # output declaration
        'out': [
            (r'\s+', Text),
            # we've already read an "out", now we want type stuff
            (nmfu_outtype, Keyword.Type),
            (r'(?<=int)\b{', Text, 'out_int'),
            (r'(?<=str)\b(\[)(\d+)(\])', bygroups(Text, Number, Text)),
            (r'=', Operator, "#pop"),
            (r';', Text, "#pop")
        ],
        'out_int': [
            (r'\s+', Text),
            (r'}', Text, "#pop"),
            (r'(size)(\s+)(\d+)', bygroups(Keyword.Type, Text, Number)),
            (r'(un)?signed', Keyword.Type),
            ('.', Text)
        ],
    }
