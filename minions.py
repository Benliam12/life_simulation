from constants import *
import random

class Minion(object):    
    def __init__(self, arena, x = 0, y = 0, char="1", energy=2.0, energy_gain=2, max_energy = 300.0, vision=3, baby_cost = 80, generation = 0, mutation_impact = 1/100):
        #Maximum values of minion caracteritics can reach
        self.max_vision = 15
        self.max_energy_storing = 1000
        self.max_energy_gain = 10

        #Position of minion
        self.x = x
        self.y = y

        #Basics information of minion
        self.age = 0
        self.generation = generation
        self.baby_count = 0
        self.victims = 0

        self.energy = energy
        self.energy_gain = energy_gain
        self.max_energy = max_energy
        self.char = char

        #Arena instance of where the minion is located
        self.arena = arena

        self.vision = vision

        self.next_food_offset = []
        self.baby_cost = baby_cost

        #Value max of changing stats to better or for worst
        self.mutation_impact = mutation_impact

        #Chance of mutating 
        self.mutation_chance = 1/5

        self.ways = [[0,1],[1,0],[0,-1],[-1,0]]

        self.log_data = dict(log_datas)
        self.log_data["char"] = self.char
      

    def eat(self, eat):
        if eat:
            #self.energy = math.log(1.025 ** (self.energy+1) + 0.4, 1.025)

            if self.energy <= self.max_energy:
                self.energy += self.energy_gain

            if self.energy >= (2*self.baby_cost - self.age):
                return
                self.make_baby()
    
    def mutate(self):
        """
        Mutation function will be applied when spawning a new baby into the arena
        """
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
        #Updating parent for more accurate informations
        self.energy -= self.baby_cost
        
        x, y = self.find_valid_direction()

        print("making-baby",self.x, self.y)
        print(x, y)

        if x == self.x and y == self.y:
            return

        self.baby_count += 1
        #Creating the baby
        baby = Minion(self.arena, char=self.char, max_energy=self.max_energy, energy_gain=self.energy_gain, generation = self.generation + 1, vision = self.vision, baby_cost=self.baby_cost)
        
        baby.char = "5"
        baby.x = x
        baby.y = y
        baby.energy = self.baby_cost

        baby.mutate()
        self.arena.spawn_baby(baby)

    def find_food(self):
        """
        Will return a direction (x, y) of where to go in order to find the closest
        food based on current position

        Minion will be looking around him at distance 1 to his max vision range in 
        each direction
        """
        ways = [[0,1],[1,0],[0,-1],[-1,0]]
        random.shuffle(ways)

        interests = [0] * 4
        for j in range(1,self.vision+1):
            for i, way in enumerate(ways):
                x = self.x + way[0]*j
                y = self.y + way[1]*j
                if self.arena.in_arena(x) and self.arena.in_arena(y):
                    if self.arena.grass_grid[x][y].is_eatable():
                        interests[i] = 1
                    elif isinstance(self.arena.positions[x][y], Minion):
                        interests[i] = self.arena.positions[x][y].energy if self.arena.positions[x][y].age >= 0.3 else 0
            if max(interests) != 0 and max(interests) < self.energy:
                return ways[interests.index(max(interests))]
        return ways[random.randint(0,3)]
    
    def find_valid_direction(self, next_offset=None, can_beat_up = False):
        """
        Returns a valid direction of where the minion can go and where it is legal to do 
        so.

        can_beat_up is wheater you can go onto case with a Minion already standing on. If the minion is younger than
        the current minion, it will eat it (and delete it)
        """
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

                            #Eating condition
                            if minion.energy < (self.energy+20) and minion.age > 0.3 and self is not minion and self.age > 0.3:
                                self.victims += 1
                                self.energy += minion.energy

                                d = self.log_data
                                d["x"] = self.x
                                d["y"] = self.y
                                d["char"] = self.char
                                d["target_x"] = minion.x
                                d["target_y"] = minion.y
                                d["target_char"] = minion.char

                                self.arena.destroy_minion(minion, datas=d)
                                minion.char = "0"
                                break
                
            next_offset = ways[random.randint(0,3)]

            imdumb -= 1 

            #If im dumb get to 0, it means the minion is stuck and cannot move.
            #TODO : Baby might spawn onto their parent if the parent is stuck while giving birth
            if not imdumb:
                return self.x, self.y
        
        return new_x, new_y

    def move(self, direction=None):
        """
        Move method is used every ticks of the program to make the minion do something
        """
        #Kills the minion if his energy dropped to 0 during this tick
        if self.energy < 0:
            self.char = "0"
            self.arena.destroy_minion(self, self.log_data)
            return
        
        next_offset = self.find_food()
        new_x, new_y = self.find_valid_direction(next_offset, False)

        self.energy -= 1
        self.age += 0.01
        self.arena.swap_position([self.x, self.y], [new_x, new_y])
        self.x = new_x
        self.y = new_y

        self.log_data["x"] = self.x
        self.log_data["y"] = self.y

    def play(self):
        self.move()
    
    def color(self):
        #TODO: Display a custom color per minion
        pass