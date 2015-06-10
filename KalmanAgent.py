import sys
import math
import time
import random
import KalmanPlotting
import numpy as np
import matplotlib.pyplot as plt


from bzrc import BZRC, Command

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
        
        self.flagZone = 150
        self.homeBase = [0, 0]
        self.goalPos = [0, 0] 
        self.goalRadius = 5
        self.distance = 0  # dist between goal and agent
        self.angle = 0  # angle between goal and agent
        self.dx = 0
        self.dy = 0
        self.oldDist = 0
        
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
        # if t < 0: return self.getDistance(point, start)
        # if t > 1: return self.getDistance(point, end)
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
        spread = 10
        beta2 = 100
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
                angle = (math.atan2(end[0] - start[0], -(end[1] - start[1]))) - math.pi / 2
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
        
    def applyDelta(self):
        threshold = .5
        # set up speed and angvel based on delta
        if self.skeetMode and not self.setup: self.curSpeed = 0
        else: self.curSpeed = math.sqrt(math.pow(self.dx, 2) + math.pow(self.dy, 2)) / 100
        angle = math.atan2(self.dy, self.dx)  # angle we want to face
        curAngle = self.currentTank.angle  # angle we are currently facing
        # print 'current speed', self.curSpeed
        # print 'target angle: ', angle
        # print 'current angle: ', curAngle
#         print 'dx: ', self.dx
#         print 'dy: ', self.dy
        
        angleDif = self.normalize_angle(angle - curAngle)
        # angleDif= math.fabs(curAngle - angle) #does this need to be normalized?
        # signedAngleDif= angle - curAngle
        # print 'Angle difference: ', angleDif
        if angleDif < threshold and angleDif > -threshold:  # this is a shot in the dark. Tuning needed
            # self.curAngVel= signedAngleDif
            self.curAngVel = angleDif * 2
        else:
            # self.curAngVel= math.copysign(1, signedAngleDif) #should come out to 1 or -1  
            self.curAngVel = math.copysign(1, angleDif)
        # print 'angvel: ', self.curAngVel 
        
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
        
        if distFlag < self.flagZone or self.skeetMode:  # defend the flag from enemies!
            targetEnemy = self.chooseTargetEnemy()
            if targetEnemy is not None:
                return targetEnemy
        
        return self.chooseTargetFlag() 
    
    def initMatrices(self):
        dt = .01  # delta t. Approximately .01 seconds pass between ticks
#         c = -.0001 # this may end up being zero
        c = 0
        dt2 = math.pow(dt, 2) / 2
        sd = 25  # standard deviation of the noise squared
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
        
#         print 'Matrix F', self.F
        
    def resetConfidence(self):
        print '\n\n------------- Resetting confidence --------------\n\n'
        pos = 5
        vel = .1  # velocity
        acc = .1  # acceleration
        self.sig_t = np.matrix([[pos, 0, 0, 0, 0, 0], [0, vel, 0, 0, 0, 0], [0, 0, acc, 0, 0, 0], [0, 0, 0, pos, 0, 0], [0, 0, 0, 0, vel, 0], [0, 0, 0, 0, 0, acc]])    
        self.Mu = np.matrix([[self.zt1.tolist()[0][0]], [1], [0], [self.zt1.tolist()[1][0]], [1], [0]])
        
    def updateK(self, A):  # A is F*sig_t*FT + sigX, but we save time by computing once, since it's used elsewhere too
        self.K = (A * self.HT) * (self.H * A * self.HT + self.sigZ).I 
        
    def updateMu(self):
        self.Mu = (self.F * self.Mu) + (self.K * (self.zt1 - (self.H * self.F * self.Mu)))
