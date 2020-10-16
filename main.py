import random
import math
import os
import time
import string
from numpy import exp

from constants import *
from food import Food

def __sigmoid(self, x):
    return 1 / (1 + exp(-x))

class Arena:
    def __init__(self, dimension = 50, ticks = 10):
        self.dimension = dimension
        self.minions = []
        self.length = dimension ** 2
        self.grid = "#" * self.length
        self.ticks = ticks
        self.positions = [[None] * self.dimension for x in range(self.dimension)]
        self.grass_grid = [[None] * self.dimension for x in range(self.dimension)]

        #Init methods
        self._generate_terrain()

        self.age = 0

    def display(self, display=False):
        output = [[None] * self.dimension for x in range(self.dimension)]
        clear = lambda: os.system('clear')
        for i in range(self.dimension):
            for j in range(self.dimension):
                value = self.positions[j][i]
                if value == None:
                    output[i][j] = str(self.grass_grid[j][i].color()) + "  " + COLOR_RESET + ""
                elif isinstance(value, Minion):
                    output[i][j] = (COLOR_BLUE + value.char + " " + COLOR_RESET + "")
                else:
                    output[i][j] = "11"
            output[i][j] += (COLOR_RESET + "\n")
        
        n_minions_list = sorted(self.minions, key=lambda x: (-x.age,x.char, x.baby_count))
        
        #Printing shits
        output.append("Simulation AGE : " + "{0:.2f}".format(round(self.age * 100)/100) + "\n")
        output.append("Amount: " + str(len(self.minions)) +  "\n")
        output.append("\n")


        for index, i in enumerate(n_minions_list):
            if(index == 6):
                break
            #pass
            sub_list = []
            sub_list.append(i.char + " has moved to (" + "{:02d}".format(i.x) + "," +"{:02d}".format(i.y)+")")
            sub_list.append("(" + "{:3d}".format(int(i.energy)) + "/{:3d}".format(int(i.max_energy)) +" Energy left)")
            sub_list.append("(E_gain: " + "{0:.2f}".format(round(i.energy_gain * 100)/100) + ")")
            sub_list.append("(Age: " + "{:.2f}".format(i.age)  + ")")
            sub_list.append("(Gen " + "{:2d}".format(i.generation) + ")")
            sub_list.append("(Babies " + "{: 2d}".format(i.baby_count) + ")")
            sub_list.append("(Vision " + "{: 2d}".format(i.vision) + ")")
            sub_list.append("(Baby cost " + "{:3d}".format(i.baby_cost) + ")")

            sub_list.append("\n")
            sub_list = ' '.join(sub_list)
            output.append(sub_list)


        printer = []

        for i in output:
            for j in i:
                printer.append(j)        
        
        output = ''.join(printer)
        clear()
        print(output)
        return output

    def _generate_terrain(self):
        for i in range(self.dimension):
            for j in range(self.dimension):
                grass = Food(j,i)
                self.grass_grid[j][i] = grass

    def generate_minions(self, amount=1):
        chars = list(string.ascii_uppercase)
        for i in range(amount):
            good = True
            while good:
                x = random.randint(0, self.dimension-1)
                y = random.randint(0, self.dimension-1)

                if not isinstance(self.positions[x][y], Minion):
                    vision = random.randint(3,5)
                    max_energy = random.randint(100, 300)
                    baby_cost = int((max_energy/2) - (random.random() * random.randint(0,math.floor((max_energy/2)-1))))
                    a = Minion(arena, x,y, chars[i], vision=vision, baby_cost=baby_cost, max_energy=max_energy)
                    self.positions[x][y] = a
                    self.minions.append(a)
                    good = False

    def _spawn(self, amount=1):
        pass

    def spawn_baby(self, baby):
        self.minions.append(baby)
        self.positions[baby.x][baby.y] = baby


    def swap_position(self, pos1, pos2):
        tmp = self.positions[pos1[0]][pos1[1]]
        self.positions[pos1[0]][pos1[1]] = self.positions[pos2[0]][pos2[1]]
        if isinstance(tmp, Minion):
            tmp.eat(self.grass_grid[pos2[0]][pos2[1]].eat())
        self.positions[pos2[0]][pos2[1]] = tmp
    
    def destroy_minion(self, minion1, minion2=None):
        if minion2 == None:
            self.positions[minion1.x][minion1.y] = None
            for index, minion in enumerate(self.minions):
                if minion is minion1:
                    self.minions.pop(index)
                    print(minion1.x, minion1.y)
                    return
            print("NO minion found!")

    def in_arena(self, value):
        return value >= 0 and value < self.dimension
    
    def clear_weird_minion(self):
        for index_x, i in enumerate(self.positions):
            for index_y, cell in enumerate(i):
                if isinstance(cell, Minion):
                    if cell.char == "0":
                        self.positions[index_x][index_y] = None


    def regen_grass(self):
        for i in self.grass_grid:
            for j in i:
                j.regen()

    def run(self):
        delay = 1/self.ticks
        while True:
            self.clear_weird_minion()
            start = time.time()

            for minion in self.minions:
                minion.play()
            self.display(True)

            if len(self.minions) == 0:
                self.generate_minions(2)
                self.age = 0 
            
            self.regen_grass()
            self.age += 0.01

            time.sleep(max(delay - (time.time() - start), 0))

