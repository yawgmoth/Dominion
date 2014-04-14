import random
import player_interface
import json
import dominion
from cStringIO import StringIO
import sys

class MonteCarloTrialPlayer(player_interface.PlayerInterface):
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats
        self.current_play = ()
        self.buyphase = False
        
    def tell_stacks(self, stacks):
        pass
        
    def tell_start_turn(self):
        pass

    def tell_hand(self, hand):
        pass
            
    def tell_deck(self, hand):
        pass

    def tell_stats(self, player):
        if self.buyphase:
            self.buys = player.buys
            self.money = player.money
            if self.current_play not in self.stats:
                self.stats[self.current_play] = (0.0,0)
            v,count = self.stats[self.current_play]
            self.stats[self.current_play] = ((v*count + self.value())/(count+1.0),count+1.0)
            self.buyphase =  False
            
    def value(self):
        # TODO: take buylist into account
        return self.money
        
    def tell_buyphase(self):
        self.buyphase = True
        
    def tell_reveal(self, player, card):
        pass
    
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
        matches = []
        
        noplayvalue = (0.0,0.0)
        for s in self.stats:
            match = True
            for i, a in enumerate(self.current_play):
                if i >= len(s) or s[i] != a:
                    match = False
            if len(s) > len(self.current_play) and s[len(self.current_play)] not in map(lambda a: a.name, actions):
                match = False
            if len(s) == len(self.current_play):
                v,c = noplayvalue
                noplayvalue = ((v*c + self.stats[s][0]*self.stats[s][1])/(c + self.stats[s][1]),(c + self.stats[s][1]))
                match = False
            if match:
                matches.append((s,self.stats[s]))
        opts = map(lambda a: a.name, actions)
        additional_options = []
        for o in opts:
            found = False
            for m,v in matches:
                if len(m) > len(self.current_play) and m[len(self.current_play)] == o:
                    found = True
            if not found:
                additional_options.append((self.current_play + (o,),(1,1)))
        matches.extend(additional_options)
        
        match_groups = {}
        for m,(mv,mc) in matches:
            seq = tuple(m[:len(self.current_play)+1])
            if seq not in match_groups:
                match_groups[seq] = (0,0)
            v,count = match_groups[seq]
            match_groups[seq] = ((v*count + mv*mc)/(count+mc),count+mc)
        if noplayvalue[0] == 0:
            noplayvalue = (1,1)
        matches = [(None, noplayvalue[0])]
        for m in match_groups:
            matches.append((m,match_groups[m][0]))
        
        def roulette_wheel(itemvalues):
            total = sum(itemvalues)
            r = random.random()*total
            at = 0.0
            i = 0
            while at <= r:
                at += itemvalues[i]
                i += 1
            return i-1        
        i = roulette_wheel(map(lambda (m,v): v, matches))
        if matches[i][0] is None:
            print "I'm done playing actions"
            return -1
        m = matches[i][0][-1]
        self.current_play = self.current_play + (m,)
        print "after careful consideration I have concluded that the best course of action is", m
        return map(lambda a: a.name, actions).index(m)
        
        
        # TODO
        
    def ask_whichbuy(self, options):
        return -1
        
    def ask_whichgain(self, options):
        result = self.ask_which(map(lambda x: x.type.name, options), message="which gain?")
        return result
        
    def ask_whichdiscard(self, cards, optional):
        if optional:
            return -1
        
        return 0
        # TODO
        
    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        if optional:
            return -1
        # TODO
        return 0
        
    def ask_putdiscard(self):
        return self.ask_yesno()
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(options)
        
    def ask_keep(self, player, card):
        # TODO
        return self.ask_yesno()
        
    def ask_wantgain(self, card):
        # TODO
        return self.ask_yesno()

    def tell_attack(self, attacker, card):
        pass
        
    def tell_winner(self, winner, *args):
        pass
    
    def get_name(self):
        return self.name
        

