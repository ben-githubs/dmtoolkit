"""Looting logic for Kibble's Crafting Guide."""
from __future__ import annotations

from collections import defaultdict
import csv
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from random import randint, choice
from typing import Any

from d20 import roll

from dmtoolkit.api.models import Monster, Item, KibblesIngredient
from dmtoolkit.api.items import get_item, list_items
from dmtoolkit.util import get_logger
from dmtoolkit.modules.models import LootResponse, ItemWrapper

log = get_logger(__name__)

LOOT_TABLE_DIR = Path(__file__).parent / "loot_tables"

class Locales(StrEnum):
    FOREST = "forest"
    DESERT = "desert"
    GRASSLAND = "grassland"
    MARSH = "marsh"
    MOUNTAINS = "mountains"
    CAVES = "caves"
    UNDERGROUND = "underground"
    JUNGLE = "jungle"
    COASTAL = "coastal"
    ARCTIC = "arctic"

class RangeDict:
    """Really quick way to represent non-overlapping ranges."""
    def __init__(self, spec: list[tuple[Any, Any, Any]]):
        self.spec = spec
    
    def __getitem__(self, index: Any) -> Any:
        for lbound, rbound, item in self.spec:
            if lbound <= index <= rbound:
                return item
        raise IndexError

@dataclass
class ItemSlot:
    item: Item
    quantity: int


def _resolve(value: int | str) -> int:
    """If 'value' is a dice expression, resolves it, otherwise returns the integer."""
    if isinstance(value, str):
        return roll(value).total
    else:
        return value


def gather(locale: Locales) -> LootResponse:
    results = gathering_tables[locale].roll()
    
    dc = 10 # Default DC
    if locale in (Locales.CAVES, Locales.UNDERGROUND, Locales.JUNGLE, Locales.COASTAL, Locales.ARCTIC):
        dc = 12

    return LootResponse(
        items = [ItemWrapper(r[0], r[1]) for r in results],
        coinage = 0,
        note = f"requires DC {dc} Wisdom (Herbalism kit) check."
    )


def loot(monster: Monster) -> LootResponse:
    """Top-level looting function. Call this on any arbitrary Monster."""
    match monster.maintype.lower():
        case "aberration" | "beast" | "dragon" | "giant" | "monstrosity" | "plant":
            return loot_harvest(monster)
        case "elemental" | "celestial" | "fiend":
            return loot_remnants(monster)
        case "undead":
            # Undead either leave remnants (if they are incorporeal) or regular harvestable items
            if any("incorporeal" in entry.title.lower() for entry in monster.traits or []):
                return loot_remnants(monster)
            else:
                return loot_harvest(monster)
        case "humanoid":
            return loot_humanoid(monster)
        case _:
            return LootResponse([], loot_coinage(monster))



def loot_harvest(monster: Monster) -> LootResponse:
    table: LootTable = {
        "aberration": aberration_loot_tables,
        "dragon": dragon_giant_monstrosity_loot_tables,
        "giant": dragon_giant_monstrosity_loot_tables,
        "monstrosity": dragon_giant_monstrosity_loot_tables,
        "plant": plant_loot_tables,
        "undead": undead_loot_tables
    }[monster.maintype][monster.cr_num]

    # Get harvest DC
    dc = RangeDict([
        (0, 4, 8),
        (5, 10, 10),
        (11, 16, 12),
        (17, 99, 15)
    ])[monster.cr_num]

    # Get skill check type
    skill = {
        "undead": "Intelligence (Arcana)",
        "plant": "Intelligence (Nature)",
        "construct": "Intelligence (Arcana)"
    }.get(monster.maintype, "Wisdom (Medicine)")

    # Roll Table
    results = table.roll()

    note = f"requires DC {dc} {skill} check and takes 10 minutes"
    coinage = sum([item.value for item, _ in results if isinstance(item, Coinage)])
    items = [ItemWrapper(item, quantity) for item, quantity in results if not isinstance(item, Coinage)]

    return LootResponse(items, coinage, note)


