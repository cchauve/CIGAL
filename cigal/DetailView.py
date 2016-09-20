# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/detailview.ui'
#
# Created: dim jan 8 09:49:41 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15
#
# WARNING! All changes made in this file will be lost!


from qt import *


class DetailView(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("DetailView")

        self.setSizeGripEnabled(1)

        DetailViewLayout = QVBoxLayout(self,11,6,"DetailViewLayout")

        self.detailTxt = QTextEdit(self,"detailTxt")
        DetailViewLayout.addWidget(self.detailTxt)

        Layout1 = QHBoxLayout(None,0,6,"Layout1")
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(Horizontal_Spacing2)

        self.okBtn = QPushButton(self,"okBtn")
        self.okBtn.setAutoDefault(1)
        self.okBtn.setDefault(1)
        Layout1.addWidget(self.okBtn)
        DetailViewLayout.addLayout(Layout1)

        self.languageChange()

        self.resize(QSize(394,237).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okBtn,SIGNAL("clicked()"),self.accept)


    def languageChange(self):
        self.setCaption(self.__tr("Cluster Text Record"))
        self.okBtn.setText(self.__tr("&OK"))
        self.okBtn.setAccel(QString.null)


    def __tr(self,s,c = None):
        return qApp.translate("DetailView",s,c)
