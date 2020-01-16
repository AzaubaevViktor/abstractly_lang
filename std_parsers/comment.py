from parser import CharParser
from .common import all_symbol, spaces

comment_parser = spaces & CharParser("#") & all_symbol[:]
