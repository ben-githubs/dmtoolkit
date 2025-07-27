import json
from pathlib import Path
import requests
from typing import Any, Generator

import click

from dmtoolkit.cmd._util import ConverterError, browser_fetch
from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import Class, Subclass, ClassFeature, Entry
from dmtoolkit.api.serialize import dump_json, load_json


DEFAULT_RAW = ROOT_DIR /  "cmd/raw_classes.json"
DEFAULT_CONV = ROOT_DIR / "api" / "data" / "classes.json"

def fetch_classes(outfile: Path):
    # URLs to fetch
    urls = [
        "https://5e.tools/data/class/class-artificer.json",
        "https://5e.tools/data/class/class-barbarian.json",
        "https://5e.tools/data/class/class-bard.json",
        "https://5e.tools/data/class/class-cleric.json",
        "https://5e.tools/data/class/class-druid.json",
        "https://5e.tools/data/class/class-fighter.json",
        "https://5e.tools/data/class/class-monk.json",
        "https://5e.tools/data/class/class-mystic.json",
        "https://5e.tools/data/class/class-paladin.json",
        "https://5e.tools/data/class/class-ranger.json",
        "https://5e.tools/data/class/class-rogue.json",
        "https://5e.tools/data/class/class-sidekick.json",
        "https://5e.tools/data/class/class-sorcerer.json",
        "https://5e.tools/data/class/class-warlock.json",
        "https://5e.tools/data/class/class-wizard.json"
    ]

    # Store info
    classes = []
    for url in urls:
        # Fetch the file
        data = browser_fetch(url)
        classes.append(json.loads(data))
    
    # Dump data in file
    with outfile.open("w") as f:
        json.dump(classes, f)

