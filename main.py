import random
import math
import os
import time
import string
from numpy import exp
from minions import Minion

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

        self.baby_list = []
        self.amount = 0

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
        
        #Printing arena data
        output.append("Simulation AGE : " + "{0:.2f}".format(round(self.age * 100)/100) + "\n")
        output.append("Amount: " + str(len(self.minions)) + " - " + str(self.amount) + "\n")
        output.append("\n")

        #Printing info from top minions
        for index, i in enumerate(n_minions_list):
            
            #Number to display
            if(index == 6):
                break

            sub_list = []
            sub_list.append(i.char + " has moved to (" + "{:02d}".format(i.x) + "," +"{:02d}".format(i.y)+")")
            sub_list.append("(" + "{:3d}".format(int(i.energy)) + "/{:3d}".format(int(i.max_energy)) +" Energy left)")
            sub_list.append("(E_gain: " + "{0:.2f}".format(round(i.energy_gain * 100)/100) + ")")
            sub_list.append("(Age: " + "{:.2f}".format(i.age)  + ")")
            sub_list.append("(Gen " + "{:2d}".format(i.generation) + ")")
            sub_list.append("(Babies " + "{: 2d}".format(i.baby_count) + ")")
            sub_list.append("(Vision " + "{: 2d}".format(i.vision) + ")")
            sub_list.append("(Baby cost " + "{:3d}".format(i.baby_cost) + ")")
            sub_list.append("(Victims " + "{:2d}".format(i.victims) + ")")

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
        """
        Filling the grid with food for minion to eat
        """
        for i in range(self.dimension):
            for j in range(self.dimension):
                grass = Food(j,i)
                self.grass_grid[j][i] = grass

    def generate_minions(self, amount=1):
        """
        Spawining random minion with a char starting from the letter A (upper case)
        """
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

    def spawn_baby(self, baby):
        self.baby_list.append(baby)
        self.positions[baby.x][baby.y] = baby

    def swap_position(self, pos1, pos2):
        """
        Used to make the minion move by swaping him (his cell) with the Value None, the default value of all other cells
        in the arena
        """
        tmp = self.positions[pos1[0]][pos1[1]]
        self.positions[pos1[0]][pos1[1]] = self.positions[pos2[0]][pos2[1]]
        if isinstance(tmp, Minion):
            tmp.eat(self.grass_grid[pos2[0]][pos2[1]].eat())
        self.positions[pos2[0]][pos2[1]] = tmp
    
    def destroy_minion(self, minion1, minion2=None, datas=log_datas):
        """
        Kills a minion
        """
        if minion2 == None:
            target = self.positions[minion1.x][minion1.y]
            if target == None:
                return

            for index, minion in enumerate(self.minions):
                if minion is minion1:
                    
                    self.positions[minion1.x][minion1.y] = None
                    self.minions.pop(index)
                    
                    print(minion1.x, minion1.y)
                    return

    def in_arena(self, value):
        return value >= 0 and value < self.dimension
    
    def clear_weird_minion(self):
        """
        Weird fixing bug method. Clear up dead bodies if they remain in the arena
        """
        self.amount = 0
        for index_x, i in enumerate(self.positions):
            for index_y, cell in enumerate(i):
                if isinstance(cell, Minion):
                    self.amount += 1
                    m = self.positions[index_x][index_y]
                    if m not in self.minions:
                        print(cell.x, cell.y)
                        print(index_x, index_y)
                    
                    if m.char == "0":
                        self.minions.pop(self.minions.index(m))
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

            for minion in self.baby_list:
                self.minions.append(minion)
            
            self.baby_list = []
            self.display(True)

            #If the simulation has killed ALL minion, restart it with 2 new minions
            if len(self.minions) == 0:
                self.generate_minions(2)
                self.age = 0 
            
            self.regen_grass()
            self.age += 0.01

            time.sleep(max(delay - (time.time() - start), 0))


arena = Arena(dimension = 40, ticks=20)
arena.generate_minions(10)

arena.run()