class Minion(object):    
    def __init__(self, arena, x = 0, y = 0, char="1", energy=2.0, energy_gain=2, max_energy = 300.0, vision=3, baby_cost = 80, generation = 0, mutation_impact = 1/100):
        self.max_vision = 15
        self.max_energy_storing = 1000
        self.max_energy_gain = 4

        self.x = x
        self.y = y

        self.energy = energy
        self.energy_gain = energy_gain
        self.max_energy = max_energy
        self.char = char

        self._nextMove = [0,0]
        self.arena = arena
        self.vision = vision

        self.next_food_offset = []
        self.baby_cost = baby_cost

        #Value max of changing stats to better or for worst
        self.mutation_impact = mutation_impact

        #Chance of mutating 
        self.mutation_chance = 1/5

        self.ways = [[0,1],[1,0],[0,-1],[-1,0]]

        self.age = 0
        self.generation = generation
        self.baby_count = 0

    def eat(self, eat):
        if eat:
            #self.energy = math.log(1.025 ** (self.energy+1) + 0.4, 1.025)

            if self.energy <= self.max_energy:
                self.energy += self.energy_gain

            if self.energy >= (2*self.baby_cost - self.age):
                self.make_baby()
    
    def mutate(self):

        up = [-1, 1]
        self.baby_cost += random.randint(1,5) * up[random.randint(0,1)] if random.random() < self.mutation_chance else 0
        self.vision += 1 * up[random.randint(0,1)] if random.random() < self.mutation_chance else 0
        self.energy_gain += (random.random() * up[random.randint(0,1)]) if random.random() < self.mutation_chance else 0
        self.max_energy += 20 * random.random() * up[random.randint(0,1)] if random.random() < self.mutation_chance else 0

        if self.vision > self.max_vision:
            self.vision = self.max_vision

        if self.max_energy > self.max_energy_storing:
            self.max_energy = self.max_energy_storing

        if self.energy_gain > self.max_energy_gain:
            self.energy_gain = self.max_energy_gain

        if self.baby_cost > self.max_energy/2:
            self.baby_cost = math.floor(self.max_energy/2)
        
    def make_baby(self):
        self.energy -= self.baby_cost
        self.baby_count += 1
        baby = Minion(self.arena, char=self.char, max_energy=self.max_energy, energy_gain=self.energy_gain, generation = self.generation + 1, vision = self.vision, baby_cost=self.baby_cost)
        x, y = self.find_valid_direction()
        baby.x = x
        baby.y = y
        baby.energy = self.baby_cost

        baby.mutate()
        self.arena.spawn_baby(baby)

        pass

    def find_food(self):
        ways = [[0,1],[1,0],[0,-1],[-1,0]]
        random.shuffle(ways)
        for j in range(1,self.vision+1):
            for i, way in enumerate(ways):
                x = self.x + way[0]*j
                y = self.y + way[1]*j
                if self.arena.in_arena(x) and self.arena.in_arena(y):
                    if self.arena.grass_grid[x][y].is_eatable():
                        return ways[i]
        return ways[random.randint(0,3)]
    
    def find_valid_direction(self, next_offset=None, can_beat_up = False):
        ways = [[0,1],[1,0],[0,-1],[-1,0]]
        if next_offset == None:
            next_offset = ways[random.randint(0,3)]

        imdumb = 10
        while True:
            x_move, y_move = next_offset[0], next_offset[1]
            new_x = self.x + x_move
            new_y = self.y + y_move

            if new_x >= 0 and new_x < self.arena.dimension and new_y >= 0 and new_y < self.arena.dimension:
                    if not isinstance(self.arena.positions[new_x][new_y], Minion):
                        break
                    else:
                        if can_beat_up:
                            minion = self.arena.positions[new_x][new_y]
                            if minion.age < self.age:
                                self.arena.destroy_minion(minion)
                                minion.char = "0"
                                break
                
            next_offset = ways[random.randint(0,3)]

            imdumb -= 1 

            if not imdumb:
                return self.x, self.y
        
        return new_x, new_y

    def move(self, direction=None):
        if self.energy < 0:
            self.arena.destroy_minion(self)
        next_offset = self.find_food()
        new_x, new_y = self.find_valid_direction(next_offset, True)

        self.arena.swap_position([self.x, self.y], [new_x, new_y])
                
        self.x = new_x
        self.y = new_y
        
        self.energy -= 1
        self.age += 0.01

    def play(self):
        self.move()
    
    def color(self):
        pass
arena = Arena(dimension = 40, ticks=20)
arena.generate_minions(10)

arena.run()





