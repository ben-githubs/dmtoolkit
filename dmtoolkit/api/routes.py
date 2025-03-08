from dataclasses import asdict
import json

from flask import Blueprint, request, abort

import dmtoolkit.api.players as players_api
from dmtoolkit.api import encounters

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


@api_bp.route("/encounters", methods=["GET"])
def list_encounters():
    return json.dumps(encounters.getall())


@api_bp.route("/encounters/<eid>", methods=["GET"])
def get_encounter(eid: str):
    return json.dumps(encounters.get(eid))


@api_bp.route("/encounters", methods=["POST", "PUT"])
def create_encounter():
    # breakpoint()
    encounter = request.json
    if not encounter or not isinstance(encounter, dict):
        return json.dumps({"error": "Invalid or null encounter value"}), 403
    eid = encounters.create_or_update(encounter)
    return json.dumps({"eid": eid})