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
        self.previous_choice = ""
        self.start_shuffle = False
        self.start_game = False
        self.shuffle_time = 0
        self.elapsed_time = 0
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
        self.draw_tiles()
        self.buttons_list = []
        self.buttons_list.append(Button(775, 100, 200, 50, "Shuffle", WHITE, BLACK))
        self.buttons_list.append(Button(775, 170, 200, 50, "Reset", WHITE, BLACK))
        self.buttons_list.append(Button(775, 240, 200, 50, "Solve", WHITE, BLACK))

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

    def shuffle(self):
        possible_moves = []
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                if tile.text == "empty":
                    if tile.right():
                        possible_moves.append("right")
                    if tile.left():
                        possible_moves.append("left")
                    if tile.up():
                        possible_moves.append("up")
                    if tile.down():
                        possible_moves.append("down")
                    break
            if len(possible_moves) > 0:
                break

        if self.previous_choice == "left":
            possible_moves.remove("right") if "right" in possible_moves else possible_moves
        elif self.previous_choice == "right":
            possible_moves.remove("left") if "left" in possible_moves else possible_moves
        elif self.previous_choice == "down":
            possible_moves.remove("up") if "up" in possible_moves else possible_moves
        elif self.previous_choice == "up":
            possible_moves.remove("down") if "down" in possible_moves else possible_moves

        choice = random.choice(possible_moves)
        self.previous_choice = choice
        if choice == "right":
            self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][
                                                                           col + 1], \
                                                                       self.tiles_grid[row][col]
        if choice == "left":
            self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][
                                                                           col - 1], \
                                                                       self.tiles_grid[row][col]
        if choice == "up":
            self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][
                                                                           col], \
                                                                       self.tiles_grid[row][col]
        if choice == "down":
            self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][
                                                                           col], \
                                                                       self.tiles_grid[row][col]

    def update(self):
        self.all_sprites.update()
        if self.start_shuffle:
            self.shuffle()
            self.draw_tiles()
            self.shuffle_time += 1
            if self.shuffle_time >= 100:
                self.start_shuffle = False

    def draw_grid(self):
        for row in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (row, 0), (row, GAMESIZE * TILESIZE))

        for col in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, col), (GAMESIZE * TILESIZE, col))

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        for button in self.buttons_list:
            button.draw(self.screen)
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        if tile.click(mouse_x, mouse_y):
                            if tile.right() and self.tiles_grid[row][col + 1] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][
                                                                                               col + 1], \
                                                                                           self.tiles_grid[row][col]

                            if tile.left() and self.tiles_grid[row][col - 1] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][
                                                                                               col - 1], \
                                                                                           self.tiles_grid[row][col]

                            if tile.up() and self.tiles_grid[row - 1][col] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][
                                                                                               col], \
                                                                                           self.tiles_grid[row][col]

                            if tile.down() and self.tiles_grid[row + 1][col] == 0:
                                print(tile.text)
                                self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][
                                                                                               col], \
                                                                                           self.tiles_grid[row][col]

                            self.draw_tiles()
                for button in self.buttons_list:
                    if button.click(mouse_x, mouse_y):
                        if button.text == "Reset":
                            self.new()
                        if button.text == "Shuffle":
                            self.shuffle_time = 0
                            self.start_shuffle = True


game = Game()
while True:
    game.new()
    game.run()
