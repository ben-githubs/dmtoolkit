import json
from pathlib import Path
from typing import Any

import click

from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import AgeParams, Entry, Race, SizeParams, Speed
from dmtoolkit.api.serialize import dump_json, load_json


DEFAULT_RAW = ROOT_DIR /  "cmd/raw_races.json"
DEFAULT_CONV = ROOT_DIR / "api" / "data" / "races.json"

def convert_race(spec: dict[str, Any]):
    """Convert a JSON representation of a race (as downloaded from 5e.tools) into a Race object."""
    return Race(
        spec["name"],
        spec["source"],
        Speed.from_spec(spec["speed"]),
        spec.get("ability", {}),
        spec["size"],
        age = AgeParams.from_spec(spec["age"]) if spec.get("age") else None,
        size_params = SizeParams.from_spec(spec.get("heightAndWeight")) if spec.get("heightAndWeight") else None,
        blindsight = spec.get("blindsight", 0),
        darkvision = spec.get("darkvision", 0),
        skills = spec.get("skill", []),
        languages = spec.get("language"),
        feats = spec.get("feat", []),
        traits = [Entry.from_spec(s) for s in spec.get("entries", [])],
        dmg_resistances = spec.get("resist", []),
        dmg_vulnerabilities = spec.get("vulnerable", []),
        dmg_immunities = spec.get("immune", []),
        cond_immunities = spec.get("conditionImmune", []),
        tool_profs = [], # TODO: Convert these
        armor_prof = [], # TODO
        weapon_profs = [] # TODO
    )

def convert(infile: Path, outfile: Path):
    """Normalizes all the raw JSON monsters in 'infile' and outputs them in 'outfile'."""
    with infile.open("r") as f:
        data = json.load(f)
    
    races_to_convert: list[dict[str, Any]] = data["race"]

    converted: list[Race] = []
    for race in races_to_convert:
        # TODO: Implement copying
        if "_copy" in race:
            continue
        try:
            converted.append(convert_race(race))
        except Exception as e:
            click.echo(json.dumps(race), err=True)
            raise e
    
    with outfile.open("w") as f:
        dump_json(converted, f)


def test(infile: Path):
    with infile.open("r") as f:
        load_json(f)