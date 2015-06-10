import sys
import math
import time
import random
import KalmanPlotting
import numpy as np
import matplotlib.pyplot as plt


from bzrc import BZRC, Command
plt.axis([-250, 250, -250, 250])
plt.ion()
plt.show()
class KalmanAgent(object):
    
    def __init__(self, bzrc):
        self.debug = True
        self.skeetMode = True
        self.setup = True
        self.firstTick = True
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        print 'team: ', self.constants['team']
        self.prevTime = 0.0
        self.timer = 5.0
        self.turnTimer = 1.5
        self.plotTimer = 0.0
        self.plotId = 0
        self.gunTimer = float(random.randrange(15, 26)) / 10
        self.estimatesX = []
        self.estimatesY = []
        self.obsX = []
        self.obsY = []
        self.flagZone = 150
        self.homeBase = [0, 0]
        self.goalPos = [0, 0] 
        self.goalRadius = 5
        self.distance = 0  # dist between goal and agent
        self.angle = 0  # angle between goal and agent
        self.dx = 0
        self.dy = 0
        self.oldDist = 0
        self.counter = 0
        self.initMatrices()
        
    def dot(self, v1, v2):
        total = 0.0;
        
        for i in range(0, v1.size()):
            total += v1[i] * v2[i]
            
        return total  
    
    def getDistance(self, point1, point2):
        return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point1[1] - point2[1], 2))
    
    def distanceToLine(self, start, end, point):
        length_sqd = (math.pow(end[0] - start[0], 2) + math.pow(start[1] - end[1], 2))
        
        t = ((point[0] - start[0]) * (end[0] - start[0]) + (point[1] - start[1]) * (end[1] - start[1])) / length_sqd
        if t < 0 or t > 1: return 9001
        
        return self.getDistance(point, [start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])])
    
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
    def attractiveField(self, x=-1, y=-1):
        if x != -1 and y != -1:
            self.currentTank.x = x
            self.currentTank.y = y
            self.goalPos = self.chooseTargetFlag()
        self.distance = math.sqrt((self.goalPos[0] - self.currentTank.x) ** 2 + (self.currentTank.y - self.goalPos[1]) ** 2)
        self.angle = math.atan2(self.goalPos[1] - self.currentTank.y, self.goalPos[0] - self.currentTank.x)
        spread = 10 
        alpha = 10  
        
        if self.distance < self.goalRadius:
            self.dx = 0
            self.dy = 0
        elif self.goalRadius <= self.distance and self.distance <= spread + self.goalRadius:
            self.dx = alpha * (self.distance - self.goalRadius) * math.cos(self.angle)
            self.dy = alpha * (self.distance - self.goalRadius) * math.sin(self.angle)
        else: 
            self.dx = alpha * spread * math.cos(self.angle)
            self.dy = alpha * spread * math.sin(self.angle)
        
    def repulsiveFields(self, x=-1, y=-1):
        if x != -1 and y != -1:
            self.currentTank.x = x
            self.currentTank.y = y
        radius = 5;
        spread = 10;
        beta = 20;
        
        if self.currentTank.flag != '-': 
            return
        
        for tank in self.mytanks:
            if tank is self.currentTank:
                continue
            
            distance = math.sqrt(math.pow(tank.x - self.currentTank.x, 2) + math.pow(self.currentTank.y - tank.y, 2))
            angle = self.normalize_angle(math.atan2(tank.y - self.currentTank.y, tank.x - self.currentTank.x))
            
            if distance < radius:
                doX = math.copysign(1, math.cos(angle)) * -9001
                doY = math.copysign(1, math.sin(angle)) * -9001
            elif radius <= distance and distance <= (spread + radius):
                doX = -beta * (spread + radius - distance) * math.cos(angle)
                doY = -beta * (spread + radius - distance) * math.sin(angle)    
            else:
                doX = 0;
                doY = 0;
                
            self.dx = self.dx + doX
            self.dy = self.dy + doY 
            
    def tangentialFields(self, x=-1, y=-1):
        if x != -1 and y != -1:
            self.currentTank.x = x
            self.currentTank.y = y
        radius = 1;
        spread = 10
        beta2 = 100
        for obstacle in self.obstacles:
            for i in range(0, 4):
                start = obstacle[i]
                if i == 3: end = obstacle[0]
                else: end = obstacle[i + 1]
                
                point = [self.currentTank.x, self.currentTank.y]
            
                distance = self.distanceToLine(start, end, point)
                angle = (math.atan2(end[0] - start[0], -(end[1] - start[1]))) - math.pi / 2
            
                if distance < radius:
                    print "It's over 9000! Tangential angle: ", angle
                    
                    doX = math.cos(angle) * 9001
                    doY = math.sin(angle) * 9001
                
                elif radius <= distance and distance <= (spread + radius):
                    print "It's within the spread! Tangential angle: ", angle
                    doX = beta2 * (spread + radius - distance) * math.cos(angle)
                    doY = beta2 * (spread + radius - distance) * math.sin(angle)    
                else: 
                    doX = 0;
                    doY = 0;
                
                self.dx = self.dx + doX
                self.dy = self.dy + doY               
        
    def applyDelta(self):
        threshold = .5
        if self.skeetMode and not self.setup: self.curSpeed = 0
        else: self.curSpeed = math.sqrt(math.pow(self.dx, 2) + math.pow(self.dy, 2)) / 100
        angle = math.atan2(self.dy, self.dx)  
        curAngle = self.currentTank.angle  
        
        angleDif = self.normalize_angle(angle - curAngle)
        if angleDif < threshold and angleDif > -threshold: 
            self.curAngVel = angleDif * 2
        else:
            self.curAngVel = math.copysign(1, angleDif)
        
    def chooseTargetFlag(self):
        bestDistance = 9999
        target = self.homeBase
        
        for flag in self.flags:
            displacement = math.sqrt(math.pow(flag.x - self.homeBase[0], 2) + math.pow(self.homeBase[1] - flag.y, 2))
            
            if flag.color == self.constants['team'] and (displacement <= 30):
                continue
            
            distance = math.sqrt(math.pow(flag.x - self.currentTank.x, 2) + math.pow(self.currentTank.y - flag.y, 2))
            
            if distance < bestDistance:
                bestDistance = distance
                target = [flag.x, flag.y]
                
        return target

    def chooseTargetEnemy(self):  
        bestDistance = 9999
        target = None
        flag = self.flags[self.teamIndex]
        
        for enemy in self.enemies:
            if enemy.status == "dead":
                continue
            distance = self.getDistance([enemy.x, enemy.y], [flag.x, flag.y])
            
            if ((distance < self.flagZone) and distance < bestDistance)  or self.skeetMode:
                target = enemy
                if not self.skeetMode: print 'Intruder!'
        if target is not None:        
            return [target.x, target.y]
        return None        
        
    def chooseTarget(self):
        curTank = self.currentTank
        flagX = self.flags[self.teamIndex].x
        flagY = self.flags[self.teamIndex].y
        
        if self.setup:
            distOrig = self.getDistance([curTank.x, curTank.y], [0, 0])
            if distOrig < 10:
                self.setup = False
            else: return [0, 0]    
        
        distFlag = self.getDistance([curTank.x, curTank.y], [flagX, flagY])
        
        if distFlag < self.flagZone or self.skeetMode:
            targetEnemy = self.chooseTargetEnemy()
            if targetEnemy is not None:
                return targetEnemy
        
        return self.chooseTargetFlag() 
    
    def initMatrices(self):
        dt = .01 
        c = 0
        dt2 = math.pow(dt, 2) / 2
        sd = 25 
        pos = .1
        vel = .2
        acc = 5
        big = 5
         
        self.F = np.matrix([[1, dt, dt2, 0, 0, 0], [0, 1, dt, 0, 0, 0], [0, c, 1, 0, 0, 0], [0, 0, 0, 1, dt, dt2], [0, 0, 0, 0, 1, dt], [0, 0, 0, 0, c, 1]])            
        self.sigX = np.matrix([[pos, 0, 0, 0, 0, 0], [0, vel, 0, 0, 0, 0], [0, 0, acc, 0, 0, 0], [0, 0, 0, pos, 0, 0], [0, 0, 0, 0, vel, 0], [0, 0, 0, 0, 0, acc]])
        self.H = np.matrix([[1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0]])
        self.sigZ = np.matrix([[sd, 0], [0, sd]])
        self.Mu = np.matrix([[0], [0], [0], [0], [0], [0]])
        self.sig_t = np.matrix([[big, 0, 0, 0, 0, 0], [0, .1, 0, 0, 0, 0], [0, 0, .1, 0, 0, 0], [0, 0, 0, big, 0, 0], [0, 0, 0, 0, .1, 0], [0, 0, 0, 0, 0, .1]])
        
        self.FT = self.F.T
        self.HT = self.H.T
        
    def resetConfidence(self):
        pos = 5
        vel = .1  
        acc = .1 
        self.sig_t = np.matrix([[pos, 0, 0, 0, 0, 0], [0, vel, 0, 0, 0, 0], [0, 0, acc, 0, 0, 0], [0, 0, 0, pos, 0, 0], [0, 0, 0, 0, vel, 0], [0, 0, 0, 0, 0, acc]])    
        self.Mu = np.matrix([[self.zt1.tolist()[0][0]], [1], [0], [self.zt1.tolist()[1][0]], [1], [0]])
        
    def updateK(self, A): 
        self.K = (A * self.HT) * (self.H * A * self.HT + self.sigZ).I 
        
    def updateMu(self):
        self.Mu = (self.F * self.Mu) + (self.K * (self.zt1 - (self.H * self.F * self.Mu)))
        
    def updateSig_t(self, A):
        I = np.matrix(np.identity(6))
        self.sig_t = (I - (self.K * self.H)) * A  
        if self.plotTimer <= 0:
            assert self.sig_t[0, 3] == self.sig_t[3, 0]
            sig2_x = self.sig_t[0, 0]
            sig_x = math.sqrt(sig2_x)
            sig2_y = self.sig_t[3, 3]
            sig_y = math.sqrt(sig2_y)
            rhoSigxSigy = self.sig_t[0, 3]
            rho = rhoSigxSigy / (sig_x * sig_y)
        
    def estimateMu(self):    
        return self.F * self.Mu 
    
    def predictMu(self, future):
        ticks = int(future / .01)
        estimate = self.estimateMu()
        for tick in range(1, ticks + 1):
            estimate = self.F * estimate
            
        return ((self.H * estimate).T).tolist()[0]    
        
    def tick(self, gameClock):   
        """Some time has passed; decide what to do next."""
        self.tickTime = gameClock - self.prevTime
        resetInterval = 10
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.obstacles = self.bzrc.get_obstacles()
        
        if self.firstTick:  # some initializing
            for flag in flags:
                if flag.color == self.constants['team']:
                    self.homeBase = [flag.x, flag.y]
            self.firstTick = False
            
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color != 
                        self.constants['team']]

        self.commands = []
        self.teamIndex = -1
        self.timer -= self.tickTime
        self.plotTimer -= self.tickTime
        
        if self.timer <= 0:
            self.timer = resetInterval
            self.resetConfidence()
        
        shouldShoot = True
        shotSpeed = 100

        for index in range(len(flags)):
            if flags[index].color == self.constants['team']:
                self.teamIndex = index
        
        self.currentTank = mytanks[0]
    
        if self.currentTank.flag != '-':
            self.goalPos = self.homeBase
        else:   
            goalReading = self.chooseTarget() 
            self.zt1 = np.matrix(goalReading).T
            estimate = (self.H * self.estimateMu()).T.tolist()[0]
            dist = self.getDistance([self.currentTank.x, self.currentTank.y], estimate)
            if self.oldDist == 0: self.oldDist = dist
            distDiff = dist - self.oldDist
            future = (dist + distDiff) / shotSpeed
            self.oldDist = dist
            self.goalPos = self.predictMu(future)
            A = (self.F * self.sig_t * self.FT) + self.sigX
            self.updateK(A)
            self.updateMu()
            self.updateSig_t(A)
            self.estimatesX.append(estimate[0])
            self.estimatesY.append(estimate[1])
            self.obsX.append(self.enemies[0].x)
            self.obsY.append(self.enemies[0].y)

    
        self.attractiveField()
        self.repulsiveFields()
        self.tangentialFields()
        self.applyDelta()
        if self.curSpeed == 0 and self.enemies[0].x > -600:
            plt.plot(estimate[0], estimate[1], 'bo', self.enemies[0].x, self.enemies[0].y, 'ro')
            plt.draw()
        command = Command(self.currentTank.index, self.curSpeed, self.curAngVel, shouldShoot)
        self.commands.append(command)
        
            
        self.bzrc.do_commands(self.commands)
        self.prevTime = gameClock
    
def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >> sys.stderr, '%s: incorrect number of arguments' % execname
        print >> sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    # bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = KalmanAgent(bzrc)

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

    # ./bin/bzrflag --world=maps/empty_condensed.bzw --red-tanks=1 --purple-tanks=1 --blue-tanks=0 --green-tanks=0 --red-port=33333 --purple-port=22222 --world-size=500 --default-posnoise=5