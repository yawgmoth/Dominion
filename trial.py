from dominion import make_player, Game
import optparse
import sys
from cStringIO import StringIO

def main():
    parser = optparse.OptionParser()
    playertypes = ["basic", "ai.random", "gtk", "ai.counting", "ai.expensive", "ai.buylist"]
    parser.add_option("-1", "--player-1", "--p1", action="store", type="choice", choices=playertypes, default="ai.random", dest="player1")
    parser.add_option("-2", "--player-2", "--p2", action="store", type="choice", choices=playertypes, default="ai.random", dest="player2")
    parser.add_option("-3", "--player-3", "--p3", action="store", type="choice", choices=playertypes, default=None, dest="player3")
    parser.add_option("-4", "--player-4", "--p4", action="store", type="choice", choices=playertypes, default=None, dest="player4")
    parser.add_option("-n", "--count", action="store", type="int", default=10000, dest="count")
    (options,args) = parser.parse_args()
    winners = {}
    
    for i in xrange(options.count):
        sys.stdout = StringIO()
        players = [make_player(options.player1, 1), make_player(options.player2, 2)]
        g = Game(players)
        for p in [options.player1, options.player2]:
            if p == "gtk":
                print >>sys.stderr, "ERROR: Can't run trials with gtk player!"
                return -1
        winner = g.run()
        if winner.name not in winners:
            winners[winner.name] = 0
        winners[winner.name] += 1
        sys.stdout = sys.__stdout__
    for w in winners:
        print w, "won", winners[w]
            
if __name__ == "__main__":
    main()