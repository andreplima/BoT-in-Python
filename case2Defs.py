import os
import numpy as np
import bootstrapped.bootstrap as bs
import bootstrapped.stats_functions as bs_stats

from sharedDefs      import tsprint
from multiprocessing import Pool
from itertools       import chain

#-----------------------------------------------------------------------------------------------------------
# Estimator functions using different execution (sequential, parallel) and solving (statistical) schemes
#-----------------------------------------------------------------------------------------------------------

def drawSample(ss, seed):

  # ensures the pseudo-random number generator will behave the same between executions
  np.random.seed(seed)

  # defines parameters for height and weight of a male human individual, Brazilian national, 20-40yrs
  # GUIMARÃES, M. Desenvolvimento do Manequim Matemático do Homem Brasileiro para Cálculos de
  #   Dosimetria Interna. 1995 (Tese de Doutorado) – Instituto de Pesquisas Energéticas e Nucleares.
  #   São Paulo).
  # (see page 29; uses data that were collected by IBGE back in 1976/1977)
  height_mu = 168.0 # in cm
  height_sd =   0.1
  weight_mu =  62.0 # in Kg
  weight_sd =   0.4

  # draws a sample with the specified size (i.e., we are rebuilding the sample from the parameters)
  # PREMISE 1: these attributes are normally distributed in the Brazilian male population
  # PREMISE 2: an individual of average height is assumed to have average weight with highest probability
  height_sample = np.random.normal(height_mu, height_sd, ss)
  weight_sample = np.random.normal(weight_mu, weight_sd, ss)
  sample = list(zip(height_sample, weight_sample))  # each point conforms to a (height, weight) tuple

  return sample

def sequential(sample):

  # computes the estimate for the mean body-mass index (BMI)
  bmi_sample = [te(height, weight) for (height, weight) in sample]
  point_estimate = np.mean(bmi_sample)

  return point_estimate

def parallel(sample, nc):

  # converts each point in the sample into a task
  tasks = sample

  # partitions the tasks into bags and execute them
  pool = Pool(processes = nc,)
  partitions = chunks(tasks, nc)
  result = pool.map(bote, partitions)

  # aggregates the results into an integrated response
  bmi_sample = list(chain(*result))
  point_estimate = np.mean(bmi_sample)

  return point_estimate

def statistical(sample, ss, sz, _alpha):

    resample = [sample[i] for i in np.random.choice(ss, min(sz, 10000))]
    bmi_sample = [te(height, weight) for (height, weight) in resample]
    res = bs.bootstrap(np.array(bmi_sample), stat_func=bs_stats.mean, alpha=_alpha)

    return (res.lower_bound, res.value, res.upper_bound)

def chunks(L, numOfCores, adjust = []):
  """
  A generator function for chopping up a given list into chunks.
  """
  listSize  = len(L)
  chunkSize = listSize // numOfCores
  remainder = listSize %  numOfCores

  if(adjust == []):
    calibration = {i: 0         for i in range(numOfCores)}
  else:
    calibration = {i: adjust[i] for i in range(numOfCores)}

  core = 0
  idxl = 0
  boundaries = []
  while (idxl < listSize and remainder > 0):
    idxr = min(idxl + chunkSize + calibration[core] + 1, listSize)
    boundaries.append((idxl, idxr))
    idxl = idxr
    core += 1
    remainder -= 1
  while (idxl < listSize):
    idxr = min(idxl + chunkSize + calibration[core],     listSize)
    boundaries.append((idxl, idxr))
    idxl = idxr
    core += 1

  for i in range(len(boundaries)):
    (idxl, idxr) = boundaries[i]
    yield L[idxl : idxr]

def bote(partition): # Bag of tasks executor
  """
  A 'bag of tasks' executor.
  """
  tsprint('   subprocess {0:5d} has been spawned.'.format(os.getpid()))
  result = []
  for task in partition:
    (height, weight) = task
    result.append(te(height, weight))
  tsprint('   subprocess {0:5d} is about to join.'.format(os.getpid()))

  return result

def te(height, weight):
  """ In 'Case 1', the task consists in computing the euclidean distance between two
      (dense) vectors. This implementation assumes that v and w are numpy arrays and
      that they have the same dimensionality
  """
  bmi = weight / (height/100) ** 2
  return bmi
