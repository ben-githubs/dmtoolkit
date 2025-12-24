from pathlib import Path

import pytest

from dmtoolkit.api.items import get_item
from dmtoolkit.api.models import Item
import dmtoolkit.modules.kibbles.loot as loot

LOOT_TABLE_DIR = Path(__file__).parent.parent.parent.parent / "dmtoolkit/modules/kibbles/loot_tables"

def test_item_registering():
    """Tests if the Kibbles items got added to the register. Does a quick spot check, not exhaustive."""
    assert get_item("Draught of Damnation|KCG") is not None

def test_ingredient_registering():
    """Tests if the Kibbles ingredients got added to the register. Does a quick spot check, not exhaustive."""
    assert get_item("Common Arcane Essence|KCG") is not None

def test_loot_item_init():
    """Tests if the LootItem object works."""
    loot.LootItem("fancy parts")

def test_loot_item_call_single():
    """Tests if the LootItem object works using the default input."""
    loot_item = loot.LootItem("fancy parts")
    item, quantity = loot_item()
    assert quantity == 1 # The quantity should be 1 by default
    assert isinstance(item, Item) # Ensure an Item object is returned
    assert item.name.lower() == "fancy parts" # Make sure it's the right item

def test_loot_item_call_many():
    """Tests if the LootItem object returns multiple values when fiven an integer quantity that is
    greater than 1."""
    QUANTITY = 5
    loot_item = loot.LootItem("fancy parts", QUANTITY)
    item, quantity = loot_item()
    assert quantity == QUANTITY # The quantity should beexactly as specified
    assert isinstance(item, Item) # Ensure an Item object is returned
    assert item.name.lower() == "fancy parts" # Make sure it's the right item

def test_loot_item_call_expr():
    """Tests if the LootItem object works when given an expression."""
    loot_item = loot.LootItem("fancy parts", "2d6")
    item, quantity = loot_item()
    assert 2 <= quantity <= 12 # The quantity should be in this range
    assert isinstance(item, Item) # Ensure an Item object is returned
    assert item.name.lower() == "fancy parts" # Make sure it's the right item

def test_loot_item_call_expr_randomness():
    """Tests if the LootItem object returns ransodm results when given an expression."""
    loot_item = loot.LootItem("fancy parts", "2d6")
    results = set()
    for _ in range(100):
        _, quantity = loot_item()
        results.add(quantity)
    assert len(results) > 1 # We should get more than 1 answer after rolling 100 times, I hope

def test_coin_loot():
    """Tests that the coin loot works as expected."""
    coinage = loot.Coinage(cp=4, sp=8, gp=2)
    assert coinage.value == 284

@pytest.mark.parametrize(("values", "string"), (
    ({"cp": 1, "sp": 2, "gp": 3}, "3 GP, 2 SP, and 1 CP"),
    ({"cp": 6}, "6 CP"),
    ({"cp": 15}, "1 SP and 5 CP"),
    ({}, "0 GP"),
    ({"cp": -10}, "-1 GP and 9 SP")
))
def test_coin_string(values, string):
    """Tests that the stringification of the Coinage works as expected."""
    coinage = loot.Coinage(**values)
    assert str(coinage) == string

@pytest.mark.parametrize(("value", "expected_result"), (
    (loot.Coinage(cp=20), 130),
    (50, 160)
))
def test_adding_coins(value, expected_result):
    """Tests that you can add two Coinage values together."""
    result = loot.Coinage(cp=110) + value
    assert isinstance(result, loot.Coinage)
    assert result.value == expected_result

@pytest.mark.parametrize(("value", "expected_result"), (
    (loot.Coinage(cp=20), 90),
    (50, 60)
))
def test_subtracting_coins(value, expected_result):
    """Tests that you can add two Coinage values together."""
    result = loot.Coinage(cp=110) - value
    assert isinstance(result, loot.Coinage)
    assert result.value == expected_result

def test_loot_coins():
    results = set()
    lc = loot.LootCoins(cp="6d10+10")
    for _ in range(100):
        coinage, quantity = lc()
        assert isinstance(coinage, loot.Coinage)
        assert quantity == 1 # All quantities for coinages should be 1, by convention
        assert 16 <= coinage.value <= 70 # #Ensure all answers are within the expected range
        results.add(coinage.value)
    assert len(results) > 1 # Ensure we got at least 2 distinct values from randomization

def test_loot_table():
    loot_table = loot.LootTable.load_from_csv(loot.LOOT_TABLE_DIR / "humanoid_cr_0_4.csv")
    result = loot_table.roll()
    assert isinstance(result, list)
    for idx, item in enumerate(result):
        assert isinstance(item, tuple), f"Error with item {idx}; expected 'tuple', got '{type(item).__name__}'"
        assert isinstance(item[0], Item), f"Error with item{idx}; expected 'Item', got '{type(item[0]).__name__}'"
        assert isinstance(item[1], int), f"Error with item{idx}; expected 'int', got '{type(item[1]).__name__}'"


def test_loot_table_dir_exists():
    """Ensures the loot table directory exists; if it doesn't, other tests might silently fail."""
    assert LOOT_TABLE_DIR.exists()
    assert LOOT_TABLE_DIR.is_dir()


@pytest.mark.parametrize(
        ("fname",),
        [(fname,) for fname in LOOT_TABLE_DIR.glob("*.csv")],
        ids = [fname.name for fname in LOOT_TABLE_DIR.glob("*.csv")])
def test_loot_table_contents(fname: Path):
    """Tests each loot table to make sure it loads properly and the entries are all real items."""
    loot_table = loot.LootTable.load_from_csv(fname)
    for _, _, item in loot_table.rows:
        item()