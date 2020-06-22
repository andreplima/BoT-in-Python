import sys
import numpy as np
import multiprocessing

from multiprocessing import Pool

ECO_SEED = 23

def sequential(ns, mu, sd):

  sample = np.random.normal(mu, sd, ns)
  point_estimate = np.mean(sample)
  return point_estimate


def main(numOfSamples, numOfPartitions):

  # ensures the pseudo-random generator behaves the same between executions
  np.random.seed(ECO_SEED)

  # convert input parameters to required type
  nos = int(numOfSamples)
  nop = int(numOfPartitions)

  # established the estimates for mean/sd of the weight of a male individual,
  # 20-40yrs, Brazilian national, 1995
  # GUIMARÃES, M. Desenvolvimento do Manequim Matemático do Homem Brasileiro para Cálculos de
  #   Dosimetria Interna. 1995 (Tese de Doutorado) – Instituto de Pesquisas Energéticas e Nucleares.
  #   São Paulo).
  mu = 62.0
  sd =  0.4

  if(nop == 1):
    point_estimate = sequential(nos, mu, sd)

  elif(nop > 1):
    point_estimate = parallel(nos, np, mu, sd)

  else:
    raise ValueError('Number of partitions was wrongly specified.')

  print('The point estimate for the distribution center is {0:4.1f}'.format(point_estimate))

if __name__ == "__main__":

  main(sys.argv[1], sys.argv[2])
