from typing import Any


def stringify(v:dict[str, Any]) -> dict[str, str]:
    for key,value in v.items():
        if not isinstance(value, str):
            v[key] = str(value)
    return v