from pathlib import Path
import json
from typing import Any

DATADIR = Path(__file__).parent / "data"
CONDITION_DATA_PATH = DATADIR / "conditions.json"

CONDITIONS: dict[str, dict[str, Any]] = {}

def _load_conditions():
    global CONDITIONS
    with CONDITION_DATA_PATH.open("r") as f:
        CONDITIONS = json.load(f)


def list_conditions() -> dict[str, dict[str, Any]]:
    """Returns a list if all condition objects."""
    return CONDITIONS.copy()


def get_condition(name: str) -> dict[str, Any]:
    return CONDITIONS.get(name, {})

# Make sure we load the conditions dict at least once on load
if not CONDITIONS:
    _load_conditions()