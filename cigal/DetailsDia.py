# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/detailsdia.ui'
#
# Created: dim jan 8 09:49:40 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15
#
# WARNING! All changes made in this file will be lost!


from qt import *


class DetailsDia(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("DetailsDia")


        DetailsDiaLayout = QVBoxLayout(self,11,6,"DetailsDiaLayout")

        self.lst = QListView(self,"lst")
        self.lst.addColumn(self.__tr("area"))
        self.lst.addColumn(self.__tr("s1 length"))
        self.lst.addColumn(self.__tr("s2 length"))
        self.lst.addColumn(self.__tr("s1 start"))
        self.lst.addColumn(self.__tr("s1 stop"))
        self.lst.addColumn(self.__tr("s2 start"))
        self.lst.addColumn(self.__tr("s2 stop"))
        self.lst.setAllColumnsShowFocus(1)
        self.lst.setShowSortIndicator(1)
        DetailsDiaLayout.addWidget(self.lst)

        layout25 = QHBoxLayout(None,0,6,"layout25")
        spacer6 = QSpacerItem(290,21,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout25.addItem(spacer6)

        self.textBtn = QPushButton(self,"textBtn")
        layout25.addWidget(self.textBtn)

        self.detailsBtn = QPushButton(self,"detailsBtn")
        layout25.addWidget(self.detailsBtn)

        self.okBtn = QPushButton(self,"okBtn")
        layout25.addWidget(self.okBtn)
        DetailsDiaLayout.addLayout(layout25)

        self.languageChange()

        self.resize(QSize(542,320).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okBtn,SIGNAL("clicked()"),self.accept)


    def languageChange(self):
        self.setCaption(self.__tr("Clusters Found!"))
        self.lst.header().setLabel(0,self.__tr("area"))
        self.lst.header().setLabel(1,self.__tr("s1 length"))
        self.lst.header().setLabel(2,self.__tr("s2 length"))
        self.lst.header().setLabel(3,self.__tr("s1 start"))
        self.lst.header().setLabel(4,self.__tr("s1 stop"))
        self.lst.header().setLabel(5,self.__tr("s2 start"))
        self.lst.header().setLabel(6,self.__tr("s2 stop"))
        self.textBtn.setText(self.__tr("text"))
        self.detailsBtn.setText(self.__tr("image"))
        self.okBtn.setText(self.__tr("&OK"))
        self.okBtn.setAccel(self.__tr("Alt+O"))


    def __tr(self,s,c = None):
        return qApp.translate("DetailsDia",s,c)
