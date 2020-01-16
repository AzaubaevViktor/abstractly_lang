import operator

from .base import parser_parser

from .empty_parser import empty_parser
from ..variable import use_variables, variables, add_variable_op

parser_parser |= empty_parser

from .char_parser import char_parser

parser_parser |= char_parser

from .or_parser import or_parser

parser_parser |= or_parser

from .and_parser import and_parser

parser_parser |= and_parser

from .key_argument import use_key_argument

parser_parser |= use_key_argument(parser_parser)

from .func_parser import use_func_parser

parser_parser |= use_func_parser(parser_parser)

# Braces

from ..braces import use_braces

parser_parser |= use_braces(parser_parser)

# Variables

parser_parser |= use_variables('@parser', parser_parser)

# |=

parser_parser |= add_variable_op(parser_parser, "|=", operator.ior)

__all__ = ("parser_parser", )
