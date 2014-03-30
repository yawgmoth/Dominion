TREASURE = 1
VICTORY = 2
ACTION = 4
CURSE = 8
REACTION = 16
ATTACK = 32

class Card(object):
    def perform_cleanup(self):
        return True
        
    def can_play(self, player):
        return True
    
    def play(self, player):
        pass
        
    def start_turn(self, player):
        pass
        
    def pre_play(self, player):
        player.actions -= 1
        del player.hand[player.hand.index(self)]
        player.in_play.append(self)
    
    def post_play(self, player):
        pass
        
    def get_points(self, player):
        return self.points
        
    @classmethod
    def from_state(cls, state):
        return cls()
    
    def get_state(self):
        return {}

class Copper(Card):
    price = 0
    type = TREASURE
    value = 1
    name = "Copper"

class Silver(Card):
    price = 3
    type = TREASURE
    value = 2
    name = "Silver"

class Gold(Card):
    price = 6
    type = TREASURE
    value = 3
    name = "Gold"
 
class Estate(Card):
    price = 2
    type = VICTORY
    points = 1
    name = "Estate"
    
class Duchy(Card):
    price = 5
    type = VICTORY
    points = 3
    name = "Duchy"
    
class Province(Card):
    price = 8
    type = VICTORY
    points = 6
    name = "Province"
    
class Curse(Card):
    price = 0
    type = CURSE
    points = -1
    name = "Curse"

class Stack:
    def __init__(self, type, count=10):
        self.type = type
        self.count = count

