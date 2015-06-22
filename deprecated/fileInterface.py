
import os.path
from ROOT import TFile

class fileInterface(object):

  """docstring for fileInterface"""
  def __init__(self):
    super(fileInterface,self).__init__()
    self._file = ""
    self._keyTable = dict()

  def pingFile(self, file):
    # This function opens the file to see
    # what data products are available
    
    # Open the file
    f = TFile(file)
    # prepare a dictionary of data products
    lookUpTable = dict()
    # Loop over the keys (list of trees)
    for key in f.GetListOfKeys():
      # keys are dataproduct_producer_tree
      thisKeyList = key.GetName().split('_')
      # gets three items in thisKeyList, which is a list
      # [dataProduct, producer, 'tree'] (don't care about 'tree')
      # check if the data product is in the dict:
      if thisKeyList[0] in lookUpTable:
        # extend the list:
        lookUpTable[thisKeyList[0]] += (thisKeyList[1], )
      else:
        lookUpTable.update( {thisKeyList[0] : (thisKeyList[1],)})


    self._keyTable = lookUpTable

  def fileExists(self, file):
    return os.path.exists(file)

  def getListOfKeys(self):
    return self._keyTable