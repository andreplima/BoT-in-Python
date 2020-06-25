import os
import numpy as np

from sharedDefs      import tsprint
from multiprocessing import Pool
from itertools       import chain

#-----------------------------------------------------------------------------------------------------------
# Estimator functions using different execution (sequential, parallel) schemes
#-----------------------------------------------------------------------------------------------------------

def drawSample(ss, nd, seed):

  # ensures the pseudo-random number generator will behave the same between executions
  np.random.seed(seed)

  # draws a sample of size <ss> of pseudo-random count <nd>-dimensional vectors from unit nd-boxes
  sample = {i: np.array([np.random.random() for _ in range(nd)]) for i in range(ss)}

  return sample

def sequential(sample, ss):

  # the task is to compute a distance between two vectors;
  # assumes the distance function (implemented in te) is symmetric
  mm = {}
  for i in range(ss - 1):
    for j in range(i + 1, ss):
      mm[(i,j)] = te(sample[i], sample[j])

  return mm

def parallel(sample, ss, nc):

  # converts each point in the sample into a task
  tasks = []
  for i in range(ss - 1):
    for j in range(i + 1, ss):
      task = ( (i,j), (sample[i], sample[j]) )
      tasks.append(task)

  # partitions the tasks into bags and execute them
  pool = Pool(processes = nc,)
  partitions = chunks(tasks, nc)
  results = pool.map(bote, partitions)

  # aggregates the results into an integrated response
  mm = dict(chain(*results))

  return mm

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
    ( (i,j), (v,w) ) = task
    result.append(( (i,j), te(v,w) ))
  tsprint('   subprocess {0:5d} is about to join.'.format(os.getpid()))

  return result

def te(v, w):
  """ In 'Case 1', the task consists in computing the euclidean distance between two
      (dense) vectors. This implementation assumes that v and w are numpy arrays and
      that they have the same dimensionality
  """
  ub = len(v)
  acc = 0.0
  for i in range(ub):
    acc += (v[i] - w[i]) ** 2
  return(acc  ** .5 )
