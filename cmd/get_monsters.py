
"""This script fetches updated monster lists from 5e.tools and then formats them in a consistant 
manner. It exists because I got frustrated at the complexity my code required in order to pander
to the many, many, MANY "edge cases" in the 5e.tools JSON files where, in an apparent attempt to
make some entries more human readable, dictionaries would be turned into single scalar values and
any other items within would be assumed."""

from __future__ import annotations
from collections.abc import Mapping, Sequence
from functools import reduce
import json
import os
from pathlib import Path
import re
from typing import Any

import click

from util import listify
from dmtoolkit.api.models import AC, HP, Entry, Monster, SkillList, Speed, SpellCasting, Scalar
from dmtoolkit.api.serialize import load_json, dump_json

# Default paths to the monster JSON files
DEFAULT_RAW = Path(__file__).parent / "raw_monsters.json"
DEFAULT_CONV = Path(__file__).parent.parent / "dmtoolkit" / "api" / "data" / "monsters.json"

# Some statblocks are pointless and broken enough that writing edge cases for them isn't worth it,
#   like young miss Cassalanter, who's entire statblock is just her name, size, and type.
IGNORE_MONSTERS = {
    "Elzerina Cassalanter-WDH",
    "Jenks-WDH",
    "Nat-WDH",
    "Squiddly-WDH",
    "Terenzio Cassalanter-WDH",
    # The source monster is miscapitalized and I don't feel like making the check case insensitive
    "Ougalop-OotA",
    "Shuushar the Awakened-OotA"
}

def convert_monster(spec: dict[str, Any]) -> Monster:
    if any(key in spec for key in ("_copy", "summonedBySpell", "summonedByClass")):
        # Implement this later
        return
    
    # Compare to ignore list
    key = f"{spec.get('name')}-{spec.get('source')}"
    if key in IGNORE_MONSTERS:
        return

    optargs = {
        "other_sources": spec.get("otherSources", [])
    }

    typ = spec.get("type")
    if isinstance(typ, str):
        maintype = typ
    elif isinstance(typ, dict):
        maintype = typ["type"]
        subtype = ""
        if tags := typ.get("tags"):
            _tags = []
            # some tags are not just strings
            for tag in tags:
                if isinstance(tag, dict):
                    _tags.append(f"{tag['prefix']} {tag['tag']}")
                else:
                    _tags.append(tag)
            subtype += ", ".join(_tags)
        if swarm_size := typ.get("swarmSize"):
            maintype = f"swarm of {get_size_string(swarm_size)} {maintype}s"
        if subtype:
            optargs["subtype"] = subtype
    else:
        raise TypeError(f"Invalid type of 'type': '{type(typ).__name__}': {typ}")
    
    # Make sure skills, saves, etc. have the expected format
    if saves := spec.get("save"):
        assert isinstance(saves, dict), f"Got type '{type(saves).__name__}'"
        for k, v in saves.items():
            assert isinstance(k, str), f"Got type '{type(k).__name__}'"
            assert isinstance(v, str), f"Got type '{type(v).__name__}'"
    
    # Make sure senses are a list of strings
    senses = spec.get("senses", [])
    assert isinstance(senses, list), f"Unexpected type '{type(senses).__name__}'"
    for item in senses:
        assert isinstance(item, str), f"Unexpected type '{type(senses).__name__}'"
    
    # Make sure passive is an int
    assert isinstance(spec["passive"], int), f"Unexpected type '{type(spec['passive']).__name__}'"
    
    # Make sure languages are a list of strings
    langs = spec.get("languages", [])
    assert isinstance(langs, list), f"Unexpected type '{type(langs).__name__}'"
    for item in langs:
        assert isinstance(item, str), f"Unexpected type '{type(langs).__name__}'"

    monster = Monster(
        name = spec["name"],
        source = spec["source"],
        page = spec.get("page", 0),
        size_str = get_size_string(spec["size"]),
        maintype = maintype,
        alignment = get_alignment_string(spec.get("alignment", ["U"])),
        ac = AC.from_spec(spec["ac"]),
        hp = HP(**spec["hp"]),
        speed = Speed.from_spec(spec["speed"]),
        cr = get_cr(spec.get("cr", "0")),
        xp = get_xp(get_cr(spec.get("cr", "0"))),
        strength = spec["str"],
        dexterity = spec["dex"],
        constitution = spec["con"],
        intelligence = spec["int"],
        wisdom = spec["wis"],
        charisma = spec["cha"],
        skills = SkillList.from_spec(spec.get("skill")),
        saves = spec.get("save"),
        dmg_vulnerabilities = get_damage_mods(spec.get("vulnerable")),
        dmg_resistances = get_damage_mods(spec.get("resist")),
        dmg_immunities = get_damage_mods(spec.get("immune")),
        cond_immunities = get_damage_mods(spec.get("conditionImmune")),
        senses = spec.get("senses", []),
        passive = spec.get("passive"),
        languages = spec.get("languages", []),
        traits = [Entry.from_spec(trait) for trait in spec.get("trait", [])],
        actions = [Entry.from_spec(action) for action in spec.get("action", [])],
        bonus_actions = [Entry.from_spec(bonus) for bonus in spec.get("bonus", [])],
        reactions = [Entry.from_spec(reaction) for reaction in spec.get("reaction", [])],
        legendary_actions = [Entry.from_spec(legendary) for legendary in spec.get("legendary", [])],
        spellcasting = [SpellCasting.from_spec(s) for s in spec.get("spellcasting", [])],
        **optargs
    )
    return monster


