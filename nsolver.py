from copy import deepcopy
from heapq import heappush, heappop

import numpy as np
import pygame
import time,sys
import matplotlib.pyplot as plt
from main import Game

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
        self.total_time = 0
        self.start_time = None
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
                 range(self.game.game_size) if tiles_grid[i][j] != 0]) +level


        def gaschnig(candidate, level=0):
            if not cost: level=0

            res = 0
            solved = [j for sub in self.game.tiles_grid_completed for j in sub]
            candidate = [j for sub in candidate for j in sub]
            while candidate != solved:
                zi = candidate.index(0)
                if solved[zi] != 0:
                    sv = solved[zi]
                    ci = candidate.index(sv)
                    candidate[ci], candidate[zi] = candidate[zi], candidate[ci]
                else:
                    for i in range(self.game.game_size * self.game.game_size):
                        if solved[i] != candidate[i]:
                            candidate[i], candidate[zi] = candidate[zi], candidate[i]
                            break
                res += 1
            return res+level

        def manhattan(candidate, level=0):
            if not cost: level=0

            solved = [j for sub in self.game.tiles_grid_completed for j in sub]
            candidate = [j for sub in candidate for j in sub]
            res = 0
            for i in range(self.game.game_size * self.game.game_size):
                if candidate[i] != 0 and candidate[i] != solved[i]:
                    ci = solved.index(candidate[i])
                    y = (i // self.game.game_size) - (ci // self.game.game_size)
                    x = (i % self.game.game_size) - (ci % self.game.game_size)
                    res += abs(y) + abs(x)
            return res+level

        def linear_conflicts(candidate, level=0):
            if not cost: level=0
            mat=candidate
            solved = [j for sub in self.game.tiles_grid_completed for j in sub]
            candidate = [j for sub in candidate for j in sub]

            def count_conflicts(candidate_row, solved_row, size, ans=0):
                counts = [0 for x in range(size)]
                for i, tile_1 in enumerate(candidate_row):
                    if tile_1 in solved_row and tile_1 != 0:
                        solved_i = solved_row.index(tile_1)
                        for j, tile_2 in enumerate(candidate_row):
                            if tile_2 in solved_row and tile_2 != 0 and i != j:
                                solved_j = solved_row.index(tile_2)
                                if solved_i > solved_j and i < j:
                                    counts[i] += 1
                                if solved_i < solved_j and i > j:
                                    counts[i] += 1
                if max(counts) == 0:
                    return ans * 2
                else:
                    i = counts.index(max(counts))
                    candidate_row[i] = -1
                    ans += 1
                    return count_conflicts(candidate_row, solved_row, size, ans)

            res = manhattan(mat)
            candidate_rows = [[] for y in range(self.game.game_size)]
            candidate_columns = [[] for x in range(self.game.game_size)]
            solved_rows = [[] for y in range(self.game.game_size)]
            solved_columns = [[] for x in range(self.game.game_size)]
            for y in range(self.game.game_size):
                for x in range(self.game.game_size):
                    idx = (y * self.game.game_size) + x
                    candidate_rows[y].append(candidate[idx])
                    candidate_columns[x].append(candidate[idx])
                    solved_rows[y].append(solved[idx])
                    solved_columns[x].append(solved[idx])
            for i in range(self.game.game_size):
                res += count_conflicts(candidate_rows[i], solved_rows[i], self.game.game_size)
            for i in range(self.game.game_size):
                res += count_conflicts(candidate_columns[i], solved_columns[i], self.game.game_size)
            return res+level
        HEURISTICS = {
            'Manhattan': manhattan_distance,
            'Misplaced': misplaced_tiles,
            'LinearConflict': linear_conflicts,
            'LinearConf': linear_conflicts,
            'Gaschnig': gaschnig,
        }

        return HEURISTICS[heuristic]





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
            self.frontier = PriorityQueue()
            self.path= []
            root = Node(None, self.game.tiles_grid,
                        self.game.get_empty_tile(), '', self.heuristic(self.game.tiles_grid), 0)
            self.frontier.push(root)
            self.is_solving = True
            self.start_time = time.time()

        while not self.frontier.empty():
            minimum = self.frontier.pop()
            self.visited_nodes.add(''.join(''.join(str(x) for x in y) for y in minimum.mat))
            self.game.solve_epochs += 1
            if self.correct(minimum.mat) == 0:
                self.total_time = time.time() - self.start_time
                #
                # print("Total time taken: ", self.total_time)
                # print("Total moves: ", minimum.level)
                # print("Total epochs: ", self.game.solve_epochs)

                self.is_solving = False
                return self.total_time, minimum.level

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
            # print(self.game.solve_epochs)


def printMatrix(mat):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            print("%d " % (mat[i][j]), end=" ")
        print()
def is_safe( x, y):
        return 0 <= x < game.game_size and 0 <= y < game.game_size

def shuffle(game, n):
    for i in range(n):
        possible_moves =[]
        for i in range(4):
            new_tile_pos = [
                game.empty_tile[0] + row[i],
                game.empty_tile[1] + col[i], ]
            choice = moves[i]

            if is_safe(new_tile_pos[0], new_tile_pos[1]):
                possible_moves.append((new_tile_pos,choice))


            if len(possible_moves) > 0:
                move = random.choice(possible_moves)
                if choice != opposite_direction[move[1]]:
                    new_mat = deepcopy(game.tiles_grid)

                    x1 = game.empty_tile[0]
                    y1 = game.empty_tile[1]
                    x2 = move[0][0]
                    y2 = move[0][1]
                    new_mat[x1][y1], new_mat[x2][y2] = new_mat[x2][y2], new_mat[x1][y1]

                    game.previous_choice = choice
                    game.tiles_grid= new_mat
                    game.empty_tile = move[0]



N = 3


def getInvCount(arr):
    arr1 = []
    for y in arr:
        for x in y:
            arr1.append(x)
    arr = arr1
    inv_count = 0
    for i in range(N * N - 1):
        for j in range(i + 1, N * N):
            # count pairs(arr[i], arr[j]) such that
            # i < j and arr[i] > arr[j]
            if (arr[j] and arr[i] and arr[i] > arr[j]):
                inv_count += 1

    return inv_count


# find Position of blank from bottom
def findXPosition(puzzle):
    # start from bottom-right corner of matrix
    for i in range(N - 1, -1, -1):
        for j in range(N - 1, -1, -1):
            if (puzzle[i][j] == 0):
                return N - i


# This function returns true if given
# instance of N*N - 1 puzzle is solvable
def isSolvable(puzzle):
    # Count inversions in given puzzle
    invCount = getInvCount(puzzle)

    # If grid is odd, return true if inversion
    # count is even.
    if (N & 1):
        return ~(invCount & 1)

    else:  # grid is even
        pos = findXPosition(puzzle)
        if (pos & 1):
            return ~(invCount & 1)
        else:
            return invCount & 1

#
#
import random
random.seed(22)
size=9
game = Game(size-1)
game.tiles_grid_completed=game.create_game()
total_time={'Manhattan':[],'Misplaced':[],'LinearConflict':[],'LinearConf':[],'Gaschnig':[]}
total_moves={'Manhattan':[],'Misplaced':[],'LinearConflict':[],'LinearConf':[],'Gaschnig':[]}
heuristics=['Manhattan','Misplaced','LinearConflict','Gaschnig']
for x in heuristics:
    for t in range(200,400):
        random.seed(22)
        game.tiles_grid = game.create_game()
        game.empty_tile = game.get_empty_tile()
        shuffle(game, t)
        while isSolvable(game.tiles_grid) != -1:
            shuffle(game, t)
        print('Shuffled')
        print("Begin", game.tiles_grid)

        solver = Solver(game)
        solver.heuristic = solver.make_heuristic(x,True)
        times, move =solver.solve()
        total_moves[x].append(move)
        total_time[x].append(times)


ns = range(200,400)
epochs = game.solve_epochs
# # plt.plot(ns, total_moves, 'g', label='Training accuracy')
# for x in heuristics:
#     plt.plot(ns, total_moves[x], label=x)
#     plt.plot(ns, total_moves['LinearConflict'],'--', label='LinearConflict')
#
#     plt.title('Number of moves (Cost)')
#     plt.xlabel('Number of shuffles')
#     plt.ylabel('Number of moves')
#     plt.legend()
#     plt.show()
for x in heuristics:
    plt.plot(ns, total_time[x], label=x)
    plt.plot(ns, total_time['LinearConflict'],'--', label='LinearConflict')
    plt.title('Running time (Cost)')
    plt.xlabel('Number of shuffles')
    plt.ylabel('Running time (s)')
    plt.legend()
    plt.show()

# Begin [[1, 2, 3], [0, 7, 6], [5, 4, 8]]