def loot_remnants(monster: Monster):
    table: LootTable = {
        "celestial": celestial_loot_tables,
        "fiend": fiend_loot_tables,
        "elemental": elemental_loot_tables,
        "undead": incorporeal_undead_loot_tables
    }[monster.maintype][monster.cr_num]

    results = table.roll()

    return LootResponse([ItemWrapper(item, quantity) for item, quantity in results], 0, "Takes 1 minute")


def loot_humanoid(monster: Monster) -> LootResponse:
    loot_table = humanoid_loot_tables[monster.cr_num]
    results = loot_table.roll()

    items = [ItemWrapper(item, quantity) for item, quantity in results]
    coinage = sum([item.value for item, _ in results if isinstance(item, Coinage)])
    return LootResponse(items, coinage)


def loot_coinage(monster: Monster) -> int:
    """Default loot for cases where we cannot determine an appropriate looting table. Just assigns 
    coinage based on the CR of the creature."""
    return monster.xp * 100


def get_gathering_variant(locale: Locales, item: Item) -> Item:
    """Given a generic item (like 'Common Reactive Reagent') and a locale, returns a variant Item
    specific to the locale itself."""
    global gathering_variants
    # Lazy-load variants
    if not gathering_variants:
        for item in list_items():
            if not isinstance(item, KibblesIngredient):
                continue
            for locale_name in item.locales:
                for property in item.properties:
                    gathering_variants[Locales(locale_name)][item.rarity][property].append(item)
    
    # Fetch random replacement
    if item.properties:
        print(gathering_variants[locale][item.rarity][item.properties[0]])
        if sample_list := gathering_variants[locale][item.rarity][item.properties[0]]:
            return choice(sample_list)
    
    return item # Return original generic item if there is no replacement



class LootItem:
    """Represents an item on a loot table. Can be called to return another callable, which returns 
    a random amount of the item."""
    def __init__(self, item: Item | str, quantity: int | str = 1):
        self.item = item
        self.quantity = quantity
    
    def __call__(self,) -> tuple[Item, int]:
        quantity = _resolve(self.quantity)
        if isinstance(self.item, str):
            if "|" not in self.item:
                self.item += "|kcg" # Look for kibbles items by default, over other modules
            item = get_item(self.item)
            if item is None:
                raise KeyError(f"Unknown item: {self.item}")
            else:
                self.item = item
        return (self.item, quantity)


class Coinage(Item):
    def __init__(self, cp: int = 0, sp: int = 0, gp: int = 0, pp: int = 0):
        self.value = cp + 10*sp + 100*gp + 1000*pp
    
    def id(self):
        return "__coinage__"
    
    def __add__(self, other):
        if isinstance(other, int):
            return Coinage(cp=self.value + other)
        elif isinstance(other, Coinage):
            return Coinage(cp=self.value + other.value)
        else:
            raise TypeError(f"Cannot add instance of '{type(other).__name__}' to instance of Coinage.")
    
    def __sub__(self, other):
        if isinstance(other, Coinage):
            return self + (-1*other.value)
        else:
            return self + (-1*other)

    def __str__(self):
        gp = self.value // 100
        sp = self.value % 100 // 10
        cp = self.value % 10

        str_parts = []
        if gp != 0:
            str_parts.append(f"{gp} GP")
        if sp != 0:
            str_parts.append(f"{sp} SP")
        if cp != 0:
            str_parts.append(f"{cp} CP")
        if not str_parts:
            return "0 GP"
        if len(str_parts) == 1:
            return str_parts[0]
        elif len(str_parts) == 2:
            return " and ".join(str_parts)
        else:
            return ", ".join(str_parts[:-1]) + ", and " + str_parts[-1]


class LootCoins(LootItem):
    """Represents a random or fixed amount of coinage."""
    def __init__(self, cp: int | str = 0, sp: int | str = 0, gp: int | str = 0):
        self.cp = cp
        self.sp = sp
        self.gp = gp
    
    def __call__(self) -> tuple[Coinage, int]:
        return (Coinage(
            cp = _resolve(self.cp),
            sp = _resolve(self.sp),
            gp = _resolve(self.gp)
        ), 1)


