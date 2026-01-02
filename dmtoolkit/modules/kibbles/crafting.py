from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum, auto
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any

from dmtoolkit.modules.kibbles.loot import ItemWrapper
from dmtoolkit.api.items import Item, get_item

_RECIPES: dict[Item, list[Recipe]] = defaultdict(list)

class CraftingType(StrEnum):
    Alchemy = auto()
    Poisoncraft = auto()
    Blacksmithing = auto()
    Cooking = auto()
    Enchanting = auto()
    Scrollscribing = auto()
    WandWhittling = "wand_whittling"

@dataclass
class Recipe:
    crafting_type: CraftingType
    result: Item
    materials: list[ItemWrapper|str]
    dc: int
    num_checks: int
    crafting_time: str = ""
    note: str = ""
    quantity: int = 1

    @staticmethod
    def from_spec(spec: dict[str, Any]) -> Recipe:
        result = get_item(spec["result"])
        if not result:
            raise ValueError(f"Unknown item: {spec["result"]}")
        materials = []
        for material in spec["materials"]:
            if isinstance(material, str):
                quantity = 1
            else:
                quantity, material = material
            item = get_item(material)
            if item:
                materials.append(ItemWrapper(item, quantity))
            else:
                materials.append(f"{str(quantity) + ' x ' if quantity != 1 else ''}{material}")

        kwargs = {}
        for optarg in ("quantity", "note"):
            if val := spec.get(optarg):
                kwargs[optarg] = val

        recipe = Recipe(
            crafting_type = CraftingType(spec["craft"]),
            result = result,
            materials = materials,
            dc = spec["dc"],
            num_checks = spec["num_checks"],
            crafting_time = spec["time"],
            **kwargs
        )
        
        global _RECIPES
        _RECIPES[recipe.result].append(recipe)

        return recipe


def list_recipes() -> MappingProxyType[Item, list[Recipe]]:
    """Get a mapping of all recipes to their resulting item."""
    # Lazy-Load all recipes
    if not _RECIPES:
        with (Path(__file__).parent / "recipes.json").open("r") as f:
            for recipe in json.load(f):
                Recipe.from_spec(recipe)
    return MappingProxyType(_RECIPES)


def get_recipe(item: Item) -> list[Recipe]:
    """Return all recipes known for a given item, if there are any."""
    return list_recipes().get(item, [])