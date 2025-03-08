from collections import defaultdict
from dataclasses import dataclass, asdict
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

MONSTERS: dict = {}
PLAYERS: list = []

def load_monsters():
    monsters = dict()
    for fname in (DATA_DIR / "monsters").glob("*.json"):
        with fname.open('r') as f:
            contents = json.load(f)
        for monster in contents.get("monster"):
            key = f"{monster.get('name')}-{monster.get('source')}"
            if not key:
                continue # Skip cases where there's no monster name or source
            # Calculte Monster Size
            monster["sizeStr"] = {
                "G": "Gargantuan",
                "H": "Huge",
                "L": "Large",
                "M": "Medium",
                "S": "Small",
                "T": "Tiny"
            }.get(monster.get("size", ["M"])[0])

            # Calculate XP and add to statblock
            cr = monster.get("cr")
            if isinstance(cr, dict):
                cr = cr.get("cr")
            monster["xp"] = {
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
            monsters[key] = monster
            monster["acStr"] = str(calc_ac_str(monster))

    return monsters


def get_monster(monster_name: str) -> dict:
    monster = MONSTERS.get(monster_name)
    if not monster:
        return None
    
    if alignment := monster.get("alignment"):
        monster["alignmentStr"] = calc_alignment(alignment)
    
    return monster


def get_monster_names() -> list[tuple[str, str]]:
    """Returns a list of monster IDs and their display names."""
    namelist = []
    for monster_id, monster in MONSTERS.items():
        namelist.append((monster_id, monster.get("name", "UNKNOWN NAME")))
    return namelist

def calc_alignment(alignment: list[str|dict]):
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
                        return "Any Goof Alignment"
    elif isinstance(alignment[0], dict):
        if len(alignment) == 1:
            if alignment_str := alignment[0].get("special"):
            # Ex: [{'special': "as the eidolon's alignment"}]
                return alignment_str
        else:
            if all("alignment" in item for item in alignment):
            # Ex: [{'alignment': ['C', 'G'], 'chance': 75}, {'alignment': ['N', 'E'], 'chance': 25}]
                alignment_strs = []
                for item in alignment:
                    s = calc_alignment(item["alignment"])
                    if chance := item.get("chance"):
                        s += f" ({chance}%)"
                    alignment_strs.append(s)
                return ", ".join(alignment_strs[:-1]) + " or " + alignment_strs[-1]
    
    return ValueError(f"Invalid alignment: {alignment}")

def calc_ac_str(monster) -> str:
    ac = monster.get("ac")
    if isinstance(ac, int) or isinstance(ac, str):
        return str(ac)
    elif isinstance(ac, list):
        if len(ac) == 1:
            ac = ac[0]
            if isinstance(ac, int):
                return str(ac)
            elif isinstance(ac, dict):
                ac_str = ""
                if "ac" in ac:
                    ac_str = str(ac["ac"])
                sources = []
                for item in ac.get("from", []):
                    sources.append(str(item))
                if sources:
                    ac_str += f" ({', '.join(sources)})"
                return ac_str

# -- NO FUNCTION DEFINITIONS PAST HERE
if not MONSTERS:
    MONSTERS = load_monsters()