import asyncio
import pickle
import random
import uuid
from dataclasses import dataclass, field
from typing import Dict

from shared import Events, CharacterInfo

PORT = 6000
SERVER = '127.0.0.1'

@dataclass
class GameScene:
    characters: Dict[str, CharacterInfo] = field(default_factory=dict)


game_scene = GameScene()


class GameServer(asyncio.Protocol):
    def __init__(self):
        super(GameServer, self).__init__()
        self.transport = {}
        self.__loop = asyncio.get_event_loop()
        self.__loop.call_later(1, self.check_connection)

    def connection_made(self, transport):
        client = transport.get_extra_info('peername')
        print('Connection from {}'.format(client))
        player_id = str(uuid.uuid4())
        color = f"#{random.randint(0, 255 ** 3):06X}"
        player_char = CharacterInfo(player_id, color=color)
        self.transport[player_id] = transport
        game_scene.characters[player_id] = player_char
        self.transport[player_id].write(pickle.dumps([Events.update_id, player_id, color]))

    def data_received(self, data):
        message = pickle.loads(data)
        print(message)
        player_id, x, y = message[1:]
        if player_id == 0:
            return
        game_scene.characters[player_id].x = x
        game_scene.characters[player_id].y = y
        update = [Events.char_pos]
        for key, char_info in game_scene.characters.items():
            update.append(char_info)
        self.transport[player_id].write(pickle.dumps(update))
        print("Updates sent")
        print(f'Send: {update}')

    def check_connection(self):
        for player_id, transport in list(self.transport.items()):
            if transport.is_closing():
                del game_scene.characters[player_id]
                del self.transport[player_id]
        self.__loop.call_later(1, self.check_connection)


async def main():
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: GameServer(), SERVER, PORT)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
