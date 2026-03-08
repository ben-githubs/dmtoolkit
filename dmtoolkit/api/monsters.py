from pathlib import Path

from dmtoolkit.api.models import Monster
from dmtoolkit.api.serialize import load_json

DEFAULT_MONSTERS_FILE = Path(__file__).parent / "data" / "monsters.json"
MONSTERS: dict[str, Monster] = {}

def get_monsters() -> dict[str, Monster]:
    """Returns the MONSTERS dict."""
    if not MONSTERS:
        with DEFAULT_MONSTERS_FILE.open("r") as f:
            monster_list: list[Monster] = load_json(f)
        for monster in monster_list:
            MONSTERS[monster.key] = monster
    
    return MONSTERS


def get_monster(key: str) -> Monster | None:
    """Fetch a specific monster by key. Returns 'None' if there is no monster with that key."""
    return get_monsters().get(key, None)


def get_monster_names(prefer_reprinted: bool = False) -> list[tuple[str, str]]:
    """Return a list of tuples containing the monster key and it's name.
    
    Args:
        prefer_reprinted (bool): If true, replaces any 5e statblocks with their 5.5e version, if possible.
    """
    namelist = []
    for monster_key, monster in get_monsters().items():
        # Exclude 2014 or 2024 depending on settings
        if monster.has_2024 == prefer_reprinted:
            continue
        namelist.append((monster_key, monster.name))
    return namelist