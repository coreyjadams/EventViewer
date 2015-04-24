LArLite Event Viewer

LICENSE:
------------------------------------
This code is free for you to use, develop with, and redistribute.
It is built on pyqt4, pyqtgraph, larlite, and perhaps someday Cython
(but no cython yet).  If you're using it, you're doing liquid argon
TPC physics, so your comments and feed back are welcome!  Send comments,
complaints, compliments, feature requests, etc., to Corey Adams:
corey.adams@yale.edu

INFO:
------------------------------------
Thanks for trying out my little toy event viewer!  I wrote this 
for myself as a way to visualize cluster data in a way that didn't suck.
It also draws wires and hits.  I've found it really useful in determining
the effectiveness of cluster merging and the wire pictures look decent.

Below I've outlined some of the implemented features and things
that are on the "to do" list.  But first, here is how to install
and run the event viewer:

REQUIREMENTS:
------------------------------------
Larlite (and it's requirements)
PyQt4  (and anything it depends on)

If you are running on Ubuntu, PyQt4 is probably already on your system.

If you run Mac OS, get it here http://www.riverbankcomputing.com/software/pyqt/download.  It also appears to be available through macports and homebrew.
I definitely recommend using port or brew for this, package managers are
much simpler.

INSTALLATION:
------------------------------------
-Check out this folder into UserDev.  In principal, I guess you could
put it anywhere.
-With larlite setup, cd into the folder EventViewer (unless you
called it something else) and type make.  It should compile two
packages, RecoViewer and RawViewer.
-source the setup script setup_evd.sh.  This adds the scripts
to your PATH and PYTHONPATH so that you can run from anywhere.

RUNNING:
------------------------------------
Current usage is very simple:
evd.py [file]

[file] is optional, but if you include a file on the command line
the viewer will open it and get ready to draw.  If not, there is 
a button to select a file.


FEATURES
------------------------------------

--DRAWS hits, clusters, wires.  Wires can be toggle with the drawRaw checkbox
  When you select a hit or cluster producer, it will draw that product.
  It will automatically scan your larlite file and find all hit and cluster
  producers.

--MOVEMENT: Zoom in and out of the image with scrolling, 
  click and drag to pan.  As you move the mouse over a view, in the bottom
  left corner it will show you the Wire, Timetick coordinate of the mouse.
  You can change this to cm/cm space with the tick box nearby. (use cm)

--DRAW WIRES: Click on an image to draw the wire the mouse clicked on, 
  if wire data available.  You will have to click the box "Wire Drawing"

--DRAW CLUSTERS: With clusters drawn, hover the mouse over a \
  cluster to highlight it. Double click sets the highlight to stick, double click again to undo it

--VIEW RANGE: The max range button will show you the entire range of data
  available.  The Auto Range button will zoom to the level that shows 
  interesting features.  Currently, it ONLY works for clusters.
  if Lock A.R. is checked, the viewer enforces that x and y dimensions are
  1 to 1, that is the scale is the same in all directions.

--FILE SELECTION: You can use the button "Select File" to pick a file to open
  It should discard the old file when you do this.

--EVENT SELECTION: The top left of the viewer shows run and event number, 
  And the entry box shows the current event in larlite index (which is
  just starting at 0 and going to N_events).  Enter a number in there
  to jump to an event.  It should complain if you enter garbage, but
  shouldn't crash.

--HOTKEYS:  
    n - next event
    p - prev event
    c - set focus to cluster selection
    h - set focus to hit selection
    up/down - change cluster/hit producer if focus is on selection.



KNOWN ISSUES, BUGS, OR REQUESTED FEATURES
------------------------------------
-- Seems to be a small bug when zooming in far, making wires offset with hits.
-- Add other 2d reco objects: vertex (projected), mctrack/mcshower.  
-- Print mctruth somewhere (bottom, next to w/t display?)
-- command line options or button to toggle argo or microboone geom (or other?)

