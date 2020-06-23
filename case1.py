import sys
import pickle
import numpy as np
import multiprocessing

from datetime        import datetime
from multiprocessing import Pool
from itertools       import chain

ECO_DATETIME_FMT = '%Y%m%d%H%M%S'
ECO_SEED = 23

#-----------------------------------------------------------------------------------------------------------
# IO helper functions
#-----------------------------------------------------------------------------------------------------------

def serialise(obj, name):
  f = open(name + '.pkl', 'wb')
  p = pickle.Pickler(f)
  p.fast = True
  p.dump(obj)
  f.close()
  p.clear_memo()

def deserialise(name):
  f = open(name + '.pkl', 'rb')
  p = pickle.Unpickler(f)
  obj = p.load()
  f.close()
  return obj

def stimestamp():
  return(datetime.now().strftime(ECO_DATETIME_FMT))

def stimediff(finishTs, startTs):
  return str(datetime.strptime(finishTs, ECO_DATETIME_FMT) - datetime.strptime(startTs, ECO_DATETIME_FMT))

def tsprint(msg):
  print('[{0}] {1}'.format(stimestamp(), msg))

def chunks(L, nc):
  """
  A generator function for chopping up a given list into chunks.
  """
  listSize  = len(L)
  chunkSize = listSize // nc
  remainder = listSize %  nc

  idxl = 0
  boundaries = []
  while (idxl < listSize):
    idxr = min(idxl + chunkSize, listSize)
    boundaries.append((idxl, idxr))
    idxl = idxr

  for i in range(len(boundaries)):
    (idxl, idxr) = boundaries[i]
    yield L[idxl : idxr]

#-----------------------------------------------------------------------------------------------------------
# Estimator functions using different execution (sequential, parallel) or solving (statistical) schemes
#-----------------------------------------------------------------------------------------------------------

def sequential(sample):

  # computes the mean estimate for the body- mass index (BMI)
  bmi_sample = [weight / (height/100) ** 2 for (height, weight) in sample]
  point_estimate = np.mean(bmi_sample)

  return point_estimate

def parallel(sample, nc):

  # splits the sample into partitions, and each partition is taken as a bag of tasks
  tasks = sample

  # partitions the sample into bags of tasks and have them executed
  tsprint('-- chunking the sample.')
  pool = Pool(processes = nc,)
  partitions = list(chunks(tasks, nc))
  #for partition in partitions:
  #  print(len(partition))
  tsprint('-- distributing load into several processes.')
  bmi_sample = list(chain(*pool.map(bote, partitions)))
  #print(len(bmi_sample))
  point_estimate = np.mean(bmi_sample)

  return point_estimate

def bote(partition): # Bag of tasks executor

  L = []
  for task in partition:
    (height, weight) = task
    bmi = weight / (height/100) ** 2
    L.append(bmi)

  return L

#-----------------------------------------------------------------------------------------------------------
# Main -- you can ask for BMI estimates obtained from different execution/solving schemes
#-----------------------------------------------------------------------------------------------------------

def main(nc, ss):

  if(nc < 0):

    # establishes estimates for height and weight of a male human individual, Brazilian national, 20-40yrs
    # GUIMARÃES, M. Desenvolvimento do Manequim Matemático do Homem Brasileiro para Cálculos de
    #   Dosimetria Interna. 1995 (Tese de Doutorado) – Instituto de Pesquisas Energéticas e Nucleares.
    #   São Paulo).
    # (see page 29; uses data collected by IBGE back in 1977)
    height_mu = 168.0 # in cm
    height_sd =   0.1
    weight_mu =  62.0 # in Kg
    weight_sd =   0.4

    # draws a sample with the specified size
    tsprint('Creating a sample with {0} million individuals.'.format(ss//int(1E6)))
    height_sample = np.random.normal(height_mu, height_sd, ss)
    weight_sample = np.random.normal(weight_mu, weight_sd, ss)
    sample = list(zip(height_sample, weight_sample))  # each point conforms to a (height, weight) tuple

    # saves the sample (this might take some time)
    tsprint('Saving the sample.')
    serialise(sample, 'sample_{0}M'.format(int(ss//1E6)))

  elif(nc == 1):

    # recovers the sample
    tsprint('Recovering a sample with {0} million individuals.'.format(ss))
    sample = deserialise('sample_{0}M'.format(ss))

    # computes the estimate for the center of the distribution using a sequential execution scheme
    tsprint('Sequential execution started.')
    startTs = stimestamp()
    point_estimate = sequential(sample)
    finishTs = stimestamp()
    tsprint('Sequential execution completed.')
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc > 1):

    # recovers the sample
    tsprint('Recovering a sample with {0} million individuals.'.format(ss))
    sample = deserialise('sample_{0}M'.format(ss))

    # computes the estimate for the center of the distribution using a parallel execution scheme
    tsprint('Parallel execution started with {0} cores.'.format(nc))
    startTs = stimestamp()
    point_estimate = parallel(sample, nc)
    finishTs = stimestamp()
    tsprint('Parallel execution completed.')
    tsprint('-- the point estimate for the center of the distribution is {0:4.1f}.'.format(point_estimate))
    tsprint('-- the process took about {0} seconds to complete.'.format(stimediff(finishTs, startTs)))

  elif(nc == 0):

    # recovers the sample
    sample = deserialise('sample_{0}M'.format(int(ss//1E6)))

    # computes the estimate for the center of the distribution using a statistical scheme
    tsprint('Parallel process started with {0} cores, {1} chunks.'.format(nc, numOfChunks))
    point_estimate = 1 #xxx
    tsprint('Parallel process completed.')

  else:
    raise ValueError('Number of cores was wrongly specified.')


if __name__ == "__main__":

  # command line:
  #
  # python case1.py <number of cores> <sample size> [<number of chunks> if <number of cores> larger than 1]
  # -- <number of cores>: how many cores can be assigned to tasks;
  #                       <0  commands sample building
  #                        1  commands sequential execution using an "exact" solver
  #                       >1  commands parallel   execution using an "exact" solver
  #                        0  commands sequential execution using an approximate solver
  # -- <sample size>: number of points in the sample, in millions of individuals (e.g. '1' means 1 million)

  nc = int(sys.argv[1])

  if(nc < 0):
    # this is a call for sample building
    ss = int(int(sys.argv[2]) * 1E6) # sample size

  elif(nc == 1):
    # this is a call for a sequential execution -- using an "exact" solver
    # the number of chunks is not required
    ss = int(sys.argv[2]) # sample size in million of individuals

  elif(nc > 1):
    # this is a call for a parallel execution
    ss = int(sys.argv[2]) # sample size in million of individuals

  elif(nc == 0):
    # this is a call for a sequential execution -- using an approximated solver
    ss = int(sys.argv[2]) # sample size in million of individuals

  main(nc, ss)
