import json
from typing import Any


def dumps(data: Any, *, ensure_ascii: bool = False, indent: int = 2) -> str:
    """Encode *data* to a JSON ``str`` with sensible defaults."""
    return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)


def loads(data: str) -> Any:
    """Decode *data* from a JSON ``str``."""
    return json.loads(data)
