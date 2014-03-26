import random
import player_interface
import json

def load_playlist(fname):
    f = open(fname)
    playlist = json.load(f)    
    f.close()
    return playlist
    
def evaluate(condition, hand):
    # {"card": "Village", "op": ">", "qty": 0} 
    qty = 0
    if condition["card"] == "Total":
        qty = len(hand)
    else:
        for h in hand:
            if h.name == condition["card"]:
                qty += 1
    if condition["op"] == ">" and qty > condition["qty"]:
        return True
    elif condition["op"] == "<" and qty < condition["qty"]:
        return True
    return False

class HeuristicPlayer(player_interface.PlayerInterface):
    def __init__(self, name, heuristic_file="default.play", playlist = None):
        self.name = name
        self.hand = []
        if playlist:
            self.playlist = playlist
        else:
            self.playlist = load_playlist(heuristic_file)
        self.last_played = ""
        
    def tell_stacks(self, stacks):
        print "Available stacks this game:"
        for s in stacks:
            print s.type.name, " (" + str(s.count) + " available)"
        
    def tell_start_turn(self):
        self.last_played = ""
        print self.name + ", it's your turn!"

    def tell_hand(self, hand):
        print "Your hand contains:"
        for h in hand:
            print " ", h.name
        self.hand = hand
            
    def tell_deck(self, hand):
        print "Your deck contains:"
        for h in hand:
            print " ", h.name

    def tell_stats(self, player):
        print "You have:"
        print " ", player.actions, "Actions"
        print " ", player.buys, "Buys"
        print " ", player.money, "Money"
        
    def tell_buyphase(self):
        print "Buyphase!"
        
    def tell_reveal(self, player, card):
        if card:
            print player.name, "reveals", card.name
    
    def ask_buy(self, money=0):
        return self.ask_yesno()

    def ask_yesno(self):
        return random.choice([True, False])
        
    def ask_action(self):
        return self.ask_yesno()
        
    def ask_which(self, choices, message=""):
        if not choices:
            return -1
        if message:
            print message
            for i, c in enumerate(choices):
                print " ", i+1, c
        return random.randint(0,len(choices)-1)
    
    def ask_whichaction(self, actions):
        for p in self.playlist["play"]:
            do = True
            for c in p["conditions"]:
                if not evaluate(c, self.hand):
                    do = False
            if do and p["card"] in map(lambda h: h.name, self.hand):
                try:
                    i = map(lambda a: a.name, actions).index(p["card"])
                    self.last_played = p["card"]
                    return i
                except ValueError:
                    print "card is in hand, but not available as an action ...", self.hand, actions
                    pass
                    
        return -1
        result = self.ask_which(map(lambda x: x.name, actions), message="Which action?")
        if not actions: return -1
        print "play", actions[result].name
        return result
        
    def ask_whichbuy(self, options):
        result = self.ask_which(map(lambda x: x.type.name, options), message="which buy?")
        if not options: return -1
        print "Buy", options[result].type.name
        return result
        
    def ask_whichgain(self, options):
        result = self.ask_which(map(lambda x: x.type.name, options), message="which gain?")
        print "gain", options[result].type.name
        return result
        
    def ask_whichdiscard(self, cards, optional):
        for p in self.playlist["trash"]:
            if p in cards:
                return cards.index(p)
        if optional:
            return -1
        for p in reversed(self.playlist["play"]):
            if p["card"] in cards:
                return cards.index(p["card"])
        return 0
    
        options = cards
        if optional:
            options = ["Do nothing"] + options
        return self.ask_which(options)
        
    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        for p in self.playlist["trash"]:
            if p in map(lambda c: c.name, cards):
                return cards.index(p)
        if optional:
            return -1
        for p in reversed(self.playlist["play"]):
            if p["card"] in map(lambda c: c.name, cards):
                return cards.index(p["card"])
        return 0
        
    def ask_putdiscard(self):
        return self.ask_yesno()
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(options)
        
    def ask_keep(self, player, card):
        import pdb
        pdb.set_trace()
        return self.ask_yesno()
        
    def ask_wantgain(self, card):
        if self.last_played in self.playlist and "gain" in self.playlist[self.last_played]:
            return card.name in self.playlist[self.last_played]["gain"]
        return self.ask_yesno()

    def tell_attack(self, attacker, card):
        pass
        
    def tell_winner(self, winner, *args):
        print winner, "has won the game!"
    
    def get_name(self):
        return self.name