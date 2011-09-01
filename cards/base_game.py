from base import Card, ACTION, TREASURE, VICTORY, CURSE, ATTACK, REACTION

class Cellar(Card):
    price = 2
    type = ACTION
    name = "Cellar"
    def play(self, player):
        player.actions += 1
        n = 0
        while player.discard(optional=True):
            n += 1
        for i in xrange(n):
            player.draw_card()
            
class Chapel(Card):
    price = 2
    type = ACTION
    name = "Chapel"
    def play(self, player):
        n = 0
        while player.trash(optional=True) and n < 4:
            n += 1

class Chancellor(Card):
    price = 3
    type = ACTION
    name = "Chancellor"
    def play(self, player):
        player.money += 2
        if player.player_interface.ask_putdiscard():
            player.discard_pile.extend(player.deck)
            player.deck = []
            
class Woodcutter(Card):
    price = 3
    type = ACTION
    name = "Woodcutter"
    def play(self, player):
        player.money += 2
        player.buys += 1

class Workshop(Card):
    price = 3
    type = ACTION
    name = "Workshop"
    def play(self, player):
        cards = []
        for s in player.game.stacks:
            if s.count > 0 and s.type.price <= 4:
                cards.append(s)
        if not cards:
            return
        gain_which = player.player_interface.ask_whichgain(cards)
        if gain_which < 0:
            gain_which = 0

        cards[gain_which].count -= 1
        player.discard_pile.append(cards[gain_which].type())
   
class Feast(Card):
    price = 4
    type = ACTION
    name = "Feast"
    def play(self, player):
        cards = []
        for s in player.game.stacks:
            if s.count > 0 and s.type.price <= 5:
                cards.append(s)
        if not cards:
            return
        gain_which = player.player_interface.ask_whichgain(cards)
        if gain_which < 0:
            gain_which = 0

        cards[gain_which].count -= 1
        player.discard_pile.append(cards[gain_which].type())
        
    def post_play(self, player):
        del player.in_play[player.in_play.rindex(self)]
        player.game.trash.append(self)

class Gardens(Card):
    price = 4
    type = VICTORY
    name = "Gardens"
    def get_points(self, player):
        return len(player.deck)/10
        
class Moneylender(Card):
    price = 4
    type = ACTION
    name = "Moneylender"
    def play(self, player):
        i = 0
        while i < len(player.hand) and player.hand[i].name != "Copper":
            i += 1
        if i < len(player.hand):
            player.game.trash(player.hand[i])
            del player.hand[i]
            player.money += 3

class Remodel(Card):
    price = 4
    type = ACTION
    name = "Remodel"
    def play(self, player):
        c = player.trash()
        max_price = c.price + 2
        cards = []
        for s in player.game.stacks:
            if s.count > 0 and s.type.price <= max_price:
                cards.append(s)
        if not cards:
            return
        gain_which = player.player_interface.ask_whichgain(cards)
        if gain_which < 0:
            gain_which = 0

        cards[gain_which].count -= 1
        player.discard_pile.append(cards[gain_which].type())
        
class ThroneRoom(Card):
    price = 4
    type = ACTION
    name = "Throne Room"
    def play(self, player):
        a = player.choose_action()
        if a:
            del player.hand[player.hand.index(a)]
            player.in_play.append(a)
            a.play(player)
            a.play(player)
            a.post_play(player)
        
class CouncilRoom(Card):
    price = 5
    type = ACTION
    name = "Council Room"
    def play(self, player):
        for i in xrange(4):
            player.draw_card()
        player.buys += 1
        for p in player.get_other_players():
            p.draw_card()
        
class Laboratory(Card):
    price = 5
    type = ACTION
    name = "Laboratory"
    def play(self, player):
        player.draw_card()
        player.draw_card()
        player.actions += 1
        
class Market(Card):
    price = 5
    type = ACTION
    name = "Market"
    def play(self, player):
        player.actions += 1
        player.buys += 1
        player.money += 1
        player.draw_card()
        
class Mine(Card):
    price = 5
    type = ACTION
    name = "Mine"
    def play(self, player):
        treasures = []
        for c in player.hand:
            if c.type & TREASURE == TREASURE:
                treasures.append(c)
        disc = self.player_interface.ask_whichtrash(treasures, False)
        if disc < 0:
            disc = 0
        idx = self.hand.index(treasures[disc])
        c = self.hand[idx]
        self.game.trash.append(self.hand[idx])
        del self.hand[idx]
        
        max_price = c.price + 3
        cards = []
        for s in player.game.stacks:
            if s.count > 0 and s.type.price <= max_price and s.type.type & TREASURE == TREASURE:
                cards.append(s)
        if not cards:
            return
        gain_which = player.player_interface.ask_whichgain(cards)
        if gain_which < 0:
            gain_which = 0

        cards[gain_which].count -= 1
        player.hand.append(cards[gain_which].type())
        
