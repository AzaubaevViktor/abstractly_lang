import operator

from .base import parser_parser
from ..op_generators import generate_operation_2
from .base import ParserPriority

or_parser = generate_operation_2(
    parser_parser,
    {
        "|": operator.or_
    },
    ParserPriority(10)
)
