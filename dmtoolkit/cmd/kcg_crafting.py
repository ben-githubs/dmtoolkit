import json
from pathlib import Path
import re

from dmtoolkit.api.items import find_item_by_name

DATA_DIR = Path(__file__).parent / "kibbles"
TARGET_FILE = Path(__file__).parent.parent / "modules/kibbles/recipes.json"

# Some items are written in such a way that programatically parsing them is a pain, and it's 
#   easier to do them manually. We put the names of them here so the code knows to skip them.
IGNORE_NAMES = [
    "Sticky Goo PotionK", # Has 2 recipes
    "Manacles", # Material has brackers in it "chain (5 feet) which is just a PITA to code around"
    "Carpet of Flying, 4 ft. × 6 ft.", # Has numbers in the name, regex no like it
    "Mantle of the Mind", # Doesn't appear to be a real item not; not listed anywhere
]

def read_file(fname: Path, crafting_type: str) -> list[dict]:
    with fname.open("r") as f:
        contents = " ".join([s.strip() for s in f.readlines()])
        contents = re.sub(r"\x01", "", contents)
    lines = re.sub(r"((?:common|uncommon|rare|very rare|legendary) [\d,]+ )(gp)", r"\1gp\n", contents).split("\n")

    p = r"(?:(?P<item_amt1>\d+) x )?(?P<item_name>(?:\+\d )?[^\s\d]+(?:\s[^\s\d\[]+)*)\s*(?P<note>\[[^\]]*\])?\s*(?: \((?P<item_amt2>[\w\s]+)\))?\s(?P<materials>(?:[\.\d,]+\s\+?[\d,]*[A-Za-z’\-\(\)\/\s]+)+)(?P<time>\d+\shours?(?:\s*\([\.\d]*\s\w+\))?)\s*(?P<num_checks>\d+)\s*(?:DC )?(?P<dc>\d+)\s*(?P<rarity>(?:[A-Za-z]+\s)+)\s*(?P<value>[\d,]+)\s?gp\s?"
    line_pattern = re.compile(p)
    # Split each line up
    recipes = []
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line or any(line.startswith(name) for name in IGNORE_NAMES):
            continue
        match = line_pattern.match(line)
        if not match:
            raise ValueError(f"Unable to parse item number {idx+1}: \"{line}\"")
        groups = match.groupdict()

        notes = []
        
        item_name = groups.get("item_name", "")
        item_id = item_name if "|" in item_name else ""
        if item_name.endswith("K"):
            item_name = item_name[:-1]
            item_id = f"{item_name}|kcg"
        elif item_name.endswith("GS"):
            continue # We don't support GS items yet
        elif item_name.endswith("TAG"):
            continue # We don't support TAG items yet
        elif item_name.endswith("DS"):
            continue # We don't support DS items yet
        elif item_name.endswith("S"):
            item_name = item_name[:-1]
            notes.append("Smelting ore requires specialized factilities. This can usually be accomplished in a fully equiped smithy, but consult your GM for where it might be appropriate. Adventurers rarely smelt their own ore, these are included primarily for informational purposes. Smelting magical ores may require more specialized facilities or locations.")
        
        if not item_id:
            item = find_item_by_name(item_name)
            if len(item) != 1:
                raise ValueError(f"Error in item {idx+1} ~ Found {len(item)} matches for '{item_name}' where 1 was expected: {item}")
            item_id = item[0].id()
        
        if note := groups.get("note"):
            notes.append(note)
        

        materials = []
        for m in re.finditer(r"(\d+)\s([A-Za-z\s]+)", groups.get("materials", "")):
            quantity, item = m.group(1), m.group(2)
            if item.startswith("gp"):
                if materials[-1][1].endswith("worth"):
                    # Means it's something like "1 diamond worth 100 gp"
                    materials[-1] = materials[-1][0], f"{materials[-1][1]} {quantity} {item}"
                    continue
                else:
                    # Means it's something like "300 gb worth of gems"
                    item = f"{quantity} {item}"
                    quantity = 1
            if item_obj := find_item_by_name(item):
                if len(item_obj) == 1:
                    item = item_obj[0].id()
            materials.append((int(quantity), item.strip()))


        time = groups.get("time", "")
        num_checks = int(groups.get("num_checks", "1"))
        dc = int(groups.get("dc", "10"))

        recipe = {
            "craft": crafting_type,
            "result": item_id,
            "quantity": groups.get("item_amt1") or groups.get("item_amt2") or "1",
            "materials": materials,
            "time": time,
            "num_checks": num_checks,
            "dc": dc,
            "note": note
        }
        recipes.append(recipe)
    
    return recipes

def convert_alchemy():
    return read_file(DATA_DIR / "raw_alchemy_recipes.txt", "alchemy")