#         print 'estimated velocity:', self.Mu[1][0] + self.Mu[4][0]
        
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
            print sig_x
            print sig_y
            print rho
            
            plt.plot([sig_x], [sig_y], 'ro')
            plt.axis([-400, 400, -400, 400])
            plt.show()
            # kalmanPlotting = KalmanPlotting.KalmanPlotting(sig2_x, sig2_y, rho, self.plotId)
            # self.plotId += 1
            # self.plotTimer = random.randrange(1, 6)
        
    def estimateMu(self):    
        return self.F * self.Mu 
    
    def predictMu(self, future):
        ticks = int(future / .01)  # ticks from now = seconds from now / (seconds per tick) 
        estimate = self.estimateMu()
        for tick in range(1, ticks + 1):
            estimate = self.F * estimate
            
        return ((self.H * estimate).T).tolist()[0]    
        
    def tick(self, gameClock):   
        """Some time has passed; decide what to do next."""
        self.tickTime = gameClock - self.prevTime
#         print 'tickTime:', self.tickTime 
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
        
#         self.gunTimer -= self.tickTime
#         # self.moveTimer -= self.tickTime
#         if self.gunTimer <= 0:
#             shouldShoot = True
#             self.gunTimer = float(random.randrange(15, 25)) / 10
#             # print 'gunTimer reset: ', self.gunTimer
#         else:
#             shouldShoot = False
#         if len(shots) != 0: print shots[0].vx, shots[0].vy
        shouldShoot = True
        shotSpeed = 100

        for index in range(len(flags)):
            if flags[index].color == self.constants['team']:
                self.teamIndex = index
        
        # test with one tank
        if self.debug:
            self.currentTank = mytanks[0]
        
            if self.currentTank.flag != '-':
                self.goalPos = self.homeBase
            else:   
                goalReading = self.chooseTarget() 
                self.zt1 = np.matrix(goalReading).T
#                 print 'last Mu:', self.Mu
                estimate = (self.H * self.estimateMu()).T.tolist()[0]
                dist = self.getDistance([self.currentTank.x, self.currentTank.y], estimate)
                if self.oldDist == 0: self.oldDist = dist
                distDiff = dist - self.oldDist
                future = (dist + distDiff) / shotSpeed
                self.oldDist = dist
#                 print 'Distance:', dist, 'future:', future
#                 futurePos = self.predictMu(future)
                self.goalPos = self.predictMu(future)

               
#                 dist2 = self.getDistance([self.currentTank.x, self.currentTank.y], futurePos)
#                 timeDiff = (dist2 - dist) / shotSpeed
#                 ticksDiff = int(timeDiff / .01)
#                 goalX = futurePos[0] + (self.estimateMu()[1][0] * abs(ticksDiff))
#                 goalY = futurePos[1] + (self.estimateMu()[4][0] * abs(ticksDiff))
#                 self.goalPos = [goalX, goalY]
#                 print 'Future position', futurePos, 'Aiming at:', self.goalPos
#                 print 'Lead if same distance:', future, 'Lead based on predicted distance', adjustedFuture
#                 self.goalPos = (self.H * self.estimateMu()).T.tolist()[0]
                
                A = (self.F * self.sig_t * self.FT) + self.sigX
                self.updateK(A)
                self.updateMu()
                self.updateSig_t(A)

#             print 'goal:', self.goalPos, 'reading:', goalReading    
        
            self.attractiveField()
            self.repulsiveFields()
            self.tangentialFields()
            self.applyDelta()
            
            command = Command(self.currentTank.index, self.curSpeed, self.curAngVel, shouldShoot)
            self.commands.append(command)
        
        else:
            # try more tanks after one works
            i = 0     
            for tank in mytanks:
                if tank.status == 'dead':
                    continue
                self.currentTank = tank
                
                if self.currentTank.flag != '-':
                    self.goalPos = self.homeBase
                else:
                    self.goalPos = self.chooseTarget()
            
                """apply fields to set up command"""
#                 if self.prevTime == 0.0 and i == 0:
#                     self.fields = fields.Fields(self)
                self.attractiveField()
                self.repulsiveFields()
                self.tangentialFields()
                self.applyDelta()
            
                command = Command(tank.index, self.curSpeed, self.curAngVel, shouldShoot)
                self.commands.append(command)
                i += 1
            
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