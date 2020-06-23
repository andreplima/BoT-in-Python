import sys
#import pickle
import numpy as np
#import multiprocessing #xxx
#import bootstrapped.bootstrap as bs
#import bootstrapped.stats_functions as bs_stats

from datetime        import datetime
from multiprocessing import Pool
from itertools       import chain


ECO_DATETIME_FMT = '%Y%m%d%H%M%S'
ECO_SEED = 23

#-----------------------------------------------------------------------------------------------------------
# Timing and I/O helper functions
#-----------------------------------------------------------------------------------------------------------

def stimestamp():
  return(datetime.now().strftime(ECO_DATETIME_FMT))

def stimediff(finishTs, startTs):
  return str(datetime.strptime(finishTs, ECO_DATETIME_FMT) - datetime.strptime(startTs, ECO_DATETIME_FMT))

def tsprint(msg):
  print('[{0}] {1}'.format(stimestamp(), msg))

#-----------------------------------------------------------------------------------------------------------
# Estimator functions using different execution (sequential, parallel) or solving (statistical) schemes
#-----------------------------------------------------------------------------------------------------------

def drawSample(ss):

  # defines parameters for height and weight of a male human individual, Brazilian national, 20-40yrs
  # GUIMARÃES, M. Desenvolvimento do Manequim Matemático do Homem Brasileiro para Cálculos de
  #   Dosimetria Interna. 1995 (Tese de Doutorado) – Instituto de Pesquisas Energéticas e Nucleares.
  #   São Paulo).
  # (see page 29; uses data that were collected by IBGE back in 1976/1977)
  height_mu = 168.0 # in cm
  height_sd =   0.1
  weight_mu =  62.0 # in Kg
  weight_sd =   0.4

  # draws a sample with the specified size
  # PREMISE 1: these attributes are normally distributed in the brazilian male population
  # PREMISE 2: an individual of average height is assumed to also have the average weight
  height_sample = np.random.normal(height_mu, height_sd, ss)
  weight_sample = np.random.normal(weight_mu, weight_sd, ss)
  sample = list(zip(height_sample, weight_sample))  # each point conforms to a (height, weight) tuple

  return sample

def sequential(sample):

  # computes the mean estimate for the body- mass index (BMI)
  bmi_sample = [weight / (height/100) ** 2 for (height, weight) in sample]
  point_estimate = np.mean(bmi_sample)

  return point_estimate

def statistical(sample, ss, sz, _alpha):

    resample = [sample[i] for i in np.random.choice(ss, min(sz, 10000))]
    bmi_sample = [weight / (height/100) ** 2 for (height, weight) in resample]
    res = bs.bootstrap(np.array(bmi_sample), stat_func=bs_stats.mean, alpha=_alpha)

    return (res.lower_bound, res.value, res.upper_bound)

def parallel(sample, ss, nc):

  # splits the sample into k partitions, with k being the number of assignable cores
  # since we assume each point in the sample is a task, then each partition is a "bag of tasks"
  tsprint('-- chunking the sample into partitions.')
  #partitions = list(chunks(sample, nc))
  #sample = None # frees up some unneeded memory space

  # assigns each partition to a process and have them executed
  tsprint('-- allocating {0} new processes.'.format(nc))
  pool = Pool(processes = nc,)

  tsprint('-- assigning partitions to running processes.')
  #res = pool.map(bote, partitions)
  chunkSize = ss // nc
  res = pool.map(bote, sample, chunksize=chunkSize)

  tsprint('-- aggregating results.')
  bmi_sample = list(chain(*res))

  tsprint('-- estimating distribution center.')
  point_estimate = np.mean(bmi_sample)

  return point_estimate

def chunks(L, nc):
  """
  A generator function for chopping up a given list into chunks with about the same size.
  """
  listSize  = len(L)
  chunkSize = listSize // nc

  idxl = 0
  boundaries = []
  while (idxl < listSize):
    idxr = min(idxl + chunkSize, listSize)
    boundaries.append((idxl, idxr))
    idxl = idxr

  for i in range(len(boundaries)):
    (idxl, idxr) = boundaries[i]
    yield L[idxl:idxr]

#def bote(partition): # Bag of tasks executor
#  """
#  A 'bag of tasks' executor.
#  """
#  L = []
#  for task in partition:
#    (height, weight) = task
#    bmi = weight / (height/100) ** 2
#    L.append(bmi)
#
#  return L

def bote(partition): # Bag of tasks executor
  """
  A 'bag of tasks' executor.
  """
  L = [22, 22]
  print('** partition is of type {0} and length {1}'.format(type(partition), len(partition)))

  return L

#-----------------------------------------------------------------------------------------------------------
# Main -- you can ask for BMI estimates obtained from different execution/solving schemes
#-----------------------------------------------------------------------------------------------------------

def main(nc, ss, sz):

  # draws a sample with the specified size
  tsprint('Drawing a sample with {0} million individuals.'.format(ss))
  ss = int(ss * 1E6)
  sample = drawSample(ss)

  if(nc == 0):

    # computes the estimate for the center of the distribution using a statistical scheme
    alpha = 0.05
    tsprint('Sequential execution started (using an approximate solver with {0} points).'.format(sz))
    startTs = stimestamp()
    (lb, point_estimate, ub) = statistical(sample, ss, sz, alpha)
    finishTs = stimestamp()
    tsprint('Sequential execution completed.')

    # presents the results obtained
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- we are {2:4.1f}% confident that the real value is between {0:4.1f} and {1:4.1f}.'.format(lb, ub, 1 - alpha))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc == 1):

    # computes the estimate for the center of the distribution using a sequential execution scheme
    tsprint('Sequential execution started (using an "exact" solver).')
    startTs = stimestamp()
    point_estimate = sequential(sample)
    finishTs = stimestamp()
    tsprint('Sequential execution completed.')

    # presents the results obtained
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc > 1):

    # computes the estimate for the center of the distribution using a parallel execution scheme
    tsprint('Parallel execution started with {0} cores (using an "exact" solver).'.format(nc))
    startTs = stimestamp()
    point_estimate = parallel(sample, ss, nc)
    finishTs = stimestamp()
    tsprint('Parallel execution completed.')

    # presents the results obtained
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  else:
    raise ValueError('Number of cores was wrongly specified.')


if __name__ == "__main__":

  # command line:
  #
  # python case1.py <number of cores> [<sample size>] [<bootstrap sample size>]
  # -- <number of cores>: how many cores can be assigned to tasks;
  #                        0  commands sequential execution of an approximate solver
  #                        1  commands sequential execution of an "exact" solver
  #                       >1  commands parallel   execution of an "exact" solver
  # -- <sample size>: number of points in the sample, in millions of individuals (e.g. '1' means 1 million)
  # -- <bootstrap sample size>: number of points in the bootstrap sample

  nc = int(sys.argv[1])
  ss = int(sys.argv[2]) # sample size in million of individuals

  if(nc == 0):
    # this is a call for a sequential execution -- using an approximated solver
    sz = int(sys.argv[3]) # bootstrap sample size
  else:
    sz = None

  main(nc, ss, sz)
