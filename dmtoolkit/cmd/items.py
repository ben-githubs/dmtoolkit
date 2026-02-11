from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from dmtoolkit.cmd._util import ConverterError, browser_fetch, deep_replace, pluralize, regex_flags, singularize, deep_get
from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import Item, Entry
from dmtoolkit.api.serialize import dump_json, dump_json_string, load_json


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
    raw_item_specs_container: dict[str, list[dict[str, Any]]] = {}
    raw_item_specs: dict[tuple[str, str], dict[str, Any]] = {}
    items: dict[tuple[str, str], Item] = {}
    with infile.open("r") as f:
        raw_item_specs_container = json.load(f)
    
    # -- Load some metadata stuff first --
    # Properties
    item_properties: dict[str, dict[str, Any]] = {}
    for prop in deep_get(raw_item_specs_container, "base", "itemProperty", default=[]):
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
    for item_type in deep_get(raw_item_specs_container, "base", "itemType", default=[]):
        if item_type.get("source", "").startswith("X"):
            # Something from 5.5e; ignore it
            continue
        item_types[f"{item_type['abbreviation']}|{item_type['source']}"] = item_type["name"]
        item_types[item_type["abbreviation"]] = item_type["name"]
    
    # -- Load base items --
    for item_spec in deep_get(raw_item_specs_container, "base", "baseitem") + deep_get(raw_item_specs_container, "magic", "item"):
        # Ignore stuff from 5.5e
        if item_spec.get("source", "").startswith("X") and item_spec.get("source", "") != "XGE":
            continue
        raw_item_specs[(item_spec["name"], item_spec["source"])] = item_spec
    
    # -- Load Copies
    def resolve_copy(item_spec: dict[str, Any]) -> dict[str, Any]:
        try:
            src_item_key = (
                deep_get(item_spec, "_copy", "name"),
                deep_get(item_spec, "_copy", "source")
            )
            src_spec = raw_item_specs[src_item_key]
            
            # IF this item is a copy, resolve it too
            if "_copy" in src_spec:
                src_spec = resolve_copy(src_spec)
            
            item_spec = src_spec | item_spec
            
            for field, mods in deep_get(item_spec, "_copy", "_mod", default={}).items():
                item_spec[field] = deepcopy(src_spec.get(field, []))
                # Normalize it to always be a list, because sometimes it isn't
                if not isinstance(mods, list):
                    mods = [mods]
                for mod in mods:
                    mode = mod.get("mode")
                    match mode:
                        case "appendArr":
                            if not isinstance(mod["items"], list):
                                mod["items"] = [mod["items"]]
                            item_spec[field] += mod["items"]
                        case "replaceArr":
                            if not isinstance(mod["items"], list):
                                mod["items"] = [mod["items"]]
                            index = deep_get(mod, "replace", "index")
                            item_spec[field] = item_spec[field][:index] + mod["items"] + item_spec[field][index+1:]
                        case "insertArr":
                            index = mod["index"]
                            item_spec[field][index] = mod["items"]
                        case "replaceTxt":
                            pattern = re.compile(mod["replace"], flags=regex_flags(mod["flags"]))
                            item_spec[field] = deep_replace(item_spec[field], pattern, mod["with"])
            return item_spec
        except BaseException as e:
            message = f"Unable to resolve copy {item_spec['name']}: {e}"
            raise ConverterError(message) from e
    

    for key, item_spec in raw_item_specs.items():
        if "_copy" in item_spec:
            raw_item_specs[key] = resolve_copy(item_spec)
    
    # -- Variants -- #
    variant_items = []
    for variant in deep_get(raw_item_specs_container, "variants", "magicvariant", default=[]):
        # Ignore 5.5e stuff
        if variant.get("edition") != "classic":
            continue

        # Find each item in the base item set which this variant applies too
        for item in raw_item_specs.values():
            try:
                if item.get("rarity") != "none":
                    continue # Skip already magic items

                # Apply the conditions of the variant
                conditions: list[dict[str, Any]] = variant.get("requires", [])
                is_match = False
                for condition in conditions:
                    if all(item.get(k) == v for k, v in condition.items()):
                        is_match = True
                        break
                if not is_match:
                    # This item isn't compatible with this variation
                    continue

                # Apply the variation
                new_specs = variant["inherits"]
                new_item = deepcopy(item)
                if "namePrefix" in new_specs:
                    new_item["name"] = new_specs["namePrefix"] + new_item["name"]
                if "nameSuffix" in new_specs:
                    new_item["name"] = new_item["name"] + new_specs["nameSuffix"]
                new_entries = new_specs.pop("entries", []) # To prevent this replacing the original entries
                new_item |= new_specs

                # Remove any fields set to None
                new_item = {k: v for k, v in new_item.items() if v is not None}

                # Handle some text formatting in the entries
                for idx in range(len(new_entries)):
                    if not isinstance(new_entries[idx], str):
                        continue
                    new_entries[idx] = re.sub(r"\{=(\w+)}", lambda x: new_specs.get(x.groups(1), ""), new_entries[idx])
                new_item["entries"] = new_entries + new_item.get("entries", [])
                
                # Add the new item to a separate list; this prevents us from creating variants of variants
                variant_items.append(new_item)
            except BaseException as e:
                raise ConverterError(
                    "Unable to create variant "
                    f"{variant['name']} for item {item['name']}: "
                    f"{type(e).__name__}: {e}"
                ) from e
        
        # Create base variant iterm (useful for crafting and stuff)
        try:
            new_entries = variant["inherits"].get("entries", [])
            for idx in range(len(new_entries)):
                if not isinstance(new_entries[idx], str):
                    continue
                new_entries[idx] = re.sub(r"\{=(\w+)}", lambda x: new_specs.get(x.groups(1), ""), new_entries[idx])
            variant_items.append({
                "name": variant["name"],
                "source": variant["inherits"]["source"],
                "page": variant["inherits"]["page"],
                "rarity": variant["inherits"]["rarity"],
                "weight": 0,
                "value": 0,
                "item_type": "generic variant",
                "entries": new_entries,
                "attunement": "requires attunement" if variant["inherits"].get("reqAttune") else ""
            })
            print(variant["name"])
        except BaseException as e:
            raise ConverterError(
                "Unable to create variant base item "
                f"{variant['name']} "
                f"{type(e).__name__}: {e}"
            ) from e
    raw_item_specs |= {(item["name"], item["source"]): item for item in variant_items}

    for item_group_spec in deep_get(raw_item_specs_container, "magic", "itemGroup"):
        # Ignore 5.5e stuff
        if item_group_spec["source"].startswith("X"):
            continue
        # Create base variant iterm (useful for crafting and stuff)
        try:
            new_entries = item_group_spec.get("entries", [])
            raw_item_specs[(item_group_spec["name"], item_group_spec["source"])] = {
                "name": item_group_spec["name"],
                "source": item_group_spec["source"],
                "page": item_group_spec["page"],
                "rarity": item_group_spec["rarity"],
                "weight": 0,
                "value": 0,
                "item_type": "generic variant",
                "entries": new_entries,
                "attunement": "requires attunement" if item_group_spec.get("reqAttune") else ""
            }
            print(item_group_spec["name"])
        except BaseException as e:
            raise ConverterError(
                "Unable to create variant base item "
                f"{item_group_spec['name']} "
                f"{type(e).__name__}: {e}"
            ) from e

    # Convert all item specs to Item objects
    for item_spec in raw_item_specs.values():
        try:
            name = item_spec["name"]
        except KeyError:
            raise ConverterError(f"Can't find name for item: {item_spec}")
        try:
            kwargs = item_spec.copy()
            kwargs["source"] = (item_spec["source"], item_spec.get("page", -1))
            
            if "type" in kwargs:
                kwargs["item_type"] = item_types.get(kwargs["type"])
            
            if "property" in kwargs:
                kwargs["properties"] = []
                for prop in kwargs["property"]:
                    if _prop := item_properties.get(prop):
                        kwargs["properties"].append(_prop["name"])
            
            new_item = Item.from_spec(kwargs)
            items[(kwargs["name"], kwargs["source"][0])] = (new_item)
            # Test serialization
            dump_json_string(new_item)
        except Exception as e:
            raise ConverterError(f"Unable to convert item {name}: {e}") from e
    
    
    with outfile.open("w") as f:
        dump_json([x for x in items.values()], f)