class Adventurer(Card):
    price = 6
    type = ACTION
    name = "Adventurer"
    def play(self, player):
        treasures = []
        cards = []
        c = player.get_top_card()
        while len(treasures) < 2 and c is not None:
            player.reveal_card(c)
            if c.type & TREASURE == TREASURE:
                treasures.append(c)
            else:
                cards.append(c)
            c = player.get_top_card()
        
        player.hand.extend(treasures)
        player.discard_pile.extend(cards)
            
        
class Village(Card):
    price = 3
    type = ACTION
    name = "Village"
    def play(self, player):
        player.draw_card()
        player.actions += 2
        
class Festival(Card):
    price = 5
    type = ACTION
    name = "Festival"
    def play(self, player):
        player.actions += 2
        player.buys += 1
        player.money += 2
        
class Smithy(Card):
    price = 4
    type = ACTION
    name = "Smithy"
    def play(self, player):
        for i in xrange(3):
            player.draw_card()
            
class Moat(Card):
    price = 2
    type = ACTION | REACTION
    name = "Moat"
    def play(self, player):
        player.draw_card()
        player.draw_card()
    
    def handle_attack(self, player, attacker):
        return False
        
class Bureaucrat(Card):
    price = 4
    type = ACTION | ATTACK
    name = "Bureaucrat"
    def play(self, player):
        silver_stack = [s for s in player.game.stacks if s.type.name == "Silver"]
        if silver_stack:
            silver_stack = silver_stack[0]
            silver_stack.count -= 1
            player.deck.insert(0, silver_stack.type())
            for p in player.get_other_players():
                if p.attack(player, self):
                    victory_cards = []
                    for c in p.hand:
                        if c.type & VICTORY == VICTORY:
                            victory_cards.append(c)
                    if not victory_cards:
                        for c in p.hand:
                            p.reveal_card(c)
                    which = p.choose_victorycard(victory_cards, self)
                    p.reveal_card(victory_cards[which])
                    idx = p.hand.index(victory_cards[which])
                    p.deck.insert(0, p.hand[idx])
                    del p.hand[idx]

class Militia(Card):
    price = 4
    type = ACTION | ATTACK
    name = "Militia"
    def play(self, player):
        player.money += 2
        for p in player.get_other_players():
            if p.attack(player, self):
                while len(p.hand) > 3:
                    p.discard()
                    
class Spy(Card):
    price = 4
    type = ACTION | ATTACK
    name = "Spy"
    def play(self, player):
        player.actions += 1
        player.draw_card()
        for p in player.game.players:
            if p == player or p.attack(player, self):
                c = p.get_top_card()
                p.reveal_card(c)
                keep = player.ask_keep(p, c)
                if keep:
                    p.deck.insert(0, c)
                else:
                    p.discard_pile.append(c)
                    
class Thief(Card):
    price = 4
    type = ACTION | ATTACK
    name = "Thief"
    def play(self, player):
        for p in player.get_other_players():
            if p.attack(player, self):
                c1 = p.get_top_card()
                p.reveal_card(c1)
                c2 = p.get_top_card()
                p.reveal_card(c2)
                treasures = []
                if c1.type & TREASURE == TREASURE:
                    treasures.append(c1)
                else:
                    p.discard_pile.append(c1)
                if c2.type & TREASURE == TREASURE:
                    treasures.append(c2)
                else:
                    p.discard_pile.append(c2)
                if treasures:
                    import pdb
                    pdb.set_trace()
                    which = player.ask_whichtrash(treasures, True)
                    if which > 0:
                        gain = player.ask_wantgain(treasures[which])
                        if gain:
                            player.discard_pile.append(treasures[which])
                        else:
                            player.game.trash.append(treasures[which])
                        del treasures[which]
                    p.discard_pile.extend(treasures)
                        
class Witch(Card):
    price = 5
    type = ACTION | ATTACK
    name = "Witch"
    def play(self, player):
        player.draw_card()
        player.draw_card()
        curse_stack = [s for s in player.game.stacks if s.type.name == "Curse"]
        curse_stack = curse_stack[0]
        for p in player.get_other_players():
            if p.attack(player, self) and curse_stack.count > 0:
                p.discard_pile.append(curse_stack.type())
                curse_stack.count -= 1
                
class Library(Card):
    price = 5
    type = ACTION
    name = "Library"
    def play(self, player):
        next = True
        aside = []
        while len(player.hand) < 7 and next:
            next_card = player.get_top_card()
            if next_card:
                if next_card.type & ACTION == ACTION:
                    if not player.ask_keep(player, next_card):
                        aside.append(next_card)
                        continue
                player.hand.append(next_card)
            else:
                next = False