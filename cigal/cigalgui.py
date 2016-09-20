#!/usr/bin/python
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" Display gene clusters of 2 fasta sequesences of gene identifiers
in FASTA format using the connecting intervals algorithm described in

  Quadratic Time Algorithms for Finding Common Intervals in Two and More
  Sequences
  T. Schmidt, J. Stoye. Proceedings of CPM 2004, LNCS 3109, 347-359, 2004.
"""

import sys
import math
from sets import Set
from pprint import pprint
from cPickle import load

from qt import *
from qtgl import *
from OpenGL.GL import *

from CIViewGui import CIViewGui
from AboutDia  import AboutDia
from ZoomerWidget import ZoomerWidget, LOOK_SIG, ZOOM_SIG
from config import NAME, VERSION, GUI

SCROLL_MAX = 1000

# TODO: we probably don't need the zoom factor

class CIView(CIViewGui):
  def __init__(self, *args):
    CIViewGui.__init__(self, *args)
    self.connect(self.leftBtn, SIGNAL("clicked()"), self.zoomer.moveLeft)
    self.connect(self.rightBtn, SIGNAL("clicked()"), self.zoomer.moveRight)
    self.connect(self.upBtn, SIGNAL("clicked()"), self.zoomer.moveUp)
    self.connect(self.downBtn, SIGNAL("clicked()"), self.zoomer.moveDown)
    self.connect(self.inBtn, SIGNAL("clicked()"), self.zoomer.zoomIn)
    self.connect(self.outBtn, SIGNAL("clicked()"), self.zoomer.zoomOut)
    
    self.connect(self.zoomSelectBtn, SIGNAL("clicked()"),
		 self.zoomer.selectRegion)

    self.connect(self.zoomHomeBtn, SIGNAL("clicked()"),
		 self.zoomer.resetZoom)
    
    self.connect(self.alphaSpn, SIGNAL("valueChanged(int)"),
                 self.zoomer.setAlpha)

    self.connect(self.filterChk, SIGNAL("stateChanged(int)"),
                 self.updateFilter)
    self.connect(self.minAreaSpn, SIGNAL("valueChanged(int)"),
                 self.updateFilter)
    self.connect(self.maxAreaSpn, SIGNAL("valueChanged(int)"),
                 self.updateFilter)

    self.connect(self.guidesChk, SIGNAL("stateChanged(int)"),
                 self.zoomer.enableGuides)

    self.connect(self.zoomer, LOOK_SIG, self.updateScrollbars)
    self.connect(self.zoomer, ZOOM_SIG, self.updateScrollbarsRange)
    self.connect(self.hScroll, SIGNAL("sliderMoved(int)"),
		 self.moveView)
    self.connect(self.vScroll, SIGNAL("sliderMoved(int)"),
		 self.moveView)

    self.scrollRange = None
    self.hScroll.setMaxValue(SCROLL_MAX)
    self.vScroll.setMaxValue(SCROLL_MAX)
    self.hScroll.installEventFilter(self)
    self.vScroll.installEventFilter(self)


  def eventFilter(self, obj, event):
      if obj in [self.hScroll, self.vScroll] \
	     and event.type() == QEvent.Wheel:
	  obj.wheelEvent(event)
	  obj.emit(SIGNAL("sliderMoved(int)"), (obj.value(), ))
	  return True

      return False


  def moveView(self, *args):
      if self.scrollRange:
	  w = self.scrollRange[1]
      else:
	  w = 1.0

      mid = SCROLL_MAX/2
      x = 1.0*(mid-self.hScroll.value())/(.5*SCROLL_MAX)
      y = 1.0*(mid-self.vScroll.value())/(.5*SCROLL_MAX)

      self.zoomer.lookAt(x, y, False)


  def updateScrollbars(self, x, y):
      if self.scrollRange:
	  w = self.scrollRange[1]
      else:
	  w = 1.0

      mid = SCROLL_MAX/2
      self.hScroll.setValue(mid-int(x*.5*SCROLL_MAX))
      self.vScroll.setValue(mid-int(y*.5*SCROLL_MAX))


  def updateScrollbarsRange(self, l, r, t, b):
      self.scrollRange = [l, r, t, b]
      pageStep = int((r-l)*SCROLL_MAX*2)
      self.hScroll.setPageStep(pageStep)
      self.vScroll.setPageStep(pageStep)


  def updateFilter(self, *args):
    self.zoomer.filterCI(self.filterChk.isChecked(),
                         self.minAreaSpn.value(),
                         self.maxAreaSpn.value())
    self.minAreaSpn.setMaxValue(self.maxAreaSpn.value())
    self.maxAreaSpn.setMinValue(self.minAreaSpn.value())    
    self.nbClustLbl.setText(str(len(self.zoomer.filtered_ci)))
    

  def fileExit(self):
      self.close()

  def fileSaveAs(self):
      self.fileSave()

  def fileSave(self):
      filename = QFileDialog.getSaveFileName(
	  "clusters.png",
	  "Images (*.png *.xpm *.jpg);;All files (*.*)",
	  self)
      print "file:", filename
      if filename:
	  pix = self.zoomer.renderPixmap()
	  pix.save(filename, "PNG")


  def fileOpen(self):
      filename = QFileDialog.getOpenFileName(
        "",
        "Clusters (*.cigal);;All files (*.*)",
        self)
      if filename:
	  print "file:", filename
	  self.loadclusters(filename)
    

  def helpAbout(self):
      dia = AboutDia(self)
      dia.nameLbl.setText("<strong>" + NAME + " " + VERSION + "</strong>")
      dia.show()

  def loadclusters(self, filename):
      # TODO: pop a message box on error
      mapping = load(open(unicode(filename)))
      self.zoomer.setMapping(mapping)
      maxArea = self.zoomer.maxCIArea()
      self.maxAreaSpn.setMaxValue(maxArea)
      self.minAreaSpn.setMaxValue(maxArea)
      self.maxAreaSpn.setValue(maxArea)
      
    
def qt_run(filename=None):
    app = QApplication(sys.argv)
    win = CIView()
    app.setMainWidget(win)
    if filename:
	win.loadclusters(filename)
    win.show()
    app.exec_loop()

def main():
    if len(sys.argv) not in [1, 2]:
        print "USAGE: %s [FILE]" % sys.argv[0]
        print "  where FILE is a coninv output file",
        sys.exit(1)
    else:
        qt_run(len(sys.argv) == 2 and sys.argv[1])
    
    
if __name__ == "__main__":
    main()
