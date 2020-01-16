import math

from parser import CharParser, KeyArgument, FuncParser
from std_parsers import number_expressions
from std_parsers.common import spaces


def test_vars(a):
    assert a("@spaces") == spaces
    assert a("__") == spaces
    # TODO: Fix MultiParser.__eq__
    assert hash(a("@number")) == hash(number_expressions)


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
    a("__test_func = a:@number => @factorial(a)")
    p = a("__test_func")
    assert isinstance(p, FuncParser)

    assert p.parser == KeyArgument('a', number_expressions)

    a("@ = __test_func")
    assert a("10") == math.factorial(10)
