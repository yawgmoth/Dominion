class PlayerInterface:
    def __init__(self, name):
        print "Welcome to Dominion", name
        self.name = name
        
    def set_game(self, game):
        pass
        
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
        print player.name, "reveals", card.name
    
    def ask_buy(self, money=0):
        return self.ask_yesno("Do you want to buy something?")

    def ask_yesno(self, message):
        response = ""
        while response not in ["Y", "N"]:
            print message, "(Y/N)"
            answer = raw_input()
            response = answer # TODO: map "yes", "YES", ... to "Y", likewise for "N"
        return response == "Y"
        
    def ask_action(self):
        return self.ask_yesno("Do you want to play an action card?")
        
    def ask_which(self, choices, message):
        print message
        for i, c in enumerate(choices):
            print " ", i+1, c
        choice = int(raw_input())
        return choice-1
    
    def ask_whichaction(self, actions):
        return self.ask_which(map(lambda a: a.name, actions), "Which action card do you want to play? (0 to stop playing actions)")
        
    def ask_whichbuy(self, options):
        return self.ask_which(map(lambda a: a.type.name + " ($" + str(a.type.price) + ", " + str(a.count) + " left)", options), "Which card do you want to buy? (0 to stop buying)")
        
    def ask_whichgain(self, options):
        return self.ask_which(map(lambda a: a.type.name + " ($" + str(a.type.price) + ", " + str(a.count) + " left)", options), "Which card do you want to gain?")
        
    def ask_whichdiscard(self, cards, optional):
        return self.ask_which(map(lambda c: c.name, cards), "Which card do you want to discard?" + (" (0 to stop discarding)" if optional else ""))
        
    def ask_whichreaction(self, cards):
        return self.ask_which(map(lambda c: c.name, cards), "Which reaction do you want to use? (0 to stop responding)")
        
    def ask_whichtrash(self, cards, optional, *args):
        return self.ask_which(map(lambda c: c.name, cards), "Which card do you want to trash?" + (" (0 to not trash anything)" if optional else ""))
        
    def ask_putdiscard(self):
        return self.ask_yesno("Do you want to put your deck into your discard pile?")
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(map(lambda c: c.name, options), "Which victory do you want to choose for " + cause.name +"?")
        
    def ask_keep(self, player, card):
        return self.ask_yesno("Can " + player.name + " keep " + card.name + "?")
        
    def ask_wantgain(self, card):
        return self.ask_yesno("Do you want to gain " + card.name + "?")

    def tell_attack(self, attacker, card):
        print attacker.name, "is attacking you with", card.name
        
    def tell_winner(self, winner, *args):
        print winner, "has won the game!"
    
    def get_name(self):
        return self.name
    
        