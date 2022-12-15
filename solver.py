import heapq
import random
import time
from copy import deepcopy
from heapq import heappush, heappop

import pygame

row = [1, 0, -1, 0]
col = [0, -1, 0, 1]
moves = ['down', 'left', 'up', 'right']

opposite_direction = {'down': 'up', 'up': 'down', 'left': 'right', 'right': 'left', '': ''}


class PriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, k):
        heappush(self.heap, k)

    def pop(self):
        return heappop(self.heap)

    def empty(self):
        if not self.heap:
            return True
        else:
            return False


class Node:
    def __init__(self, parent, mat, empty_tile_pos, move,
                 cost, level):
        self.parent = parent
        self.mat = mat
        self.empty_tile_pos = empty_tile_pos
        self.move = move
        self.cost = cost
        self.level = level
        self.path = []

    def __lt__(self, nxt):
        return self.cost < nxt.cost


class Solver:
    def __init__(self, game):
        self.is_solving = False
        self.path = []
        self.game = game
        self.visited = []
        self.visited_nodes = set()
        self.frontier = PriorityQueue()
        self.heuristic = None

    def is_safe(self, x, y):
        return 0 <= x < self.game.game_size and 0 <= y < self.game.game_size

    def correct(self, tiles_grid):
        return len([1 for i in range(self.game.game_size) for j in range(self.game.game_size) if
                        tiles_grid[i][j] != i * self.game.game_size + j + 1 and tiles_grid[i][j] != 0])

    def make_heuristic(self, heuristic, cost=False):
        def misplaced_tiles(tiles_grid, level=0):
            if not cost: level=0
            return len([1 for i in range(self.game.game_size) for j in range(self.game.game_size) if
                        tiles_grid[i][j] != i * self.game.game_size + j + 1 and tiles_grid[i][j] != 0]) + level

        def distance(tiles_grid, level=0):
            if not cost: level=0
            return sum(
                [abs(tiles_grid[i][j] - (i * self.game.game_size + j + 1)) for i in range(self.game.game_size) for j in
                 range(self.game.game_size) if tiles_grid[i][j] != 0]) + level

        def manhattan_distance(tiles_grid, level=0):
            if not cost: level=0
            return sum(
                [abs(i - (tiles_grid[i][j] - 1) // self.game.game_size) + abs(
                    j - (tiles_grid[i][j] - 1) % self.game.game_size) for i in range(self.game.game_size) for j in
                 range(self.game.game_size) if tiles_grid[i][j] != 0])

        if heuristic == 'Misplaced' or heuristic == 'Misplaced C':
            return misplaced_tiles
        elif heuristic == 'Distance' or heuristic == 'Distance C':
            return distance




    def new_node(self, mat, empty_tile_pos, new_empty_tile_pos, move,
                 level, parent) -> Node:
        new_mat = deepcopy(mat)

        x1 = empty_tile_pos[0]
        y1 = empty_tile_pos[1]
        x2 = new_empty_tile_pos[0]
        y2 = new_empty_tile_pos[1]
        new_mat[x1][y1], new_mat[x2][y2] = new_mat[x2][y2], new_mat[x1][y1]

        cost = self.heuristic(new_mat, level)

        new_node = Node(parent, new_mat, new_empty_tile_pos, move,
                        cost, level)
        return new_node


    def solve(self):
        if not self.is_solving:
            self.visited_nodes = set()
            root = Node(None, self.game.tiles_grid,
                        self.game.get_empty_tile(), '', self.heuristic(self.game.tiles_grid), 0)
            self.frontier.push(root)
            self.is_solving = True

        while not self.frontier.empty():
            minimum = self.frontier.pop()
            self.visited_nodes.add(''.join(''.join(str(x) for x in y) for y in minimum.mat))
            self.game.solve_epochs += 1
            if self.correct(minimum.mat) == 0:
                self.printPath(minimum)

                print("Total moves: ", minimum.level)
                print("Total epochs: ", self.game.solve_epochs)

                for i in self.path:
                    self.game.tiles_grid = i
                    self.game.draw_tiles()
                    self.game.all_sprites.update()
                    self.game.draw()

                    pygame.time.wait(200)

                self.frontier = PriorityQueue()
                self.game.solve = False
                self.game.start_game = True
                self.is_solving = False
                return

            for i in range(4):
                new_tile_pos = [
                    minimum.empty_tile_pos[0] + row[i],
                    minimum.empty_tile_pos[1] + col[i], ]

                if self.is_safe(new_tile_pos[0], new_tile_pos[1]):
                    child = self.new_node(minimum.mat, minimum.empty_tile_pos, new_tile_pos, moves[i],
                                          minimum.level + 1, minimum)
                    if child.move != opposite_direction[minimum.move] and ''.join(''.join(str(x) for x in y) for y in child.mat)not in self.visited_nodes:
                        self.game.tiles_grid = child.mat
                        # self.game.draw_tiles()
                        self.frontier.push(child)
            print(self.game.solve_epochs)


    def printPath(self,root):
        if root is None:
            return
        self.printPath(root.parent)
        print(root.move)
        self.path.append(root.mat)
        printMatrix(root.mat)
        print()


def printMatrix(mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            print("%d " % (mat[i][j]), end=" ")
        print()


