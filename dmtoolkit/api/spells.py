from pathlib import Path

from dmtoolkit.util import normalize_name
from dmtoolkit.api.models import Spell
from dmtoolkit.api.serialize import load_json

DATADIR = Path(__file__).parent / "data"
SPELL_DATA_PATH = DATADIR / "spells.json"

SPELLS: dict[str, Spell] = {}

def _load_spells():
    global SPELLS
    with SPELL_DATA_PATH.open("r") as f:
        SPELLS = {normalize_name(c.name): c for c in load_json(f)}


def list_spells() -> list[Spell]:
    """Returns a list if all spell objects."""
    return list(SPELLS.values())


def get_spell(name: str) -> Spell:
    return SPELLS[normalize_name(name)]

# Make sure we load the spells dict at least once on load
if not SPELLS:
    _load_spells()