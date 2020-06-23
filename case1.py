import os
import sys
import numpy as np

from sharedDefs import tsprint, stimestamp, stimediff
from case1Defs  import drawSample, sequential, parallel

ECO_SEED = 23

#-----------------------------------------------------------------------------------------------------------
# CASE 1 - computing a distance matrix
#-----------------------------------------------------------------------------------------------------------

def main(nc, ss, nd):

  # draws a sample with the specified size
  tsprint('Drawing a sample with {0} {1}D-vectors.'.format(ss, nd))
  sample = drawSample(ss, nd, ECO_SEED)

  if(nc == 1):

    # obtains the distance matrix using a sequential execution scheme
    tsprint('Sequential execution started (process {0}).'.format(os.getpid()))
    startTs = stimestamp()
    mm = sequential(sample, ss)
    finishTs = stimestamp()
    tsprint('Sequential execution completed.')

    # presents the results obtained
    tsprint('-- the distance matrix has {0} elements.'.format(len(mm)))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc > 1):

    # computes the estimate for the center of the distribution using a parallel execution scheme
    tsprint('Parallel execution started with {0} processes spawned from {1}.'.format(nc, os.getpid()))
    startTs = stimestamp()
    mm = parallel(sample, ss, nc)
    finishTs = stimestamp()
    tsprint('Parallel execution completed.')

    # presents the results obtained
    tsprint('-- the distance matrix has {0} elements.'.format(len(mm)))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  else:
    raise ValueError('Number of cores was wrongly specified.')


if __name__ == "__main__":

  # command line:
  #
  # python case1.py <number of cores> <sample size> <dimensionality>
  # -- <number of cores>: how many cores can be assigned to tasks;
  # -- <sample size>: number of vectors that will comprise the sample, in thousands
  # -- <dimensionality>: the number of dimensions of the sampling space

  nc = int(sys.argv[1])
  ss = int(sys.argv[2])
  nd = int(sys.argv[3])

  main(nc, ss, nd)
