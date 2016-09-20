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

""" widget to allow navigatio of the generated clusters """

from pprint import pprint
from colorsys import hsv_to_rgb
import os
import sys

from qt import *
from qtgl import *
from OpenGL.GL import *
#from OpenGL.GLUT import *

from cigal import remove_dups
from DetailView import DetailView
from DetailsDia import DetailsDia
from ClustImgDia import ClustImgDia

import math

# this is hackish...
HAS_PYGAME = False
try:
    import pygame
    HAS_PYGAME = True
except:
    pass


LOOK_SIG = PYSIGNAL("newLook(float,float)")
ZOOM_SIG = PYSIGNAL("newZoom(float,float,float,float)")

DEFAULT_ZOOM = 1.0
FAR = 20.0
NEAR = -5.0
S1 = 1
S2 = 2
FONTFILE = "FreeSansBold.ttf"
FONTSIZE = 32
FONTCOLOR = [80, 80, 80, 0]
TEX_SIZE = 256

IMG_HEIGHT = 60
BOX_WIDTH = 10

LABELS_ALPHA = .3

def font_path():
    if os.path.isdir("ttf"):
        return "ttf"
    else:
        return os.path.join(sys.prefix, "share", "ttf")

def clust_area(clust):
    p1, p2 = clust
    # remember kids, those are not (x, y) points
    return (p1[1] - p1[0] + 1) * (p2[1] - p2[0] + 1)

def inRect(x, y, rx1, ry1, rx2, ry2):
    return rx1 <= x <= rx2 and ry1 <= y <= ry2


def rainbow(nb_col):
    return map(lambda i: map(lambda x:int(x*255),
			     hsv_to_rgb(i*(1.0/(nb_col+1)),
					.50,
					.85)),
	       range(nb_col))


class DetailsGui(DetailsDia):
    def __init__(self, parent=None, *args):
	DetailsDia.__init__(self, parent, *args)
	self.connect(self.detailsBtn, SIGNAL("clicked()"), self.showDetails)
	self.connect(self.textBtn, SIGNAL("clicked()"), self.showTextDetails)
	self.connect(self.lst,
		     SIGNAL("doubleClicked(QListViewItem*)"),
		     self.handleClick)
	self.colormap = None

    def handleClick(self, item):
	self.showDetails()

    def setColormap(self, ref_genes):
	# pick colors

	genes = remove_dups(ref_genes)
	colors = rainbow(len(genes))
	self.colormap = dict(zip(genes, colors))
	
	#parent = self.parent()
	#s1 = parent.s1
	#s2 = parent.s2
	
	#keys = clustermap.keys()
## 	for k in keys:
## 	    p1, p2 = k
## 	    genes = map(lambda x:s2[x], range(p1[0]-1, p1[1])) + \
## 		    map(lambda x:s1[x], range(p2[0]-1, p2[1]))
## 	    for g in genes:
## 		self.colormap[g] = None

