import json
from pathlib import Path
from typing import Any

from dmtoolkit.cmd._util import ConverterError, browser_fetch, pluralize, singularize, deep_get
from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import Spell, Subclass, ClassFeature, Entry
from dmtoolkit.api.serialize import dump_json, load_json


DEFAULT_RAW = ROOT_DIR /  "cmd/raw_spells.json"
DEFAULT_CONV = ROOT_DIR / "api" / "data" / "spells.json"

def fetch_spells(outfile: Path):
    # URLs to fetch
    urls = [
        "https://5e.tools/data/spells/spells-aag.json",
        "https://5e.tools/data/spells/spells-ai.json",
        "https://5e.tools/data/spells/spells-aitfr-avt.json",
        "https://5e.tools/data/spells/spells-egw.json",
        "https://5e.tools/data/spells/spells-ftd.json",
        "https://5e.tools/data/spells/spells-ftd.json",
        "https://5e.tools/data/spells/spells-idrotf.json",
        "https://5e.tools/data/spells/spells-llk.json",
        "https://5e.tools/data/spells/spells-phb.json",
        "https://5e.tools/data/spells/spells-scc.json",
        "https://5e.tools/data/spells/spells-tce.json",
        "https://5e.tools/data/spells/spells-xge.json",
        "https://5e.tools/data/spells/spells-tdcsr.json",
        "https://5e.tools/data/spells/spells-bmt.json",
        "https://5e.tools/data/spells/spells-sato.json",
        # "https://5e.tools/data/spells/spells-xphb.json"
    ]

    # Store info
    spells = []
    for url in urls:
        # Fetch the file
        data = browser_fetch(url)
        spells.append(json.loads(data))
    
    # Dump data in file
    with outfile.open("w") as f:
        json.dump(spells, f)

def convert(infile: Path, outfile: Path) -> list[Spell]:
    raw_spell_specs: list[dict[str, Any]] = []
    spells: list[Spell] = []
    with infile.open("r") as f:
        raw_spell_specs = json.load(f)
    
    for group in raw_spell_specs:
        for spell_spec in group["spell"]:
            if "name" not in spell_spec:
                print(spell_spec)
                raise Exception
            spell_name = spell_spec["name"]
            spell_params = {
                "entries": [],
                "duration": "",
                "level": spell_spec["level"],
                "name": spell_name,
                "range": "",
                "school": spell_spec["school"],
                "source": (spell_spec["source"], int(spell_spec["page"])),
                "time": "",
            }

            for entry in spell_spec["entries"]:
                spell_params["entries"].append(Entry.from_spec(entry))
            for entry in spell_spec.get("entriesHigherLevel", []):
                spell_params["entries"].append(Entry.from_spec(entry))

            try:
                duration_spec = spell_spec["duration"][0] # Only ever has one entry
                spell_params["duration"] = _fmt_duration(duration_spec) 
                spell_params["range"] = _fmt_range(spell_spec["range"])
                spell_params["time"] = _fmt_time(spell_spec["time"])
            except BaseException as e:
                raise ConverterError(f"{spell_name}: {e}") from e
            if spell_params["duration"].startswith("Concentration"):
                spell_params["is_concentration"] = True
            
            for additional_source in spell_spec.get("additional_sources", []):
                if "additional_sources" not in spell_params:
                    spell_params["additional_sources"] = []
                spell_params["additional_sources"].append(
                    (additional_source["source"], additional_source["page"])
                )
            
            if deep_get(spell_spec, "components", "v"):
                spell_params["is_verbal"] = True
            if deep_get(spell_spec, "components", "s"):
                spell_params["is_somatic"] = True
            if material_component_spec := deep_get(spell_spec, "components", "m"):
                spell_params["is_material"] = True
                if isinstance(material_component_spec, dict):
                    spell_params["material_components"] = material_component_spec["text"]
                else:
                    spell_params["material_components"] = str(material_component_spec)
            
            spell_params["is_ritual"] = deep_get(spell_spec, "meta", "ritual", default=False)

            try:
                spells.append(Spell(**spell_params))
            except BaseException as e:
                raise ConverterError(f"{spell_name}: Unable to convert: {e}") from e
    
    with outfile.open("w") as f:
        dump_json(spells, f)


def _fmt_duration(duration: dict[str, Any]) -> str:
    match duration["type"]:
        case "instant":
            return "Instantaneous"
        case "permanent":
            end_conditions = []
            for end_cond in duration["ends"]:
                match end_cond:
                    case "dispel":
                        end_conditions.append("dispelled")
                    case "trigger":
                        end_conditions.append("triggered")
                    case _:
                        raise ConverterError(f"Unknown end condition '{end_cond}'")
            if len(end_conditions) == 1:
                return "Until " + end_conditions[0]
            else:
                return "Until " + ", ".join(end_conditions[:-1]) + ", or " + end_conditions[-1]
        case "special":
            return "Special"
        case "timed":
            mag = duration["duration"]["amount"]
            unit = duration["duration"]["type"]
            return f"{mag} {unit}"
        case _:
            raise ConverterError(f"Unexpected type name '{duration['type']}'")
    if duration.get("concentration"):
        return "Concentration, up to " + spell_params["duration"]
    
    # Raise an error if we have a duration which isn't resolved by the above logic
    raise ConverterError("No logic to resolve duration spec.")


def _fmt_range(range_spec: dict[str, Any]) -> str:
    """Logic for formatting the range string of a spell."""
    distance = range_spec.get("distance", {})
    match range_type := range_spec["type"]:
        case "line" | "cone" | "cube" | "hemisphere" | "sphere":
            shape = range_spec["type"]
            # The test display for hemispheres is slightly different
            if shape == "hemisphere":
                shape = "-radius hemisphere"
            match distance.get("type"):
                case "feet":
                    nfeet = distance["amount"]
                    return f"Self ({nfeet}-foot {shape})"
                case _:
                    raise ConverterError(f"Unexpected range unit for shape: '{distance.get('type')}'")
        case "point":
            match distance.get("type"):
                case "self" | "touch" | "sight" | "unlimited":
                    return distance.get("type").title()
                case "feet" | "miles":
                    return "{} {}".format(range_spec["distance"]["amount"], range_spec["distance"]["type"])
        case "radius":
            return f"Self ({distance['amount']}-{singularize(distance['type'])} radius)"
        case "special":
            return "Special"
        case _:
            raise ConverterError(f"Unexpected range type: '{range_type}'")
    
    # Raise an error if we have a range_spec which isn't resolved by the above logic
    raise ConverterError("No logic to resolve range spec.")


def _fmt_time(time_specs: list[dict[str, Any]]) -> str:
    time_strs: list[str] = []

    for time_spec in time_specs:
        if time_spec["number"] == 1:
            if time_spec["unit"] == "bonus":
                time_strs.append("Bonus Action")
            else:
                time_strs.append(time_spec["unit"].title())
        else:
            time_strs.append("{} {}".format(time_spec["number"], pluralize(time_spec["unit"]).title()))
        if condition := time_spec.get("contition"):
            time_strs[-1] = f"{time_strs[-1]}, {condition}"

    if len(time_strs) != len(time_specs):
        raise ConverterError("No logic path to conver time spec")
    
    # Join in format "x, y, or z"
    return ", or ".join([", ".join(time_strs[:-1]), time_strs[-1]])