from __future__ import annotations

from types import MappingProxyType
from typing import Callable, Optional

from flask import current_app as app

from dmtoolkit.api.models import Monster
from dmtoolkit.modules.models import LootResponse

_MODULES: dict[str, Module] = {}

def get_modules() -> MappingProxyType[str, Module]:
    return MappingProxyType(_MODULES)


def flatten_modules(module_names: list[str]) -> Module:
    """Given a list of module names, returns a single module object, where the functions for each 
    hook are the first module in the list to override them."""
    module = Module("__temp__")

    for module_name in module_names:
        _module = _MODULES.get(module_name)
        if not _module:
            app.logger.warning("Unable to find module with name %s", module_name)
            continue
        if _module.generate_loot and not module.generate_loot:
            module.register_loot_generator(_module.generate_loot)
    
    return module


class Module:
    """Provides a framework modules can use to define their various functionalities."""
    def __init__(self, name: str):
        self.name = name
        self.generate_loot: Optional[Callable[[Monster], LootResponse]] = None
    

    def register_loot_generator(self, func: Callable[[Monster], LootResponse]) -> None:
        self.generate_loot = func
