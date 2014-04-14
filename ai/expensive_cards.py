import random
import player_interface

class ExpensiveCardPlayer(player_interface.PlayerInterface):
    def __init__(self, name):
        self.name = name
        
    def tell_stacks(self, stacks):
        print "Available stacks this game:"
        for s in stacks:
            print s.type.name, " (" + str(s.count) + " available)"
        
    def tell_start_turn(self):
        print self.name + ", it's your turn!"

    def tell_hand(self, hand):
        print "Your hand contains:"
        for h in hand:
            print " ", h.name
            
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
        actions = actions[:]
        random.shuffle(actions)
        maxcost = 0
        choice = -1
        for i, a in enumerate(actions):
            if a.price > maxcost:
                maxcost = a.price
                choice = i
        return choice
        
    def ask_whichbuy(self, options):
        maxcost = 0
        choice = -1
        options = options[:]
        random.shuffle(options)
        for i, o in enumerate(options):
            if o.type.price > maxcost:
                maxcost = o.type.price
                choice = i
        return choice
        
    def ask_whichgain(self, options):
        maxcost = 0
        choice = -1
        
        for i, o in enumerate(options):
            if o.type.price > maxcost:
                maxcost = o.type.price
                choice = i
        return choice
        
    def ask_whichdiscard(self, cards, optional):
        options = cards
        if optional:
            return -1

        return self.ask_which(options)
        
    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        if optional: return -1
        return self.ask_which(cards)
        
    def ask_putdiscard(self):
        return self.ask_yesno()
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(options)
        
    def ask_keep(self, player, card):
        return self.ask_yesno()
        
    def ask_wantgain(self, card):
        return self.ask_yesno()

    def tell_attack(self, attacker, card):
        pass
        
    def tell_winner(self, winner, *args):
        print winner, "has won the game!"
    
    def get_name(self):
        return self.name