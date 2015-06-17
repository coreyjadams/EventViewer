
from larlite import larlite as fmwk
from larlite import larutil
import numpy as np

class geoBase(object):
  """docstring for geometry"""
  def __init__(self):
    super(geoBase, self).__init__()
    self._nViews = 2
    self._tRange = 1600
    self._wRange = [240, 240]
    self._aspectRatio = 4
    self._time2Cm = 0.1
    self._wire2Cm = 0.4
    self._levels = [ (-15,15), (-10,30) ]

  def nViews(self):
    return self._nViews

  def tRange(self):
    return self._tRange

  def wRange(self, plane):
    return self._wRange[plane]

  def getLevels(self,plane):
    return self._levels[plane]

  def aspectRatio(self):
    return self._aspectRatio

  def getBlankData(self,plane):
    return np.ones((self._wRange[plane], self._tRange))

  def wire2cm(self):
    return self._wire2Cm

  def timewire2cm(self):
    return self._time2Cm

class geometry(geoBase):

  def __init__(self):
    super(geometry, self).__init__()
    self._nViews=larutil.Geometry.GetME().Nviews()
    self._time2Cm = larutil.GeometryUtilities.GetME().TimeToCm()
    self._wire2Cm = larutil.GeometryUtilities.GetME().WireToCm()
    self._aspectRatio = self._wire2Cm / self._time2Cm
    self._tRange = larutil.DetectorProperties.GetME().ReadOutWindowSize()
    self._wRange = []
    for v in range(0, self._nViews):
      self._wRange.append(larutil.Geometry.GetME().Nwires(v))   



class microboone(geometry):

  def __init__(self):
    # Try to get the values from the geometry file.  Configure for microboone
    # and then call the base class __init__
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kMicroBooNE)
    super(microboone, self).__init__()
    self._levels = [ (-15,15),(-15,15),(-10,10) ]

class argoneut(geometry):

  def __init__(self):
    # Try to get the values from the geometry file.  Configure for microboone
    # and then call the base class __init__
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kArgoNeuT)
    super(argoneut, self).__init__()
    self._levels = [ (-15,15),(2,20) ]

class lariat(geometry):

  def __init__(self):
    # Try to get the values from the geometry file.  Configure for microboone
    # and then call the base class __init__
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kArgoNeuT)
    super(lariat, self).__init__()
    # lariat has a different number of time ticks
    # fix it directly:
    self._tRange = 3072/2
    self._levels = [ (-15,15),(-10,10) ]



