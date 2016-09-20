
                      C I G A L -- A L P H A
                      ======================

This software is a processor for clusters of conserved genes in two
genomes.  It consists of two programs: one command line tool to
compute conserved clusters and one graphical application to view them.

The only requirement to compute the cluster is a Python interpreter,
2.3 or better.  To install this software, just type

  make install

or 

 /path/to/python setup.py install

You don't need to install it, you can run the software from where you
extracted the package archive.

See the included fasta examples to get an idea of the required input
format.  You can launch a computation like this

  cd examples
  cigal ecoli-small.fas salty-small.fas out.cigal

After the computation you can view the clusters with the graphical
tool.  This part requires the Qt toolkit, the Python bindings for Qt,
a working OpenGL installation and pygame, a set of python bindings to
libsdl.  OpenGL in software mode (ie mesa software) is supported but
will probably be too slow for sequences of 1000 or more genes.  See
these links for the dependencies:

  http://www.trolltech.com/
  http://www.riverbankcomputing.co.uk/pyqt/
  http://www.pygame.org/
  http://www.libsdl.org/


To view your precomputed clusters, simply launch the viewer like that:

  cigalgui

or

  cigalgui out.cigal

The interface should be self explaining but do not despair if your all
lost, there will be documentation with the stable release.  Among the
non-obvious feature, you can use the arrows, HOME, + and - keys for
fast navigation, you can drag the cluster view with the left click and
see details for a cluster area (red block) with the right click.

Tip: disable filtering when you play with the parameter then re-enable
it, it will be faster.

This software is brought to you by the CGL at UQAM

  http://cgl.bioinfo.uqam.ca/



This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Genera l Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
