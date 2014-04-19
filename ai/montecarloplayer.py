import random
import player_interface
import json
import dominion
from cStringIO import StringIO
import sys

class DummyCard:
    def __init__(self, name):
        self.name = name
        
# how to value unknown branches of the tree (high = higher probability of choosing them)
EXPLORATION_RATE = 1000

# king croesus, the wealthy: maximize money output
def croesus(player):
    return player.money
    
# king midas: turn everything into "gold": maximize average cost of card in deck
def midas(player):
    g = player.game
    pl = None
    for p in g.players:
        if p.player_interface.get_name() == player.get_name():
            pl = p

    value = sum(map(lambda c: c.price, pl.hand + pl.in_play + pl.deck + pl.discard_pile)) + player.money
    return value/(1.0 + len(pl.hand + pl.in_play + pl.deck + pl.discard_pile))
    
# god of intellect: maximize cards drawn+played
def coeus(player):
    g = player.game
    pl = None
    for p in g.players:
        if p.player_interface.get_name() == player.get_name():
            pl = p
    return len(pl.hand + pl.in_play)
    
# god of war, bloodshed and violence: maximize attacks played
def ares(player):
    import cards.base
    g = player.game
    pl = None
    for p in g.players:
        if p.player_interface.get_name() == player.get_name():
            pl = p
    c = 0
    for c in pl.in_play:
        if c.type & cards.base.ATTACK:
            c += 1
    return c
    
personality_map = {"midas": midas, "croesus": croesus, "coeus": coeus, "ares": ares}

class MonteCarloTrialPlayer(player_interface.PlayerInterface):
    def __init__(self, name, stats, personality=croesus):
        self.name = name
        self.stats = stats
        self.current_play = ()
        self.buyphase = False
        self.personality = personality
        
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
        return self.personality(self)
        
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
    

    
    def monte_carlo_decision(self, actions, optional=False):
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
                additional_options.append((self.current_play + (o,),(EXPLORATION_RATE,1)))
        matches.extend(additional_options)
        
        match_groups = {}
        for m,(mv,mc) in matches:
            seq = tuple(m[:len(self.current_play)+1])
            if seq not in match_groups:
                match_groups[seq] = (0,0)
            v,count = match_groups[seq]
            match_groups[seq] = ((v*count + mv*mc)/(count+mc),count+mc)
        if noplayvalue[0] == 0:
            noplayvalue = (EXPLORATION_RATE,1)
        if optional:
            matches = [([""], noplayvalue[0])]
        else:
            matches = []
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
        if not matches[i][0][-1] and optional:
            self.current_play = self.current_play + ("",)
            return -1
        m = matches[i][0][-1]
        self.current_play = self.current_play + (m,)
        return map(lambda a: a.name, actions).index(m)
    
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
                additional_options.append((self.current_play + (o,),(EXPLORATION_RATE,1)))
        matches.extend(additional_options)
        
        match_groups = {}
        for m,(mv,mc) in matches:
            seq = tuple(m[:len(self.current_play)+1])
            if seq not in match_groups:
                match_groups[seq] = (0,0)
            v,count = match_groups[seq]
            match_groups[seq] = ((v*count + mv*mc)/(count+mc),count+mc)
        if noplayvalue[0] == 0:
            noplayvalue = (EXPLORATION_RATE,1)
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
            return -1
        m = matches[i][0][-1]
        self.current_play = self.current_play + (m,)
        return map(lambda a: a.name, actions).index(m)
        
        
    def ask_whichbuy(self, options):
        return -1
        
    def ask_whichgain(self, options):
        result = self.ask_which(map(lambda x: x.type.name, options), message="which gain?")
        return result
        
    def ask_whichdiscard(self, cards, optional):
        return self.monte_carlo_decision(cards, optional)

    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        return self.monte_carlo_decision(cards, optional)
        
    def ask_putdiscard(self):
        return self.monte_carlo_decision([DummyCard("yes"), DummyCard("no")]) == 0
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(options)
        
    def ask_keep(self, player, card):        
        return self.monte_carlo_decision([DummyCard("yes"), DummyCard("no")]) == 0
        
    def ask_wantgain(self, card):
        return self.monte_carlo_decision([DummyCard("yes"), DummyCard("no")]) == 0

    def tell_attack(self, attacker, card):
        pass
        
    def tell_winner(self, winner, *args):
        pass
    
    def get_name(self):
        return self.name
        
    def set_game(self, game):
        self.game = game
        

class MonteCarloPlayer(player_interface.PlayerInterface):
    def __init__(self, name, trials=300, write_stats=False, personality="croesus"):
        self.name = name
        self.hand = []
        self.last_played = ""
        self.trials = trials
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
        self.personality = personality
        self.plan = []
        
    def set_game(self, game):
        self.game = game
        
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
        return self.monte_carlo_decision(actions)
    
    def monte_carlo_decision(self, actions, use_plan=False, optional=True):
        if use_plan and self.plan:
            if self.write_stats:
                f = file("stats.log", "a+")
                print >>f, "use plan", self.plan
                print >>f, "choose from:", map(lambda a: a.name, actions)
                f.close()
            if self.plan and not self.plan[0]:
                self.plan = self.plan[1:]
                return -1
            for i,a in enumerate(actions):
                if a.name == self.plan[0]:
                    self.plan = self.plan[1:]
                    return i
            return random.randint(-1,len(actions)-1)
        elif use_plan:
            if optional:
                return -1
            return random.randint(0, len(actions))

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
                        players.append(MonteCarloTrialPlayer("Player %d"%j, stats=stats, personality=personality_map[self.personality]))
                    else:
                        players.append(MonteCarloTrialPlayer("Player %d"%j, stats={}, personality=personality_map[self.personality]))
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

        bestplan = -100
        bestplanat = (bestat,)

        for s in stats:
            if stats[s][0] > bestplan and s and s[0] == bestat:
                bestplan = best
                bestplanat = s

        self.plan = []
        if bestplanat and bestat:
            self.plan = bestplanat[1:]

        if self.write_stats:
           f = file("stats.log", "a+")
           print >>f, "needed", dt
           print >>f, "Hand:", map(lambda a: a.name, self.hand)
           print >>f, "money:", self.money, "buys:", self.buys, "actions:", self.actions
           print >>f, "stats:", stats
           print >>f, "stat groups:", stat_groups
           print >>f, "stat group values:", stat_group_values
           print >>f, "\naction:", bestat
           print >>f, "plan:", self.plan, bestplanat
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
        return self.monte_carlo_decision(cards, use_plan=True, optional=optional)
        
    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
        return self.monte_carlo_decision(cards, use_plan=True, optional=optional)
        
    def ask_putdiscard(self):
        return self.monte_carlo_decision([DummyCard("yes"), DummyCard("no")], use_plan=True) == 0
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(options)
        
    def ask_keep(self, player, card):
        return self.monte_carlo_decision([DummyCard("yes"), DummyCard("no")], use_plan=True) == 0
        
    def ask_wantgain(self, card):
        return self.monte_carlo_decision([DummyCard("yes"), DummyCard("no")], use_plan=True) == 0

    def tell_attack(self, attacker, card):
        pass
        
    def tell_winner(self, winner, *args):
        print "Times:", self.times
    
    def get_name(self):
        return self.name