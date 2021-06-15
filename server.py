import asyncore
import pickle
import random
import socket
import uuid
from dataclasses import dataclass, field
from typing import Dict

from shared import CharacterInfo, Events

BUFFERSIZE = 512
PORT = 6000


@dataclass
class GameScene:
    characters: Dict[str, CharacterInfo] = field(default_factory=dict)


clients_connected = []
game_scene = GameScene()


def update_world(message):
    if message is not None:
        data_arr = pickle.loads(message)
        print(data_arr)
        player_id = data_arr[1]
        x = data_arr[2]
        y = data_arr[3]
        if player_id == 0:
            return
        game_scene.characters[player_id].x = x
        game_scene.characters[player_id].y = y

    broken_clients = []

    for player_id, client in clients_connected:
        update = [Events.char_pos]

        for key, character_info in game_scene.characters.items():
            update.append(character_info)
        try:
            client.send(pickle.dumps(update))
        except OSError:
            broken_clients.append((player_id, client))
            continue
        print('обновления отправлены')

    for player_id, client in broken_clients:
        clients_connected.remove((player_id, client))
        del game_scene.characters[player_id]


class GameServer(asyncore.dispatcher):
    def __init__(self, port=PORT):
        super(GameServer, self).__init__()
        self.create_socket(socket.AF_INET,
                           socket.SOCK_STREAM)  # сказать про семейство адресов, сказать про поток/датаграммы
        self.bind(('', port))
        self.listen(5)

    def handle_accept(self) -> None:
        conn, addr = self.accept()
        print(f"Подключился клиент с адреса {addr[0]} {addr[1]}")
        player_id = str(uuid.uuid4())
        clients_connected.append((player_id, conn))
        color = f'#{random.randint(0, 255 ** 3):06X}'
        player_character = CharacterInfo(player_id, color=color)
        game_scene.characters[player_id] = player_character
        conn.send(pickle.dumps([Events.update_id, player_id, color]))
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        received_data = self.recv(BUFFERSIZE)
        if received_data:
            update_world(received_data)
        else:
            self.close()


if __name__ == '__main__':
    GameServer()
    asyncore.loop()