def copy_monster(orig: dict[str, Any], copy: dict[str, Any]) -> dict[str, Any]:
    """Takes a raw monster spec and the copy spec and returns the new monster spec."""
    new_spec = orig | copy # Copy the fields over
    copy_spec = copy["_copy"]

    # Apply modifications
    def replace_text(obj: Any, old: str, new: str):
        """Replaces all occurences of old with new."""
        # The 'new' pattern is using $1 instead of \1 for backreferences, so we need to adjust it
        new = re.sub(r"$(\d+)", r"\\\1", new)
        if isinstance(obj, str):
            return re.sub(old, new, obj)
        if isinstance(obj, Mapping):
            for k, v in obj.items():
                obj[k] = replace_text(v, old, new)
            return obj
        if isinstance(obj, Sequence):
            return [replace_text(x, old, new) for x in obj]
        return obj
    
    for target, mods in copy_spec.get("_mod", {}).items():
        mods = listify(mods)
        

        for mod in mods:
            # Sometimes, mod is a string instead of a modification spec
            if isinstance(mod, str):
                match mod:
                    case "remove":
                        del new_spec[target]
                    case _:
                        raise ValueError(f"Unknown modification: '{mod}'")
                continue
            match mod.get("mode"):
                case "replaceTxt":
                    old_str = mod.get("replace", "")
                    new_str = mod.get("with", "")
                    if target == "*":
                        new_spec = replace_text(new_spec, old_str, new_str)
                    else:
                        new_spec[target] = replace_text(new_spec[target], old_str, new_str)
                case "appendArr" | "appendIfNotExistsArr":
                    # Initialize the array if it doesn't exist
                    if target not in new_spec:
                        new_spec[target] = []
                    # Add new item
                    new_spec[target].append(mod.get("items"))
                case "insertArr":
                    insert_arr(new_spec, mod, target)
                case "prependArr":
                    # Basically we just call insert_arr with an index of 0.
                    insert_mod_spec = {
                        "index": 0,
                        **mod
                    }
                    insert_arr(new_spec, insert_mod_spec, target)
                case "replaceArr":
                    new_arr = mod.get("items")
                    new_arr = listify(new_arr)
                    new_spec[target] = new_arr
                case "removeArr":
                    # Two posibilities: we're removing a scalar (string) from a list, or
                    #   we're removing named entries.
                    if "items" in mod:
                        items = listify(mod["items"])
                        new_spec[target] = [x for x in new_spec[target] if x not in items]
                    elif "names" in mod:
                        # Remove an entry from an array if the name matches
                        # Annoyingly, names can be either a string or a list of names
                        names = set(listify(mod.get("names")))
                        new_spec[target] = [
                            x for x in new_spec[target] if x.get("name") not in names
                        ]
                    else:
                        raise ValueError(f"Unexpected removeArr spec :(")
                case "addSkills":
                    new_skills = mod.get("skills", {})
                    new_spec["skills"] = new_spec.get("skills", {}) | new_skills
                case "addSpells":
                    # Add new spells
                    for spellcasting_spec in new_spec.get("spellcasting", []):
                        extend_nested_array(mod, spellcasting_spec)
                case "removeSpells":
                    for spellcasting_spec in new_spec.get("spellcasting", []):
                        for field in ("daily", "spells"):
                            if spell_list := mod.get(field):
                                for k, v in spell_list.items():
                                    v = listify(v)
                                    spellcasting_spec[field][k] = [x for x in spellcasting_spec[field][k] if x not in v]
                case "replaceSpells":
                    spell_replacements = mod.get("spells")
                    for spellcasting_spec in new_spec.get("spellcasting", []):
                        old_spells = spellcasting_spec.get("spells", {})
                        for level, replace_specs in spell_replacements.items():
                            for replace_spec in replace_specs:
                                old_spell = replace_spec["replace"]
                                new_spell = replace_spec["with"]
                                if level in old_spells:
                                    # one-liner replacement:
                                    old_spells[level] = [x if x != old_spell else new_spell for x in old_spells]
                case _:
                    raise ValueError(f"Unknown mod mode '{mod.get('mode')}'")
    
    return new_spec


