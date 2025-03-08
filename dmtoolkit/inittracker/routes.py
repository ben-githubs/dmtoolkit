import json

from flask import Blueprint, render_template, request

import dmtoolkit.inittracker.api as api
from dmtoolkit.api.players import list_players

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
    monsters = api.get_monster_names()
    monster = api.get_monster("Poltergeist-MM")
    return render_template(
        "tracker.jinja2",
        page = page,
        monsters = monsters,
        players = list_players(),
        monster = monster
    )

@tracker_bp.route("/api/monsters", methods=["GET"])
def get_monster():
    name = request.args.get("name")
    monster = api.get_monster(name)
    return json.dumps(monster)

@tracker_bp.route("/api/monsters-combat-overview", methods=["GET"])
def get_monster_combat_overview():
    name = request.args.get("name")
    monster = api.get_monster(name)
    ac = monster.get("ac")
    if isinstance(ac, list):
        ac = ac[0]
    if isinstance(ac, dict):
        ac = ac.get("ac")
    hp = monster.get("hp")
    if isinstance(hp, dict):
        hp = hp.get("average")
    init_mod = int(monster.get("dex")) // 2 - 5
    pp = monster.get("passive")
    if not pp:
        if perception_mod := monster.get("skill", {}).get("perception"):
            pp = 10 + perception_mod
        else:
            wis_mod = int(monster.get("wis")) // 2 - 5
            pp = 10 + wis_mod
    return json.dumps({
        "name": monster["name"],
        "ac": ac,
        "hp": hp,
        "initMod": init_mod,
        "xp": monster.get("xp"),
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
    # Assume it's a monster
    # TODO: Add statblocks for players
    monster = api.get_monster(id)
    if not monster:
        return f"Preview Unavailable for {id}"
    
    return render_template("statblock.jinja2", monster=monster)