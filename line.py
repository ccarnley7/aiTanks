import sys
import time

from bzrc import BZRC, Command

class Agent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.prevTime= 0.0
        self.timer = 5.0
        
    def tick(self, gameClock):   
        """Some time has passed; decide what to do next."""
        self.commands = []
        command = Command(0, 1, 0, False)
        self.commands.append(command)
            
        self.bzrc.do_commands(self.commands)
        self.prevTime = gameClock
    
def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()