# our crazy pigeon

import sys
import time
import random

from bzrc import BZRC, Command

class Agent(object):
	
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.num_ticks = 0
        self.MAXTICKS = 100
        

    def tick(self, time_diff):
        """Some time has passed;"""
        
        
        self.commands = []
        
        if self.num_ticks % self.MAXTICKS == 0:
            
                
            magnitude = random.random() * 0.5 + 0.5
            relative_angle = 0.5
            command = Command(0, magnitude, 2 * relative_angle, False)
            self.commands.append(command)
            results = self.bzrc.do_commands(self.commands)
        
        self.num_ticks = self.num_ticks + 1

def main():

	# Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc)

    prev_time = time.time()

    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()

if __name__ == '__main__':
    main()







