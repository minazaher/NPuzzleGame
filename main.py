import math
from copy import deepcopy

import pygame
import random
import time
from sprite import *
from settings import *
from solver import *


class Game:
    def __init__(self, size):
        self.tiles_grid = [[]]
        self.game_size = int(math.sqrt(size + 1))
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH + size * 10, HEIGHT + size * 3))
        pygame.display.set_caption(str(size) + " Puzzle")
        self.clock = pygame.time.Clock()
        self.shuffle_time = 0
        self.start_shuffle = False
        self.previous_choice = ""
        self.start_game = False
        self.start_timer = False
        self.solve = False
        self.solve_epochs = 0
        self.elapsed_time = 0
        self.timer = 0


        # self.high_score = float(self.get_high_scores()[0])
        self.visited = []
        self.path = []
        self.empty_tile = (-1, -1)
        self.frontier = []
    #
    # def get_high_scores(self):
    #     with open("high_score.txt", "r") as file:
    #         scores = file.read().splitlines()
    #     return scores
    #
    # def save_score(self):
    #     with open("high_score.txt", "w") as file:
    #         file.write(str("%.3f\n" % self.high_score))

    def create_game(self):
        grid = [[x + y * self.game_size for x in range(1, self.game_size + 1)] for y in range(self.game_size)]
        grid[-1][-1] = 0
        return grid

    def get_possible_moves(self, row, col):
        possible_moves = []
        if self.tiles[row][col].left():
            possible_moves.append("left")
        if self.tiles[row][col].right():
            possible_moves.append("right")
        if self.tiles[row][col].up():
            possible_moves.append("up")
        if self.tiles[row][col].down():
            possible_moves.append("down")
        return possible_moves

    def get_empty_tile(self):
        for row, x in enumerate(self.tiles_grid):
            for col, tile in enumerate(x):
                if tile == 0:
                    return row, col

    def apply_choice(self, choice):
        row,  col = self.get_empty_tile()
        if choice not in self.get_possible_moves(row, col):
            return
        if choice == "right":
            self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], \
                                                                       self.tiles_grid[row][col]
        elif choice == "left":
            self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], \
                                                                       self.tiles_grid[row][col]
        elif choice == "up":
            self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], \
                                                                       self.tiles_grid[row][col]
        elif choice == "down":
            self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], \
                                                                   self.tiles_grid[row][col]
    def move(self, move):
        grid = deepcopy(self.tiles_grid)
        return self.get_apply_choice(move, self.empty_tile[0], self.empty_tile[1], grid)

    def get_apply_choice(self, x, row, col, tiles_grid):
        if x == "right":
            tiles_grid[row][col], tiles_grid[row][col + 1] = tiles_grid[row][col + 1], \
                                                             tiles_grid[row][col]
        elif x == "left":
            tiles_grid[row][col], tiles_grid[row][col - 1] = tiles_grid[row][col - 1], \
                                                             tiles_grid[row][col]
        elif x == "up":
            tiles_grid[row][col], tiles_grid[row - 1][col] = tiles_grid[row - 1][col], \
                                                             tiles_grid[row][col]
        elif x == "down":
            tiles_grid[row][col], tiles_grid[row + 1][col] = tiles_grid[row + 1][col], \
                                                             tiles_grid[row][col]
        return tiles_grid

    def make_move(self, selector, shuffle=False):
        possible_moves = []
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                if tile.text == "empty":
                    self.empty_tile = (row, col)
                    for move in self.get_possible_moves(row, col):
                        possible_moves.append(move)
                    if shuffle:
                        possible_moves = self.get_possible_moves(row, col)
                    break
            if len(possible_moves) > 0:
                break
        if True:
            if self.previous_choice == "right":
                possible_moves.remove("left") if "left" in possible_moves else possible_moves
            elif self.previous_choice == "left":
                possible_moves.remove("right") if "right" in possible_moves else possible_moves
            elif self.previous_choice == "up":
                possible_moves.remove("down") if "down" in possible_moves else possible_moves
            elif self.previous_choice == "down":
                possible_moves.remove("up") if "up" in possible_moves else possible_moves

        if not shuffle:
            choice, state = selector(possible_moves)
            self.tiles_grid = state
        else:
            choice = selector(possible_moves)
        self.empty_tile = (row, col)

        self.apply_choice(choice)

        self.previous_choice = choice
        if not shuffle:
            self.path.append(choice)

    def shuffle(self):
        self.make_move(random.choice, shuffle=True)

    def play(self):
        if self.tiles_grid == self.tiles_grid_completed:
            print("You win!")
            self.solve = False
        else:
            self.make_move(sol.selector)
        print("Path ", self.path)

    def draw_tiles(self):
        self.tiles = []
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile in enumerate(x):
                if tile != 0:
                    self.tiles[row].append(Tile(self, col, row, str(tile)))
                else:
                    self.tiles[row].append(Tile(self, col, row, "empty"))

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.create_game()
        self.tiles_grid_completed = self.create_game()
        self.elapsed_time = 0
        self.start_timer = False
        self.start_game = False
        self.buttons_list = []
        # Fix  the grid for 15, 24 and 35 puzzle
        self.buttons_list.append(Button(500, 100, 200, 50, "Shuffle", WHITE, BLACK))
        self.buttons_list.append(Button(500, 170, 200, 50, "Reset", WHITE, BLACK))
        self.buttons_list.append(Button(500, 310, 200, 50, "Misplaced", WHITE, BLACK))
        self.buttons_list.append(Button(500, 380, 200, 50, "Distance", WHITE, BLACK))
        self.buttons_list.append(Button(500, 450, 200, 50, "Misplaced C", WHITE, BLACK))
        self.buttons_list.append(Button(500, 520, 200, 50, "Distance C", WHITE, BLACK))
        self.draw_tiles()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        if self.start_game:
            if self.tiles_grid == self.tiles_grid_completed:
                self.start_game = False
                # if self.high_score > 0:
                #     self.high_score = self.elapsed_time if self.elapsed_time < self.high_score else self.high_score
                # else:
                #     self.high_score = self.elapsed_time
                # self.save_score()

            if self.start_timer:
                self.timer = time.time()
                self.start_timer = False
            self.elapsed_time = time.time() - self.timer

        if self.start_shuffle:
            self.shuffle()
            self.draw_tiles()
            self.shuffle_time += 1
            if self.shuffle_time > 50:
                self.start_shuffle = False
                self.start_game = True
                self.start_timer = True

        if self.solve:
            sol.solve()

        self.all_sprites.update()

    def draw_grid(self):
        for row in range(-1, self.game_size * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (row, 10), (row, self.game_size * TILESIZE))
        for col in range(-1, self.game_size * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (10, col), (self.game_size * TILESIZE, col))

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.all_sprites.draw(self.screen)
        self.draw_grid()
        for button in self.buttons_list:
            button.draw(self.screen)
        # UIElement(550, 35, "%.3f" % self.elapsed_time).draw(self.screen)
        UIElement(500, 255, "Solve ").draw(self.screen)
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
                                self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][
                                                                                               col], \
                                                                                           self.tiles_grid[row][col]

                            self.draw_tiles()
                            # sol.solve()

                for button in self.buttons_list:
                    available_algo = ["Misplaced", "Distance", "Misplaced C", "Distance C"]
                    if button.click(mouse_x, mouse_y):
                        if button.text == "Shuffle":
                            self.shuffle_time = 0
                            self.start_shuffle = True
                        if button.text in available_algo:
                            self.solve_epochs = 0
                            self.path = []
                            self.visited = []
                            self.solve = True
                            if button.text == "Misplaced" or button.text == "Distance":
                                sol.heuristic = sol.make_heuristic(button.text)
                            if button.text == "Misplaced C" or button.text == "Distance C":
                                sol.heuristic = sol.make_heuristic(button.text.split(' ')[0], True)
                        if button.text == "Reset":
                            self.new()


n = int(input("Enter the size of the puzzle: "))
game = Game(n)


sol = Solver(game)


while True:
    game.new()
    game.run()

    sol.solve()
