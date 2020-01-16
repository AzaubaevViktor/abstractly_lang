from parser import CharParser
from .common import all_symbol

comment_parser = CharParser("#") & all_symbol[:]