def insert_arr(monster_spec: dict, mod_spec: dict, target: str):
    """Insert an entry into an array within monster_spec."""
    # Add a new item at a specific index
    target_arr = monster_spec.get(target, [])
    target_arr.insert(mod_spec.get("index", 0), mod_spec.get("item"))
    monster_spec[target] = target_arr


def get_nested_paths(obj: Mapping[str, Any]) -> list[list[str]]:
    """Returns all nested paths to non-mapping objects inside obj."""
    paths: list[list[str]] = []
    for k, v in obj.items():
        if isinstance(v, Mapping):
            paths.extend([[k] + p for p in get_nested_paths(v)])
        else:
            paths.append([k])
    return paths



def deep_get(dictionary: dict, *keys, default=None):
    """Safely return the value of an arbitrarily nested map

    Inspired by https://bit.ly/3a0hq9E
    """
    out = reduce(
        lambda d, key: d.get(key, default) if isinstance(d, Mapping) else default, keys, dictionary
    )
    if out is None:
        return default
    return out


def extend_nested_array(mod_spec: dict, obj: dict):
    # Remove any potentiall keywords from mod_type
    mode = mod_spec.pop("mode")
    paths = get_nested_paths(mod_spec)
    for path in paths:
        # Get nested list in spec
        extensions = deep_get(mod_spec, *path, default=[])
        o = deep_get(obj, *path)
        o.extend(extensions) # Extend is in-place, so this is fine


