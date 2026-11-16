"""Minimal S-expression reader/writer for KiCad files."""


class Sym(str):
    """Bare (unquoted) atom."""
    __slots__ = ()


def parse(text):
    pos = 0
    n = len(text)
    stack = [[]]
    while pos < n:
        c = text[pos]
        if c in " \t\r\n":
            pos += 1
        elif c == "(":
            new = []
            stack[-1].append(new)
            stack.append(new)
            pos += 1
        elif c == ")":
            stack.pop()
            pos += 1
        elif c == '"':
            pos += 1
            buf = []
            while text[pos] != '"':
                if text[pos] == "\\":
                    pos += 1
                    e = text[pos]
                    buf.append({"n": "\n", "t": "\t", "r": "\r"}.get(e, e))
                else:
                    buf.append(text[pos])
                pos += 1
            pos += 1
            stack[-1].append("".join(buf))
        else:
            start = pos
            while pos < n and text[pos] not in " \t\r\n()":
                pos += 1
            stack[-1].append(Sym(text[start:pos]))
    return stack[0][0]


def _atom(a):
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, str):
        return '"' + a.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(a, bool):
        return "yes" if a else "no"
    if isinstance(a, float):
        s = f"{a:.4f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return str(a)


def dump(x, indent=0):
    if not isinstance(x, list):
        return _atom(x)
    flat = "(" + " ".join(dump(i) for i in x) + ")"
    if len(flat) < 100 or not any(isinstance(i, list) for i in x):
        return flat
    pad = "\t" * (indent + 1)
    out = ["(" + _atom(x[0])]
    for i in x[1:]:
        if isinstance(i, list):
            out.append("\n" + pad + dump(i, indent + 1))
        else:
            out.append(" " + _atom(i))
    out.append("\n" + "\t" * indent + ")")
    return "".join(out)


def find(x, key):
    for i in x:
        if isinstance(i, list) and i and i[0] == key:
            return i
    return None


def findall(x, key):
    return [i for i in x if isinstance(i, list) and i and i[0] == key]


def S(*a):
    """Build a list whose head is a bare symbol."""
    return [Sym(a[0])] + list(a[1:])
