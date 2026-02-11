import random
import re

from dmtoolkit.api.models import Monster
from dmtoolkit.api.items import get_item
from dmtoolkit.modules.models import LootResponse, ItemWrapper

def loot(monster: Monster) -> LootResponse:
    """Basic, custom approach to enemy loot."""
    # Very basic initial approach: we just convert XP to money
    coinage = int(random.gauss(monster.xp, monster.xp/4))

    item_set = {}
    for entry in (monster.traits or []):
        for item_id in re.finditer(r"{@item (.*?)}", str(entry.body)):
            item = get_item(item_id.group(1))
            if item:
                item_set[item.id] = item
    
    # Grab weapon
    for entry in monster.actions or []:
        # Only drop usable item 1 in 10 times
        if random.random() > 1/10:
            continue
        if item := get_item(entry.title):
            item_set[item.id] = item
    
    # Grab Armor
    for ac_entry in monster.ac:
        for item_id in re.finditer(r"{@item (.*?)}", str(ac_entry.note)):
            if random.random() > 1/10:
                continue
            if item := get_item(item_id.group(1)):
                item_set[item.id] = item
    
    return LootResponse([ItemWrapper(item, 1) for item in item_set], coinage)