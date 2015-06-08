# Kalman Plotting


class KalmanPlotting(object):

    def __init__(self, sigX, sigY, rho, plotId):
        self.sig_x = sigX
        self.sig_y = sigY
        self.rho = rho
        self.plotId = plotId
        self.FILENAME = 'kalman' + str(self.plotId) + '.gpi'
        self.WORLDSIZE = 800
        
        self.driver()
        
    def gnuplot_header(self, minimum, maximum):
        '''Return a string that has all of the gnuplot sets and unsets.'''
        s = ''
        s += 'set xrange [%s: %s]\n' % (minimum, maximum)
        s += 'set yrange [%s: %s]\n' % (minimum, maximum)
        s += 'set pm3d\n'
        s += 'set view map\n'
        # The key is just clutter.  Get rid of it:
        s += 'unset key\n'
        # Make sure the figure is square since the world is square:
        s += 'set size square\n\n'
        
        s += 'unset arrow\n'
        # Add a pretty title (optional):
        # s += "set title 'Potential Fields'\n"
        print 'gnuplot_header: ', s
        return s
    
    def gnuplot_palette(self):
        s = ''
        s += 'set palette model RGB functions 1-gray, 1-gray, 1-gray\n'
        print s
        return s
    
    def gnuplot_isosamples(self, numSamples):
        s = ''
        s += 'set isosamples %s\n' % (numSamples)
        print s
        return s
    
    def gnuplot_setXYRho(self, x, y, rho):
        s = ''
        s += 'sigma_x = %s\n' % (x)
        s += 'sigma_y = %s\n' % (y)
        s += 'rho = %s\n' % (rho)
        print s
        return s
        
    def gnuplot_splot(self):
        s = ''
        s += 'splot 1.0/(2.0 * pi * sigma_x * sigma_y * sqrt(1 - rho**2)) \
* exp(-1.0/2.0 * (x**2 / sigma_x**2 + y**2 / sigma_y**2 \
- 2.0*rho*x*y/(sigma_x*sigma_y))) with pm3d'
        print s
        return s
        
    def driver(self):
        outfile = open(self.FILENAME, 'w')
        print >> outfile, self.gnuplot_header(-self.WORLDSIZE / 2, self.WORLDSIZE / 2)
        print >> outfile, self.gnuplot_palette()
        print >> outfile, self.gnuplot_isosamples(100)
        print >> outfile, self.gnuplot_setXYRho(self.sig_x, self.sig_y, self.rho)
        print >> outfile, self.gnuplot_splot()



        