def get_alignment_string(alignment: list[str|dict]) -> str:
    alignment_words = {
        "A": "Any",
        "U": "Unaligned",
        "L": "Lawful",
        "N": "Neutral",
        "C": "Chaotic",
        "G": "Good",
        "E": "Evil"
    }

    if isinstance(alignment[0], str):
        if len(alignment) <= 2:
            # Very simple case, like "chaotic neutral", "any evil", etc.
            alignment_parts = []
            for char in alignment:
                alignment_parts.append(alignment_words.get(char, "X"))
            return " ".join(alignment_parts)
        else:
            # More complex; these are the "anything but" ones...
            alignments = {"E", "G", "C", "L", "NY", "NX"}
            alignment_set = set(alignment)
            if len(alignment) == 5:
                # Find the one that's missing
                missing = (alignments - alignment_set).pop()
                return f"Any Non-{alignment_words.get(missing)} Alignment"
            elif len(alignment) == 4:
                # Determine which axis is allowed
                if {"E", "G"} < alignment_set:
                    if "C" in alignment_set:
                        return "Any Chaotic Alignment"
                    elif "L" in alignment_set:
                        return "Any Lawful Alignment"
                elif {"L", "C"} < alignment_set:
                    if "E" in alignment_set:
                        return "Any Evil Alignment"
                    elif "G" in alignment_set:
                        return "Any Good Alignment"
            elif alignment_set == {"NX", "NY", "N"}:
                # Usually this is represented by ["A", "N"], but currently there's exactly ONE
                #   monster that uses this godforsaken notation
                return "Any Neutral Alignment"
    elif isinstance(alignment[0], dict):
        if len(alignment) == 1:
            if alignment_str := alignment[0].get("special"):
            # Ex: [{'special': "as the eidolon's alignment"}]
                return alignment_str

        if all("alignment" in item for item in alignment):
        # Ex: [{'alignment': ['C', 'G'], 'chance': 75}, {'alignment': ['N', 'E'], 'chance': 25}]
        #     [{'alignment': ['C', 'G'], 'note': 'chaotic evil when fully possessed'}]
            alignment_strs = []
            for item in alignment:
                s = get_alignment_string(item["alignment"])
                if chance := item.get("chance"):
                    s += f" ({chance}%)"
                if note := item.get("note"):
                    s += f" ({note})"
                alignment_strs.append(s)
            return ", ".join(alignment_strs[:-1]) + " or " + alignment_strs[-1]
    
    raise ValueError(f"Invalid alignment: {alignment}")


def get_cr(cr: str | dict) -> str:
    """Fetch the CR string and return it."""
    if isinstance(cr, str):
        return cr
    if isinstance(cr, dict):
        # Ex. cr = {"cr": "1", "xp": "100"}
        return cr["cr"]
    raise TyperError(f"Unexpected type '{type(cr).__name__}")


def get_damage_mods(spec: list[str|dict]) -> list[Scalar]:
    """Converts a list of damage/condition vulnerabilities/resistsences/immunities."""
    if not spec:
        return []
    items = []
    for item in spec:
        if isinstance(item, str):
            items.append(Scalar(item))
        elif isinstance(item, dict):
            # the key could be "vulnerable", "resist", or "immune"
            val = item.get("vulnerable") or item.get("resist") or item.get("immune")
            note = item.get("note")
            items.append(Scalar(val, note))
        else:
            raise TypeError(f"Unexpected type '{type(item).__name__}'")
    return items


def get_size_string(size_spec: list[str]) -> str:
    return {
        "G": "Gargantuan",
        "H": "Huge",
        "L": "Large",
        "M": "Medium",
        "S": "Small",
        "T": "Tiny"
    }.get(size_spec[0])


def get_speed(speed_spec):
    args = {}
    for x in ("walk", "fly", "burrow", "swim", "climb"):
        if x not in speed_spec:
            continue
        if isinstance(speed_spec[x], int):
            args[x] = Scalar(speed_spec[x])
        else:
            args[x] = Scalar(speed_spec[x]["number"], speed_spec[x]["condition"])
    if "canHover" in speed_spec:
        args["can_hover"] = speed_spec["canHover"]
    s = Speed(**args)
    return s


def get_xp(cr: str) -> int:
    return {
        "0": 10,
        "1/8": 25,
        "1/4": 50,
        "1/2": 100,
        "1": 200,
        "2": 450,
        "3": 700,
        "4": 1100,
        "5": 1800,
        "6": 2300,
        "7": 2900,
        "8": 3900,
        "9": 5000,
        "10": 5900,
        "11": 7200,
        "12": 8400,
        "13": 10000,
        "14": 11500,
        "15": 13000,
        "16": 15000,
        "17": 18000,
        "18": 20000,
        "19": 22000,
        "20": 25000,
        "21": 33000,
        "22": 41000,
        "23": 50000,
        "24": 62000,
        "25": 75000,
        "26": 90000,
        "27": 105000,
        "28": 120000,
        "29": 135000,
        "30": 155000
    }.get(cr, 0)

@click.group()
def cli():
    pass

