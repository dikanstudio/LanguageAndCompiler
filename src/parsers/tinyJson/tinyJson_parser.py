from parsers.common import *

type Json = str | int | dict[str, Json]

def ruleJson(toks: TokenStream) -> Json:
    """
    Parses a JSON object, a JSON string, or a JSON number.
    """
    t = toks.next()
    match t.type:
        case 'STRING':
            print('STRING')
            # return without first and last element
            return t.value[1:-1]
        case 'INT':
            print('INT')
            print('t.value:', t.value)
            return int(t.value)
        case 'LBRACE':
            print('LBRACE')
            dictTemp = ruleEntryList(toks)
            toks.ensureNext('RBRACE')
            return dictTemp
        case 'COLON':
            toks.next()
            return ruleJson(toks)
        case 'RBRACE':
            toks.next()
            return ruleJson(toks)
        case _:
            raise ParseError(f'Unexpected token {t}')

def ruleEntryList(toks: TokenStream) -> dict[str, Json]:
    """
    Parses the content of a JSON object.
    """
    # {"k1": 1}
    t = toks.lookahead()
    match t.type:
        case 'STRING':
            print('STRING')
            key = t.value[1:-1]
            toks.next()
            toks.ensureNext('COLON')
            value = ruleJson(toks)
            a = {key : value}
            if toks.lookahead().type == "COMMA":
                toks.next()
                return {**a, **ruleEntryList(toks)}
                # TODO
                # if there are more entryies
            #    return {key: value}
            # print dict
            print({key: value})
            # return dict containing key-value pair
            return {key: value}
        case _:
            return {}

def parse(code: str) -> Json:
    parser = mkLexer("./src/parsers/tinyJson/tinyJson_grammar.lark")
    tokens = list(parser.lex(code))
    log.info(f'Tokens: {tokens}')
    toks = TokenStream(tokens)
    res = ruleJson(toks)
    toks.ensureEof(code)
    return res
