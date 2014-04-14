import random
import player_interface
import dominion
import os

class CombiningPlayer(player_interface.PlayerInterface):
    def __init__(self, name, buy="ai.buylist", play="ai.heuristic", buyopts="", playopts=""):
        self.name = name
        nr = 10
        try:
            nr = int(self.name.split()[-1])*10
        except Exception: 
            pass
        self.buy = dominion.make_player(buy, nr + 1, buyopts.replace(";",","), interface_only=True)
        self.play = dominion.make_player(play, nr + 2, playopts.replace(";",","), interface_only=True)

    def set_game(self, game):
        self.game = game
        
    def tell_stacks(self, stacks):
        self.buy.tell_stacks(stacks)
        self.play.tell_stacks(stacks)        
            
    def tell_start_turn(self):
        self.buy.tell_start_turn()
        self.play.tell_start_turn()

    def tell_hand(self, hand):
        self.buy.tell_hand(hand)
        self.play.tell_hand(hand)
            
    def tell_deck(self, deck):
        self.buy.tell_deck(deck)
        self.play.tell_deck(deck)

    def tell_stats(self, player):
        self.buy.tell_stats(player)
        self.play.tell_stats(player)
        
    def tell_buyphase(self):
        self.buy.tell_buyphase()
        self.play.tell_buyphase()
        
    def tell_reveal(self, player, card):
        self.buy.tell_reveal(player, card)
        self.play.tell_reveal(player, card)
    
    def ask_buy(self, money=0):
        return self.buy.ask_buy(money)

    def ask_yesno(self):
        return self.play.ask_yesno()
        
    def ask_action(self):
        return self.play.ask_action()
        
    def ask_which(self, choices, message=""):
        return self.play.ask_which(choices, message)
    
    def ask_whichaction(self, actions):
        return self.play.ask_whichaction(actions)
        
    def ask_whichbuy(self, options):
        return self.buy.ask_whichbuy(options)

    def ask_whichgain(self, options):
        return self.buy.ask_whichgain(options)
        
    def ask_whichdiscard(self, cards, optional):
        return self.play.ask_whichdiscard(cards, optional)
        
    def ask_whichreaction(self, cards):
        return self.play.ask_whichreaction(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        return self.play.ask_whichtrash(cards, optional, *args)
        
    def ask_putdiscard(self):
        return self.play.ask_putdiscard()
        
    def ask_whichvictorycard(self, options, cause):
        return self.play.ask_whichvictorycard(options, cause)
        
    def ask_keep(self, player, card):
        return self.play.ask_keep(player, card)
        
    def ask_wantgain(self, card):
        return self.buy.ask_wantgain(card)

    def tell_attack(self, attacker, card):
        self.play.tell_attack(attacker, card)
        self.buy.tell_attack(attacker, card)
        
    def tell_winner(self, winner, *args):
        self.play.tell_winner(winner, *args)
        self.buy.tell_winner(winner, *args)
    
    def get_name(self):
        return self.name
        
    def set_game(self, game):
        self.play.set_game(game)
        self.buy.set_game(game)