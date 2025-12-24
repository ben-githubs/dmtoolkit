from __future__ import annotations

from types import MappingProxyType

from flask import current_app as app

from dmtoolkit.modules.models import Module
from dmtoolkit.modules.kibbles import kcg_module

_MODULES: dict[str, Module] = {}

def get_modules() -> MappingProxyType[str, Module]:
    return MappingProxyType(_MODULES)


def flatten_modules(module_names: list[str]) -> Module:
    """Given a list of module names, returns a single module object, where the functions for each 
    hook are the first module in the list to override them."""
    module = Module("__temp__", "", "")

    for module_name in module_names:
        _module = _MODULES.get(module_name)
        if not _module:
            app.logger.warning("Unable to find module with name %s", module_name)
            continue
        if _module.generate_loot and not module.generate_loot:
            module.register_loot_generator(_module.generate_loot)
    
    return module

def register_module(module: Module):
    global _MODULES
    if not _MODULES:
        _MODULES[module.module_id] = module

# REGISTER MODULES
register_module(kcg_module)