## 	keys = self.colormap.keys()
## 	for i,k in enumerate(keys):
## 	    self.colormap[k] = map(lambda x:int(x*255),
## 				   hsv_to_rgb(i*(1.0/(len(keys)+1)),
## 					      .50,
## 					      .85))

    def drawCluster(self, genes, label, signs):
	# leave enough space for the arrows
	revmapper = self.parent().revmapper
        names = map(lambda g_id, s:" "+["-", "+"][s]+revmapper[g_id]+" ",
                    genes, signs)

        font = self.parent().font()
        metrics = QFontMetrics(font)
        widths = map(lambda n:metrics.width(n), names)
        box_width = max([metrics.height(), BOX_WIDTH])+1
        img_height = max(widths+[IMG_HEIGHT])
	size = [len(genes)*box_width, img_height+box_width+2]
	label.setMinimumSize(*size)

	pix = QPixmap(*size)
	pnt = QPainter(pix)
        pnt.setFont(font)
	pnt.setBrush(self.paletteBackgroundColor())
	pnt.setPen(self.paletteBackgroundColor())
	pnt.drawRect(0, 0, size[0], size[1])

	for i,g_id in enumerate(genes):
	    pnt.setPen(QColor(*self.colormap[g_id]))
	    pnt.setBrush(QColor(*self.colormap[g_id]))
		
	    pnt.drawRect(i*box_width, box_width/2+1,
			 box_width, img_height)

	    # do the arrow
	    for j in range(box_width/2+1):
		t = box_width/2-j
		b = img_height+box_width/2+j

		if not signs[i]:
		    t, b = b, t
		
		pnt.drawLine(i*box_width+j, t,
			     (i+1)*box_width-j, t)

	    pnt.rotate(90.0)
	    pnt.setPen(QColor(0,0,0))
	    pnt.drawText(box_width/2, -i*box_width-metrics.descent(), names[i])
	    pnt.resetXForm()
	    
	pnt.end()
	label.setPixmap(pix)
	

    def showTextDetails(self):
	item = self.lst.selectedItem()
	if not item:
	    item = self.lst.firstChild()

	parent = self.parent()
	clust = item.getCluster()
	rec = parent.expandCluster(clust)

	dia = DetailView(self)
	dia.detailTxt.setText(rec)
	dia.show()


	    
    def showDetails(self):	
	item = self.lst.selectedItem()
	if not item:
	    item = self.lst.firstChild()

	parent = self.parent()
	revmapper = parent.revmapper
	s1 = parent.s1
	s2 = parent.s2
	s1_signs = parent.s1_signs
	s2_signs = parent.s2_signs
	
	p1, p2 = item.getCluster()
	g_s1, g_s2 = [map(lambda x:s2[x], range(p1[0]-1, p1[1])),
		      map(lambda x:s1[x], range(p2[0]-1, p2[1]))]
	s_s1, s_s2 = [map(lambda x:s2_signs[x], range(p1[0]-1, p1[1])),
		      map(lambda x:s1_signs[x], range(p2[0]-1, p2[1]))] 
	
	dia = ClustImgDia(self)
	# stupid inversion bug...
	dia.s1NameLbl.setText(parent.s2_name)
	dia.s2NameLbl.setText(parent.s1_name)

	self.setColormap(g_s1)
	#self.colors = rainbow(len())

	self.drawCluster(g_s1, dia.s1ImgLbl, s_s1)
	self.drawCluster(g_s2, dia.s2ImgLbl, s_s2)
	
	dia.show()


class ClustListViewItem(QListViewItem):
    def __init__(self, parent=None, *args):
	QListViewItem.__init__(self, parent, *args)

    def compare(self, other, col, ascending_p):
	# the doc says to ignore ascending_p
	val = int(str(self.text(col))) - int(str(other.text(col)))
	return val

    def setCluster(self, clust):
	self.clust = clust

    def getCluster(self):
	return self.clust
    
    

