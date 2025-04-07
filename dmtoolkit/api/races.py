from pathlib import Path

from dmtoolkit.api.models import Race
from dmtoolkit.api.serialize import load_json

DATADIR = Path(__file__).parent / "data"
RACE_DATA_PATH = DATADIR / "races.json"

RACES: dict[str, Race] = {}

def list_races() -> list[str]:
    """Returns a list of all race names. Also lazily loads the Races dictionary."""
    if not RACES:
        with RACE_DATA_PATH.open("r") as f:
            races: list[Race] = load_json(f)
        for race in races:
            RACES[race.name] = race
    
    return list(races.keys())


def get_race(name: str) -> Race:
    """Returns the race with the given name. If no race with the name exists, return None."""
    return RACES.get(name)
