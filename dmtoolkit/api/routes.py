from dataclasses import asdict
import json

from flask import Blueprint, request, make_response

import dmtoolkit.api.players as players_api
from dmtoolkit.api.models import Class
from dmtoolkit.api import races, classes
from dmtoolkit.api.serialize import dump_json_string


api_bp = Blueprint(
    "api_bp",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/api/static",
    url_prefix = "/api"
)


@api_bp.route("/players/<player_name>", methods=["GET"])
def get_player(player_name: str):
    player = players_api.get_player(player_name)
    if not player:
        return json.dumps(None)
    return json.dumps(asdict(player))


@api_bp.route("/players/list")
def list_players():
    player_list = [asdict(player) for player in players_api.list_players()]
    return json.dumps(player_list)


@api_bp.route("/races/<rid>", methods=["GET"])
def get_race(rid: str):
    race = races.get_race(rid)
    if not race:
        return json.dumps({"null"}), 404
    else:
        return json.dumps(race)

def _get_class(class_name: str) -> tuple[Class|str, int]:
    try:
        return classes.get_class(class_name), 200
    except KeyError:
        return "{null}", 404
    except Exception:
        return json.dumps(
            {"message": "An unknown error occured while processing your request."}
        ), 500


@api_bp.route("/classes/<class_name>", methods=["GET"])
def get_class(class_name: str):
    resp, code = _get_class(class_name)
    if code != 200:
        return str(resp), code
    return dump_json_string(resp), 200

@api_bp.route("/classes/<class_name>/subclasses", methods=["GET"])
def list_subclasses(class_name: str):
    resp, code = _get_class(class_name)
    if code != 200:
        return str(resp), code
    
    class_ = classes.get_class(class_name)
    return dump_json_string([c.name for c in class_.subclasses]), 200