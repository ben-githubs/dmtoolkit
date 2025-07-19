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
