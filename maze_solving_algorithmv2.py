"""ПРИМЕЧАНИЕ:
Игра - генерирует лабиринт. Ходить можно с помощью клавиш со стрелками.
Если нажать пробел в любое время, компютер сам найдет путь до выхода и пройдет его.
"""

"""My Maze Solving Algorithm.

For a small Python project, I created a basic maze game. Additionally, an algorithm was created so that the computer can find
a short and reasonable path from the beginning to the end point. If there is no available path, the program should say so.

The principle behind the maze-solving algorithm is that computer will search for possible locations to 
move to, and will always select the location that was previously visited the least number of times. 
The visited location will then be added to a list for future reference. This method will eventually get the agent to the end
of the maze, after which the list of visited positions will be filtered to remove any repeating elements. 
By deleting all elements between two similar indices, we will remove any 'dead-end paths', and obtain a reasonable path
to the maze's exit. 

In theory, this path will not always be the absolute shortest if there are multiple, reasonable paths to
reach the exit, however in this context there is generally only one corridor that leads to the end. Altering the algorithm
to search for the absolute shortest path in all cases would be trivial, yielding a very useful and widely-applicable algorithm
that is used for many route-finding purposes, such as searching for the shortest route via GPS.

When the computer attempts to solve this problem, all movements will be made using a recursive function, 
which will stop calling itself when the exit is reached.

If the end is not reached after a large number of times, we will run a check: we will see if there are any positions that we can
visit in one move, from any of the positions that we already visited. We will do this by placing a virtual 'player' at every
location we've been, and seeing if any of them can move to a location that wasn't already visited. If there aren't any such
locations, that means we already went everywhere we could, and did not reach the end: hence the maze is not navigable. 
In practice, the maze generation algorithm will always generate a navigable maze, 
but this feature was added as a failsafe that was added as a proof of concept to prevent infinite recursion.

The starter code and the very clever maze generation algorithm was provided by Chuck Programming's video series on Youtube.

"""

import random
import pygame as pg
import time
import sys

pg.init()

#The maze is constructed out of nodes, each of which start with four walls. A clever algorithm then removes some of these walls,
#resulting in a neat, navigable maze.
class Node:
    def __init__(self, row, col, size):
        self.row = row
        self.col = col
        self.size = size
        self.walls = {}
                
    def draw(self, screen):
        if self.walls["North"] != None:
            start_pos, end_pos = (self.row * self.size, self.col * self.size), ((self.row + 1) * self.size, self.col * self.size)
            pg.draw.line(screen, (0, 0, 0), start_pos, end_pos, 1)
        if self.walls["South"] != None:
            start_pos, end_pos = (self.row * self.size, (self.col + 1) * self.size), ((self.row + 1) * self.size, (self.col + 1) * self.size)
            pg.draw.line(screen, (0, 0, 0), start_pos, end_pos, 1)
        if self.walls["West"] != None:
            start_pos, end_pos = (self.row * self.size, self.col * self.size), (self.row * self.size, (self.col + 1) * self.size)
            pg.draw.line(screen, (0, 0, 0), start_pos, end_pos, 1)
        if self.walls["East"] != None:
            start_pos, end_pos = ((self.row + 1) * self.size, self.col * self.size), ((self.row + 1) * self.size, (self.col + 1) * self.size)
            pg.draw.line(screen, (0, 0, 0), start_pos, end_pos, 1)
            
    def disconnect(self, node, flag = True):
        for side, wall in self.walls.items():
            if wall is not None and wall.row == node.row and wall.col == node.col: 
                self.walls[side] = None
                
        if flag:
            node.disconnect(self, False)
            
class Player:
    def __init__(self, position):
        self.position = position
            
        
    def draw(self, screen):
        pg.draw.rect(screen, (255, 0, 0), ([self.position[0] * node_size + 1, self.position[1] * node_size + 1], [node_size - 1, node_size - 1]))
        
    def move(self, direction, search_mode = False):
        if direction == "up": self.position[1] -= 1
        if direction == "right": self.position[0] += 1
        if direction == "down": self.position[1] += 1
        if direction == "left": self.position[0] -= 1
            
        if not search_mode: updatedisplay()
        
    #Helper function to receive the coordinates of a nearby location without actually moving there.
    #Used extensively in the maze solving algorithm, and in the algorithm which is used to follow the obtained path.
    def project(self, direction):
        if direction == "up": return([self.position[0], self.position[1] - 1])
        elif direction == "right": return([self.position[0] + 1, self.position[1]])
        elif direction == "down": return([self.position[0], self.position[1] + 1])
        elif direction == "left": return([self.position[0] - 1, self.position[1]])
        
