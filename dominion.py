from player_interface import PlayerInterface
import random
import sys
import optparse
import cards
import threading
import gtk
import gobject

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
            raise
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
        
    def ask_whichtrash(self, choices, optional=False, reason=None):
        return self.player_interface.ask_whichtrash(choices, optional, reason)
        
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
        except Exception:
            raise
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
            raise
            disc = -1
        if disc < 0 and optional:
            return False
        if disc < 0:
            disc = 0
        if disc > len(self.hand) -1:
            disc = len(self.hand) -1
        self.discard_pile.append(self.hand[disc])
        del self.hand[disc]
        return True
        
    def trash(self, optional=False):
        if not self.hand:
            return None
        try:
            disc = self.player_interface.ask_whichtrash(self.hand, optional)
        except Exception:
            raise
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
                result = result and reactions[which].handle_attack(self.player_interface, attacker)
                del reactions[which]
        return result
    
    def calculate_points(self):
        self.points = 0
        self.deck = self.in_play + self.deck + self.hand + self.discard_pile
        which = {}
        for c in self.deck:
            if c.type & cards.VICTORY == cards.VICTORY:
                self.points += c.get_points(self)
                if c.name not in which:
                    which[c.name] = 0
                which[c.name] += 1
            if c.type & cards.CURSE == cards.CURSE:
                self.points += c.get_points(self)
                if c.name not in which:
                    which[c.name] = 0
                which[c.name] += 1
        print self.name, "has"
        for c in which:
            print "\t",which[c], c
    
    
    def tell_stacks(self, stacks):
        self.player_interface.tell_stacks(stacks)
                
    def tell_winner(self, winner, *args):
        self.player_interface.tell_winner(winner.player_interface.get_name(), *args)
        
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
        for p in self.players:
            print "%s: %d"%(p.name, p.points)
            print >> sys.stderr, "%s: %d"%(p.name, p.points)
        print >> sys.stderr, "%s WON!"%self.players[-1].name
        winner = self.players[-1]
        for p in self.players:
            p.tell_winner(winner, p.points, sum(map(lambda p: p.points, self.players)))

    def check_game_end(self):
        return self.stacks[-1].count == 0

def make_start_deck():
    return [cards.Copper() for i in xrange(7)] + [cards.Estate() for i in xrange(3)]
    
def make_player(type, nr):
    if type == "basic":
        interface = PlayerInterface("Player %d"%nr)
    elif type == "ai.random":
        import ai
        interface = ai.RandomPlayer("Player %d"%nr)
    elif type == "ai.counting":
        import ai
        interface = ai.CountingPlayer("Player %d"%nr)
    elif type == "ai.expensive":
        import ai
        interface = ai.ExpensiveCardPlayer("Player %d"%nr)
    elif type == "gtk":
        import ui
        interface = ui.GtkPlayer("Player %d"%nr)
    return Player(make_start_deck(), interface, "Player %d"%nr)

def main():
    parser = optparse.OptionParser()
    parser.add_option("-1", "--player-1", "--p1", action="store", type="choice", choices=["basic", "ai.random", "gtk", "ai.counting", "ai.expensive"], default="ai.random", dest="player1")
    parser.add_option("-2", "--player-2", "--p2", action="store", type="choice", choices=["basic", "ai.random", "gtk", "ai.counting", "ai.expensive"], default="ai.random", dest="player2")
    parser.add_option("-3", "--player-3", "--p3", action="store", type="choice", choices=["basic", "ai.random", "gtk", "ai.counting", "ai.expensive"], default=None, dest="player3")
    parser.add_option("-4", "--player-4", "--p4", action="store", type="choice", choices=["basic", "ai.random", "gtk", "ai.counting", "ai.expensive"], default=None, dest="player4")
    (options,args) = parser.parse_args()
    players = [make_player(options.player1, 1), make_player(options.player2, 2)]
    g = Game(players)
    use_gtk = False
    for p in [options.player1, options.player2]:
        if p == "gtk":
            use_gtk = True
    if use_gtk:
        import gobject
        import gtk
        gobject.threads_init()
        t = threading.Thread(target=g.run)
        t.start()
        gtk.main()
    else:
        g.run()
        
if __name__ == "__main__":
    main()