def convert_poisoncraft():
    return read_file(DATA_DIR / "raw_poisoncraft_recipes.txt", "poisoncraft")

def convert_blacksmithing():
    return read_file(DATA_DIR / "raw_blacksmithing_recipes.txt", "blacksmithing")

def convert_cooking():
    return read_file(DATA_DIR / "raw_cooking_recipes.txt", "cooking")

def convert_enchanting():
    return read_file(DATA_DIR / "raw_enchanting_recipes.txt", "enchanting")

def convert_scrollscribing():
    return read_file(DATA_DIR / "raw_scrollscribing_recipes.txt", "scrollscribing")

def convert_wand_whittling():
    return read_file(DATA_DIR / "raw_wand_whittling_recipes.txt", "wand_whittling")

def convert_leatherworking():
    return read_file(DATA_DIR / "raw_leatherworking_recipes.txt", "leatherworking")

def hard_coded_recipes():
    return [
        {
            "craft": "alchemy",
            "result": "sticky goo potion|kcg",
            "quantity": 1,
            "materials": [
                [1, "finely-shredded scroll of web"],
                [1, "uncommon reactive reagent"],
                [1, "glass flask"]
            ],
            "time": "2 hours",
            "num_checks": 1,
            "dc": 14,
        },
        {
            "craft": "alchemy",
            "result": "sticky goo potion|kcg",
            "quantity": 1,
            "materials": [
                [2, "uncommon poisonous reagent"],
                [1, "uncommon reactive reagent"],
                [1, "glass flask"]
            ],
            "time": "2 hours",
            "num_checks": 1,
            "dc": 14,
        },
        {
            "craft": "blacksmithing",
            "result": "manacles|phb",
            "quantity": 1,
            "materials": [
                [1, "chain (5 feet)"],
                [5, "iron ingot"],
                [1, "lock"]
            ],
            "time": "2 hours",
            "num_checks": 1,
            "dc": 14,
        },
        {
            "craft": "enchanting",
            "result": "Carpet of Flying, 4 ft. × 6 ft.|dmg",
            "quantity": 1,
            "materials": [
                [1, "fancy carpet worth 1000 gp"],
                [1, "scroll of fly"],
                [1, "scroll of levitate"],
                [1, "scroll of animate objects"],
                [1, "very rare arcane essence"],
                [1, "very rare primal essence"]
            ],
            "time": "32  hours (4 days)",
            "num_checks": 16,
            "dc": 19,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 1st-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "common essence"],
                [1, "scroll of the spell"],
                [1, "common branch"]
            ],
            "time": "4 hours",
            "num_checks": 2,
            "dc": 12,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 2nd-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "common essence"],
                [1, "scroll of the spell"],
                [1, "common branch"]
            ],
            "time": "4 hours",
            "num_checks": 2,
            "dc": 14,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 3rd-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "uncommon essence"],
                [1, "scroll of the spell"],
                [1, "uncommon branch"]
            ],
            "time": "4 hours",
            "num_checks": 2,
            "dc": 15,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 4th-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "uncommon essence"],
                [1, "scroll of the spell"],
                [1, "uncommon branch"]
            ],
            "time": "4 hours",
            "num_checks": 2,
            "dc": 16,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 5th-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "rare essence"],
                [1, "scroll of the spell"],
                [1, "rare branch"]
            ],
            "time": "8 hours",
            "num_checks": 4,
            "dc": 16,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 6th-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "rare essence"],
                [1, "scroll of the spell"],
                [1, "rare branch"]
            ],
            "time": "8 hours",
            "num_checks": 4,
            "dc": 17,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 7th-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "very rare essence"],
                [1, "scroll of the spell"],
                [1, "very rare branch"]
            ],
            "time": "16 hours",
            "num_checks": 8,
            "dc": 17,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 8th-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "very rare essence"],
                [1, "scroll of the spell"],
                [1, "very rare branch"]
            ],
            "time": "16 hours",
            "num_checks": 8,
            "dc": 18,
        },
        {
            "craft": "wand_whittling",
            "result": "Lesser Wand of 9th-Level Spell",
            "quantity": 1,
            "materials": [
                [1, "legendary essence"],
                [1, "scroll of the spell"],
                [1, "legendary branch"]
            ],
            "time": "24 hours",
            "num_checks": 12,
            "dc": 20,
        }
    ]

def convert():
    recipes = (
        hard_coded_recipes() +
        # convert_alchemy() + 
        # convert_poisoncraft() + 
        # convert_blacksmithing() + 
        # convert_cooking() + 
        # convert_enchanting() + 
        # convert_scrollscribing() + 
        # convert_wand_whittling() + 
        convert_leatherworking()
    )
    with TARGET_FILE.open("w") as f:
        json.dump(recipes, f, indent=2)