#Kalman Agent
import sys
import math
import time
import random
import KalmanPlotting
import numpy as np

from bzrc import BZRC, Command

class KalmanAgent(object):
	
	def __init__(self, bzr):
		self.bzrc = bzr
		self.constants = self.bzrc.get_constants()
		self.commands = []
		print 'team: ', self.constants['team']
		self.prevTime = 0.0
		self.timer = 5.0
		self.turnTimer = 1.5
		self.plotTimer = 0.0
		self.plotId = 0
		self.gunTimer = float(random.randrange(15, 26)) / 10
		self.oldDist = 0
        # self.flagZone = 150
        # self.homeBase = [0, 0]
        # self.goalPos = [0, 0] 
        # self.goalRadius = 5
        # self.distance = 0  # dist between goal and agent
        # self.angle = 0  # angle between goal and agent
        # self.dx = 0
        # self.dy = 0
        # self.oldDist = 0
		self.initMatrices()

	def initMatrices(self):
        
		
		#c = -.0001 # this may end up being zero
		c = 0
		dt2 = math.pow(.01, 2) / 2
		sd = 25  # standard deviation of the noise squared
		pos = .1
		vel = .2
		acc = 5
		big = 5
         
		self.F = np.matrix([[1, .01, dt2, 0, 0, 0], [0, 1, .01, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, .01, dt2], [0, 0, 0, 0, 1, .01], [0, 0, 0, 0, 0, 1]])            
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
			kalmanPlotting = KalmanPlotting.KalmanPlotting(sig2_x, sig2_y, rho, self.plotId)
			self.plotId += 1
			self.plotTimer = random.randrange(1, 6)
        
	def estimateMu(self):    
		return self.F * self.Mu 
    
	def predictMu(self, future):
		ticks = int(future / .01)  # ticks from now = seconds from now / (seconds per tick) 
		estimate = self.estimateMu()
		for tick in range(1, ticks + 1):
			estimate = self.F * estimate
            
		return ((self.H * estimate).T).tolist()[0]

	def getDistance(self, point1, point2):
		return math.sqrt(math.pow(point2[0] - point1[0], 2) + math.pow(point1[1] - point2[1], 2))

	def tick(self, gameClock):
		self.tickTime = gameClock - self.prevTime
		resetInterval = 10

		self.commands = []
		self.teamIndex = -1
		self.timer -= self.tickTime
		self.plotTimer -= self.tickTime
        
		if self.timer <= 0:
			self.timer = resetInterval
			self.resetConfidence()

		shouldShoot = True
		shotSpeed = 100

		mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
		self.othertanks = othertanks
		goalReading = othertanks[1]
		self.zt1 = np.matrix(goalReading).T
		estimate = (self.H * self.estimateMu()).T.tolist()[0]
		dist = self.getDistance([mytanks[0].x, mytanks[0].y], estimate)
		if self.oldDist == 0: self.oldDist = dist
		distDiff = dist - self.oldDist
		future = (dist + distDiff) / shotSpeed
		self.oldDist = dist
		self.goalPos = self.predictMu(future)
		A = (self.F * self.sig_t * self.FT) + self.sigX
		self.updateK(A)
		self.updateMu()
		self.updateSig_t(A)
		command = Command(0, self.curSpeed, self.curAngVel, shouldShoot)
		self.commands.append(command)


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


