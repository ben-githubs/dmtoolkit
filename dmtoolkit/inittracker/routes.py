import json

from flask import Blueprint, render_template, request

from dmtoolkit.api.classes import get_class
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
    return json.dumps({
        "name": monster.name,
        "ac": ac,
        "hp": hp,
        "initMod": init_mod,
        "xp": monster.xp,
        "pp": pp
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

@tracker_bp.route("/tooltips/spells/<spell_name>", methods=["GET"])
def get_spell_tooltip(spell_name: str):
    spell = get_spell(spell_name)
    return render_template("spell-statblock.jinja2", spell=spell)
