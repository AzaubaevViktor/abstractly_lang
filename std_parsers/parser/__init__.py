

from .base import parser_parser

from .empty_parser import empty_parser

parser_parser |= empty_parser

from .char_parser import char_parser

parser_parser |= char_parser

__all__ = ("parser_parser", )
