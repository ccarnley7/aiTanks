#!/usr/bin/python -tt

from bzrc import BZRC, Command
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
        bases = self.bzrc.get_bases()
        self.bases = bases
        self.homeBase = [0, 0]
        self.goalPos = [0, 0] 
        self.goalRadius = 5
        self.distance = 0  # dist between goal and agent
        self.angle = 0  # angle between goal and agent
        self.dx = 0
        self.dy = 0
        self.curSpeed = 0
        self.curAngVel = 0
        self.curAngle = 0
        for base in bases:
        	if base.color == self.constants['team']:
        		self.mybase = base

    def tick(self, time_diff):
        '''Some time has passed; decide what to do next'''
        # Get information from the BZRC server
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.obstacles = self.bzrc.get_obstacles()
        self.enemies = [tank for tank in othertanks if tank.color !=
                self.constants['team']]

        # Reset my set of commands (we don't want to run old commands)
        self.commands = []

        # print self.constants
        # self.get_flag(mytanks[0], flags[3])
        self.currentTank = mytanks[0]
        self.flag = flags[0]
        self.attractiveField()
        print "we ran attractiveField"
        self.repulsiveFields()
        print "we ran repulsiveFields"
        self.tangentialFields()
        print "we ran tangentialFields"
        self.applyDelta()
        print "we ran applyDelta"
        command = Command(0, self.curSpeed, self.curAngVel, False)
        self.commands.append(command)
        # Decide what to do with each of my tanks
        # for bot in mytanks:
            # self.attack_enemies(bot)

        # Send the commands to the server

        results = self.bzrc.do_commands(self.commands)

    def get_flag(self, bot, flag):
    	'''Go get the flag without running into anything'''
    	if bot.flag == "-":
    		print "here"
    		self.move_to_position(bot, flag.x, flag.y)
    	else:
    		self.return_to_base(bot)
		# if flag.color == self.mytanks[0].color:
		# 	continue
		# if flag.poss_color == self.mytanks[0].color:
		# 	continue

    def getDistance(self, point1, point2):
        return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point1[1] - point2[1], 2))   

    def distanceToLine(self, start, end, point):
        length_sqd = (math.pow(end[0] - start[0], 2) + math.pow(start[1] - end[1], 2))
        
        t = ((point[0] - start[0]) * (end[0] - start[0]) + (point[1] - start[1]) * (end[1] - start[1])) / length_sqd
        # if t < 0: return self.getDistance(point, start)
        # if t > 1: return self.getDistance(point, end)
        if t < 0 or t > 1: return 9001
        
        return self.getDistance(point, [start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])])     

    def attractiveField(self, x=-1, y=-1):
        if x != -1 and y != -1:
            self.currentTank.x = x
            self.currentTank.y = y
            self.goalPos = self.flag
        self.distance = math.sqrt((self.goalPos[0] - self.currentTank.x) ** 2 + (self.currentTank.y - self.goalPos[1]) ** 2)
        self.angle = math.atan2(self.goalPos[1] - self.currentTank.y, self.goalPos[0] - self.currentTank.x)
        # normalize angle?
        spread = 10  # not sure what this should be
        alpha = 10  # not sure what this should be
        
        if self.distance < self.goalRadius:
            self.dx = 0
            self.dy = 0
        elif self.goalRadius <= self.distance and self.distance <= spread + self.goalRadius:
            self.dx = alpha * (self.distance - self.goalRadius) * math.cos(self.angle)
            self.dy = alpha * (self.distance - self.goalRadius) * math.sin(self.angle)
        else:  # distance > spread+radius
            self.dx = alpha * spread * math.cos(self.angle)
            self.dy = alpha * spread * math.sin(self.angle)
        
        # print 'dx: ', self.dx
        # print 'dy: ', self.dy    

    def repulsiveFields(self, x=-1, y=-1):
        if x != -1 and y != -1:
            self.currentTank.x = x
            self.currentTank.y = y
        radius = 5;
        spread = 10;
        beta = 20;
        
        if self.currentTank.flag != '-':  # they should get out of HIS way
            return
        
        for tank in self.mytanks:
            if tank is self.currentTank:
                continue
            
            distance = math.sqrt(math.pow(tank.x - self.currentTank.x, 2) + math.pow(self.currentTank.y - tank.y, 2))
            angle = self.normalize_angle(math.atan2(tank.y - self.currentTank.y, tank.x - self.currentTank.x))
            # normalize angle?
            
            if distance < radius:
                doX = math.copysign(1, math.cos(angle)) * -9001
                doY = math.copysign(1, math.sin(angle)) * -9001
            elif radius <= distance and distance <= (spread + radius):
                doX = -beta * (spread + radius - distance) * math.cos(angle)
                doY = -beta * (spread + radius - distance) * math.sin(angle)    
            else:  # distance > spread + radius
                doX = 0;
                doY = 0;
                
            self.dx = self.dx + doX
            self.dy = self.dy + doY 
            
    def tangentialFields(self, x=-1, y=-1):
        if x != -1 and y != -1:
            self.currentTank.x = x
            self.currentTank.y = y
        radius = 1;
        spread = 10;
        beta2 = 100;
        for obstacle in self.obstacles:
            # i= 0
            for i in range(0, 4):
                # print 'obstacle[',i,']: ', obstacle[i]
                start = obstacle[i]
                if i == 3: end = obstacle[0]
                else: end = obstacle[i + 1]
                
                point = [self.currentTank.x, self.currentTank.y]
            
                distance = self.distanceToLine(start, end, point)
                # angle = self.normalize_angle(math.atan2(end[1] - start[1], end[0] - start[0]))  # - math.pi/2 ?
                angle = (math.atan2(end[0] - start[0], -(end[1] - start[1])) ) - math.pi / 2
                # normalize?
            
                if distance < radius:
                    print "It's over 9000! Tangential angle: ", angle
                    
                    doX = math.cos(angle) * 9001
                    doY = math.sin(angle) * 9001
                
                elif radius <= distance and distance <= (spread + radius):
                    print "It's within the spread! Tangential angle: ", angle
                    doX = beta2 * (spread + radius - distance) * math.cos(angle)
                    doY = beta2 * (spread + radius - distance) * math.sin(angle)    
                else:  # distance > spread + radius
                    doX = 0;
                    doY = 0;
                
                self.dx = self.dx + doX
                self.dy = self.dy + doY   

                 
		
    def return_to_base(self, bot):
    	'''Return to base!!'''
    	self.move_to_position(bot, self.mybase.corner1_x, self.mybase.corner1_y)

    def attack_enemies(self, bot):
        '''Find the closest enemy and chase it, shooting as you go'''
        best_enemy = None
        best_dist = 2 * float(self.constants['worldsize'])
        for enemy in self.enemies:
            if enemy.status != 'alive':
                continue
            dist = math.sqrt((enemy.x - bot.x)**2 + (enemy.y - bot.y)**2)
            if dist < best_dist:
                best_dist = dist
                best_enemy = enemy
        if best_enemy is None:
            command = Command(bot.index, 0, 0, False)
            self.commands.append(command)
        else:
            self.move_to_position(bot, best_enemy.x, best_enemy.y)

    def move_to_position(self, bot, target_x, target_y):
        target_angle = math.atan2(target_y - bot.y,
                target_x - bot.x)
        relative_angle = self.normalize_angle(target_angle - bot.angle)
        command = Command(bot.index, 1, 2 * relative_angle, True)
        self.commands.append(command)

    def normalize_angle(self, angle):
        '''Make any angle be between +/- pi.'''
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle


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

# vim: et sw=4 sts=4
