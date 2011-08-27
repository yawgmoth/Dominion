

from base_game import *
from base import *

import random

all_kingdom_cards = [Cellar, Chapel, Chancellor, Woodcutter, Workshop, Feast, Gardens, Moneylender, 
                     Remodel, ThroneRoom, CouncilRoom, Laboratory, Market, Mine, Adventurer, Village,
                     Festival, Smithy, Moat, Bureaucrat, Militia, Spy, Thief, Witch]

random.shuffle(all_kingdom_cards)
                     
def make_stacks():
    return [Stack(Copper, 30), Stack(Silver, 30), Stack(Gold, 30)] + \
            map(lambda t: Stack(t, 10), all_kingdom_cards[:10]) + \
           [Stack(Curse, 40), Stack(Estate, 20), Stack(Duchy, 12), Stack(Province, 12)]