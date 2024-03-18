from prettyprinter import doc
from prettyprinter import doctypes
from prettyprinter import render
from prettyprinter import layout
from prettyprinter import syntax
from typing import Iterable

type Doc = doc.Doc

LPAREN = doc.annotate(syntax.Token.PUNCTUATION, '(')
RPAREN = doc.annotate(syntax.Token.PUNCTUATION, ')')

def strDoc(s: str) -> Doc:
    return doc.annotate(syntax.Token.NAME_BUILTIN, s)

def enclose(l: Doc, r: Doc, x: Doc) -> Doc:
    return doc.concat([l, x, r])

def concat(ds: Iterable[Doc]) -> Doc:
    return doc.concat(ds)

def vsep(docs: list[Doc]) -> Doc:
    return doc.concat(intersperse(doctypes.LINE, docs))

def sep(docs: list[Doc]) -> Doc:
    return doc.group(vsep(docs))

def intersperse(sep: Doc, ys: list[Doc]) -> list[Doc]:
    l = []
    for i, y in enumerate(ys):
        l.append(y)
        if i < len(ys) - 1:
            l.append(sep)
    return l

def align(d: Doc) -> Doc:
    return doc.align(d)

def indent(d: Doc) -> Doc:
    return doc.nest(2, d)

def renderDoc(d: Doc) -> str:
    return render.default_render_to_str(layout.layout_smart(d))
