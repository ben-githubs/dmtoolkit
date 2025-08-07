from pathlib import Path

from dmtoolkit.util import normalize_name
from dmtoolkit.api.models import Item
from dmtoolkit.api.serialize import load_json

DATADIR = Path(__file__).parent / "data"
ITEM_DATA_PATH = DATADIR / "items.json"

ITEMS: dict[str, Item] = {}

def _load_items():
    global ITEMS
    with ITEM_DATA_PATH.open("r") as f:
        item_objects: list[Item] = load_json(f)
        ITEMS = {}
        for item in item_objects:
            item_name = normalize_name(item.name)
            item_source = item.source[0].lower()
            ITEMS[item_name] = item
            ITEMS[f"{item_name}|{item_source}"] = item


def list_items() -> list[Item]:
    """Returns a list if all item objects."""
    return list(set(ITEMS.values()))


def get_item(name: str) -> Item:
    norm_name = normalize_name(name)
    # If the key also has the source, we need to normalize differently
    if "|" in name:
        norm_name = "|".join(normalize_name(part) for part in name.split("|"))
    try:
        return ITEMS[norm_name]
    except:
        print("\t".join(ITEMS.keys()))
        print(norm_name)

# Make sure we load the items dict at least once on load
if not ITEMS:
    _load_items()