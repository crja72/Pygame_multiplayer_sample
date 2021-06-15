from dataclasses import dataclass


class Events:
    update_id = 'update_id'
    char_pos = 'char_pos'
    pos_upd = 'pos_upd'


@dataclass
class CharacterInfo:
    owner_id: str
    color: str = "#ffffff"
    x: int = 50
    y: int = 50