class MonteCarloPlayer(player_interface.PlayerInterface):
    def __init__(self, name, trials=500, write_stats=False):
        self.name = name
        self.hand = []
        self.last_played = ""
        self.trials = 100
        self.times = (0,0)
        self.write_stats = write_stats
        if self.write_stats == "False":
            self.write_stats = False
        if self.write_stats:
            f = file("stats.log", "a+")
            f.close()
        self.hand = []
        self.actions = 0
        self.buys = 0
        self.money = 0
        
    def tell_stacks(self, stacks):
        print "Available stacks this game:"
        for s in stacks:
            if self.write_stats:
                f = file("stats.log", "a+")
                print >>f, s.type.name, " (" + str(s.count) + " available)"
                f.close()
            print s.type.name, " (" + str(s.count) + " available)"
        
    def tell_start_turn(self):
        self.last_played = ""
        print self.name + ", it's your turn!"

    def tell_hand(self, hand):
        print "Your hand contains:"
        self.hand = hand
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
        self.actions = player.actions
        self.buys = player.buys
        self.money = player.money
        
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
        
    def set_game(self, game):
        self.game = game
    
    def ask_whichaction(self, actions):            
        state = self.game.get_state()
        stats = {}
        stdout = sys.stdout
        stderr = sys.stderr
        import time
        t0 = time.time()
        try:
            
            for i in xrange(self.trials):
                sys.stdout = StringIO()
                sys.stderr = StringIO()
                players = []
                for j in xrange(len(self.game.players)):
                    if j == self.game.active_player:
                        players.append(MonteCarloTrialPlayer("Player %d"%j, stats=stats))
                    else:
                        players.append(MonteCarloTrialPlayer("Player %d"%j, stats={}))
                g = dominion.Game.from_state(state, players, shuffle=True)
                g.run(limit=1, fill_hand=False)
                
            sys.stdout = stdout
            sys.stderr = stderr
        except Exception:
            sys.stdout = stdout
            sys.stderr = stderr
            raise
        dt = time.time() - t0
        t,c = self.times
        self.times = ((t*c+dt)/(c+1.0),c+1.0)
        
        best = stats[stats.keys()[0]][0]
        bestat = stats.keys()[0]
        
        stat_groups = {}
        for s in stats:
            act = None
            if s:
                act = s[0] 
            if act not in stat_groups:
                stat_groups[act] = []
            stat_groups[act].append(stats[s])
            
        stat_group_values = {}
        for s in stat_groups:
            stat_group_values[s] = 0
            total = sum(map(lambda (v,c): c, stat_groups[s]))
            stat_group_values[s] = sum(map(lambda (v,c): v*c/total, stat_groups[s]))
        
        best = stat_group_values[stat_group_values.keys()[0]]
        bestat = stat_group_values.keys()[0]
        for s in stat_group_values:
            if stat_group_values[s] > best:
                best = stat_group_values[s]
                bestat = s
                        

        if self.write_stats:
           f = file("stats.log", "a+")
           print >>f, "needed", dt
           print >>f, "Hand:", map(lambda a: a.name, self.hand)
           print >>f, "money:", self.money, "buys:", self.buys, "actions:", self.actions
           print >>f, "stats:", stats
           print >>f, "stat groups:", stat_groups
           print >>f, "stat group values:", stat_group_values
           print >>f, "\nplan:", bestat
           print >>f, "\n\n"
           f.close()
        
        if not bestat:
            return -1
        next = bestat
        
        if next not in map(lambda a: a.name, actions):
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            import pdb
            pdb.set_trace()
        return map(lambda a: a.name, actions).index(next)
        
        
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
        #import pdb
        #pdb.set_trace()
        return self.ask_yesno()
        
    def ask_wantgain(self, card):
        if self.last_played in self.playlist and "gain" in self.playlist[self.last_played]:
            return card.name in self.playlist[self.last_played]["gain"]
        return self.ask_yesno()

    def tell_attack(self, attacker, card):
        pass
        
    def tell_winner(self, winner, *args):
        print "Times:", self.times
    
    def get_name(self):
        return self.name