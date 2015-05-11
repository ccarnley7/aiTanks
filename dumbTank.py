'''
Created on Sep 19, 2014

@author: Jon "Neo" Pimentel
'''
import sys
import math
import time
import random

from bzrc import BZRC, Command

class Agent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.prevTime= 0.0
        self.timer = 5.0
        self.moveTimer = random.randrange(3,9)
        self.turnTimer = 1.5
        self.gunTimer = float(random.randrange(15, 26))/10
        
    def tick(self, gameClock):   
        """Some time has passed; decide what to do next."""
        self.tickTime = gameClock - self.prevTime
        
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []
        self.timer -= gameClock
        
        self.gunTimer -= self.tickTime
        self.moveTimer -= self.tickTime
        if self.gunTimer <= 0:
            shouldShoot = True
            self.gunTimer = float(random.randrange(15, 25))/10
        else:
            shouldShoot = False
        
        if self.moveTimer <= 0:
            #turn
            self.turnTimer -= self.tickTime
            speed = 0
            angVel = 1
            if self.turnTimer <= 0:
                self.moveTimer = random.randrange(3,9)
                self.turnTimer = 1.5
        else:
            #keep moving forward
            speed = 1
            angVel = 0
        
        for i in range(2):
            command = Command(i, speed, angVel, shouldShoot)
            self.commands.append(command)
            
        results = self.bzrc.do_commands(self.commands)
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