import json
from pathlib import Path
from typing import Any

from dmtoolkit.cmd._util import ConverterError, browser_fetch, pluralize, singularize, deep_get
from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import Spell, Subclass, ClassFeature, Entry
from dmtoolkit.api.serialize import dump_json, load_json


DEFAULT_RAW = ROOT_DIR /  "cmd/raw_items.json"
DEFAULT_CONV = ROOT_DIR / "api" / "data" / "items.json"


def fetch_items(outfile: Path):
    # URLs to fetch
    urls = {
        "base": "https://5e.tools/data/items-base.json",
        "magic": "https://5e.tools/data/items.json",
        "variants": "https://5e.tools/data/magicvariants.json",
    }

    # Store info
    items = {}
    for item_type, url in urls.items():
        # Fetch the file
        data = browser_fetch(url)
        items[item_type] = json.loads(data)
    
    # Dump data in file
    with outfile.open("w") as f:
        json.dump(items, f)

# def convert(infile: Path, outfile: Path) -> list[Spell]:
#     raw_spell_specs: list[dict[str, Any]] = []
#     spells: list[Spell] = []
#     with infile.open("r") as f:
#         raw_spell_specs = json.load(f)
    
#     for group in raw_spell_specs:
#         for spell_spec in group["spell"]:
#             if "name" not in spell_spec:
#                 print(spell_spec)
#                 raise Exception
#             spell_name = spell_spec["name"]
#             spell_params = {
#                 "entries": [],
#                 "duration": "",
#                 "level": spell_spec["level"],
#                 "name": spell_name,
#                 "range": "",
#                 "school": SCHOOLS[spell_spec["school"]],
#                 "source": (spell_spec["source"], int(spell_spec["page"])),
#                 "time": "",
#             }

#             for entry in spell_spec["entries"]:
#                 spell_params["entries"].append(Entry.from_spec(entry))
#             for entry in spell_spec.get("entriesHigherLevel", []):
#                 spell_params["entries"].append(Entry.from_spec(entry))

#             try:
#                 duration_spec = spell_spec["duration"][0] # Only ever has one entry
#                 spell_params["duration"] = _fmt_duration(duration_spec) 
#                 spell_params["range"] = _fmt_range(spell_spec["range"])
#                 spell_params["time"] = _fmt_time(spell_spec["time"])
#             except BaseException as e:
#                 raise ConverterError(f"{spell_name}: {e}") from e
#             if spell_params["duration"].startswith("Concentration"):
#                 spell_params["is_concentration"] = True
            
#             for additional_source in spell_spec.get("additional_sources", []):
#                 if "additional_sources" not in spell_params:
#                     spell_params["additional_sources"] = []
#                 spell_params["additional_sources"].append(
#                     (additional_source["source"], additional_source["page"])
#                 )
            
#             if deep_get(spell_spec, "components", "v"):
#                 spell_params["is_verbal"] = True
#             if deep_get(spell_spec, "components", "s"):
#                 spell_params["is_somatic"] = True
#             if material_component_spec := deep_get(spell_spec, "components", "m"):
#                 spell_params["is_material"] = True
#                 if isinstance(material_component_spec, dict):
#                     spell_params["material_components"] = material_component_spec["text"]
#                 else:
#                     spell_params["material_components"] = str(material_component_spec)
            
#             spell_params["is_ritual"] = deep_get(spell_spec, "meta", "ritual", default=False)

#             try:
#                 spells.append(Spell(**spell_params))
#             except BaseException as e:
#                 raise ConverterError(f"{spell_name}: Unable to convert: {e}") from e
    
#     with outfile.open("w") as f:
#         dump_json(spells, f)