def convert(infile: Path, outfile: Path) -> list[Class]:
    # Load classes
    with infile.open("r") as f:
        raw_data: list[dict] = json.load(f)
    
    classes: list[Class] = []

    for full_class_spec in raw_data:
        class_name = full_class_spec.get("class", [{}])[0].get("name", "UNKNOWN CLASS")
        try:
            # Extract subclass features
            subclass_feats_raw: dict[str, dict] = {}
            subclass_feats: dict[str, ClassFeature] = {}
            subclass_copies: list[dict] = []
        
            for feat in full_class_spec.get("subclassFeature", []):
                # If this subclass feature is based on another one, we should wait until after
                #   loading all the subclass features before we try to process it
                if "_copy" in feat:
                    subclass_copies.append(feat)
                    continue
                subclass_name = feat["subclassShortName"]
                subclass_source = feat["subclassSource"]
                feature_name = feat["name"]
                class_name = feat["className"]
                class_source = feat["classSource"]
                aux_source = feat["source"] # idk what to call it, it's just 'source'
                level = feat["level"]

                # This is the key used in the actual subclass spec to indicate which feats are earned
                #   at each level. Annoyingly, sometimes one or both sources are omitted in the references,
                #   and somemes they add the aux source at the end.
                keys = [
                    f"{feature_name}|{class_name}|{class_source}|{subclass_name}|{subclass_source}|{level}",
                    f"{feature_name}|{class_name}||{subclass_name}|{subclass_source}|{level}",
                    f"{feature_name}|{class_name}|{class_source}|{subclass_name}||{level}",
                    f"{feature_name}|{class_name}||{subclass_name}||{level}"
                ]
                keys += [x + "|" + aux_source for x in keys]
                for key in keys:
                    subclass_feats_raw[key] = feat
            
            for copy_feat in subclass_copies:
                subclass_name = copy_feat["subclassShortName"]
                subclass_source = copy_feat["subclassSource"]
                feature_name = copy_feat["name"]
                class_name = copy_feat["className"]
                class_source = copy_feat["classSource"]
                level = copy_feat["level"]

                key_fields = ["name", "className", "classSource", "subclassShortName", "subclassSource", "level"]
                copy_key = "|".join(str(copy_feat["_copy"][field]) for field in key_fields)
            
                new_feat = subclass_feats_raw[copy_key] | copy_feat
                
                key = "|".join(str(new_feat[field]) for field in key_fields)
                subclass_feats_raw[key] = new_feat
            
            for feat in subclass_feats_raw.values():
                    try:
                        # Check if this references another feat
                        feat["entries"] = [_get_entry(e, subclass_feats_raw, "refSubclassFeature", "subclassFeature") for e in feat["entries"]]
                    except Exception as e:
                        feat_name = feat.get("name", "UNKNOWN FEAT")
                        raise ConverterError(f"Error while reoslving references for {feat_name}") from e
            
            for key, feat in subclass_feats_raw.items():
                    # Last pass, we can now convert the class features into actual objects
                    try:
                        entries = subclass_feats_raw[key]["entries"]
                        subclass_feats[key] = ClassFeature(
                            title=feat["name"],
                            level=feat["level"],
                            body=[Entry.from_spec(entry) for entry in entries]
                        )
                    except Exception as e:
                        raise ConverterError(f"Unable to convert subclass feature '{key}'") from e
                
        except Exception as e:
            raise ConverterError(f"Unable to process subclass features for {class_name}") from e
            
        try:
            # Extract regular class features
            class_feats_raw: dict[str, dict] = {}
            class_feats: dict[str, ClassFeature] = {}

            for feat in full_class_spec.get("classFeature", []):
                feature_name = feat["name"]
                class_name = feat["className"]
                class_source = feat["classSource"]
                level = feat["level"]
                source = feat["source"]

                # Just as with as the subclass feature key, we use the same formatting here as is used
                #   in the class spec. Like subclasses, sometimes the source is omitted in references.
                keys = [
                    f"{feature_name}|{class_name}|{class_source}|{level}",
                    f"{feature_name}|{class_name}||{level}"
                ]
                keys += [f"{x}|{source}" for x in keys]
                for key in keys:
                    class_feats_raw[key] = feat
            
            for feat in class_feats_raw.values():
                    # Check if this references another feat
                    feat["entries"] = [_get_entry(e, class_feats_raw, "refClassFeature", "classFeature") for e in feat["entries"]]
            
            # Special fixes
            #   There's some malformated data from the source; the simplest solution is to add
            #   one-off fixes here, rather than break the code in models.py to account for bad data

            # Add missing style to the XPHB Wild Shape table
            if bad_feat := class_feats_raw.get("Wild Shape|Druid||2"):
                bad_feat["entries"][1]["entries"][2]["colStyles"].append("col-3")

            for key, feat in class_feats_raw.items():
                try:
                    class_feats[key] = ClassFeature(
                        title=feat["name"],
                        level=feat["level"],
                        body=[Entry.from_spec(entry) for entry in feat["entries"]]
                    )
                except Exception as e:
                    raise ConverterError(f"Unable to convert class feature {key}") from e
            
        except Exception as e:
            raise ConverterError(f"Unable to process class features for {class_name}") from e

        try:
            # Compile all the subclasses
            subclasses: list[Subclass] = []
            for subclass_spec in full_class_spec.get("subclass", []):
                # Skip stuff from 5.5e
                if subclass_spec.get("edition") != "classic":
                    continue

                subclasses.append(
                    Subclass(
                        name = subclass_spec["name"],
                        subclass_features = [subclass_feats[x] for x in subclass_spec.get("subclassFeatures", [])]
                    )
                )
            
        except Exception as e:
            raise ConverterError(f"Unable to process subclasses for {class_name}") from e
            
        try:
            for class_spec in full_class_spec["class"]:
                # -- Finally, compile the class --
                if class_spec.get("edition") != "classic":
                    continue
                if class_spec.get("isSidekick"):
                    continue

                # Proficiencies are usually just strings, but some optional ones are dicts.
                def prof_generator(arr: list[str|dict]) -> Generator[str, Any, Any]:
                    for item in arr:
                        if isinstance(item, str):
                            yield item
                        else:
                            # Sometimes there's a more explicit string we can use
                            if "full" in item:
                                yield item["full"]
                            # If the proficinecy is optional, list it as such
                            elif "optional" in item:
                                yield item["proficiency"] + " (optional)"
                
                # Class Feature specs are usually string references but sometimes are dicts
                def feat_generator(arr: list[str|dict]) -> Generator[ClassFeature, Any, Any]:
                    for item in arr:
                        if isinstance(item, dict):
                            # The other fields are usually flags I don't care about; I just want the name
                            item = item["classFeature"]
                        yield class_feats[item]


                classes.append(Class(
                    name = class_spec["name"],
                    spellcasting_ability = class_spec.get("spellcastingAbility", ""),
                    multiclassing = {},
                    hitdice = f"{class_spec['hd']['number']}d{class_spec['hd']['faces']}",
                    weapon_profs = list(prof_generator(class_spec["startingProficiencies"].get("weapons", []))),
                    armor_profs = list(prof_generator(class_spec["startingProficiencies"].get("armor", []))),
                    tool_profs = list(prof_generator(class_spec["startingProficiencies"].get("tools", []))),
                    class_features = list(feat_generator(class_spec["classFeatures"])),
                    subclasses = subclasses
                ))
        
        except Exception as e:
            raise ConverterError(f"Unable to process class for {class_name}") from e

    # Dump to file
    with outfile.open("w") as f:
        dump_json(classes, f)

    return classes

def _get_entry(entry: dict, all_items: dict[str, dict], typ: str, field: str):
    if isinstance(entry, dict):
        if entry.get("type") == typ:
            return all_items[entry[field]]
        if entries := entry.get("entries"):
            entry["entries"] = [_get_entry(e, all_items, typ, field) for e in entries]
        if entries := entry.get("items"):
            entry["items"] = [_get_entry(e, all_items, typ, field) for e in entries]
    return entry
