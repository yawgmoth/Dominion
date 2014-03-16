

from base_game import *
from base import *

import random

all_kingdom_cards = [Cellar, Chapel, Chancellor, Woodcutter, Workshop, Feast, Gardens, Moneylender, 
                     Remodel, ThroneRoom, CouncilRoom, Laboratory, Market, Mine, Adventurer, Village,
                     Festival, Smithy, Moat, Bureaucrat, Militia, Spy, Thief, Witch, Library]

random.shuffle(all_kingdom_cards)
                     
def get_default_stacks():
    return [Stack(Copper, 30), Stack(Silver, 30), Stack(Gold, 30),
            Stack(Curse, 40), Stack(Estate, 20), Stack(Duchy, 12), Stack(Province, 12)]

def make_stacks():
    return get_default_stacks() + map(lambda t: Stack(t, 10), all_kingdom_cards[:10])
           
           
def card_by_name(name):
    for c in all_kingdom_cards + [Gold, Silver, Copper, Curse, Estate, Duchy, Province]:
        if name == c.name: return c()
    return None
    
def type_by_name(name):
    for c in all_kingdom_cards + [Gold, Silver, Copper, Curse, Estate, Duchy, Province]:
        if name == c.name: return c
    return None