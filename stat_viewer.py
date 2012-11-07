import ai.counting_player
import os
import cPickle

def main():
    for nr in xrange(5):
        fname = "Player %d"%nr
        if os.path.exists(fname):
            print "found stats for player:", fname
            f = open(fname)
            stats = cPickle.load(f)
            f.close()
            print stats
        
if __name__ == '__main__':
    main()