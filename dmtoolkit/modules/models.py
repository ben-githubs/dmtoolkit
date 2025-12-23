from __future__ import annotations

from dataclasses import dataclass

from dmtoolkit.api.models import Item


@dataclass
class LootResponse:
    """Common data model for loot."""
    items: list[ItemWrapper] # List of items to award
    coinage: int # Value of coinage, in CP
    note: str = "" # Note to be attached to the loot

    def __add__(self, other: LootResponse) -> LootResponse:
        # Combine item lists
        items: dict[tuple[Item, str], int] = {}
        for x in (self.items, other.items):
            for item_wrapper in x:
                key = (item_wrapper.item, item_wrapper.note)
                if items[key]:
                    items[key] += item_wrapper.quantity
                else:
                    items[key] = item_wrapper.quantity
        # Turn back into list
        items_list = [ItemWrapper(key[0], val, key[1]) for key, val in items.items()]

        # Make new note
        if self.note and other.note:
            note = f"{self.note}\n\n{other.note}"
        else:
            note = self.note or other.note or ""

        return LootResponse(items_list, self.coinage + other.coinage, note=note)

@dataclass
class ItemWrapper:
    """Common wrapper for items with notations"""
    item: Item
    quantity: int
    note: str = ""