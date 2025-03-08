""" Code for storing, creating, and editing combat encounters."""

import json
from pathlib import Path
from uuid import uuid4

datadir = Path(__file__).parent / "data"

_ENCOUNTERS = {}
def _load_from_file(fname: Path = datadir / "encounters.json"):
    """Load the encounter set from a file."""
    global _ENCOUNTERS
    with fname.open("r") as f:
        _ENCOUNTERS = json.load(f)

def _save_to_file(fname: Path = datadir / "encounters.json"):
    """Save the current set of encounters to a file."""
    global _ENCOUNTERS
    with fname.open("w") as f:
        json.dump(_ENCOUNTERS, f)

_load_from_file()

"""
 -- FUNCTION DEFINITIONS --
"""

def getall():
    """Return all encounters."""
    global _ENCOUNTERS
    return _ENCOUNTERS.copy()


def get(eid: str):
    """Fetch a single encounter, using it's encounter ID."""
    global _ENCOUNTERS
    encounter: dict = _ENCOUNTERS.get(eid)
    if not encounter:
        return None
    return encounter.copy()


def create_or_update(encounter: dict) -> str:
    """Save an encounter. Returns the UUID assigned to it."""
    global _ENCOUNTERS
    eid = encounter.get("id") or str(uuid4())
    encounter["id"] = eid
    _ENCOUNTERS[eid] = encounter
    _save_to_file()
    return eid


def delete(eid: str):
    """Delete an encounter."""
    global _ENCOUNTERS
    _ENCOUNTERS.pop(eid)
    _save_to_file()
