"""Modules for Kibble's Crafting Guide"""

from dmtoolkit.modules.models import Module
from dmtoolkit.modules.kibbles.loot import loot as generate_loot

kcg_module = Module(
    module_id = "kcg",
    name = "Kibble's Crafting Guide",
    description = "Kibble's Crafting Guide contains a set of recipes, items, and loot tables to "
    "implement a full crafting system within your game. The Guide defines a wide array of item "
    "types players can make, ranging from potions and poisons, to spell scrolls and wands, to "
    "weapons and armour, to finely cooked meals. Enabling this module will override the default "
    "encounter loot tables to drop crafting materials instead."
)
kcg_module.register_loot_generator(generate_loot)