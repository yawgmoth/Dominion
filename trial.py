from dominion import make_player, Game, filecontent
import optparse
import sys
from cStringIO import StringIO
import time

def main():
    parser = optparse.OptionParser()
    playertypes = ["basic", "ai.random", "gtk", "ai.counting", "ai.expensive", "ai.buylist", "ai.heuristic", "ai.combining"]
    parser.add_option("-1", "--player-1", "--p1", action="store", type="choice", choices=playertypes, default="ai.random", dest="player1")
    parser.add_option("-2", "--player-2", "--p2", action="store", type="choice", choices=playertypes, default="ai.random", dest="player2")
    parser.add_option("-3", "--player-3", "--p3", action="store", type="choice", choices=playertypes, default=None, dest="player3")
    parser.add_option("-4", "--player-4", "--p4", action="store", type="choice", choices=playertypes, default=None, dest="player4")
    parser.add_option("-a", "--player-1-options", dest="player1_options", default="")
    parser.add_option("-b", "--player-2-options", dest="player2_options", default="")
    parser.add_option("-c", "--player-3-options", dest="player3_options", default="")
    parser.add_option("-d", "--player-4-options", dest="player4_options", default="")
    parser.add_option("-o", "--game-options", dest="game_options", default="")
    parser.add_option("-n", "--count", dest="count", default=1000)
    (options,args) = parser.parse_args()
    opts = {}
    if options.game_options:
        opts = dict(map(lambda o: o.split("="), options.game_options.split(",")))
    winners = {}
    t0 = time.time()
    for i in xrange(int(options.count)):
        sys.stdout = StringIO()
        players = [make_player(options.player1, 1, options.player1_options), make_player(options.player2, 2, options.player2_options)]
        if options.player3:
            players.append(make_player(options.player3, 3, options.player3_options))
        if options.player4:
            players.append(make_player(options.player4, 4, options.player4_options))

        
    
        if "load" in opts:
            g = Game.from_state(filecontent(opts["load"]), map(lambda p: p.player_interface, players))
        else:
            g = Game(players, **opts)

        if "gtk" in [options.player1, options.player2, options.player3, options.player4]:
            print >>sys.stderr, "ERROR: Can't run trials with gtk player!"
            return -1
        winner = g.run()
        if winner.name not in winners:
            winners[winner.name] = 0
        winners[winner.name] += 1
        sys.stdout = sys.__stdout__

    print options.count, "runs done in", time.time()-t0, "seconds"    
    winsum = sum(winners.values())
    for w in winners:
        print w, "won", winners[w], "( = %.3f%%)"%(winners[w]*100.0/winsum)
            
if __name__ == "__main__":
    main()