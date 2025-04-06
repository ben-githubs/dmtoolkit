from dmtoolkit.inittracker.api import MONSTERS
fields = set()
for m in MONSTERS.values():
    fields |= set(m.get("speed", {}).keys())

for s in fields:
    print(s)