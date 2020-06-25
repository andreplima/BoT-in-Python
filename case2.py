import os
import sys
import numpy as np

from sharedDefs import tsprint, stimestamp, stimediff
from case2Defs  import drawSample, statistical, sequential, parallel

ECO_SEED = 23

#-----------------------------------------------------------------------------------------------------------
# CASE 2 -- computing the average of a large sample
#-----------------------------------------------------------------------------------------------------------

def main(nc, ss, sz):

  # draws a sample with the specified size
  tsprint('Drawing a sample with {0} million individuals.'.format(ss))
  ss = int(ss * 1E6)
  sample = drawSample(ss, ECO_SEED)

  if(nc == 0):

    # obtains the estimate for the center of the distribution using a statistical scheme
    alpha = 0.05
    tsprint('Sequential execution started (using an approximate solver with {0} points).'.format(sz))
    startTs = stimestamp()
    (lb, point_estimate, ub) = statistical(sample, ss, sz, alpha)
    finishTs = stimestamp()
    tsprint('Sequential execution completed.')

    # presents the obtained results
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- we are {2:4.1f}% confident that the real value is between {0:4.1f} and {1:4.1f}.'.format(lb, ub, 100 * (1 - alpha)))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc == 1):

    # obtains the estimate for the center of the distribution using a sequential execution scheme
    tsprint('Sequential execution started (using an "exact" solver, process {0}).'.format(os.getpid()))
    startTs = stimestamp()
    point_estimate = sequential(sample)
    finishTs = stimestamp()
    tsprint('Sequential execution completed.')

    # presents the obtained results
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc > 1):

    # obtains the estimate for the center of the distribution using a parallel execution scheme
    tsprint('Parallel execution with {0} processes spawed from {1}.'.format(nc, os.getpid()))
    startTs = stimestamp()
    point_estimate = parallel(sample, nc)
    finishTs = stimestamp()
    tsprint('Parallel execution completed.')

    # presents the obtained results
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  else:
    raise ValueError('Number of cores was wrongly specified.')


if __name__ == "__main__":

  # command line:
  #
  # python case2.py <number of cores> [<sample size>] [<bootstrap sample size>]
  # -- <number of cores>: how many cores can be assigned to tasks;
  #                        0  commands sequential execution of an approximate solver
  #                        1  commands sequential execution of an "exact" solver
  #                       >1  commands parallel   execution of an "exact" solver
  # -- <sample size>: number of points in the sample, in millions (e.g. '1' means 1 million points)
  # -- <bootstrap sample size>: number of points in the bootstrap (re)sample

  nc = int(sys.argv[1])
  ss = int(sys.argv[2]) # sample size, in million of points

  if(nc == 0):
    # this is a call for a sequential execution using an approximated solver ...
    sz = int(sys.argv[3]) # .. so we need the sample size for the bootstrapping approximation
  else:
    sz = None

  main(nc, ss, sz)
