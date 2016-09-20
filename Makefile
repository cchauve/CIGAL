
ALL_UI=cigal/AboutDia.py cigal/CIViewGui.py cigal/ClustImgDia.py \
       cigal/DetailsDia.py cigal/DetailView.py

all: ${ALL_UI}

.PHONY: dist
dist: ${ALL_UI}
	python setup.py sdist --formats=gztar,zip

install:
	python setup.py install

clean:
	rm -r ${ALL_UI}

cigal/AboutDia.py: ui/aboutdia.ui
	pyuic ui/aboutdia.ui > cigal/AboutDia.py

cigal/CIViewGui.py: ui/civiewgui.ui
	pyuic ui/civiewgui.ui > cigal/CIViewGui.py

cigal/ClustImgDia.py: ui/clustimgdia.ui
	pyuic ui/clustimgdia.ui > cigal/ClustImgDia.py

cigal/DetailsDia.py: ui/detailsdia.ui
	pyuic ui/detailsdia.ui > cigal/DetailsDia.py

cigal/DetailView.py: ui/detailview.ui
	pyuic ui/detailview.ui > cigal/DetailView.py
