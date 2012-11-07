import random
import os
import cPickle

EXPLORATION_RATE = 1.0
STRETCH_FACTOR = 1.0

class TotalWinDict:
    def __init__(self):
        self.total = dict()
        self.total_orig = dict()
        self.won = dict()
    def initialize(self):
        self.total_orig = self.total
        self.total = dict()
    def finalize(self, won, points, totalpoints):
        for k in self.total:
            if k not in self.total_orig:
                self.total_orig[k] = 0
            self.total_orig[k] += self.total[k]*abs(2*points - totalpoints)
            if won:
                if k not in self.won:
                    self.won[k] = 0
                self.won[k] += self.total[k]*abs(totalpoints-2*points)
        self.total = self.total_orig
        self.total_orig = dict()
    def select(self, choices):
        probs = []
        for c in choices:
            if c in self.won:
                wincount = self.won[c]
                if wincount < 0:
                    wincount = 1
                perc = wincount*1.0/self.total_orig[c]
                dev = perc-0.5
                sgn = -1 if dev < 0 else 1
                stretched = sgn*(abs(dev)**STRETCH_FACTOR) + 0.5**STRETCH_FACTOR
                probs.append(stretched)
            else:
                probs.append(EXPLORATION_RATE)
        probsum = sum(probs)
        which = random.random()*probsum
        
        p = 0
        i = 0
        while p < which:
            p += probs[i]
            i += 1
        i -= 1
        print choices
        print "select", which, "(at", i, ") from", probs
        if choices[i] not in self.total:
            self.total[choices[i]] = 0
        self.total[choices[i]] += 1
        return choices[i]
        
    def __str__(self):
        lines = []
        result = ""
        for k in self.total:
            wincount = 0
            if k in self.won:
                wincount = self.won[k]
            if self.total[k] != 0:
                perc = wincount*100.0/self.total[k]
                lines.append((perc, "\t%s: %.2f%% (%d/%d won)\n"%(k, perc, wincount, self.total[k])))
            else:
                lines.append((0, "\t%s: %d\n"%(k,wincount*100.0)))
        lines.sort(key=lambda x: -x[0])
        for l in lines:
            result += l[1]
        return result
        

class GameStats:
    def __init__(self):
        self.count = 0
        self.won = 0
        self.bought = dict() #TotalWinDict()
        self.played = TotalWinDict()
        self.decisions = dict()
        self.discarded = TotalWinDict()
        self.trashed = TotalWinDict()

    def finalize(self, won, points, totalpoints):
        for k in self.bought:
            self.bought[k].finalize(won, points, totalpoints)
        self.played.finalize(won, points, totalpoints)
        for k in self.decisions:
            self.decisions[k].finalize(won, points, totalpoints)
        self.discarded.finalize(won, points, totalpoints)
        self.trashed.finalize(won, points, totalpoints)
        self.count += 1
        if won:
            self.won += 1
        
    def initialize(self):
        for k in self.bought:
            self.bought[k].initialize()
        self.played.initialize()
        for k in self.decisions:
            self.decisions[k].initialize()
        self.discarded.initialize()
        self.trashed.initialize()
        
    def __str__(self):
        result = "Won %d of %d games\n"%(self.won, self.count)
        result += "buy stats:\n"
        for k in self.bought:
            result += "for " + str(k) + ":\n"
            result += str(self.bought[k])
        result += "play stats:\n"
        result += str(self.played)
        result += "discard stats:\n"
        result += str(self.discarded)
        result += "trash stats:\n"
        result +=  str(self.trashed)
        return result
        

class CountingPlayer:
    def __init__(self, name):
        self.name = name
        self.fname = name
        if os.path.exists(self.fname):
            f = open(self.fname)
            self.stats = cPickle.load(f)
            self.stats.initialize()
            f.close()
        else:
            self.stats = GameStats()
        
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
        self.money = player.money
        self.actions = player.actions
        self.buys = player.buys
        
    def tell_buyphase(self):
        print "Buyphase!"
        
    def tell_reveal(self, player, card):
        if card:
            print player.name, "reveals", card.name
    
    def ask_buy(self, money=0):
        raise "Not implemented"
        return self.ask_yesno()

    def ask_yesno(self):
        return random.choice([True, False])
        
    def ask_action(self):
        raise "Not implemented"
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
        result = self.stats.played.select(["None"] + map(lambda x: x.name, actions))
        #import pdb
        #pdb.set_trace()
        for i, a in enumerate(actions):
            if a.name == result:
                print "play", result
                return i
        print "play nothing"
        return -1
        
    def ask_whichbuy(self, options):
        #import pdb
        #pdb.set_trace()
        self.money = 0
        if self.money not in self.stats.bought:
            self.stats.bought[self.money] = TotalWinDict()
        result = self.stats.bought[self.money].select(["None"] + map(lambda x: x.type.name, options))
        for i, a in enumerate(options):
            if a.type.name == result:
                print "buy", result
                return i
        print "buy nothing"
        return -1
        result = self.ask_which(map(lambda x: x.type.name, options), message="which buy?")
        print "Buy", options[result].type.name
        return result
        
    def ask_whichgain(self, options):
        maxcost = 0
        for o in options:
            if o.type.price > maxcost:
                maxcost = o.type.price
        maxcost = 0
        if maxcost not in self.stats.bought:
            self.stats.bought[maxcost] = TotalWinDict()
        result = self.stats.bought[maxcost].select(["None"] + map(lambda x: x.type.name, options))
        for i, a in enumerate(options):
            if a.type.name == result:
                print "gain", result
                return i
        print "gain nothing"
        return -1
        result = self.ask_which(map(lambda x: x.type.name, options), message="which gain?")
        print "gain", options[result].type.name
        return result
        
    def ask_whichdiscard(self, cards, optional):
        prefix = ["None"] if optional else []
        result = self.stats.discarded.select(prefix + map(lambda x: x.name, cards))
        for i, a in enumerate(cards):
            if a.name == result:
                print "discard", result
                return i
        print "discard nothing"
        return -1
        options = cards
        if optional:
            options = ["Do nothing"] + cards
        return self.ask_which(options)
        
    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        prefix = ["None"] if optional else []
        result = self.stats.trashed.select(prefix + map(lambda x: x.name, cards))
        for i, a in enumerate(cards):
            if a.name == result:
                print "trash", result, i, "of", len(cards)
                return i
        print "trash nothing"
        return -1
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
        
    def tell_winner(self, winner, points, totalpoints):
        print winner, "has won the game!"
        self.stats.finalize(winner==self.name, points, totalpoints)
        f = open(self.name, "w")
        cPickle.dump(self.stats, f)
        f.close()
    
    def get_name(self):
        return self.name
        
