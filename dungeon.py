# Copyright (C) Sirtaj Singh Kang, 2006
__doc__=\
'''Dungeon Generator.

Algorithm Specification:

Start with a rectangular grid, x units wide and y units tall. Mark each
cell in the grid unvisited.

Pick a random cell in the grid and mark it visited. This is the
current cell.

From the current cell, pick a random direction (north, south, east,
or west). If (1) there is no cell adjacent to the current cell in
that direction, or (2) if the adjacent cell in that direction has been
visited, then that direction is invalid, and you must pick a different
random direction. If all directions are invalid, pick a different random
visited cell in the grid and start this step over again.

Let's call the cell in the chosen direction C. Create a corridor between
the current cell and C, and then make C the current cell. Mark C visited.

Repeat steps 3 and 4 until all cells in the grid have been visited.

Once that process finishes, you'll have your maze! There are a few
variations you can do to make the maze more interesting; for example,
my dungeon generator has a parameter called "randomness". This is a
percentage value (0–100) that determines how often the direction of
a corridor changes. If the value of randomness is 0, the corridors go
straight until they run into a wall or another corridor—you wind up
with a maze with lots of long, straight halls. If the randomness is
100, you get the algorithm given above—corridors that twist and turn
unpredictably from cell to cell.
'''

from random import sample, randint, choice



class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size = (width, height)
    
    def generate(self):
        width, height = self.width, self.height
        unvisited = dict(((x, y), 0)
                    for y in range(height) for x in range(width))
        visited = {}

        def random_cell(w = (width-1), h = (height-1), rnd = randint):
            return (rnd(0, w), rnd(0, h))

        def visit(cell, val):
            del unvisited[cell]
            visited[cell] = val

        def random_neighbour((x, y),
                exits = [(0, 1, 1, 2),
                        (0, -1, 2, 1),
                        (1, 0, 4, 8),
                        (-1, 0, 8, 4)]):
            for xd, yd, my_exit, your_exit in sample(exits, 4):
                ncell = xd+x, yd+y
                if ncell in unvisited:
                    return ncell, (my_exit, your_exit)
            return None

        current_cell = random_cell()
        visit(current_cell, 0)

        while len(unvisited) > 0:
            neighbour = random_neighbour(current_cell)
            if neighbour is None:
                while True:
                    current_cell = random_cell()
                    if current_cell in visited: break
                continue

            cell, (my_exit, your_exit) = neighbour
            visited[current_cell] |= my_exit
            visit(cell, your_exit)
            current_cell = cell

        self.visited = visited

    def sparsify(self, sparseness):
        single_corridor = {
            1: (0, 1, -2),
            2: (0, -1, -1),
            4: (1, 0, -8),
            8: (-1, 0, -4)}
        visited = self.visited

        for sp_pass in range(sparseness):
            for (x, y), mask in visited.items():
                if mask not in single_corridor:
                    continue
                nxd, nyd, diff = single_corridor[mask]
                visited[(x, y)] = 0
                visited[(x+nxd, y+nyd)] += diff


def make_maze(width, height, sparseness):
    maze = Maze(width, height)
    maze.generate()
    maze.sparsify(sparseness)
    return maze


def draw_maze(maze):
    '''Create a surface big enough to draw the entire maze.
    We need
        "0" -- room with atleast one corridor
        "-" -- horizontal corridor
        "|" -- vertical corridor
    '''
    ROOM_DIAMETER = 10
    CORRIDOR_LENGTH = 5
    CORRIDOR_THICKNESS = 3
    MARGIN_LR = 30
    MARGIN_TB = 30
    ROOM_DELTA = ROOM_DIAMETER + CORRIDOR_LENGTH
    CORR_E_YD = (ROOM_DIAMETER - CORRIDOR_THICKNESS) / 2
    CORR_S_XD = (ROOM_DIAMETER - CORRIDOR_THICKNESS) / 2

    from pygame import Rect
    from pygame.draw import ellipse, rect
    black = (0, 0, 0)
    white = (255,255,255)

    surf = pygame.display.set_mode(
            ((maze.width * ROOM_DELTA) - CORRIDOR_LENGTH + 2 * MARGIN_LR,
                (maze.height * ROOM_DELTA) - CORRIDOR_LENGTH + 2 * MARGIN_TB))
    surf.fill(black)

    # draw rooms
    rooms = maze.visited
    curr_sy = MARGIN_TB - ROOM_DELTA
    
    for y in range(maze.height):
        curr_sy += ROOM_DELTA
        curr_sx = MARGIN_LR - ROOM_DELTA
        for x in range(maze.width):
            curr_sx += ROOM_DELTA
            rmask = rooms[(x, y)]
            if rmask == 0:
                continue

            ellipse(surf, white,
                    Rect(curr_sx, curr_sy, ROOM_DIAMETER, ROOM_DIAMETER))

            if rmask & 4:
                rect(surf, white,
                        Rect(curr_sx + ROOM_DIAMETER, curr_sy + CORR_E_YD,
                            CORRIDOR_LENGTH, CORRIDOR_THICKNESS))
            if rmask & 1:
                rect(surf, white,
                        Rect(curr_sx + CORR_S_XD, curr_sy + ROOM_DIAMETER,
                            CORRIDOR_THICKNESS, CORRIDOR_LENGTH))


def draw_app():
    import pygame
    pygame.init()

    while True:
        SPARSENESS = randint(1, 25)
        #SPARSENESS = 0
        print "Sparseness:", SPARSENESS
        draw_maze(make_maze(60, 40, SPARSENESS))
        pygame.display.flip()

        while True:
            ev = pygame.event.wait()
            if ev.type == pygame.QUIT:
                return
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                break

if __name__ == '__main__':
    draw_app()
