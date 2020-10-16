import random
from constants import *

class Food(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = 1
    
    def regen(self):
        if self.value <1:
            self.value += 0.001 * random.randint(0,7)

    def eat(self):
        if self.value >= 1:
            self.value = 0
            return True
        else:
            return False
    def is_eatable(self):
        return (self.value >= 1)

    def color(self):
        if self.value >= 1:
            return COLOR_GREEN
        elif self.value > 0.5:
            return COLOR_LIGHT_GREEN
        else:
            return COLOR_GREY
