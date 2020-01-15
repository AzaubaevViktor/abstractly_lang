from typing import Dict, Callable, Any, Optional

from parser import BasePriority, FuncParser, KeyArgument, DictParser, PriorityParser
from parser.base import BaseParser
from std_parsers.common import spaces


def generate_operation_2(
        base_expr: BaseParser,
        ops: Dict[str, Callable[[Any, Any], Any]],
        priority: Optional[BasePriority]
):
    # Создаёт операцию от двух переменных с оператором symbol

    def _func_wrapper(*args, a, op: Callable, b):
        return op(a, b)

    parser = FuncParser(
        KeyArgument('a', base_expr) & spaces
        & KeyArgument('op', DictParser(ops)) & spaces
        & KeyArgument('b', base_expr),
        _func_wrapper
    )
    if priority:
        parser = PriorityParser(parser, priority)

    return parser