@cli.command()
@click.option("--outfile", "-o", default=DEFAULT_RAW, type=click.Path(writable=True, path_type=Path))
def get(outfile: Path):
    if not outfile.is_absolute():
        outfile = Path(__file__).parent / outfile
    if outfile.is_dir():
        outfile /= "raw_monsters.json"
    urls = [
        "https://5e.tools/data/bestiary/bestiary-ai.json",
        "https://5e.tools/data/bestiary/bestiary-bam.json",
        "https://5e.tools/data/bestiary/bestiary-bgdia.json",
        "https://5e.tools/data/bestiary/bestiary-cm.json",
        "https://5e.tools/data/bestiary/bestiary-cos.json",
        "https://5e.tools/data/bestiary/bestiary-dc.json",
        "https://5e.tools/data/bestiary/bestiary-dip.json",
        "https://5e.tools/data/bestiary/bestiary-dmg.json",
        "https://5e.tools/data/bestiary/bestiary-dosi.json",
        "https://5e.tools/data/bestiary/bestiary-dsotdq.json",
        "https://5e.tools/data/bestiary/bestiary-erlw.json",
        "https://5e.tools/data/bestiary/bestiary-esk.json",
        "https://5e.tools/data/bestiary/bestiary-ftd.json",
        "https://5e.tools/data/bestiary/bestiary-ggr.json",
        "https://5e.tools/data/bestiary/bestiary-gos.json",
        "https://5e.tools/data/bestiary/bestiary-hol.json",
        "https://5e.tools/data/bestiary/bestiary-hotdq.json",
        "https://5e.tools/data/bestiary/bestiary-idrotf.json",
        "https://5e.tools/data/bestiary/bestiary-jttrc.json",
        "https://5e.tools/data/bestiary/bestiary-kkw.json",
        "https://5e.tools/data/bestiary/bestiary-lmop.json",
        "https://5e.tools/data/bestiary/bestiary-lox.json",
        "https://5e.tools/data/bestiary/bestiary-mm.json",
        "https://5e.tools/data/bestiary/bestiary-mpmm.json",
        "https://5e.tools/data/bestiary/bestiary-mot.json",
        "https://5e.tools/data/bestiary/bestiary-mtf.json",
        "https://5e.tools/data/bestiary/bestiary-oota.json",
        "https://5e.tools/data/bestiary/bestiary-oow.json",
        "https://5e.tools/data/bestiary/bestiary-phb.json",
        "https://5e.tools/data/bestiary/bestiary-pota.json",
        "https://5e.tools/data/bestiary/bestiary-rot.json",
        "https://5e.tools/data/bestiary/bestiary-scc.json",
        "https://5e.tools/data/bestiary/bestiary-sdw.json",
        "https://5e.tools/data/bestiary/bestiary-skt.json",
        "https://5e.tools/data/bestiary/bestiary-slw.json",
        "https://5e.tools/data/bestiary/bestiary-tce.json",
        "https://5e.tools/data/bestiary/bestiary-tftyp.json",
        "https://5e.tools/data/bestiary/bestiary-toa.json",
        "https://5e.tools/data/bestiary/bestiary-vgm.json",
        "https://5e.tools/data/bestiary/bestiary-vrgr.json",
        "https://5e.tools/data/bestiary/bestiary-xge.json",
        "https://5e.tools/data/bestiary/bestiary-wbtw.json",
        "https://5e.tools/data/bestiary/bestiary-wdh.json",
        "https://5e.tools/data/bestiary/bestiary-wdmm.json",
        "https://5e.tools/data/bestiary/bestiary-kftgv.json",
        "https://5e.tools/data/bestiary/bestiary-bgg.json",
        "https://5e.tools/data/bestiary/bestiary-pabtso.json",
        "https://5e.tools/data/bestiary/bestiary-mpp.json",
        "https://5e.tools/data/bestiary/bestiary-tofw.json",
        "https://5e.tools/data/bestiary/bestiary-bmt.json",
        "https://5e.tools/data/bestiary/bestiary-ditlcot.json",
        "https://5e.tools/data/bestiary/bestiary-veor.json",
        "https://5e.tools/data/bestiary/bestiary-qftis.json",
        "https://5e.tools/data/bestiary/bestiary-xphb.json",
        "https://5e.tools/data/bestiary/bestiary-xdmg.json",
        "https://5e.tools/data/bestiary/bestiary-egw.json",
    ]

    # If you try to fetch the URLs above, you get a "Please wait" HTML response, and presumably 
    # some JS code that loads the JSON data async then serves it. In the browser, I see only JSON,
    # but fetching those URLs in cURL or requests just gives me HTML. Thus, I have to use selenium
    # to actually get the data 🥲
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    opts = Options()
    opts.headless = True
    os.environ["MOZ_HEADLESS"] = "1"
    driver = webdriver.Firefox(options=opts)
    monsters = []
    for url in urls:
        try:
            driver.get("view-source:" + url)
            import time
            time.sleep(0)
            data = json.loads(driver.find_element(By.TAG_NAME, "pre").text)
        except Exception as e:
            print(f"Unable to load URL {url}: {repr(e)}")
            with open("errors.txt", "a") as f:
                f.write(driver.page_source)
            continue
        monsters += data["monster"]
    driver.close()

    with outfile.open("w") as f:
        json.dump(monsters, f)


