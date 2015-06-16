from dataInterface import *
from ROOT import *

bdi = baseDataInterface("lariat", "daq")
rdi = rawDaqInterface()

path = "/media/cadams/data_linux/lariat_daq/"

files = [ "dqm_run_005310_spill_0096.root",
          # "dqm_run_005310_spill_0097.root",
          # "dqm_run_005310_spill_0098.root",
          # "dqm_run_005310_spill_0099.root"
        ]

event_list =  [
                0,
                # 0,
                # 2,
                # 0 
              ]

i = 0;
for file in files:
  rdi.set_input_file(path+file)
  rdi._event = event_list[i]
  i += 1
  # get the 3d array of data: [plane][wire][tick]
  img = rdi.get_img()
  print len(img)
  print len(img[0])
  print type(img)
  for plane in range(0,len(img)):
    print "Plane ", plane
    for wire in range(0,len(img[plane])):
      rms = np.std(img[plane][wire])
      print len(img[plane][wire])
      print "\tWire " , wire , ", rms: ", rms
