from dataclasses import dataclass, asdict
import json
from pathlib import Path

from flask import Response, request

DATA_DIR = Path(__file__).parent / "data"

PLAYERS: list = []

@dataclass
class Player:
    name: str
    hp: int
    ac: int
    pp: int
    
    enabled: bool = False

def list_players() -> list[Player]:
    player_specs = json.loads(request.cookies.get("players", "[]"))
    return [Player(**spec) for spec in player_specs]

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
    response.set_cookie("players", json.dumps([asdict(player) for player in players]))
