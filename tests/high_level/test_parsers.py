import math

from parser import CharParser, KeyArgument, FuncParser, AndParser, PriorityParser
from std_parsers import number_expressions
from std_parsers.common import spaces
from std_parsers.numbers import NumberPriority


def test_vars(a):
    assert a("@spaces") == spaces
    assert a("__") == spaces
    assert a("@number") is number_expressions


def test_char_parser(a):
    assert a("`x`") == CharParser('x')


def test_str_parser(a):
    assert a("`xyz`") == CharParser.line('xyz')


def test_change_str_parser(a):
    assert a("`\\t`") == CharParser("\t")


def test_smile_parser(a):
    assert a("`^_^`") == CharParser.line('^_^')


def test_key_argument_parser(a):
    assert a("a:@number") == KeyArgument('a', number_expressions)


def test_and_parser(a):
    assert a("`x` & `y`") == CharParser('x') & CharParser('y')


def test_priority_parser(a):
    assert a("`x` | `y` & `z`") == CharParser('x') | CharParser('y') & CharParser('z')


def test_braces(a):
    assert a("(`x` | `y`) & `z`") == (CharParser('x') | CharParser('y')) & CharParser('z')


def test_ior_parser(a):
    a("__test_ior = `x` | `y`")
    assert a("__test_ior") == CharParser('x') | CharParser('y')

    a("__test_ior |= `z`")

    assert a("__test_ior") == CharParser('x') | CharParser('y') | CharParser('z')


def test_func_parser(a):
    a("__test_func = `^` & a:@number => @factorial(a)")
    p = a("__test_func")
    assert isinstance(p, FuncParser)

    assert p.parser == CharParser('^') & KeyArgument('a', number_expressions)

    a("@ |= __test_func")
    assert a("^10") == math.factorial(10)


def test_func_2_key_arg(a):
    ka2 = a("b:@number & a:@number")
    assert isinstance(ka2, AndParser)
    assert len(ka2.parsers) == 2
    for parser in ka2.parsers:
        assert isinstance(parser, KeyArgument)


def test_func2_parser(a):
    a("__test_func = a:@number & `^` & b:@number => a + b")
    p = a("__test_func")
    assert isinstance(p, FuncParser)

    # assert p.parser == KeyArgument('a', number_expressions) & CharParser('^') & KeyArgument('a', number_expressions)

    a("@ |= __test_func")
    assert a("2^5") == 7


def test_priority_parser_generate(a):
    a("aaa = [`x` / NumberPriority / 100]")
    p = a("aaa")

    assert isinstance(p, PriorityParser)
    assert isinstance(p.priority, NumberPriority)
    assert p.priority.priority == 100
    assert p.parser == CharParser('x')