class ZoomerWidget(QGLWidget):
    def __init__(self,parent=None,name=None):
	QGLWidget.__init__(self,parent,name)
	font = QFont(self.font())
	font.setPointSize(16)
	font.setBold(True)
	self.setFont(font)

	self.initPosition()
	
	self.regionStart = None
	self.selectionRect = None
	self.selectingRegion = False
	self.grabing = False
	self.ci = None
	self.filtered = False
	self.guides = False

	self.gridDisplayList = None
	self.clusterDisplayList = None
    

    def initPosition(self):
	self.z = -5.0
	self.zoom = DEFAULT_ZOOM
	self.lookAt(0.0, 0.0)

	self.z_inc = 0.2
	self.p_inc = 0.1
	self.alpha = .3


    def setMapping(self, mapping):
	[revmapper,
	 s1, s1_signs, s1_name,
	 s2, s2_signs, s2_name,
	 ci] = mapping
	self.revmapper = revmapper
	self.s1 = s1
	self.s1_signs = s1_signs
	self.s1_name = s1_name.strip()
	self.s2 = s2
	self.s2_signs = s2_signs
	self.s2_name = s2_name.strip()
	self.ci = ci
	self.filtered_ci = ci
	self.initPosition()

	if self.isValid():
	    self.makeGridDisplayList()
	    self.makeClusterDisplayList()
	    self.rezoom()
	  

    def enableGuides(self, val):
	self.guides = val
	self.update()
	

    def filterCI(self, on, minArea, maxArea):
	if on:
	    new_ci = filter(lambda cl:minArea <= clust_area(cl) <= maxArea,
			    self.ci)
	    self.filtered_ci = new_ci
	else:
	    self.filtered_ci = self.ci

	if not (not self.filtered and not on):
	    if self.isValid():
		self.makeGridDisplayList()
		self.makeClusterDisplayList()
	    self.update()
	self.filtered = on
      

    def lookAt(self, x, y, emitp=True):
	self.x = x
	self.y = y

	if emitp:
	    self.emit(LOOK_SIG, (x, y))
	
	self.update()


    def maxCIArea(self):
	return max(map(clust_area, self.ci))


    def zoomIn(self):
	self.zoom *= (1.0-self.z_inc)
	self.rezoom()


    def zoomOut(self):
	self.zoom *= (1.0+self.z_inc)
	self.rezoom()


    def moveUp(self):
	self.lookAt(self.x,
		    self.y + self.p_inc*self.zoom)


    def moveDown(self):
	self.lookAt(self.x,
		    self.y - self.p_inc*self.zoom)


    def moveLeft(self):
	self.lookAt(self.x + self.p_inc*self.zoom,
		    self.y)


    def moveRight(self):
	self.lookAt(self.x - self.p_inc*self.zoom,
		    self.y)


    def wheelEvent(self, event):
	self.zoom *= (1.0 + (self.z_inc/2.0)*event.delta()/120.0)

	event.accept()
	self.rezoom()

    def mousePressEvent(self, event):
	if self.selectingRegion:
	    self.regionStart = (event.x(), event.y())
	    event.accept()
	elif event.button() == Qt.LeftButton:
	    self.grabing = True
	    self.setCursor(QCursor(Qt.SizeAllCursor))
	    self.regionStart = (event.x(), event.y())


    def mouseMoveEvent(self, event):
	if self.selectingRegion and self.regionStart:
	    start = self.regionStart
	    stop = (event.x(), event.y())
	    event.accept()
	    self.selectionRect = (min([start[0], stop[0]]),
				  min([start[1], stop[1]]),
				  abs(start[0] - stop[0]),
				  abs(start[1] - stop[1]))
	    self.update()
	elif self.grabing:
	    start = self.mapToGLViewPort(*self.regionStart)
	    stop = self.mapToGLViewPort(event.x(), event.y())
	    self.regionStart = (event.x(), event.y())
	    event.accept()
	    self.lookAt(self.x + start[0] - stop[0],
			self.y + start[1] - stop[1])
	    

    def mouseReleaseEvent(self, event):
	if self.selectingRegion:
	    start = self.mapToGLViewPort(*self.regionStart)
	    stop = self.mapToGLViewPort(event.x(), event.y())
	    dx = .5*abs(start[0] - stop[0])
	    dy = .5*abs(start[1] - stop[1])

	    self.lookAt(min([start[0], stop[0]]) + dx,
			min([start[1], stop[1]]) + dy)
	    self.zoom = max([dx, dy])

	    event.accept()
	    self.unsetCursor()
	    self.selectingRegion = False
	    self.selectionRect = None
	    self.regionStart = None
	    
	    self.rezoom()
	elif self.grabing:
	    self.regionStart = False
	    self.grabing = False
	    self.unsetCursor()
	    event.accept()
	elif event.button() == Qt.RightButton:
	    self.showSelectedClusters(event.x(), event.y())


    def mouseDoubleClickEvent(self, event):
	self.showSelectedClusters(event.x(), event.y())


    def expandCluster(self, clust):
	# TODO: we lost who is s1 and who s2, that shoulb be fixed
	p1, p2 = clust
	g_s1, g_s2 =  [map(lambda x:["-","+"][self.s2_signs[x]] \
			   + self.revmapper[self.s2[x]],
			   range(p1[0]-1, p1[1])),
		       map(lambda x:["-","+"][self.s1_signs[x]] \
			   + self.revmapper[self.s1[x]],
			   range(p2[0]-1, p2[1]))]
	# TODO: make is less ugly
	return ("Cluster on %s from %d to %d\n"
		"        on %s from %d to %d\n\n"
		"on %s the genes are \n%s\n"
		"on %s the genes are \n%s\n") % ((self.s2_name,) \
						 + p1 + \
						 (self.s1_name,) \
						 + p2 + \
						 (self.s2_name,
						  g_s1,
						  self.s1_name,
						  g_s2,))
  

    def showSelectedClusters(self, x, y):
	x, y = self.mapToSequences(x, y)
	in_ci = filter(lambda clust:inRect(x, y,
					   clust[1][0]-1,
					   clust[0][0]-1,
					   clust[1][1]-1,
					   clust[0][1]-1),
		       self.filtered_ci)
	#pprint(in_ci)
	#msg = "\n======\n".join(map(self.expandCluster, in_ci))
	#print msg
	#print "================="
	if in_ci:
	    dia = DetailsGui(self)
	    #colormap = {}
	    for clust in in_ci:
		#colormap[clust] = None
		item = ClustListViewItem(dia.lst,
					 str(clust_area(clust)),
					 str(clust[1][1] - clust[1][0] + 1),
					 str(clust[0][1] - clust[0][0] + 1),
					 str(clust[1][0]),
					 str(clust[1][1]),
					 str(clust[0][0]),
					 str(clust[0][1]) )
		item.setCluster(clust)
	    #dia.detailTxt.setText(msg)
 	    #dia = QMessageBox("Clusters Found", msg, QMessageBox.Information,
	    #		    True, False, False, self)
	    #dia.setColormap(colormap)
	    dia.show()


    def keyPressEvent(self, event):
	if event.key() == event.Key_Plus:
	    self.zoomIn()
	    event.accept()

	if event.key() == event.Key_Minus:
	    self.zoomOut()
	    event.accept()

	if event.key() == event.Key_Left:
	    self.moveLeft()
	    event.accept()
	  
	if event.key() == event.Key_Right:
	    self.moveRight()
	    event.accept()

	if event.key() == event.Key_Up:
	    self.moveUp()
	    event.accept()

	if event.key() == event.Key_Down:
	    self.moveDown()
	    event.accept()

	if event.key() == event.Key_Home:
	    self.resetZoom()
	    event.accept()


    def selectRegion(self):
	self.setCursor(QCursor(Qt.CrossCursor))
	self.selectingRegion = True

    def resetZoom(self):
	self.zoom = DEFAULT_ZOOM
	self.lookAt(0.0, 0.0)
	self.rezoom()

    def setAlpha(self, val):
	self.alpha = val/100.0
	self.update()


    def makeGridDisplayList(self):
	self.gridDisplayList=glGenLists(1)
	glNewList(self.gridDisplayList,GL_COMPILE)
	
	l, r, t, b = self.glViewPortBox()
	w, h = len(self.s1)+1, len(self.s2)+1

	# choose the increment so that the grid is not rendrered as a
	# flat grey background
	min_inc = (r-l)/75.0
	step = max([1, int(math.ceil( min_inc * w / 2.0 ))])

	for i in range(w+1):
	    if i % step == 0:
		glBegin( GL_LINES )

		glVertex3f(2.0*(i)/w-1.0, -1.0, -0.1)
		glVertex3f(2.0*(i)/w-1.0,  1.0, -0.1)

		glEnd()


	min_inc = (t-b)/75.0
	step = max([1, int(math.ceil( min_inc * w / 2.0 ))])

	for i in range(h+1):
	    if i % step == 0:
		glBegin( GL_LINES )

		glVertex3f(-1.0, 2.0*(i)/h-1.0, -0.1)
		glVertex3f( 1.0, 2.0*(i)/h-1.0, -0.1)

		glEnd()
	glEndList()

      

    def makeClusterDisplayList(self):
	self.clusterDisplayList=glGenLists(1)
	glNewList(self.clusterDisplayList,GL_COMPILE)

	w, h = len(self.s1)+1, len(self.s2)+1

	z = FAR/2
	inc = z / len(self.filtered_ci)

	for p2, p1 in self.filtered_ci:
	    glBegin( GL_QUADS )
	    
	    glVertex3f(2.0*(p1[1])/w-1.0, 2.0*(p2[0]-1)/h-1.0, z)
	    glVertex3f(2.0*(p1[0]-1)/w-1.0, 2.0*(p2[0]-1)/h-1.0, z)
	    glVertex3f(2.0*(p1[0]-1)/w-1.0, 2.0*(p2[1])/h-1.0, z)
	    glVertex3f(2.0*(p1[1])/w-1.0, 2.0*(p2[1])/h-1.0, z)
	    z -= inc

	    glEnd()
	glEndList()
      

    def makeLabelTexture(self, id, text):
	if not HAS_PYGAME:
	    return
	
	glBindTexture(GL_TEXTURE_2D, id)

	# TODO: do that in init...
	pygame.font.init()

        fontfile = os.path.join(font_path(), FONTFILE)
	font = pygame.font.Font(fontfile, FONTSIZE)
	t_surf = font.render(text, True, FONTCOLOR)
	pygame.display.init()
	surf = pygame.Surface((TEX_SIZE, TEX_SIZE), pygame.SRCALPHA, 32)
	surf.fill([255, 255, 255, 0])
	surf.blit(t_surf, (0, 0))

	tex = pygame.image.tostring(surf, "RGBA", True)

	glBindTexture(GL_TEXTURE_2D, id)
	glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA,
		      surf.get_width(), surf.get_height(),
		      0, GL_RGBA, GL_UNSIGNED_BYTE, tex )

	glTexParameterf(GL_TEXTURE_2D,
			GL_TEXTURE_MAG_FILTER,
			GL_LINEAR)
	
	glTexParameterf(GL_TEXTURE_2D,
			GL_TEXTURE_MIN_FILTER,
			GL_LINEAR)

	#glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	return [1.0*t_surf.get_width()/TEX_SIZE,
		1.0*t_surf.get_height()/TEX_SIZE]


    def drawLabel(self, id, size, rot):
	if not HAS_PYGAME:
	    return
	
	glMatrixMode(GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	glOrtho( .0, 1.0, .0, 1.0, NEAR, FAR)

	glMatrixMode(GL_MODELVIEW)
	glPushMatrix()
	glLoadIdentity()

	w, h = size

	if rot:
	    glRotatef(rot, 0.0, 0.0, 1.0)
	    glTranslatef(0.0, -1.0, 0.0)

	    w_scale = 1.0*TEX_SIZE/self.height()
	    h_scale = 1.0*TEX_SIZE/self.width()

	else:
	    w_scale = 1.0*TEX_SIZE/self.width()
	    h_scale = 1.0*TEX_SIZE/self.height()
	    
	n_w = w*w_scale
	n_h = h*h_scale

	glBindTexture(GL_TEXTURE_2D, id)
	glEnable(GL_TEXTURE_2D)

	glBegin(GL_QUADS)

	glTexCoord2f(w, 1.0-h)
	glVertex3f((1.0+n_w)/2.0, 1.0-n_h, -1.0)

	glTexCoord2f(w, 1.0)
	glVertex3f((1.0+n_w)/2.0, 1.0, -1.0)

	glTexCoord2f(0.0, 1.0)
	glVertex3f((1.0-n_w)/2.0, 1.0, -1.0)

	glTexCoord2f(0.0, 1.0-h)
	glVertex3f((1.0-n_w)/2.0, 1.0-n_h, -1.0)

	glEnd()

	glDisable(GL_TEXTURE_2D)

	glMatrixMode(GL_MODELVIEW)
	glPopMatrix()

	glMatrixMode(GL_PROJECTION)
	glPopMatrix()
	
	glMatrixMode(GL_MODELVIEW)
		

	  
    def paintGL(self):
      	grid_color = [.85, .85, .85, .4]
	cluster_color = [.8, .2, .2, self.alpha]
	text_color = [.0, .0, .0, 1.0]
	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

	if not (self.gridDisplayList and self.clusterDisplayList):
	    return
        
	glLoadIdentity()
	glTranslatef( self.x, self.y, self.z)

	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	# grid
	glColor4f(*grid_color)
	glCallList(self.gridDisplayList)

	# clusters
	glColor4f(*cluster_color)
	glCallList(self.clusterDisplayList)


	# selection highlight
	if self.selectingRegion and self.selectionRect:
	    l, t, w, h = self.selectionRect

	    x0, y0 = self.mapToGLViewPort(l, t)
	    x1, y1 = self.mapToGLViewPort(l+w, t+h)

	    glColor4f(0.0, 0.0, 0.0, 1.0)
	    glBegin(GL_LINE_LOOP)
	    glVertex3f(-x0, -y1, 0.0)
	    glVertex3f(-x1, -y1, 0.0)
	    glVertex3f(-x1, -y0, 0.0)
	    glVertex3f(-x0, -y0, 0.0)
	    glEnd()

	    glColor4f(0.0, 0.0, 0.0, .1)
	    glBegin(GL_QUADS)
	    glVertex3f(-x0, -y1, 0.1)
	    glVertex3f(-x1, -y1, 0.1)
	    glVertex3f(-x1, -y0, 0.1)
	    glVertex3f(-x0, -y0, 0.1)
	    glEnd()

	# guides
	if self.guides:
	    glLoadIdentity()
	    l, r, t, b = self.glViewPortBox()
	    glColor4f(.2, .2, .7, .3)
	    glBegin(GL_LINES)
	    glVertex3f(l, (b+t)/2.0, .0)
	    glVertex3f(r, (b+t)/2.0, .0)

	    glVertex3f((l+r)/2.0, b, .0)
	    glVertex3f((l+r)/2.0, t, .0)
	    glEnd()


	# labels
	# TODO: we could compute the lables textures only once
	self.s1_label_size = self.makeLabelTexture(1, self.s1_name)
	self.s2_label_size = self.makeLabelTexture(2, self.s2_name)

	glColor4f(1.0, 1.0, 1.0, LABELS_ALPHA)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
	self.drawLabel(1, self.s1_label_size,  0.0)
	self.drawLabel(2, self.s2_label_size, 90.0)


    def glViewPortBox(self):
	pad = 0.0 # 0.05 * self.zoom
	w = h = (1.0 + pad)*self.zoom
	return(-w, w, h, -h)


    def rezoom(self):
	l, r, t, b = self.glViewPortBox()

	glViewport( 0, 0, self.width(), self.height() )
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho( l, r, t, b, NEAR, FAR )

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef( self.x, self.y, self.z)

	if self.ci:
	    self.makeGridDisplayList()

	self.emit(ZOOM_SIG, (l, r, t, b))
	self.emit(LOOK_SIG, (self.x, self.y))
	self.update()


    def mapToGLViewPort(self, x, y):
	l, r, t, b = self.glViewPortBox()

	n_x = self.x - (r-l)*(1.0*x/self.width() - .5)
	n_y = self.y + (b-t)*(1.0*y/self.height() - .5)
	return n_x, n_y


    def mapToSequences(self, x, y):
	w, h = len(self.s1)+1, len(self.s2)+1

	x, y = self.mapToGLViewPort(x, y)

	n_x = w - (x+1.0)/2.0 * w
	n_y = h - (y+1.0)/2.0 * h
      
	return int(n_x), int(n_y)
    

    def resizeGL(self, width, height):
	self.rezoom()


    def initializeGL(self):
	glShadeModel (GL_SMOOTH);
	glEnable(GL_CULL_FACE)

	glClearColor(1.0, 1.0, 1.0, 1.0)
	glClearDepth(1.0)

	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	
	glDisable(GL_DEPTH_TEST)
	glEnable(GL_BLEND)
    
	glEnable(GL_NORMALIZE)

	glEnable(GL_TEXTURE_2D)
	glShadeModel(GL_FLAT)


	if self.ci:
	    self.makeGridDisplayList()
	    self.makeClusterDisplayList()