@cli.command("convert")
@click.option("--infile", "-i", default=DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert(infile: Path, outfile: Path):
    if not infile.is_absolute():
        infile = Path(__file__).parent / infile
    if not outfile.is_absolute():
        outfile = Path(__file__).parent.parent / "dmtoolkit" / "api" / "data" / outfile
    
    if infile.is_dir():
        infile /= "raw_monsters.json"
    if outfile.is_dir():
        outfile /= "monsters.json"
    
    with infile.open("r") as f:
        monsters = json.load(f)
        monsters_dict: dict[str, dict[str, Any]] = {}
        monsters_to_copy: dict[str, dict[str, Any]] = {}
        converted_monsters = []
        for monster in monsters:
            key = f"{monster.get('name')}-{monster.get('source')}"
            monsters_dict[key] = monster
            try:
                if key in IGNORE_MONSTERS:
                    continue
                if "_copy" in monster:
                    monsters_to_copy[key] = monster
                    continue
                if converted_monster := convert_monster(monster):
                    converted_monsters.append(converted_monster)
            except Exception as e:
                print(json.dumps(monster))
                raise e
        
        # Process copied monsters
        copy_monster_keys = set(monsters_to_copy.keys())
        n_iter = 0
        while len(copy_monster_keys) > 0 or n_iter < 1000:
            n_iter += 1 # Loop counter
            for new_monster_key, copy_spec in monsters_to_copy.items():
                if new_monster_key not in copy_monster_keys:
                    # Means we've already copied it in a previous iteration
                    continue
                try:
                    src_monster_key = f"{copy_spec['_copy'].get('name')}-{copy_spec['_copy'].get('source')}"
                    if src_monster_key in copy_monster_keys:
                        # Means the source of this monster is another monster
                        continue
                    # Else, we can copy this guy
                    old = monsters_dict.get(src_monster_key)
                    if not old:
                        raise ValueError(
                            f"Unable to copy '{new_monster_key}'; "
                            f"no target with key '{src_monster_key}'"
                        )
                    new_monster = copy_monster(old, copy_spec)
                    if converted_monster := convert_monster(new_monster):
                        converted_monsters.append(converted_monster)
                    copy_monster_keys.remove(new_monster_key)
                except Exception as e:
                    print(json.dumps(copy_spec))
                    raise e

    
    with outfile.open("w") as f:
        dump_json(converted_monsters, f)

@cli.command("test")
@click.option("--infile", "-i", default=DEFAULT_CONV, type=click.Path(exists=True, path_type=Path))
def test(infile: Path):
    if not infile.is_absolute():
        infile = Path(__file__).parent.parent / "dmtoolkit" / "api" / "data" / infile

    if infile.is_dir():
        infile /= "monsters.json"
    
    with infile.open("r") as f:
        load_json(f)


@cli.command("all")
def full():
    get()
    convert()
    test()


if __name__ == "__main__":
    cli()