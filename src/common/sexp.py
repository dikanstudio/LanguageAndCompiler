from __future__ import annotations
from dataclasses import dataclass
import common.pretty as pretty
from typing import *
import json

type RenderResult = pretty.Doc

@dataclass(frozen=True)
class SExpNum:
    val: int | float
    def render(self) -> RenderResult:
        return pretty.strDoc(str(self.val))

@dataclass(frozen=True)
class SExpStr:
    val: str
    def render(self) -> RenderResult:
        return pretty.strDoc(json.dumps(self.val))

@dataclass(frozen=True)
class SExpId:
    id: str
    def render(self) -> RenderResult:
        return pretty.strDoc(self.id)

@dataclass(frozen=True)
class SExpSeq:
    sexps: list[SExp]
    def append(self, other: SExpSeq | Iterable[SExp]) -> SExpSeq:
        if isinstance(other, SExpSeq):
            other = other.sexps
        return SExpSeq(self.sexps + list(other))
    def render(self) -> RenderResult:
        l = [x.render() for x in self.sexps]
        return pretty.enclose(pretty.LPAREN, pretty.RPAREN, pretty.align(pretty.sep(l)))

@dataclass(frozen=True)
class SExpBlockItem:
    start: str
    sexps: list[SExp]
    def render(self) -> pretty.Doc:
        l = [x.render() for x in self.sexps]
        return pretty.sep([pretty.strDoc(self.start),
                           pretty.indent(pretty.align(pretty.sep(l)))])

@dataclass(frozen=True)
class SExpBlock:
    content: list[SExpBlockItem]
    @staticmethod
    def singleItem(start: str, sexps: list[SExp]) -> SExpBlock:
        return SExpBlock([SExpBlockItem(start, sexps)])
    def render(self) -> RenderResult:
        return pretty.sep([x.render() for x in self.content] + [pretty.strDoc('end')])

type SExp = SExpNum | SExpStr | SExpId | SExpSeq | SExpBlock

def renderSExp(s: SExp) -> str:
    d = s.render()
    return pretty.renderDoc(d)

def mkSeq(*es: SExp) -> SExpSeq:
    return SExpSeq(list(es))

def mkNamedSeq(i: str, *es: SExp) -> SExpSeq:
    return mkSeq(SExpId(i), *es)