class LootTable:
    """Represents a table which can be rolled from, like the ones found in various D&D source
    books. Each row has a range, and if the value randomly determined from the dice falls within 
    that range, the row is returned. This class supports returning multiple rows, (i.e. allows rows
    to have overlapping ranges) if you want that for some reason."""

    def __init__(self, size: int):
        self.rows: list[tuple[int, int, LootItem]] = []
        self.size = size
    
    def add_row(self, min: int, max: int, row: LootItem):
        """Add a new row to the table."""
        if min < 1:
            raise ValueError(f"'min' must be 1 or higher; got '{min}'.")
        if max > self.size:
            raise ValueError(f"'max' cannot exceed '{self.size}' for this table; got '{max}'.")
        self.rows.append((min, max, row))
    
    def roll(self) -> list[tuple[Item, int]]:
        """Return a list of items (and their quantites) chosen randomly from the table."""
        x = randint(1, self.size)
        # We collect items in a default dict, so that if two rows have the same items, the output
        #   is one row for that item with their combined quantities.
        itemdict: dict[str, int] = defaultdict(lambda: 0)
        items: dict[str, Item] = {}
        # We are not doing this efficiently, but it should be fine
        for xmin, xmax, lootitem in self.rows:
            if xmin <= x <= xmax:
                item, quantity = lootitem()
                itemdict[item.id()] += quantity
                items[item.id()] = item
        return [(items[item], quantity) for item, quantity in itemdict.items()]

    @staticmethod
    def load_from_csv(fname: Path) -> LootTable:
        csvrows = []
        with fname.open("r") as f:
            reader = csv.DictReader(f)
            csvrows = [row for row in reader]
        max_value = max(int(row["max"]) for row in csvrows)
        table = LootTable(max_value)
        idx = 0
        for row in csvrows:
            try:
                x1, x2, item, amt, gp, sp, cp = row["min"], row["max"], row["item"], row["amt"], row["gp"], row["sp"], row["cp"]
                if item:
                    loot_item = LootItem(item, amt)
                    table.add_row(int(x1), int(x2), loot_item)
                if gp or sp or cp:
                    gp = int(gp) if gp.isdigit() else gp or 0
                    sp = int(sp) if sp.isdigit() else sp or 0
                    cp = int(cp) if cp.isdigit() else cp or 0
                    table.add_row(int(x1), int(x2), LootCoins(cp=cp, sp=sp, gp=gp))
            except Exception as e:
                log.error(f"Unable to create row for '{csvrows[idx]}': {e}")
            idx += 1

        return table

humanoid_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "humanoid_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "humanoid_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "humanoid_cr_5_10.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "humanoid_cr_5_10.csv"))
])

dragon_giant_monstrosity_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "dragon_giant_monstrosity_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "dragon_giant_monstrosity_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "dragon_giant_monstrosity_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "dragon_giant_monstrosity_cr_17+.csv")),
])

construct_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "construct_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "construct_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "construct_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "construct_cr_17+.csv")),
])

aberration_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "aberration_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "aberration_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "aberration_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "aberration_cr_17+.csv")),
])

undead_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "undead_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "undead_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "undead_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "undead_cr_17+.csv")),
])

plant_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "plant_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "plant_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "plant_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "plant_cr_17+.csv")),
])

celestial_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "celestial_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "celestial_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "celestial_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "celestial_cr_17+.csv")),
])

fiend_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "fiend_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "fiend_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "fiend_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "fiend_cr_17+.csv")),
])

elemental_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "elemental_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "elemental_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "elemental_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "elemental_cr_17+.csv")),
])

incorporeal_undead_loot_tables = RangeDict([
    (0, 4, LootTable.load_from_csv(LOOT_TABLE_DIR / "incorporeal_undead_cr_0_4.csv")),
    (5, 10, LootTable.load_from_csv(LOOT_TABLE_DIR / "incorporeal_undead_cr_5_10.csv")),
    (11, 16, LootTable.load_from_csv(LOOT_TABLE_DIR / "incorporeal_undead_cr_11_16.csv")),
    (17, 99, LootTable.load_from_csv(LOOT_TABLE_DIR / "incorporeal_undead_cr_17+.csv")),
])

gathering_tables = {enum: LootTable.load_from_csv(LOOT_TABLE_DIR / f"gathering_{enum}.csv") for enum in Locales}
gathering_variants: dict[str, dict[str, dict[str, list[Item]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))