#Most of the maze class is obtained from Chuck Programming, with the exception of the maze's exit.
#The code was optimized for the purposes of this maze, and simplified in its length to increase computational ease.
class Maze:
    def __init__(self, num_rows, num_cols, node_size):
        #num_rows, num_cols, and node_size allow us to control the dimensions of the maze, and the graphical size of each node.
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.node_size = node_size
        self.nodes = [[Node(row, col, self.node_size) for col in range(self.num_cols)] for row in range(self.num_rows)]
        self.mazethickness = 3
        self.mazeend = self.Mazeend(self)
    
    #Every maze must have an exit in the same relative location. A nested class was created to provide this.
    class Mazeend:
        def __init__(self, parentclass):
            self.position = (parentclass.num_cols * parentclass.node_size - 2, 0)
            self.size = (parentclass.mazethickness, parentclass.node_size)
            
        def draw(self, screen):
            pg.draw.rect(screen, (0, 0, 255), (self.position, self.size))
            
    def draw(self, screen):
        self.draw_boundaries(screen)
        self.mazeend.draw(screen)
        for node in self.iterate_nodes():
            node.draw(screen)
        
    #Draws the boundaries for the maze.    
    def draw_boundaries(self, screen):
        coordinates = [(0, 0), (self.node_size * self.num_cols, 0), \
                      (0, self.node_size * self.num_cols), (self.node_size * self.num_rows, \
                      self.node_size * self.num_cols)]
        
        pg.draw.line(screen, (0, 0, 0), coordinates[0], coordinates[1], self.mazethickness)
        pg.draw.line(screen, (0, 0, 0), coordinates[0], coordinates[2], self.mazethickness)
        pg.draw.line(screen, (0, 0, 0), coordinates[2], coordinates[3], self.mazethickness)
        pg.draw.line(screen, (0, 0, 0), coordinates[1], coordinates[3], self.mazethickness)
        
    def connect_nodes(self):
        for node in self.iterate_nodes():
            node.walls["West"] = self.get_node(node.row - 1, node.col)
            node.walls["East"] = self.get_node(node.row + 1, node.col)
            node.walls["South"] = self.get_node(node.row, node.col + 1)
            node.walls["North"] = self.get_node(node.row, node.col - 1)
        
    #A helper function used to iterate through all nodes in the maze, courtesy of Chuck Programming. 
    def iterate_nodes(self):
        for i in range(num_rows):
            for j in range(num_cols):
                yield self.nodes[i][j]
                
    def get_node(self, row, col):
        if row >= 0 and row < self.num_rows and col >= 0 and col < self.num_cols:
            return self.nodes[row][col]
        else:
            return None
        

    def generate(self):
        self.connect_nodes()
        for node in self.iterate_nodes():
            north_side_disc = self.get_node(node.row - 1, node.col)
            east_side_disc = self.get_node(node.row, node.col + 1)
            if north_side_disc is None and east_side_disc is None:
                disc = None
            elif north_side_disc is not None and east_side_disc is None:
                disc = north_side_disc
            elif east_side_disc is not None and north_side_disc is None:
                disc = east_side_disc
            else:
                disc = random.choice([north_side_disc, east_side_disc])
            if disc is not None:
                node.disconnect(disc)
                
moves = ["up", "right", "down", "left"]

#Helper function to get value using dictionary keys
def get_val(testdict, mykey): 
    for key, value in testdict.items(): 
         if mykey == key: 
            return value

#This function checks if a player is allowed to move somewhere (ie. if there isn't a wall in the way).
def valid(player, maze, direction):
    i, j = player.position[0], player.position[1]
    if direction == "up":
        if get_val(maze.get_node(i, j).walls, "North") is None and j > 0:
            return True
    elif direction == "right": 
        if get_val(maze.get_node(i, j).walls, "East") is None and i < num_cols - 1:
            return True
    elif direction == "down": 
        if get_val(maze.get_node(i, j).walls, "South") is None and j < num_rows - 1:
            return True
    elif direction == "left": 
        if get_val(maze.get_node(i, j).walls, "West") is None and i > 0:
            return True
    return False

#Helper function used to refresh the screen.
def updatedisplay():
    screen.fill((255, 255, 255))
    maze.draw(screen)
    player.draw(screen)
    
#The solve_algorithm function uses a nested function, so that the outer function can declare some variables
#and the inner function can be called recursively. 

