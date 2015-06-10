#!/usr/bin/python -tt

from bzrc import BZRC, Command
from random import randint
import sys, math, time

# An incredibly simple agent.  All we do is find the closest enemy tank, drive
# towards it, and shoot.  Note that if friendly fire is allowed, you will very
# often kill your own tanks with this code.

#################################################################
# NOTE TO STUDENTS
# This is a starting point for you.  You will need to greatly
# modify this code if you want to do anything useful.  But this
# should help you to know how to interact with BZRC in order to
# get the information you need.
# 
# After starting the bzrflag server, this is one way to start
# this code:
# python agent0.py [hostname] [port]
# 
# Often this translates to something like the following (with the
# port name being printed out by the bzrflag server):
# python agent0.py localhost 49857
#################################################################

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.tankSeconds = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]

    def tick(self, time_diff):
        '''Some time has passed; decide what to do next'''
        # Get information from the BZRC server
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color !=
                self.constants['team']]

        # Reset my set of commands (we don't want to run old commands)
        self.commands = []
        print time_diff

        # Decide what to do with each of my tanks
        i = 0;
        #for bot in mytanks:
            #if tankSeconds are negative then it is turning
            #if tankSeconds are positive then it is moving

        for bot in mytanks:
            initialSec = self.tankSeconds[i]
            pos = (bot.x, bot.y)
            if self.tankSeconds[i]<0:
                # print 'INCREMENT'+str(initialSec)
                self.tankSeconds.pop(i)
                self.tankSeconds.insert(i,initialSec+1)
                # print 'INCREMENT RESULT'+str(self.tankSeconds[i])
            elif self.tankSeconds[i]>0:
                # print 'DECREMENT '+str(initialSec)
                self.tankSeconds.pop(i)
                self.tankSeconds.insert(i,initialSec-1)
                # print 'DECREMENT RESULT '+str(self.tankSeconds[i])
            print "top of tank seconds is:{}\n".format(self.tankSeconds[i])
            if initialSec == -1:
                # print 'GO'
                go = Command(bot.index,1,0,False)
                self.commands.append(go)
                self.tankSeconds.pop(i)
                self.tankSeconds.insert(i,randint(3,8))

            i += 1
           
            if math.ceil(time_diff)%2 == 0:
                # print 'SHOOT!'
                self.bzrc.shoot(bot.index)
                #shoot and turn
        # Send the commands to the server
        results = self.bzrc.do_commands(self.commands)

    def speed(self,vx,vy):
        #I'll need to figure out how these commands work
        #MOVE 
        return math.sqrt(math.pow(vx,2)+math.pow(vy,2))

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
    last_time = 0
    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            if last_time != math.floor(time_diff):
                agent.tick(time_diff)
            last_time = math.floor(time_diff)

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
