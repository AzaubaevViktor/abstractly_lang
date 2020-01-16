

from .base import parser_parser

from .empty_parser import empty_parser
from ..variable import use_variables

parser_parser |= empty_parser

from .char_parser import char_parser

parser_parser |= char_parser

from .or_parser import or_parser

parser_parser |= or_parser

parser_parser |= use_variables('@parser', parser_parser)

__all__ = ("parser_parser", )