#The variable 'limit' is initialized as a nonlocal variable, to demonstrate the feasbility of doing this.
#Functions are initialized as nonlocal variables to increase computational efficiency, preventing them from being defined
#each time the inner function is recursively called.

#Side note: using recursion may not have been the best idea due to the maximum recursion depth limit. Using a 'while' loop
#makes more sense, but recursion is more interesting from a programming perspective.

def solve_algorithm(agent, maze):
    limit = 1
    marked_positions = []
    agent.position = player.position
       
    def least_visited(agent, maze, valid_moves, marked):
        num_times = {}; nonlocal limit
        for move in valid_moves:
            if move not in num_times:
                num_times[move] = marked.count(agent.project(move))
                #If a node has been visited too many times, run a check. If the check passes, increase the limit
                #for how many times a node can be visited before running the check again.
                if num_times[move] >= maze.num_rows*limit:
                    if not check_if_solution(maze, marked):
                        return False
                    else:
                        limit += 1
        least = min(num_times, key = num_times.get)
        return least

    #This function is used to check if a solution exists to the maze,
    #if the least_visited function reports that any node has been visited more than a certain number of times.
    def check_if_solution(maze, marked):
        marked = delete_repeating_elements(marked); templist = []
        for pos in marked:
            tester = Player([pos[0], pos[1]])
            valid_moves = []
            for i in range(len(moves)):
                if valid(tester, maze, moves[i]):
                    valid_moves.append(moves[i])
            for i in valid_moves:
                templist.append(tester.project(i))
            for pos in delete_repeating_elements(templist):
                if pos not in marked:
                    return True
            print("There is no solution to the maze.")
            return False
    
    def inner_solve(agent, maze):
        nonlocal least_visited; nonlocal check_if_solution
        
        marked_positions.append([agent.position[0], agent.position[1]])
        valid_moves = []
        if win_conditions(agent): return True

        for i in range(len(moves)):
            if valid(agent, maze, moves[i]):
                valid_moves.append(moves[i])
        l_v = least_visited(agent, maze, valid_moves, marked_positions)
        if not l_v: return False
        agent.move(l_v, search_mode = True)

        if inner_solve(agent, maze):
            return True
        
    if inner_solve(agent, maze):
        return marked_positions
    else: return False

    
#After the path to the exit is explored, this function will move the player according to that path.
#In this function, the movements will be drawn onto the screen and a short delay will be added between each move,
#so that the human eye can follow the player.
def go_to_finish(agent, solution_path):
    solution_path = delete_repeating_elements(solution_path)
    for i in solution_path:
        for j in moves:
            if agent.project(j) == i:
                agent.move(j)
                pg.display.update()
                time.sleep(0.05)
                
#This function is used to filter a list, by removing any duplicate elements and all the elements between two duplicates.
#When used on the 'marked_positions' list, it yields an efficient path to the exit.
def delete_repeating_elements(alist):
    filtered_list = []; counter = 0
    for i in alist:
        if i in filtered_list:
            for j in range(filtered_list.index(i), counter):
                filtered_list[j] = 0
        filtered_list.append(i)
        counter += 1
    filtered_list[:] = (value for value in filtered_list if value != 0)
    return filtered_list
    
num_rows = 20
num_cols = 20
node_size = 30

#Define what conditions must be met to 'win'; player must reach the exit node.
def win_conditions(player):
    maze_exit_coords = [num_cols - 1, 0]
    if player.position == maze_exit_coords:
        return True

maze = Maze(num_rows, num_cols, node_size)
player = Player([0, num_rows - 1])
maze.generate()


screen = pg.display.set_mode((900, 900), 0, 32)
screen.fill((255, 255, 255))

maze.draw(screen)
player.draw(screen)

run = True
while run is True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and valid(player, maze, "up"): player.move("up")
            elif event.key == pg.K_DOWN and valid(player, maze, "down"): player.move("down")
            elif event.key == pg.K_LEFT and valid(player, maze, "left"): player.move("left")
            elif event.key == pg.K_RIGHT and valid(player, maze, "right"): player.move("right")
                
            elif event.key == pg.K_SPACE:  
                pos = [player.position[0], player.position[1]]
                path_to_solution = solve_algorithm(player, maze)
                player.position = pos
                
                if path_to_solution: go_to_finish(player, path_to_solution)
            
            if win_conditions(player):
                print("You Win!")
                run = False
    pg.display.update()
pg.quit()
sys.exit()