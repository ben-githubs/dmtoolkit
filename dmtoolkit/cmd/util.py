from collections.abc import Sequence
from typing import Any

def listify(item: Any) -> list:
    """Return item wrapped in a list. If item is already a list, return it unchanged."""
    if isinstance(item, Sequence) and not isinstance(item, str):
        return item
    return [item]