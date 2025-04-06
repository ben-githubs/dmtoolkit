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
            if not monster:
                breakpoint()
            MONSTERS[monster.key] = monster
    
    return MONSTERS


def get_monster(key: str) -> Monster:
    """Fetch a specific monster by key. Returns 'None' if there is no monster with that key."""
    return get_monsters().get(key, None)


def get_monster_names() -> list[tuple[str, str]]:
    """Return a list of tuples containing the monster key and it's name."""
    namelist = []
    for monster_key, monster in get_monsters().items():
        namelist.append((monster_key, monster.name))
    return namelist