import operator

from .base import parser_parser
from ..op_generators import generate_operation_2
from .base import ParserPriority

and_parser = generate_operation_2(
    parser_parser,
    {
        "&": operator.and_
    },
    ParserPriority(20)
)
