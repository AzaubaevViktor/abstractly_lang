from typing import Any


def exec_ret(line: str) -> Any:
    _var = {'x': None}
    exec(f"_var['x'] = ({line})", {'_var': _var})
    return _var['x']