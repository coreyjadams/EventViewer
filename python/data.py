
from larlite import larlite as fmwk
from ROOT import evd
import numpy as np


# These classes provide the basic interfaces for drawing objects
# It's meant to be inherited from for specific instances
# There is a class for drawing the following things:
#   - Raw wire data
#   - a collection of rectangles (hits and clusters)
#   - markers (vertices, endpoints, etc)
#   - splines (for projecting tracks, etc.)


class wire(object):
  """docstring for wire"""
  def __init__(self):
    super(wire, self).__init__()
    self._process = evd.RawBase()
    
    # This is the (clunky) converter to native python
    self._c2p = evd.Converter()

  def get_img(self):
    d = []
    for i in range(0,self._nviews):
      d.append(np.array(self._c2p.Convert(self._process.getDataByPlane(i))) )
      # print "got a plane, here is a sample: ", d[i][0][0]
    return d

  def getPlane(self,plane):
    return np.array(self._c2p.Convert(self._process.getDataByPlane(i)))

  def get_wire(self, plane, wire):
    return np.array(self._c2p.Convert(self._process.getWireData(plane,wire)))



