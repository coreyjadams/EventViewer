from dataInterface import *
from ROOT import *
import time

bdi = baseDataInterface("argoneut", "")
bdi._dataHandle.set_input_file("python/nue_larlite_all.root")
bdi._dataHandle.add_drawing_process("wire","caldata")
bdi._dataHandle._event = 6
bdi._dataHandle.processEvent()

print "Conversions are: "
print bdi._wire2Cm, " cm per wire"
print bdi._time2Cm, " cm per time tick"

# get the images:
img = bdi._dataHandle._daughterProcesses['wire'].get_img()


xmin = 100
xmax = 220
ymin = 500
ymax = 1600
zmin = -2
zmax = 30

# c = TCanvas("canv","canv",1000,800)
# c.cd()


hist = TH2D("2Dimage","2D Image",xmax-xmin,xmin,xmax-1, ymax-ymin,ymin,ymax-1,)
for x in range(xmin,xmax):
  for y in range(ymin, ymax):
    # print "(",x,",",y,"): ",img[-1][x][y]
    hist.SetBinContent(x-xmin,y-ymin,img[-1][x][y])
    # hist.Fill(x-xmin,y-ymin,img[-1][x][y])
# set the bins:
hist.SetFillColor(kRed)
hist.Draw("surf4 A FB BB")
# hist.Draw("iso")

time.sleep(500)