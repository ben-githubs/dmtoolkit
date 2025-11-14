import json
import random
import re

from flask import Blueprint, render_template, render_template_string, request

from dmtoolkit.api.classes import get_class
from dmtoolkit.api.items import get_item
from dmtoolkit.api.monsters import get_monster, get_monster_names
from dmtoolkit.api.players import list_players, get_player
from dmtoolkit.api.races import get_race
from dmtoolkit.api.spells import get_spell

tracker_bp = Blueprint(
    "tracker_bp",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/inittracker/static"
)

@tracker_bp.route("/", methods=["GET"])
def tracker():
    """Tracker Page"""
    page = {
        "title": "DMTTools - Init Tracker"
    }
    monsters = get_monster_names()
    monster = get_monster("Poltergeist-MM")
    return render_template(
        "tracker.jinja2",
        page = page,
        monsters = monsters,
        players = list_players(),
        monster = monster
    )

@tracker_bp.route("/api/monsters", methods=["GET"])
def get_monster_page():
    name = request.args.get("name")
    monster = get_monster(name)
    return json.dumps(monster)

@tracker_bp.route("/api/monsters-combat-overview", methods=["GET"])
def get_monster_combat_overview():
    name = request.args.get("name")
    monster = get_monster(name)
    ac = monster.ac[0].value
    hp = monster.hp.average
    init_mod = int(monster.dexterity) // 2 - 5
    pp = monster.passive
    if not pp:
        if perception_mod := monster.skills.get("perception"):
            pp = 10 + perception_mod
        else:
            wis_mod = int(monster.wisdom) // 2 - 5
            pp = 10 + wis_mod
        
    # Very basic initial approach: we just convert XP to money
    total = int(random.gauss(monster.xp, monster.xp/4))
    # Exchange copper pieces for silver and gold
    gp = total // 100
    sp = (total - gp*100) // 10
    cp = total % 10

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

    return json.dumps({
        "name": monster.name,
        "ac": ac,
        "hp": hp,
        "initMod": init_mod,
        "xp": monster.xp,
        "pp": pp,
        "dead": False,
        "flag_xp": True,
        "flag_loot": True,
        "loot": {
            "total": total,
            "cp": cp,
            "sp": sp,
            "gp": gp,
            "items": [item.id() for item in item_set.values()]
        },
        "statuses": []
    })

@tracker_bp.app_template_filter("ordinal")
def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

@tracker_bp.route("/statblock/<id>", methods=["GET"])
def get_statblock_html(id: str):
    if id.endswith('.player'):
        name = id[:-7]
        player = get_player(name)
        if not player:
            return f"Unable to find player with name '{name}'."
        race = get_race(player.race_id) 
        class_ = get_class(player.class_id)
        subclass= [c for c in class_.subclasses if c.name == player.subclass_id]
        if subclass:
            subclass = subclass[0]
        else:
            subclass = {}
        
        return render_template("player-statblock.jinja2", player=player, race=race, class_=class_, subclass=subclass)
    
    monster = get_monster(id)
    if not monster:
        return f"Unable to find data for '{id}'"
    
    return render_template("statblock.jinja2", monster=monster)

@tracker_bp.route("/lootblock", methods=["POST"])
def get_loot_statblock():
    raw_loot = request.json or {}
    loot = {
        "coinage": {},
        "items": [f"{{@item {item}}}" for item in raw_loot["items"]]
    }
    gp = raw_loot["coinage"] // 100
    sp = (raw_loot["coinage"] % 100) // 10 
    cp = raw_loot["coinage"] % 10
    if gp > 0:
        loot["coinage"]["GP"] = gp
    if sp > 0:
        loot["coinage"]["SP"] = sp
    if cp > 0:
        loot["coinage"]["CP"] = sp
    loot["approximate_coinage"] = f"{gp} GP" if gp > 0 else f"{sp} SP" if sp > 0 else f"{cp} CP"
    return render_template("loot-statblock.jinja2", loot=loot)


@tracker_bp.route("/tooltips/spells/<spell_name>", methods=["GET"])
def get_spell_tooltip(spell_name: str):
    spell = get_spell(spell_name)
    return render_template("spell-statblock.jinja2", spell=spell)

@tracker_bp.route("/tooltips/items/<item_name>", methods=["GET"])
def get_item_tooltip(item_name: str):
    item = get_item(item_name)
    return render_template("item-statblock.jinja2", item=item)

@tracker_bp.route("/tooltips/conditions/<condition>")
def get_condition_tooltip(condition: str):
    return "A condition " + condition