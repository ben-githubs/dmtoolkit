from dataclasses import dataclass, asdict
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

PLAYERS: list = []

@dataclass
class Player:
    name: str
    hp: int
    ac: int
    pp: int
    
    enabled: bool = False


def _load_players() -> list[Player]:
    fname = DATA_DIR / "players.json"

    if not fname.exists():
        return []
    
    with fname.open('r') as f:
        players: list[dict] = json.load(f)
    
    return [Player(**spec) for spec in players]


def _save_players():
    global PLAYERS
    fname = DATA_DIR / "players.json"
    players = [asdict(player) for player in PLAYERS]
    with fname.open("w") as f:
        json.dump(players, f)
    

def get_player(name: str) -> Player:
    for player in list_players():
        if player.name == name:
            return player
    return None


def list_players() -> list[Player]:
    global PLAYERS
    if not PLAYERS:
        PLAYERS = _load_players()
    return PLAYERS.copy()


def create_player(**kwargs) -> Player:
    global PLAYERS
    if any(player.name == kwargs["name"] for player in PLAYERS):
        raise ValueError(f"Cannot create player; name '{kwargs['name']}' is already in use")
    player = Player(**kwargs)
    PLAYERS.append(player)
    _save_players()
    return player


def update_player(orig_name: str, **kwargs) -> Player:
    player = get_player(orig_name)
    if not player:
        create_player(**kwargs)
    
    # Raise error if we try to change the name of an existing player to a name already used by
    #   another player
    if "name" in kwargs and get_player(kwargs["name"]) and kwargs["name"] != orig_name:
        raise ValueError(f"Cannot change name to '{kwargs['name']}' as it is already in use")

    # Replace player item
    global PLAYERS
    for idx in range(len(PLAYERS)):
        if PLAYERS[idx] is player:
            new_player = Player(**(asdict(player) | kwargs))
            PLAYERS[idx] = new_player
            return new_player
    
    # Shouldn't ever reach this, so raise an error
    raise ValueError("Unable to update player")