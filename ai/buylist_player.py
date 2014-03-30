import random
import player_interface
import dominion
import os

def load_buylist(fname):
    f = open(fname)
    buylist = []
    for l in f:
        if l:
            item, count = l.rsplit(" ",1)
            buylist.append([item,int(count)])
    f.close()
    return buylist
	
def create_buylist(self):
    kingdom = get_kingdoms(self)
	#remove copper, silver, gold, and province- already accounted for in template strategy
    del kingdom[0]
    del kingdom[0]
    del kingdom[0]
    del kingdom[3]
    self.kingdom = kingdom
    random.shuffle(kingdom);
    self.adaptiveBuyFile = "adaptiveBuylist.buys"
	#just random for now
    target = open (self.adaptiveBuyFile, 'w')
    target.write("%s %d\n" % (kingdom[0], 3))
    target.write("Province 99\n")
    target.write("Gold 99\n")
    target.write("%s %d\n" % (kingdom[1], 3))
    target.write("%s %d\n" % (kingdom[2], 3))
    target.write("%s %d\n" % (kingdom[3], 3))	
    target.write("%s %d\n" % (kingdom[4], 3))
    target.write("%s %d\n" % (kingdom[5], 3))	
    target.write("Silver 99\n")	
    target.write("%s %d\n" % (kingdom[6], 3))
    target.write("%s %d\n" % (kingdom[7], 3))
    target.write("%s %d\n" % (kingdom[8], 3))
    target.write("%s %d" % (kingdom[9], 3))	
    target.close()
    return load_buylist(self.adaptiveBuyFile)   
	
def get_kingdoms(self):
    kingdom = []
    for s in self.game.stacks:
        kingdom.append(s.type.name)
    return kingdom

def run_trials(self, trials):
        state = self.game.get_state()
        winners = {}
        for i in xrange(trials):
            players = [BuylistPlayer("Player %d"%j, buylist=self.buylist, run_trials=False, show_text=False, adaptive = False) for j,p in enumerate(self.game.players)]
            g = dominion.Game.from_state(state, players, shuffle=True)
            s0 = g.get_state()

            winner = g.run()
            for p in g.players:
                if p.name not in winners:
                    winners[p.name] = 0
            winners[winner.name] += 1
            if i == 0 and self.logs:
                f = open("games/game_%d.log"%self.n, "w")
                self.n += 1
                print >>f, "Starting from", state
                print >>f, "should be the same:", s0
                print >>f, "ending in", g.get_state()
                print >>f, "winner", winner.name
                print >>f, "Game ended because:", g.end_reason
                print >>f, "buylist was", self.buylist
                f.close()
        winsum = sum(winners.values())
        finalstat =0
        for w in winners:
            if w not in self.stats:
                self.stats[w] = []
            self.stats[w].append(winners[w]*100.0/winsum)
            finalstat = winners[w]*100.0/winsum
        #return final winrate
        return finalstat
		
def test_initial_buylist(self):
    result = 0
    result= run_trials(self, 10)
    if(result > 50.0):
        print "Buylist wins over 50% to start"
    else:
        i=1
        while result < 50.0:
            create_buylist(self)
            result = run_trials(self,10)
            i+=1
        print "Took %d iterations to get a win with result %d" % (i, result)
        

class BuylistPlayer(player_interface.PlayerInterface):
    def __init__(self, name, buylist_file="default.buys", buylist = None, run_trials=True, show_text=False, graph=False, logs=False, adaptive=True):
        self.name = name
		#adaptive overrides using a set buylist, creates one turn by turn
        self.adaptive = adaptive
        if self.adaptive == "False":
            self.adaptive = False
        if not adaptive:
            if buylist:
                self.buylist = map(lambda l: l[:], buylist)
            else:
                self.buylist = load_buylist(buylist_file)
        self.run_trials = run_trials
        if self.run_trials == "False":
            self.run_trials = False
        self.show_text = show_text
        self.stats = {}
        self.graph = graph
        self.n = 0
        self.logs = logs
        self.kingdom = None
        self.adaptiveBuyFile = None
        if self.logs:
            if not os.path.exists("games"):
                os.makedirs("games")

    def set_game(self, game):
        self.game = game
		#knowledge of stacks after game is set
        if self.adaptive:
            self.buylist = create_buylist(self)
            print "Running buylist test"
            test_initial_buylist(self)
        
    def tell_stacks(self, stacks):
        if self.show_text:
            print "Available stacks this game:"
            for s in stacks:
                print s.type.name, " (" + str(s.count) + " available)"
            
    def tell_start_turn(self):
        if self.run_trials:
            run_trials(self, 10)
        if self.show_text:
            print self.name + ", it's your turn!"

    def tell_hand(self, hand):
        if self.show_text:
            print "Your hand contains:"
            for h in hand:
                print " ", h.name
            
    def tell_deck(self, hand):
        if self.show_text:
            print "Your deck contains:"
            for h in hand:
                print " ", h.name

    def tell_stats(self, player):
        if self.show_text:
            print "You have:"
            print " ", player.actions, "Actions"
            print " ", player.buys, "Buys"
            print " ", player.money, "Money"
        
    def tell_buyphase(self):
        if self.show_text:
            print "Buyphase!"
        
    def tell_reveal(self, player, card):
        if card and self.show_text:
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
        if message and self.show_text:
            print message
            for i, c in enumerate(choices):
                print " ", i+1, c
        return random.randint(0,len(choices)-1)
    
    def ask_whichaction(self, actions):
        result = self.ask_which(map(lambda x: x.name, actions), message="Which action?")
        if not actions: return -1
        if self.show_text:
            print "play", actions[result].name
        return result
        
    def ask_whichbuy(self, options):
        opts = map(lambda x: x.type.name, options)
        for l in self.buylist:
            if l[1] > 0 and l[0] in opts:
                l[1] -= 1
                return opts.index(l[0])
        return -1

    def ask_whichgain(self, options):
        opts = map(lambda x: x.type.name, options)
        for l in self.buylist:
            if l[1] > 0 and l[0] in opts:
                l[1] -= 1
                return opts.index(l[0])
        
        result = self.ask_which(map(lambda x: x.type.name, options), message="which gain?")
        if self.show_text:
            print "gain", options[result].type.name
        return result

    def ask_whichdiscard(self, cards, optional):
        options = cards
        if optional:
            options = ["Do nothing"] + options
        return self.ask_which(options)
        
    def ask_whichreaction(self, cards):
        return self.ask_which(cards)
        
    def ask_whichtrash(self, cards, optional, *args):
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
        if self.show_text:
            print winner, "has won the game!"
        if not self.run_trials: return
        if self.graph:
            from mpl_toolkits.axes_grid.axislines import SubplotZero
            import matplotlib.pyplot as plt
            fig = plt.figure(1)
            ax = SubplotZero(fig, 111)
            fig.suptitle("Winrate of %s over time"%(self.stats.keys()[0]))
            fig.add_subplot(ax)
            ax.plot(self.stats.values()[0])
            plt.show()
        print self.stats.values()[0]
    
    def get_name(self):
        return self.name