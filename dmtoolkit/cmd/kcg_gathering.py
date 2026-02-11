from pathlib import Path
from collections import defaultdict
import csv

KCG_DATA_DIR = Path(__file__).parent.parent / "modules/kibbles/loot_tables"

def convert():
    gathering_tables: dict[str, list[dict[str, str]]] = defaultdict(list)
    with (KCG_DATA_DIR / "gathering.csv").open("r") as f:
        reader = csv.DictReader(f)
    
        for row in reader:
            gathering_tables[row["locale"]].append({
                "min": row["min"],
                "max": row["max"],
                "item": row["item"],
                "amt": row["quantity"],
                "gp": "",
                "sp": "",
                "cp": ""
            })
    
    for locale in gathering_tables.keys():
        rows = sorted(gathering_tables[locale], key=lambda x: x["min"])
        with (KCG_DATA_DIR / f"gathering_{locale}.csv").open("w") as f:
            writer = csv.DictWriter(f, fieldnames = rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)