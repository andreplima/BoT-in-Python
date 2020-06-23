import pickle
from datetime        import datetime

#-----------------------------------------------------------------------------------------------------------
# Timing and I/O helper functions
#-----------------------------------------------------------------------------------------------------------

ECO_DATETIME_FMT = '%Y%m%d%H%M%S'

def stimestamp():
  return(datetime.now().strftime(ECO_DATETIME_FMT))

def stimediff(finishTs, startTs):
  return str(datetime.strptime(finishTs, ECO_DATETIME_FMT) - datetime.strptime(startTs, ECO_DATETIME_FMT))

def tsprint(msg):
  print('[{0}] {1}'.format(stimestamp(), msg))

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
