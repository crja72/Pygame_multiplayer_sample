import pickle
import select
import socket
import sys

import pygame
import pygame.locals as pyloc

from shared import CharacterInfo, Events

# region Constants
WIDTH = 400
HEIGHT = 400
BUFFERSIZE = 2048
SERVER = '127.0.0.1'
PORT = 6000
SPRITE_WIDTH = 50
SPRITE_HEIGHT = 50
BACKGROUND = "#000000"
# endregion

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Simple multiplayer')

clock = pygame.time.Clock()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER, PORT))


class Character:
    def __init__(self, player_id, x, y, color):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.id = player_id
        self.color = color
        self.sprite = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT))
        self.sprite.fill(self.color)

    def start_movement(self, key):
        if key not in {pyloc.K_LEFT, pyloc.K_RIGHT, pyloc.K_UP, pyloc.K_DOWN}:
            return
        if event.key == pyloc.K_LEFT:
            main_hero.vx = -10
        elif event.key == pyloc.K_RIGHT:
            main_hero.vx = 10
        elif event.key == pyloc.K_UP:
            main_hero.vy = -10
        elif event.key == pyloc.K_DOWN:
            main_hero.vy = 10

    def stop_movement(self, key):
        if key not in {pyloc.K_LEFT, pyloc.K_RIGHT, pyloc.K_UP, pyloc.K_DOWN}:
            return
        if key == pyloc.K_LEFT and self.vx == -10:
            self.vx = 0
        if key == pyloc.K_RIGHT and self.vx == 10:
            self.vx = 0
        if key == pyloc.K_UP and self.vy == -10:
            main_hero.vy = 0
        if key == pyloc.K_DOWN and self.vy == 10:
            self.vy = 0

    def get_server_params(self, player_id, color):
        self.id = player_id
        self.color = color
        self.sprite.fill(self.color)

    def get_info(self):
        return self.id, self.x, self.y

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x > WIDTH - SPRITE_WIDTH:
            self.x = WIDTH - SPRITE_WIDTH
        if self.x < 0:
            self.x = 0
        if self.y > HEIGHT - SPRITE_HEIGHT:
            self.y = HEIGHT - SPRITE_HEIGHT
        if self.y < 0:
            self.y = 0

    def render(self):
        screen.blit(self.sprite, (self.x, self.y))

    @classmethod
    def from_character_info(cls, info: CharacterInfo):
        return Character(info.owner_id, info.x, info.y, info.color)


main_hero = Character(0, 50, 50, "#ffffff")

characters = []

while True:
    ins, outs, ex = select.select([client_socket], [], [], 0)
    for inm in ins:
        game_event = pickle.loads(inm.recv(BUFFERSIZE))
        if game_event[0] == Events.update_id:
            main_hero.get_server_params(game_event[1], game_event[2])
        if game_event[0] == Events.char_pos:
            game_event.pop(0)
            characters = []
            for character_info in game_event:
                if character_info.owner_id != main_hero.id:
                    characters.append(Character.from_character_info(character_info))

    for event in pygame.event.get():
        if event.type == pyloc.QUIT:
            pygame.quit()
            client_socket.close()
            sys.exit()
        if event.type == pyloc.KEYDOWN:
            main_hero.start_movement(event.key)
        if event.type == pyloc.KEYUP:
            main_hero.stop_movement(event.key)

    clock.tick(60)
    screen.fill(BACKGROUND)

    main_hero.update()

    for character in characters:
        character.render()

    main_hero.render()

    pygame.display.flip()
    game_event = [Events.pos_upd, *main_hero.get_info()]
    client_socket.send(pickle.dumps(game_event))
