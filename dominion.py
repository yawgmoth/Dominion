from player_interface import PlayerInterface
import random

import cards


class Player:
    def __init__(self, deck, player_interface, name):
        self.hand = []
        self.deck = deck
        self.discard_pile = []
        self.in_play = []
        self.player_interface = player_interface
        self.name = name
        
    def get_other_players(self):
        players = []
        for p in self.game.players:
            if p != self:
                players.append(p)
        return players
        
    def reshuffle(self):
        self.deck.extend(self.discard_pile)
        self.discard_pile = []
        random.shuffle(self.deck)

    def start_turn(self):
        self.player_interface.tell_start_turn()
        #self.player_interface.tell_deck(self.deck)
        self.actions = 1
        self.buys = 1
        self.money = 0
        while self.in_play:
            self.in_play[0].start_turn(self)
            del self.in_play[0]
        self.player_interface.tell_hand(self.hand)
        self.player_interface.tell_stats(self)
   
    def choose_action(self):
        actions = []
        for c in self.hand:
            if c.type & cards.ACTION == cards.ACTION and c.can_play(self):
                actions.append(c)
        if not actions:
            return None
        try:
            which = self.player_interface.ask_whichaction(actions)
            if which < 0:
                return None
            a = actions[which]
        except Exception:
            return None
        return a
            
    def perform_action(self):
        a = self.choose_action()
        if not a:
            return False
        a.pre_play(self)
        a.play(self)
        a.post_play(self)
        self.player_interface.tell_hand(self.hand)
        self.player_interface.tell_stats(self)
        return True
        
    def play_money(self):
        # TODO: ask player if they want to play all money
        #       and which they want to play, if not all
        i = 0
        while i < len(self.hand):
            if self.hand[i].type & cards.TREASURE == cards.TREASURE:
                self.money += self.hand[i].value
                self.in_play.append(self.hand[i])
                del self.hand[i]
            else:
                i += 1
        
    def tell_buyphase(self):
        self.player_interface.tell_buyphase()
        self.player_interface.tell_stats(self)
        
    def ask_keep(self, player, card):
        return self.player_interface.ask_keep(player, card)
        
    def ask_whichtrash(self, choices, optional=False):
        return self.player_interface.ask_whichtrash(choices, optional)
        
    def ask_wantgain(self, card):
        return self.player_interface.ask_wantgain(card)
        
    def perform_buy(self):
        options = []
        for c in self.game.stacks:
            if c.type.price <= self.money and c.count:
                options.append(c)
        try:
            which = self.player_interface.ask_whichbuy(options)
            if which < 0:
                return False
            c = options[which]
        except:
            return False
        self.discard_pile.append(c.type())
        c.count -= 1
        self.buys -= 1
        self.money -= c.type.price
        return True

    def end_turn(self):
        i = 0
        while i < len(self.in_play):
            if self.in_play[i].perform_cleanup():
                self.discard_pile.append(self.in_play[i])
                del self.in_play[i]
            else:
                i += 1
        self.discard_pile.extend(self.hand)
        self.hand = []
        
        for i in xrange(5):
            self.draw_card()
        
    def get_top_card(self):
        if not self.deck and self.discard_pile:
            self.reshuffle()
        if not self.deck:
            return None
        result = self.deck[0]
        self.deck = self.deck[1:]
        return result
    
    def draw_card(self):
        result = self.get_top_card()
        if not result:
            return None
        self.hand.append(result)
        
    def reveal_card(self, card):
        for p in self.game.players:
            p.tell_reveal(self, card)
    
    def tell_reveal(self, player, card):
        self.player_interface.tell_reveal(player, card)
        
    def discard(self, optional=False):
        if not self.hand:
            return False
        try:
            disc = self.player_interface.ask_whichdiscard(self.hand, optional)
        except Exception:
            disc = -1
        if disc < 0 and optional:
            return False
        if disc < 0:
            disc = 0
        self.discard_pile.append(self.hand[disc])
        del self.hand[disc]
        return True
        
    def trash(self, optional=False):
        if not self.hand:
            return None
        try:
            disc = self.player_interface.ask_whichtrash(self.hand, optional)
        except Exception:
            disc = -1
        if disc < 0 and optional:
            return None
        if disc < 0:
            disc = 0
        c = self.hand[disc]
        self.game.trash.append(self.hand[disc])
        del self.hand[disc]
        return c
    
    def choose_victorycard(self, choices, why):
        idx = self.player_interface.ask_whichvictorycard(choices, why)
        if idx < 0:
            idx = 0
        return idx
        
    def attack(self, attacker, card):
        self.player_interface.tell_attack(attacker, card)
        reactions = []
        for c in self.hand:
            if c.type & cards.REACTION == cards.REACTION:
                reactions.append(c)
        result = True
        which = 0
        while reactions and which >= 0:
            which = self.player_interface.ask_whichreaction(reactions)
            if which >= 0:
                result = result and reactions[which].handle_attack()
                del reactions[which]
        return result
    
    def calculate_points(self):
        self.points = 0
        self.deck = self.in_play + self.deck + self.hand + self.discard_pile
        for c in self.deck:
            if c.type & cards.VICTORY == cards.VICTORY:
                self.points += c.get_points(self)
            if c.type & cards.CURSE == cards.CURSE:
                self.points += c.get_points(self)
    
    
    def tell_stacks(self, stacks):
        self.player_interface.tell_stacks(stacks)
                
    def tell_winner(self, winner):
        self.player_interface.tell_winner(winner.player_interface.get_name())
        
class Game:
    def __init__(self, players):
        self.players = players
        self.stacks = cards.make_stacks()
        self.trash = []
        for p in self.players:
            p.game = self

    def run(self):
        for p in self.players:
            p.tell_stacks(self.stacks)
        self.active_player = 0
        for p in self.players:
            p.reshuffle()
            for i in xrange(5):
                p.draw_card()
        while not self.check_game_end():
            p = self.players[self.active_player]
            p.start_turn()
            want_play = True
            while p.actions > 0 and want_play:
                want_play = p.perform_action()
            p.play_money()
            p.tell_buyphase()
            want_buy = True
            while p.buys > 0 and want_buy:
                want_buy = p.perform_buy()
            p.end_turn()
            self.active_player += 1
            self.active_player %= len(self.players)
        for p in self.players:
            p.calculate_points()
        self.players.sort(key=lambda p: p.points)
        winner = self.players[0]
        for p in self.players:
            p.tell_winner(winner)

    def check_game_end(self):
        return self.stacks[-1].count == 0

def main():
    players = [Player([cards.Copper() for i in xrange(7)] + [cards.Estate() for i in xrange(3)], 
                      PlayerInterface("Player %d"%j), "Player %d"%j) for j in xrange(2)]
    g = Game(players)
    g.run()
        
if __name__ == "__main__":
    main()