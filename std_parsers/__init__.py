
import std_parsers.common
from .numbers import number_expressions
from .system import system_expressions
from .comment import comment_parser
from .parser import parser_parser, use_priority_parser

parser_parser |= use_priority_parser(number_expressions)
