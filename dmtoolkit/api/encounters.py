""" Code for storing, creating, and editing combat encounters."""

import json
from uuid import uuid4

from flask import request, Response

DEFAULT_ENCOUNTERS = {
    "sample1": {
        "title": "(Sample) Bandits",
        "desc": "A group of bandits ambushes the party.",
        "monsters": ["Bandit-MM", "Bandit-MM", "Bandit-MM", "Bandit Captain-MM"]
    }
}

def getall():
    """Return all encounters."""
    return json.loads(request.cookies.get("encounters", "{}")) or DEFAULT_ENCOUNTERS


def get(eid: str):
    """Fetch a single encounter, using it's encounter ID."""
    encounter: dict = getall().get(eid)
    if not encounter:
        return None
    return encounter.copy()


def create_or_update(resp: Response, encounter: dict) -> str:
    """Save an encounter. Returns the UUID assigned to it."""
    encounters = getall()
    eid = encounters.get("id") or str(uuid4())
    encounter["id"] = eid
    encounters[eid] = encounter
    _save_encounters(resp, encounters)
    return eid


def delete(resp: Response, eid: str):
    """Delete an encounter."""
    encounters = getall()
    encounters.pop(eid)
    _save_encounters(resp, encounters)

def _save_encounters(resp: Response, encounters: dict):
    resp.set_cookie("encounters", json.dumps(encounters))
