from ROOT import *

f = TFile("/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root")

lookUpTable = dict()

for key in f.GetListOfKeys():
  # print key.GetName()
  thisKeyList = key.GetName().split('_')
  # print thisKeyList
  # gets three items in thisKeyList, which is a list
  # [dataProduct, producer, 'tree'] (don't care about 'tree')
  # check if the data product is in the dict:
  if thisKeyList[0] in lookUpTable:
    # extend the list:
    lookUpTable[thisKeyList[0]] += (thisKeyList[1], )
  else:
    lookUpTable.update( {thisKeyList[0] : (thisKeyList[1],)})


print lookUpTable
print ""
print lookUpTable['cluster']