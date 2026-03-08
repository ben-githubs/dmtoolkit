from pathlib import Path

from dmtoolkit.util import normalize_name
from dmtoolkit.api.models import Spell
from dmtoolkit.api.serialize import load_json

DATADIR = Path(__file__).parent / "data"
SPELL_DATA_PATH = DATADIR / "spells.json"

SPELLS: dict[str, Spell] = {}
SPELLS_2024: dict[str, Spell] = {}

def _load_spells():
    global SPELLS
    with SPELL_DATA_PATH.open("r") as f:
        spells: list[Spell] = load_json(f)
        for spell in spells:
            normalized_name = normalize_name(spell.name)
            if spell.is_2024:
                SPELLS_2024[normalized_name] = spell
            elif spell.has_2024:
                SPELLS[normalized_name] = spell
            else:
                SPELLS[normalized_name] = spell
                SPELLS_2024[normalized_name] = spell


def _get_spell_list(use_2024_content: bool = False) -> dict[str, Spell]:
    return SPELLS_2024 if use_2024_content else SPELLS


def list_spells(use_2024_content: bool = False) -> list[Spell]:
    """Returns a list if all spell objects."""
    return list(_get_spell_list(use_2024_content).values())


def get_spell(name: str, use_2024_content: bool = False) -> Spell:
    return _get_spell_list(use_2024_content)[normalize_name(name)]

# Make sure we load the spells dict at least once on load
if not SPELLS:
    _load_spells()