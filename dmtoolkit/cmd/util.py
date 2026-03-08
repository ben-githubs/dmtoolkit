from collections.abc import Sequence
from typing import Any

from dmtoolkit.api.models import Model

NEW_2024_SOURCES = {
    "XPHB",
    "XDMG",
    "XMM"
}

def listify(item: Any) -> list:
    """Return item wrapped in a list. If item is already a list, return it unchanged."""
    if isinstance(item, Sequence) and not isinstance(item, str):
        return item
    return [item]

def mark_2024(items: list[Model]):
    """Iterates through the list and marks items as either being 2024, or having a 2024 version."""
    for item in items:
        if item.source in NEW_2024_SOURCES:
            item.is_2024 = True
        if any(key.split("-")[-1] in NEW_2024_SOURCES for key in item.reprinted_as):
            item.has_2024 = True
