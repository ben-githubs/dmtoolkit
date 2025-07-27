from pathlib import Path

from dmtoolkit.api.models import Class
from dmtoolkit.api.serialize import load_json

DATADIR = Path(__file__).parent / "data"
CLASS_DATA_PATH = DATADIR / "classes.json"

CLASSES: dict[str, Class] = {}

def _load_classes():
    global CLASSES
    with CLASS_DATA_PATH.open("r") as f:
        CLASSES = {c.name: c for c in load_json(f)}


def list_classes() -> list[Class]:
    """Returns a list if all class objects."""
    return list(CLASSES.values())


def get_class(name: str) -> Class:
    return CLASSES[name]

# Make sure we load the classes dict at least once on load
if not CLASSES:
    _load_classes()