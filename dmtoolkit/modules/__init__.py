from __future__ import annotations

from types import MappingProxyType
from typing import Callable, Optional

from dmtoolkit.api.models import Monster
from dmtoolkit.modules.models import LootResponse

_MODULES: dict[str, Module] = {}

def get_modules() -> MappingProxyType[str, Module]:
    return MappingProxyType(_MODULES)


class Module:
    """Provides a framework modules can use to define their various functionalities."""
    def __init__(self, name: str):
        self.name = name
        self.generate_loot: Optional[Callable[[Monster], LootResponse]] = None
    

    def register_loot_generator(self, func: Callable[[Monster], LootResponse]) -> None:
        self.generate_loot = func
