from ROOT import *
import numpy

c = CToNumpy()
# a = c.Convert(c.getTestVector())
# print type(a)
# print len(a)
# print a

b = c.Convert(c.getTestVector2d())
print type(b)
print len(b)
print len(b[0])
print b
exit()