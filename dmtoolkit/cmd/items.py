import json
from pathlib import Path
from typing import Any

from dmtoolkit.cmd._util import ConverterError, browser_fetch, pluralize, singularize, deep_get
from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import Item, Entry
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

def convert(infile: Path, outfile: Path):
    raw_item_specs: dict[str, list[dict[str, Any]]] = []
    items: list[Item] = []
    with infile.open("r") as f:
        raw_item_specs = json.load(f)
    
    # -- Load some metadata stuff first --
    # Properties
    item_properties: dict[str, dict[str, Any]] = {}
    for prop in deep_get(raw_item_specs, "base", "itemProperty", default=[]):
        if prop.get("source", "").startswith("X"):
            # Something from 5.5e; ignore it
            continue
        # Infer the name of the property
        if "name" not in prop:
            # Set a sensible default
            prop["name"] = prop["abbreviation"]
            # Override default if there's an entry with a name
            if "entries" in prop:
                if name := prop["entries"][0].get("name"):
                    prop["name"] = name
            
        item_properties[f"{prop['abbreviation']}|{prop['source']}"] = prop

    # Item Types
    item_types: dict[str, dict[str, Any]] = {}
    for item_type in deep_get(raw_item_specs, "base", "itemType", default=[]):
        if item_type.get("source", "").startswith("X"):
            # Something from 5.5e; ignore it
            continue
        item_types[f"{item_type['abbreviation']}|{item_type['source']}"] = item_type["name"]
        item_types[item_type["abbreviation"]] = item_type["name"]
    
    # -- Load base items --
    for item_spec in deep_get(raw_item_specs, "base", "baseitem"):
        if item_spec.get("source", "").startswith("X"):
            # Something from 5.5e; ignore it
            continue
        name = item_spec["name"]
        try:
            kwargs = item_spec.copy()
            kwargs["source"] = (item_spec["source"], item_spec["page"])
            
            if "type" in kwargs:
                kwargs["item_type"] = item_types.get(kwargs["type"])
            
            if "property" in kwargs:
                kwargs["properties"] = []
                for prop in kwargs["property"]:
                    if _prop := item_properties.get(prop):
                        kwargs["properties"].append(_prop["name"])
            
            items.append(Item.from_spec(kwargs))
        except Exception as e:
            raise ConverterError(f"Unable to convert item {name}: {e}") from e
    
    
    with outfile.open("w") as f:
        dump_json(items, f)
