from math import sqrt

import pygame
import random
import time

from Settings import *
from Sprite import *

Size = int(input("Enter your value: ")) + 1
GAMESIZE = int(sqrt(Size))

title = str((Size - 1)) + " Puzzle Game"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def create_game(self):
        grid = []
        numbers = 1
        for x in range(GAMESIZE):
            grid.append([])
            for y in range(GAMESIZE):
                grid[x].append(numbers)
                numbers += 1
        grid[-1][-1] = 0
        return grid

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.create_game()
        self_tiles_completed = self.create_game()

    def draw_tiles(self):
        self.tiles = []
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile in enumerate(x):
                if tile != 0:
                    self.tiles[row].append(Tile(self, col, row, str(tile)))
                else:
                    self.tiles[row].append(Tile(self, col, row, "empty"))

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

    def draw_grid(self):
        for row in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (row, 0), (row, GAMESIZE * TILESIZE))

        for col in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, col), (GAMESIZE * TILESIZE, col))

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        self.draw_tiles()
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)


game = Game()
while True:
    game.new()
    game.run()
