from pathlib import Path

from dmtoolkit.util import normalize_name, get_logger
from dmtoolkit.api.models import Item
from dmtoolkit.api.serialize import load_json

log = get_logger(__name__)

DATADIR = Path(__file__).parent / "data"
KIBBLES_DIR = DATADIR.parent.parent / "modules/kibbles/"
ITEM_DATA_PATHS = (
    DATADIR / "items.json",
    KIBBLES_DIR / "items.json",
    KIBBLES_DIR / "ingredients.json",
    KIBBLES_DIR / "variants.json",
)

ITEMS: dict[str, Item] = {}

def _load_items():
    global ITEMS
    ITEMS = {}
    for ITEM_DATA_PATH in ITEM_DATA_PATHS:
        with ITEM_DATA_PATH.open("r") as f:
            try:
                item_objects: list[Item] = load_json(f)
            except Exception as e:
                log.error(f"Unable to load items from {ITEM_DATA_PATH}: {e}")
                raise e
            for item in item_objects:
                item_name = normalize_name(item.name)
                item_source = item.source[0].lower()
                ITEMS[item_name] = item
                ITEMS[f"{item_name}|{item_source}"] = item


def list_items() -> list[Item]:
    """Returns a list if all item objects."""
    return list(set(ITEMS.values()))


def get_item(name: str) -> Item | None:
    norm_name = normalize_name(name)
    # If the key also has the source, we need to normalize differently
    if "|" in name:
        norm_name = "|".join(normalize_name(part) for part in name.split("|")[:2])
    try:
        return ITEMS[norm_name]
    except:
        log.warning(f"Unable to find item {norm_name}")

# Make sure we load the items dict at least once on load
if not ITEMS:
    _load_items()