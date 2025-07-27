from dataclasses import dataclass, asdict
from pathlib import Path

from flask import Response, request

from dmtoolkit.api.models import Player, Race
from dmtoolkit.api.serialize import load_json_string, dump_json_string

DATA_DIR = Path(__file__).parent / "data"

PLAYERS: list = []

def list_players() -> list[Player]:
   return load_json_string(request.cookies.get("players", "[]"))

def get_player(player_name: str) -> Player | None:
    for player in list_players():
        if player.name == player_name:
            return player

def create_player(response: Response, params: dict) -> Player:
    player = Player(**params)
    _save_players(response, list_players() + [player])
    return player

def delete_player(response: Response, player_name: str):
    players = [p for p in list_players() if p.name != player_name]
    _save_players(response, players)

def _save_players(response: Response, players: list[Player]) -> None:
    response.set_cookie("players", dump_json_string(players))
