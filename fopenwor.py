# -*- coding: iso-8859-1 -*-
import sys
try:
    from osgeo import gdal
    from osgeo import osr
    from osgeo.gdalconst import *
except:
    import gdal
    import osr
    
import ConfigParser
import os, glob
import shutil
import csv
from ow_utils import *

from symbology import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from PyQt4.Qt import *

global findNext 
global tempLayer
global subtempLayer
global nProj4
global nProj4Infos

findNext = False
nProj4 = -1
tempLayer, subtempLayer ="", ""

class Ui_Dialog_OW(object):
    def __init__(self, iface):
        self.iface = iface
        
    def setupUi(self, Dialog):
        global nProj4Infos

        Dialog.setObjectName("DialogOW")
        Dialog.setMinimumSize(QtCore.QSize(728,540))
        Dialog.setMaximumSize(QtCore.QSize(728,540))
        Dialog.resize(728,500)

        self.masterLayout = QtGui.QVBoxLayout(Dialog)
        self.masterLayout.setObjectName("masterLayout")

        self.widget = QtGui.QWidget(Dialog)
        self.widget.setMinimumSize(QtCore.QSize(700, 70))
        self.widget.setMaximumSize(QtCore.QSize(700, 70))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(Dialog) 
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.labelImage = QtGui.QLabel(self.widget)
        self.labelImage.setMinimumSize(QtCore.QSize(50, 50))
        self.labelImage.setMaximumSize(QtCore.QSize(50, 50))
        self.labelImage.setGeometry(QtCore.QRect(10,15,50,50))

        myDefPath = getThemeIcon("selectplus.png")
        carIcon = QtGui.QImage(myDefPath)
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.labelImage.setObjectName("lblVersion")
        self.horizontalLayout.addWidget(self.labelImage)

        self.TxtFile = QtGui.QTextEdit(self.widget)
        self.TxtFile.setMinimumSize(QtCore.QSize(570, 40))
        self.TxtFile.setMaximumSize(QtCore.QSize(570, 40))
        self.TxtFile.setGeometry(QtCore.QRect(70,10,570,40))
        self.TxtFile.setAcceptRichText(False)
        self.TxtFile.setReadOnly(True)
        self.TxtFile.setObjectName("TxtFile")
        self.TxtFile.setPlainText("")
        self.horizontalLayout.addWidget(self.TxtFile)
        
        self.BOpenFile = QtGui.QPushButton(self.widget)
        self.BOpenFile.setMinimumSize(QtCore.QSize(50, 20))
        self.BOpenFile.setMaximumSize(QtCore.QSize(50, 20))
        self.BOpenFile.setGeometry(QtCore.QRect(650,10,50,20))
        self.BOpenFile.setObjectName("BOpenFile")
        self.horizontalLayout.addWidget(self.BOpenFile)

        self.labelprogressBar = QtGui.QLabel(self.widget)
        self.labelprogressBar.setMinimumSize(QtCore.QSize(70, 20))
        self.labelprogressBar.setMaximumSize(QtCore.QSize(70, 20))
        self.labelprogressBar.setGeometry(QtCore.QRect(70,50,70,20))
        self.labelprogressBar.setObjectName("labelprogressBar")
        

        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", QtCore.QVariant(0))
        self.progressBar.setMinimumSize(QtCore.QSize(160, 15))
        self.progressBar.setMaximumSize(QtCore.QSize(160, 15))
        self.progressBar.setGeometry(QtCore.QRect(130,55,160,15))
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet(
            """QProgressBar {border: 2px solid grey; border-radius: 5px; text-align: center;}"""
            """QProgressBar::chunk {background-color: #6C96C6; width: 20px;}"""
        )
        self.horizontalLayout.addWidget(self.progressBar)

        self.labelprogressBarL = QtGui.QLabel(self.widget)
        self.labelprogressBarL.setMinimumSize(QtCore.QSize(70, 20))
        self.labelprogressBarL.setMaximumSize(QtCore.QSize(70, 20))
        self.labelprogressBarL.setGeometry(QtCore.QRect(300,50,70,20))
        self.labelprogressBarL.setObjectName("labelprogressBarL")


        self.progressBarL = QtGui.QProgressBar(Dialog)
        self.progressBarL.setProperty("value", QtCore.QVariant(0))
        self.progressBarL.setMinimumSize(QtCore.QSize(280, 15))
        self.progressBarL.setMaximumSize(QtCore.QSize(280, 15))
        self.progressBarL.setGeometry(QtCore.QRect(360,55,0,15))
        self.progressBarL.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBarL.setTextVisible(True)
        self.progressBarL.setObjectName("progressBarL")
        self.progressBarL.setStyleSheet(
            """QProgressBar {border: 2px solid grey; border-radius: 5px; text-align: center;}"""
            """QProgressBar::chunk {background-color: #6C96C6; width: 10px; margin: 0.5px;}"""
        )
        self.horizontalLayout.addWidget(self.progressBarL)
       

        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setMinimumSize(QtCore.QSize(690, 440))
        self.tabWidget.setMaximumSize(QtCore.QSize(690, 440))
        self.tabWidget.setGeometry(QtCore.QRect(10, 80, 690,440))

        self.tab1 = QtGui.QWidget()
        self.tab1.setObjectName("tab1")
        self.tab1.setMinimumSize(QtCore.QSize(650, 440))
        self.tab1.setMaximumSize(QtCore.QSize(650, 440))
        self.gridLayout1 = QtGui.QVBoxLayout(self.tab1)
        self.gridLayout1.setObjectName("gridLayout1")

        self.sgridLayout10 = QtGui.QHBoxLayout(self.tab1)
        self.sgridLayout10.setObjectName("sgridLayout10")

        #******************************************
        # CHOIX DE LA CARTE A CHARGER             :
        #******************************************
        self.labelMap = QtGui.QLabel(self.tab1)
        self.labelMap.setMinimumSize(QtCore.QSize(120, 20))
        self.labelMap.setMaximumSize(QtCore.QSize(120, 20))
        self.labelMap.setGeometry(QtCore.QRect(10,20,120,20))
        self.labelMap.setObjectName("labelMap")
        self.sgridLayout10.addWidget(self.labelMap)

        self.comboMap = QtGui.QComboBox(self.tab1)
        self.comboMap.setMinimumSize(QtCore.QSize(140, 20))
        self.comboMap.setMaximumSize(QtCore.QSize(140, 20))
        self.comboMap.setGeometry(QtCore.QRect(125, 20, 140,20))
        self.comboMap.setObjectName("comboMap")
        self.sgridLayout10.addWidget(self.comboMap)

        
        #******************************************
        # CONTENU DES CARTES A CHARGER            :
        #******************************************
        self.ViewTAB = QtGui.QListView(self.tab1)
        self.ViewTAB.setObjectName("ViewTAB")
        self.ViewTAB.setMinimumSize(QtCore.QSize(360, 90))
        self.ViewTAB.setMaximumSize(QtCore.QSize(360, 90))
        self.ViewTAB.setGeometry(QtCore.QRect(280,20,360, 90))
        self.sgridLayout10.addWidget(self.ViewTAB)

        #******************************************
        # ETIQUETTES INFORMATIONS COUCHE / CARTE  :
        #******************************************
        self.labelInfoLayerMap = QtGui.QLabel(self.tab1)
        self.labelInfoLayerMap.setMinimumSize(QtCore.QSize(140, 20))
        self.labelInfoLayerMap.setMaximumSize(QtCore.QSize(140, 20))
        self.labelInfoLayerMap.setGeometry(QtCore.QRect(10,100,140,20))
        self.labelInfoLayerMap.setObjectName("labelInfoLayerMap")
        self.sgridLayout10.addWidget(self.labelInfoLayerMap)

        #******************************************
        # CARACTERISTIQUES DES COUCHES DE LA CARTE:
        #****************************)**************
        self.ViewLAYERMAP = QtGui.QTextEdit(self.tab1)
        self.ViewLAYERMAP.setUndoRedoEnabled(False)
        self.ViewLAYERMAP.setReadOnly(True)
        self.ViewLAYERMAP.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.ViewLAYERMAP.setObjectName("ViewLAYERMAP")
        self.ViewLAYERMAP.setMinimumSize(QtCore.QSize(630, 100))
        self.ViewLAYERMAP.setMaximumSize(QtCore.QSize(630, 100))
        self.ViewLAYERMAP.setGeometry(QtCore.QRect(10,120,630, 100))
        self.sgridLayout10.addWidget(self.ViewLAYERMAP)

        #******************************************
        # LABEL MISE EN PAGE + CHOIX MISE EN PAGE :
        #******************************************
        self.labelComposer = QtGui.QLabel(self.tab1)
        self.labelComposer.setMinimumSize(QtCore.QSize(100, 20))
        self.labelComposer.setMaximumSize(QtCore.QSize(100, 20))
        self.labelComposer.setGeometry(QtCore.QRect(10,230,100,20))
        self.labelComposer.setObjectName("labelComposer")
        self.sgridLayout10.addWidget(self.labelComposer)

        self.comboComposer = QtGui.QComboBox(self.tab1)
        self.comboComposer.setMinimumSize(QtCore.QSize(140, 20))
        self.comboComposer.setMaximumSize(QtCore.QSize(140, 20))
        self.comboComposer.setGeometry(QtCore.QRect(125, 230, 140,20))
        self.comboComposer.setObjectName("comboComposer")
        self.sgridLayout10.addWidget(self.comboComposer)

        #******************************************
        # ETIQUETTES BLOC OPTIONS                 :
        #******************************************
        self.labelOptions = QtGui.QLabel(self.tab1)
        self.labelOptions.setMinimumSize(QtCore.QSize(140, 20))
        self.labelOptions.setMaximumSize(QtCore.QSize(140, 20))
        self.labelOptions.setGeometry(QtCore.QRect(10,260,140,20))
        self.labelOptions.setObjectName("labelInfoLayerMap")
        self.sgridLayout10.addWidget(self.labelOptions)

        #******************************************
        # OPTIONS                                 :
        #******************************************
        self.CkBx_Surcharge = QtGui.QCheckBox(self.tab1)
        self.CkBx_Surcharge.setGeometry(QtCore.QRect(125,260,300,25))
        self.CkBx_Surcharge.setObjectName("CkBx_Surcharge")
        self.sgridLayout10.addWidget(self.CkBx_Surcharge)

        self.CkBx_ForceUnitsMap = QtGui.QCheckBox(self.tab1)
        self.CkBx_ForceUnitsMap.setGeometry(QtCore.QRect(125,280,300,25))
        self.CkBx_ForceUnitsMap.setObjectName("CkBx_ForceUnitsMap")
        self.sgridLayout10.addWidget(self.CkBx_ForceUnitsMap)

        self.CkBx_UniProj = QtGui.QCheckBox(self.tab1)
        self.CkBx_UniProj.setGeometry(QtCore.QRect(125,305,120,25))
        self.CkBx_UniProj.setObjectName("CkBx_UniProj")
        self.sgridLayout10.addWidget(self.CkBx_UniProj)

        self.TxtProjMap = QtGui.QTextEdit(self.tab1)
        self.TxtProjMap.setMinimumSize(QtCore.QSize(390, 25))
        self.TxtProjMap.setMaximumSize(QtCore.QSize(390, 25))
        self.TxtProjMap.setGeometry(QtCore.QRect(250, 305 , 390, 25))
        self.TxtProjMap.setAcceptRichText(False)
        self.TxtProjMap.setReadOnly(True)
        self.TxtProjMap.setEnabled(False)
        self.TxtProjMap.setObjectName("TxtProjMap")
        self.TxtProjMap.setPlainText("")
        self.sgridLayout10.addWidget(self.TxtProjMap)


        zProjTemp = self.iface.mapCanvas().mapRenderer().destinationCrs()
        nProj4 = QString(zProjTemp.toProj4())
        destinationCRS = QgsCoordinateReferenceSystem()
        destinationCRS.createFromProj4(nProj4)

        self.buttonProjMap = QtGui.QPushButton(self.tab1)
        self.buttonProjMap.setMinimumSize(QtCore.QSize(100, 20))
        self.buttonProjMap.setMaximumSize(QtCore.QSize(100, 20))
        self.buttonProjMap.setGeometry(QtCore.QRect(10, 305, 140,20))
        self.buttonProjMap.setObjectName("buttonProjMap")
        self.sgridLayout10.addWidget(self.buttonProjMap)

        
        self.CkBx_NoZoomStep = QtGui.QCheckBox(self.tab1)
        self.CkBx_NoZoomStep.setGeometry(QtCore.QRect(125,330,200,25))
        self.CkBx_NoZoomStep.setObjectName("CkBx_NoZoomStep")
        self.sgridLayout10.addWidget(self.CkBx_NoZoomStep)

        self.CkBx_InterActiveMode = QtGui.QCheckBox(self.tab1)
        self.CkBx_InterActiveMode.setGeometry(QtCore.QRect(125,355,200,25))
        self.CkBx_InterActiveMode.setObjectName("CkBx_InterActiveMode")
        self.sgridLayout10.addWidget(self.CkBx_InterActiveMode)


        #******************************************
        # BOUTON CHARGER CARTE ET MISE EN PAGE    :
        #******************************************
        self.buttonMap = QtGui.QPushButton(self.tab1)    
        self.buttonMap.setMinimumSize(QtCore.QSize(200, 30))
        self.buttonMap.setMaximumSize(QtCore.QSize(200, 30))
        self.buttonMap.setGeometry(QtCore.QRect(440, 380, 200,30))
        self.buttonMap.setObjectName("buttonMap")
        self.sgridLayout10.addWidget(self.buttonMap)
        self.tabWidget.addTab(self.tab1, "")

        #******************************************
        # ONGLET VUE MOTEUR OPENWOR               :
        #******************************************     
        self.tab2 = QtGui.QWidget()
        self.tab2.setObjectName("tab2")
        self.gridLayout2 = QtGui.QGridLayout(self.tab2)
        self.gridLayout2.setObjectName("gridLayout2")
 
        self.ViewLOG = QtGui.QTextEdit(self.tab2)
        self.ViewLOG.setUndoRedoEnabled(False)
        self.ViewLOG.setReadOnly(True)
        self.ViewLOG.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.ViewLOG.setObjectName("ViewLOG")
        self.gridLayout2.addWidget(self.ViewLOG)

        self.TreeView = QtGui.QTreeView(self.tab2)
        self.TreeView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.TreeView.setObjectName("TreeView")
    
        myPathIconvLine = getThemeIcon("vline.png") 
        myPathIconBranchMore = getThemeIcon("branch-more.png")
        myPathIconBranchEnd = getThemeIcon("branch-end.png") 
        myPathIconBranchClosed = getThemeIcon("branch-closed.png")
        myPathIconBranchOpen = getThemeIcon("branch-open.png")             

        self.TreeView.setStyleSheet(
            """QTreeView  {show-decoration-selected: 1;}"""
            """QTreeView::title {}"""
            """QTreeView::item  {border: 1px solid #d9d9d9; border-top-color: transparent; border-bottom-color: transparent;}"""
            """QTreeView::item:hover  {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1); border: 1px solid #bfcde4;}"""
            """QTreeView::item:selected  {border: 1px solid #567dbc;}"""
            """QTreeView::item:selected:active {background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);}"""
            """QTreeView::item:selected:!active  { background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);}"""
            """QTreeView::item {margin: 5px;}"""
            """QTreeView::branch:has-siblings:!adjoins-item  {border-image: url("""+myPathIconvLine+""") 0;}"""
            """QTreeView::branch:has-siblings:adjoins-item  {border-image: url("""+myPathIconBranchMore+""") 0;}"""
            """QTreeView::branch:!has-children:!has-siblings:adjoins-item  {border-image: url("""+myPathIconBranchEnd+""") 0;}"""
            """QTreeView::branch:has-children:!has-siblings:closed, QTreeView::branch:closed:has-children:has-siblings  {border-image: none; image: url("""+myPathIconBranchClosed+""");}"""
            """QTreeView::branch:open:has-children:!has-siblings,QTreeView::branch:open:has-children:has-siblings   { border-image: none; image: url("""+myPathIconBranchOpen+""");}"""
        )

        self.TreeView.setHeaderHidden(True)
        self.TreeView.setWordWrap(True)
        self.TreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout2.addWidget(self.TreeView)
        self.tabWidget.addTab(self.tab2, "")

   

        #******************************************
        # ONGLET DOCUMENT MAPINFO                 :
        #****************************************** 
        self.tab3 = QtGui.QWidget()
        self.tab3.setObjectName("tab3")
        self.gridLayout3 = QtGui.QGridLayout(self.tab3)
        self.gridLayout3.setObjectName("gridLayout3")
 
        self.ViewFILE = QtGui.QTextEdit(self.tab3)
        self.ViewFILE.setUndoRedoEnabled(False)
        self.ViewFILE.setReadOnly(True)
        self.ViewFILE.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.ViewFILE.setObjectName("ViewFILE")
        self.gridLayout3.addWidget(self.ViewFILE, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab3, "")


        #***************************************************
        # ONGLET RECHERCE DOCUMENT MAPINFO                 :
        #*************************************************** 
        self.tab4 = QtGui.QWidget()
        self.tab4.setObjectName("tab4")
        self.gridLayout4 = QtGui.QGridLayout(self.tab4)
        self.gridLayout4.setObjectName("gridLayout4")

        self.labelRep = QtGui.QLabel(self.tab4)
        self.labelRep.setMinimumSize(QtCore.QSize(200, 20))
        self.labelRep.setMaximumSize(QtCore.QSize(200, 20))
        self.labelRep.setGeometry(QtCore.QRect(0,0,200,20))
        self.labelRep.setObjectName("labelRep")
        self.gridLayout4.addWidget(self.labelRep)

        self.TxtRep = QtGui.QTextEdit(self.tab4)
        self.TxtRep.setMinimumSize(QtCore.QSize(660, 25))
        self.TxtRep.setMaximumSize(QtCore.QSize(660, 25))
        self.TxtRep.setGeometry(QtCore.QRect(0,0,660,25))
        self.TxtRep.setAcceptRichText(False)
        self.TxtRep.setReadOnly(True)
        self.TxtRep.setObjectName("TxtRep")
        self.TxtRep.setPlainText("")
        self.gridLayout4.addWidget(self.TxtRep)
        
        self.BDefineRep = QtGui.QPushButton(self.tab4)
        self.BDefineRep.setMinimumSize(QtCore.QSize(100, 20))
        self.BDefineRep.setMaximumSize(QtCore.QSize(100, 20))
        self.BDefineRep.setGeometry(QtCore.QRect(510,10,100,20))
        self.BDefineRep.setObjectName("BDefineRep")
        self.gridLayout4.addWidget(self.BDefineRep)

        self.ExeSearchFILE = QtGui.QPushButton(self.tab4)
        self.ExeSearchFILE.setMinimumSize(QtCore.QSize(100, 20))
        self.ExeSearchFILE.setMaximumSize(QtCore.QSize(100, 20))
        self.ExeSearchFILE.setGeometry(QtCore.QRect(560,10,100,20))
        self.ExeSearchFILE.setObjectName("ExeSearchFILE")
        self.gridLayout4.addWidget(self.ExeSearchFILE)

        self.labelSearchFILE = QtGui.QLabel(self.tab4)
        self.labelSearchFILE.setMinimumSize(QtCore.QSize(660, 20))
        self.labelSearchFILE.setMaximumSize(QtCore.QSize(660, 20))
        self.labelSearchFILE.setGeometry(QtCore.QRect(0,0,660,20))
        self.labelSearchFILE.setObjectName("labelSearchFILE")
        self.gridLayout4.addWidget(self.labelSearchFILE)        

        self.SearchFILE = QtGui.QListWidget(self.tab4)
        self.SearchFILE.setObjectName("SearchFILE")
        self.SearchFILE.setMinimumSize(QtCore.QSize(660, 260))
        self.SearchFILE.setMaximumSize(QtCore.QSize(660, 260))
        self.SearchFILE.setGeometry(QtCore.QRect(0,0, 660, 260))         
        self.gridLayout4.addWidget(self.SearchFILE)
        self.tabWidget.addTab(self.tab4, "")
    

        #******************************************
        # ONGLET WARNINGS                         :
        #****************************************** 
        self.tab5 = QtGui.QWidget()
        self.tab5.setObjectName("tab5")
        self.gridLayout5 = QtGui.QGridLayout(self.tab5)
        self.gridLayout5.setObjectName("gridLayout5")

        self.Warnings = QtGui.QTextEdit(self.tab5)
        self.Warnings.setUndoRedoEnabled(False)
        self.Warnings.setReadOnly(True)
        self.Warnings.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.Warnings.setObjectName("Warnings")
        self.gridLayout5.addWidget(self.Warnings, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab5, "")

        self.ImgWarnings = QtGui.QLabel(self.tab5)
        self.ImgWarnings.setMinimumSize(QtCore.QSize(165, 220))
        self.ImgWarnings.setMaximumSize(QtCore.QSize(165, 220))
        self.ImgWarnings.setGeometry(QtCore.QRect(480, 10, 165, 220))
        carIcon = QtGui.QImage(getThemeIcon("concepteur.png")) 
        self.ImgWarnings.setPixmap(QtGui.QPixmap.fromImage(carIcon))
        self.gridLayout5.addWidget(self.Warnings)

        self.FixeTxtLabel(Dialog)
        self.MakeWarnings()

        QtCore.QObject.connect(self.BOpenFile, SIGNAL("clicked()"), self.LoadWOR)
        QtCore.QObject.connect(self.buttonMap, SIGNAL("clicked()"), self.MakeMap)
        QtCore.QObject.connect(self.CkBx_UniProj, SIGNAL("clicked()"), self.FixeUniProjection)
        QtCore.QObject.connect(self.CkBx_InterActiveMode, SIGNAL("clicked()"), self.InterActiveMode)
        QtCore.QObject.connect(self.comboMap, SIGNAL("currentIndexChanged(QString)"), self.MakeListTables)
        QtCore.QObject.connect(self.buttonProjMap, SIGNAL("clicked()"), self.CallQgsProjectionSelector)
        QtCore.QObject.connect(self.ViewTAB, SIGNAL("doubleClicked(QModelIndex)"), self.ReturnInfosLayerMap)
        QtCore.QObject.connect(self.TreeView, SIGNAL("doubleClicked(QModelIndex)"), self.FixeInfosViewHTML)
        
        QtCore.QObject.connect(self.BDefineRep, SIGNAL("clicked()"), self.FixeREPSearchFILE)
        QtCore.QObject.connect(self.ExeSearchFILE, SIGNAL("clicked()"), self.DoREPSearchFILE)
        QtCore.QObject.connect(self.SearchFILE, SIGNAL("doubleClicked(QModelIndex)"), self.ChangeWOR)
        
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.TxtFile,self.BOpenFile)


        savefile = os.path.join(os.path.dirname(__file__),"savesession.ini")
        if os.path.exists(savefile):
           p = ConfigParser.ConfigParser()
           p.read(savefile)
           fileName = str(p.get('general','filename'))
           fileName = fileName.rstrip()

           ssurcharge = str(p.get('general','surcharge'))
           self.CkBx_Surcharge.setChecked((ssurcharge=="oui"))
           
           szoomstep = str(p.get('general','zoomstep'))
           self.CkBx_NoZoomStep.setChecked((szoomstep=="oui"))

           sinteractivemode = str(p.get('general','interactivemode'))
           self.CkBx_InterActiveMode.setChecked((sinteractivemode=="oui"))           

           zProjTemp = self.iface.mapCanvas().mapRenderer().destinationCrs()
           self.TxtProjMap.setText(str(zProjTemp.description()))
           nProj4 = int(zProjTemp.srsid())

           zTempo = str(zProjTemp.authid())
           zTempo.replace("EPSG:","") 
           nProj4Infos = str(zProjTemp.description()) + "|" + str(nProj4) + "|" +  zTempo.replace("EPSG:","") + "|" + QString(zProjTemp.toProj4())
           self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(0) 

           sprojunit = str(p.get('general','projunit'))
           self.CkBx_UniProj.setChecked((sprojunit=="oui")) 
           self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(1) if sprojunit=="oui" else self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(0)

           sforceUnitsMap = str(p.get('general','forceunitsmap'))
           self.CkBx_ForceUnitsMap.setChecked((sforceUnitsMap=="0"))

           if os.path.exists(fileName):
              self.TxtFile.setPlainText(fileName)
              mystr = AnalyseWOR(self, fileName)           

        if QSettings().value("Qgis/use_symbology_ng", QVariant("")).toBool() == False : QSettings().setValue("Qgis/use_symbology_ng", QVariant(True)) 
           
        MajCtrlButtonMap(self)
        VerifSVGPaths()

        zPath = os.path.dirname(__file__)
        zPath = zPath.replace("\\","/")        
        zPathDir = os.path.join(zPath + "/myworks/")
        if not os.path.exists(zPathDir) : os.makedirs(zPathDir)


    def FixeREPSearchFILE(self):
        InitDir = os.path.dirname(__file__) if self.TxtFile.toPlainText()=="" else os.path.dirname(str(self.TxtFile.toPlainText())) 
        inputDir = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier pour la recherche", InitDir, QFileDialog.ShowDirsOnly|QFileDialog.DontResolveSymlinks)
        if inputDir.isEmpty(): return
        self.TxtRep.setPlainText(inputDir)

    def DoREPSearchFILE(self):
        zRep = self.TxtRep.toPlainText()
        if zRep == "":  QMessageBox.information(None,"Fonction de recherche", "Aucun dossier à analyser !")
        else :
            if os.path.exists(zRep) :
               zRep = str(CorrigePath(zRep))
               zRep = zRep.replace("\\","/")
               self.SearchFILE.clear()
               QApplication.setOverrideCursor( QCursor( Qt.WaitCursor ) )
               listdirectory(self, zRep.encode("utf-8"))
               self.labelSearchFILE.setText(str(self.SearchFILE.count()) + " résultat(s).")
               QApplication.restoreOverrideCursor()

    def ChangeWOR(self):
        zFile = self.SearchFILE.currentItem().text()
        if zFile != "" :
           self.TxtFile.setPlainText(zFile)
           mystr = AnalyseWOR(self, zFile)
           MajCtrlButtonMap(self)
        
 
    def CallQgsProjectionSelector(self):
         global nProj4
         global nProj4Infos
         
         dialog = SRSDialog() 
         if dialog.exec_():
            nProj4Infos = str(dialog.epsg())
            lInfosProj4 = nProj4Infos.split("|")
            self.TxtProjMap.setText(str(lInfosProj4[0]))
            nProj4 = int(lInfosProj4[2]) 
            self.FixenProj4(lInfosProj4[3])


    def LoadWOR(self):
        InitDir = os.path.dirname(__file__) if self.TxtFile.toPlainText()=="" else os.path.dirname(str(self.TxtFile.toPlainText()))
        fileName = QFileDialog.getOpenFileName(None,QString.fromLocal8Bit("Document MapInfo :"),InitDir,"*.wor")
        if fileName.isNull(): return
        else:
           self.TxtFile.setPlainText(fileName)
           mystr = AnalyseWOR(self, fileName)
           MajCtrlButtonMap(self)

    
    def FindComposer(self, iMap):
        self.comboComposer.clear()
        self.comboComposer.addItem("Aucune mise en page")

        zKey = "MAP"+str(iMap)
        refTitle = ""
        if tMap.has_key(zKey):
           zSTR = tMap[zKey].split("|")
           refTitle = zSTR[0]
      
        for key in tComposer.keys():
            findIndex = -1 
            zSTR = tComposer[key].split("|")
            for i in range(len(zSTR)):
                nSTR = str(zSTR[i])
                if nSTR.find("Title")!=-1:
                    
                   zMap = 'Carte' if len(tMap) == 1 or (self.comboMap.currentIndex()+1 == 1) else 'Carte:'+str(self.comboMap.currentIndex()+1)
                     
                   nSTR = NetStrInfos(nSTR, True, True, False, False, ("Title ","'"))
                   nSTR = nSTR.split(" ") 
                   if nSTR[len(nSTR)-1]==zMap:
                      tempo = str(key).replace("COMPOSER","")
                      findIndex = int(tempo)
                      break                       
            
            if findIndex !=-1: self.comboComposer.addItem("Mise en Page "+str(findIndex)) 

        self.comboComposer.addItem("Mise en Page OpenWor")
        self.comboComposer.setCurrentIndex(0)


    def MakeListTables(self):
        global tMap
        global tLayer

        if len(tMap)>0 :
           iMap = self.comboMap.currentIndex()
           
           if tMap.has_key('MAP'+str(iMap)):
               ic='MAP'+str(iMap)
               cCarte = str(tMap[ic])
               tempo = cCarte.split("|")
               layero = ""

               for i in range(len(tempo)):
                   stempo = NetStrInfos(tempo[i], True, False, False, False, ())
                   x = stempo.upper()
                   if x.startswith("POSITION"): break
                   else : layero = layero + str(tempo[i])
                
               layero = NetStrInfos(layero, False, True, False, False, ("Map From", "Map from", "MAP FROM","|"))
               ssLayer = layero.split(",")

               nTAB = QStringList()
               for i in range(len(ssLayer)):
                   nLAYER = NetStrInfos(ssLayer[i], True, True, False, False, (")"))
                   if nLAYER.upper().find("GROUPLAYER")==-1: nTAB <<  nLAYER

               self.modele = QStringListModel(nTAB)
               self.ViewTAB.setModel(self.modele)
               self.ViewTAB.setSelectionMode(QAbstractItemView.SingleSelection)
               self.ViewTAB.setEditTriggers(QAbstractItemView.NoEditTriggers)
               self.ViewLAYERMAP.clear()
               self.FindComposer(iMap)  


    def FixeInfosViewHTML(self):
               global findNext 
               zItem = self.TreeView.model().itemFromIndex(self.TreeView.currentIndex())
               zInfos = zItem.text()
               #QTextCursor.Start #QTextCursor.End #QTextCursor.PreviousCharacter #QTextCursor.NextCharacter
               self.ViewLOG.moveCursor(QTextCursor.Start) if not findNext else self.ViewLOG.moveCursor(QTextCursor.NextCharacter)
               findNext = True if (self.ViewLOG.find(str(zInfos))) else False
               

    def ReturnInfosLayerMap(self):                    
               selection = self.ViewTAB.selectionModel()
               indexElementSelectionne = int(selection.currentIndex().row())+1
               global tMap
               if len(tMap)>0 :
                  iMap = self.comboMap.currentIndex()
                  MyKey = 'MAP'+ str(iMap) + ".LAYER" + str(indexElementSelectionne)
                  if tLayerMap.has_key(MyKey):
                     self.ViewLAYERMAP.clear()   
                     self.ViewLAYERMAP.setText(str(tLayerMap[MyKey]))    

    def MakeMap(self):
        global tMap
        if len(tMap)>0 :
           iMap = self.comboMap.currentIndex()
           if tMap.has_key('MAP'+str(iMap)): MakeMapCanvas(self, iMap)

           zKey = NetStrInfos(str(self.comboComposer.currentText()), True, True, False, False,())
           if zKey != "Aucune mise en page": 
               zKey = zKey.replace("Mise en Page ","")
               if zKey == "OpenWor": MakeComposer(self, -1, "")
               elif tComposer.has_key("COMPOSER"+str(zKey)): MakeComposer(self, int(zKey), tComposer["COMPOSER"+str(zKey)])

    def InterActiveMode(self):
        if self.CkBx_InterActiveMode.isChecked(): mystr = AnalyseWOR(self, self.TxtFile.toPlainText()) 

    def FixenProj4(self, theProj):
        destinationCRS = QgsCoordinateReferenceSystem()
        destinationCRS.createFromProj4(QString(theProj))
        self.iface.mapCanvas().mapRenderer().setDestinationCrs(destinationCRS) 
        self.iface.mapCanvas().setMapUnits(destinationCRS.mapUnits()) 
        self.iface.mapCanvas().updateScale()

    def FixeUniProjection(self):
        self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(1) if self.CkBx_UniProj.isChecked() else  self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(0) 


    def FixeTxtLabel(self, Dialog):
        Dialog.setWindowTitle("Outil OPENWOR 1.9")
        self.BOpenFile.setText("...")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), "Options de restitution")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab2), "Moteur OPENWOR")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab3), "Document en entrée")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab4), "Recherche de documents")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab5), "Attention !")
        self.labelMap.setText("Carte à  représenter :")
        self.labelInfoLayerMap.setText("Informations de la couche :")
        self.labelComposer.setText("Mise en page :")
        self.labelOptions.setText("Options :")        
        self.CkBx_Surcharge.setText("Surcharger la session")
        self.buttonProjMap.setText("Projections ...")        
        self.CkBx_UniProj.setText("Projection unique")
        self.CkBx_ForceUnitsMap.setText("Forcer des unités cartes")
        self.CkBx_NoZoomStep.setText("Ignorer les seuils de zoom")
        self.CkBx_InterActiveMode.setText("Activer le mode interactif")
        self.buttonMap.setText("Charger la carte et la mise en page")        
        self.labelprogressBar.setText("Couche(s) :")   
        self.labelprogressBarL.setText("Analyse(s) :")

        self.labelRep.setText("Répertoire de recherche :")
        self.BDefineRep.setText("Sélection ...")
        self.ExeSearchFILE.setText("Rechercher")
        self.labelSearchFILE.setText("0 résultat(s).")


    def MakeWarnings(self):
        zPath = os.path.dirname(__file__)
        zPath = zPath.replace("\\","/")+"/warnings.htm"
        if os.path.exists(zPath) :
            f = QFile(zPath)
            f.open(QFile.ReadOnly|QFile.Text)
            istream = QTextStream(f)
            self.Warnings.setHtml(istream.readAll())
            f.close()
 


class SRSDialog(QDialog): 
       def __init__(self): 
         QDialog.__init__(self) 
         layout = QVBoxLayout(self) 
         self.selector = QgsProjectionSelector(self) 
         buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close) 
         self.connect(buttonBox, SIGNAL("accepted()"), self.accept) 
         self.connect(buttonBox, SIGNAL("rejected()"), self.reject) 
         layout.addWidget(self.selector) 
         layout.addWidget(buttonBox) 
         self.setLayout(layout) 
  
       def epsg(self):
         return  str(self.selector.selectedName()) + "|" + str(self.selector.selectedCrsId()) + "|" + str(self.selector.selectedEpsg()) + "|" + str(self.selector.selectedProj4String()) 


#-------------------------------------
# BLOC Mise en conformité bouton CARTE
#-------------------------------------
def MajCtrlButtonMap(self):
        global tMap
        global tLayer

        if QString(self.TxtFile.toPlainText()) == "" :
           self.labelMap.setText("Aucune carte :")
           self.buttonMap.setEnabled(False)
           return

        if len(tMap)==0 :
           self.labelMap.setText("Aucune carte :")
           self.buttonMap.setEnabled(False)
        else : 
           self.labelMap.setText("Carte à représenter :") if len(tMap)==1 else self.labelMap.setText("Cartes à représenter :")
           self.buttonMap.setEnabled(True) if len(tLayer)!=0 else self.buttonMap.setEnabled(False)


    
#-----------------------------------
# BLOC Analyse WOR ...
#-----------------------------------
def AnalyseWOR(self, nFile):
    global tLayer
    global uLayer

    mywor = open(nFile, 'r')
    mylistWOR = mywor.readlines()
    mywor.close()

    subtempLayer = ""
    tempLayer = "<br><h3><font color='#0000ff'>"+str(nFile)+"</font></h3>"
    tempLayer = tempLayer + "<table width='100%' border=0.5px>"
    tempLayer = tempLayer + "<tr bgcolor='#ccc'><td>Ressource : </td><td align='center'>Disponible</td><td width='75%'>URI</td></tr>"
    
    #remise à zéro des tableaux associatifs
    InitAllTableau(self)

    mytextfile, iLayer = "", 0
    nDir = CorrigePath(os.path.dirname(str(nFile)))
    
    zDim = int(len(mylistWOR))
    if zDim == 0 : zDim = 1
    self.progressBarL.setValue(0)


    for k in range(len(mylistWOR)):    
        line = mylistWOR[k]
        astring = str(QString.fromLocal8Bit(mylistWOR[k]))
        mytextfile = mytextfile + astring

        #Progression de l'analyse  
        zPercent = int(100 * float(float(k)/zDim))
        self.progressBarL.setValue(zPercent)
        
        if astring.upper().startswith('OPEN TABLE'): 
           iLayer=iLayer+1
           lst = astring.rsplit("\"")

           nTable = NetStrInfos(lst[1], False, False, False, False, ("'")) 
           nTable = nTable.replace("\\","/")
          
           tempoALIAS = str(lst[2])
           theTest = NetStrInfos(tempoALIAS, True, True, True, False, ())

           if nTable.upper().rfind(".TAB",len(nTable)-4)==-1: nTable=nTable+".TAB"

           if theTest == "INTERACTIVE":
              tempoALIAS = " AS " +  os.path.splitext(os.path.basename(str(nTable)))[0]
              #Il faut rechercher la vraie ressource !!! Table logique
              nTable = GetAdress(nTable, nDir)
              nRessource = GetRessourceFile(nTable)
              if nRessource != "": nTable = nRessource 
                 
           slst, nTable = tempoALIAS.split(), GetAdress(nTable, nDir)

           if nTable == "" and theTest and (self.CkBx_InterActiveMode.isChecked()):
              zCible = str(lst[1])
              QMessageBox.information(None, "Avertissement chargement : " , "La table <b>[" + zCible +"]</b> n'a pas été localisée.<br>Veuillez indiquer le chemin pour cette table.<br>A défaut, elle sera <b><font color='#ff0000'>exclue</font></b> du document restitué.")
              InitDir = os.path.dirname(__file__) if self.TxtFile.toPlainText()=="" else os.path.dirname(str(self.TxtFile.toPlainText()))
              fileName = QFileDialog.getOpenFileName(None,QString.fromLocal8Bit("Table MapInfo : ["+ zCible +"]"),InitDir,"*.tab")
              if not fileName.isNull():
                 zFile = str(os.path.basename(str(fileName)))
                 if zCible.upper().rfind(".TAB",len(zCible)-4)==-1: zCible=zCible+".TAB"
                 if zFile.upper() == zCible.upper() or zFile.upper() == os.path.basename(zCible.upper()): nTable = fileName
         
           
           if nTable!="":
              tempLayer = tempLayer+"<tr><td>Fichier num."+str(iLayer)+"</td><td align='center'>Ok</td><td><font color='#00ff00'>"+str(line)+"</font></td></tr>" 
              nTypeTable = str(GetTypeTable(nTable)) 
              nTypeTable = nTypeTable.upper()

              if nTypeTable == "NATIVE" : tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTable.replace("\"",""))
              elif nTypeTable == "SHAPEFILE" :
                 nTableRaster = GetRasterFile(nTable, True, False)
                 if nTableRaster!="": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTableRaster.replace("\"",""))
              elif nTypeTable == "XLS" :
                 nTableRaster = GetRasterFile(nTable, False, True)
                 if nTableRaster!="": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTableRaster.replace("\"","")) 
              elif nTypeTable == "RASTER" :
                 nTableRaster = GetRasterFile(nTable, False, False)
                 if nTableRaster!="": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTableRaster.replace("\"",""))
              elif nTypeTable == "WMS" :
                 nTableRaster = GetRasterFile(nTable, False, False)
                 if nTableRaster!="": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTableRaster.replace("\"",""))
              elif nTypeTable == "ASCII" :   
                 nTableRaster = GetRasterFile(nTable, False, True)
                 if nTableRaster!="": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTableRaster.replace("\"",""))
           else:
              tempLayer = tempLayer+"<tr><td>Fichier num."+str(iLayer)+"</td><td align='center'>Ko</td><td><b><font color='#ff0000'>"+str(line)+"</font></b></td></tr>" 
               
        elif astring.upper().startswith('SELECT'):
              nstr = astring.replace("\"","'")
              nstr = nstr.rstrip("\n")
              k = MaketSelect(self, mylistWOR, nstr, k)

        elif astring.upper().startswith('ADD COLUMN'):
              nstr = astring.replace("\"","'")
              nstr = nstr.rstrip("\n")
              k = MaketJoin(self, mylistWOR, nstr, k)
            
        elif astring.upper().startswith('MAP FROM'):
              nstr = astring.replace("\"","'")
              nstr = nstr.rstrip("\n")
              k = MaketMap(self, mylistWOR, nstr, k)

        elif astring.upper().startswith('BROWSE *'):
              nstr = astring.replace("\"","'")
              nstr = nstr.rstrip("\n")
              k = MaketBrowse(self, mylistWOR, nstr, k)    
 
        elif astring.upper().startswith('LAYOUT'): #'SET WINDOW FRONTWINDOW() PRINTER') :
              nstr = astring.replace("\"","'")
              nstr = nstr.rstrip("\n")
              k = MaketComposer(self, mylistWOR, nstr, k)
              
        else:
              pass

    ReOrgtLayerMapAna()
    
    #On alimente les deux onglets de restitution des informations du document en entrée
    MakeHTMLView(self, tempLayer, subtempLayer)
    MakeTreeView(self)
    #On alimente l'onglet "document en entrée"
    self.ViewFILE.setText(mytextfile)

    self.comboMap.clear()
    if len(tMap)>0 :
       for i in range(len(tMap)): self.comboMap.addItem('Carte '+str(i))
       self.comboMap.setCurrentIndex(0)
    self.progressBar.setValue(0)
    self.progressBarL.setValue(0)
    return tempLayer

#-----------------------------------------------------------------
#FONCTIONS DE CONSTRUCTION DES TABLEAUX OPENWOR 
# - 
#-----------------------------------------------------------------
def InitAllTableau(self):
    global tLayer
    global uLayer
    global tComposer
    global tBrowse    
    global tMap
    global tLayerMap
    global tLayerMapAna
    global tSelect
    global tJoin
    global tGroupLayer
    tLayer = {}
    uLayer = {}
    tComposer = {}
    tBrowse = {}
    tMap = {}    
    tLayerMap = {}
    tLayerMapAna = {}
    tSelect = {}
    tJoin = {}
    tGroupLayer = {}
  
    
def MaketMap(self, zlistWOR, Rac, wpos):
    global tMap
    tpos = -1    
    zMap = Rac
    if wpos == (len(zlistWOR)-1): return wpos+1    
    for mpos in range(wpos+1, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[mpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if mpos > tpos :
            if x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or  x.startswith('SET LEGEND') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
                 break
            elif x.startswith('LAYER') :
                 indexMap = len(tMap)
                 tpos = MaketLayerMap(self, zlistWOR, mpos, indexMap)
            elif x.startswith('GROUPLAYER') :
                 indexMap = len(tMap)
                 tpos = MaketGroupLayer(self, zlistWOR, mpos, indexMap)                
            else :
               nstr = astring.replace("\"","'")
               nstr = nstr.rstrip("\n")
               zMap = zMap + "|" + nstr
    indexMap = len(tMap)
    tMap['MAP'+str(indexMap)] = zMap
    return mpos


def MaketLayerMap(self, zlistWOR, wpos, indexMap):
    global tLayerMap
    global tLayerMapAna
    iLayerMap, iLayerMapAna, iC  = 1, 0, 0
    zLayerMap, zKey = "", ""
    if wpos == (len(zlistWOR)-1): return wpos+1
    for lpos in range(wpos, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[lpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('GROUPLAYER') or x.startswith('LAYOUT') or  x.startswith('SET LEGEND') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('BROWSE *') or x.startswith('MAP FROM') or x.startswith('DIM WORKSPACEMAXIMIZEDWINDOW') or x.startswith('SET COORDSYS') or lpos==(len(zlistWOR)-1): 
           tzLayerMap = zLayerMap.split("|[LAYER]|") 

           for k in range(1,len(tzLayerMap)):
               zTempo = tzLayerMap[k]
               y = zTempo.upper()
               findLabel, findGlobal = False, False
               if y.find("LABEL")!=-1 or y.find("DISPLAY GRAPHIC")!=-1 or y.find("DISPLAY GLOBAL")!=-1  or y.find("INFLECT")!=-1: findLabel = True
               if y.find("GLOBAL")!=-1 or y.find("DISPLAY VALUE")!=-1: findGlobal = True
               if not findLabel:
                   if findGlobal: iLayerMapAna, iC = iLayerMapAna + 1, iC + 1
                   else: iLayerMap, iLayerMapAna, iC = iLayerMap + 1 , 0, 0
               if not findLabel:
                   if findGlobal:
                      zKey = 'MAP'+str(indexMap)+".LAYER"+str(iLayerMap)+"_"+ str(iLayerMapAna)
                      tLayerMapAna[zKey] = zTempo
                   else:
                      zKey = 'MAP'+str(indexMap)+".LAYER"+str(iLayerMap) 
                      tLayerMap[zKey] = zTempo
               else:    
                   zKey = 'MAP'+str(indexMap)+".LAYER"+str(iLayerMap)
                   tLayerMap[zKey] = zTempo
               if findLabel :
                   iLayerMap+= 1
                   iLayerMapAna, iC = 0, 0
           return lpos-1
        elif x.startswith('LAYER') : zLayerMap = zLayerMap + "|[LAYER]|" + x
        else:
             nstr = astring.replace("\"","'")
             nstr = nstr.rstrip("\n")
             zLayerMap = zLayerMap + "|" + nstr
    return lpos

def MaketGroupLayer(self, zlistWOR, wpos, indexMap):
    global tGroupLayer
    zGroupLayer, zKey = "", ""
    if wpos == (len(zlistWOR)-1): return wpos+1
    for gpos in range(wpos, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[gpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYER') or x.startswith('LAYOUT') or x.startswith('SET WINDOW FRONTWINDOW() TITLE')  or x.startswith('ADD COLUMN') or x.startswith('SELECT') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
           tzGroupLayer = zGroupLayer.split("|[GROUPLAYER]|")
           for k in range(1,len(tzGroupLayer)):
               tGroupLayer['GROUPLAYER'+str(len(tGroupLayer))] = tzGroupLayer[k]
           return gpos-1
        elif x.startswith('GROUPLAYER') : zGroupLayer = zGroupLayer + "|[GROUPLAYER]|" + x
        else:
             nstr = astring.replace("\"","'")
             nstr = nstr.rstrip("\n")
             zGroupLayer = zGroupLayer + "|" + nstr
    return gpos


def MaketSelect(self, zlistWOR, Rac, wpos):
    global tSelect
    zSelect = Rac
    if wpos == (len(zlistWOR)-1): return wpos+1
    for spos in range(wpos+1, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[spos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or x.startswith('SET WINDOW FRONTWINDOW() TITLE')  or x.startswith('ADD COLUMN') or x.startswith('SELECT') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
           break
        else :
           nstr = astring.replace("\"","'")
           nstr = nstr.rstrip("\n")
           zSelect = zSelect + "|" + nstr
    indexSelect = len(tSelect)
    tSelect['SELECT'+str(indexSelect)] = zSelect
    return spos

def MaketJoin(self, zlistWOR, Rac, wpos):
    global tJoin
    zJoin = Rac
    if wpos == (len(zlistWOR)-1): return wpos+1
    for spos in range(wpos+1, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[spos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or x.startswith('SET WINDOW FRONTWINDOW() TITLE')  or x.startswith('ADD COLUMN') or x.startswith('SELECT') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
           break
        else :
           nstr = astring.replace("\"","'")
           nstr = nstr.rstrip("\n")
           zJoin = zJoin + "|" + nstr
    indexJoin = len(tJoin)
    tJoin['JOIN'+str(indexJoin)] = zJoin
    return spos


def MaketBrowse(self, zlistWOR, Rac, wpos):
    global tBrowse
    zBrowse = Rac
    if wpos == (len(zlistWOR)-1): return wpos+1
    for bpos in range(wpos+1, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[bpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('SELECT') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
           break
        else :
           nstr = astring.replace("\"","'")
           nstr = nstr.rstrip("\n")
           zBrowse = zBrowse + "|" + nstr
    indexBrowse = len(tBrowse)
    tBrowse['BROWSE'+str(indexBrowse)] = zBrowse
    return bpos


def MaketComposer(self, zlistWOR, Rac, wpos):
    global tComposer
    zComposer = Rac
    debComposer = False
    if wpos == (len(zlistWOR)-1): return wpos+1
    for cpos in range(wpos+1, len(zlistWOR)):    
        astring = str(QString.fromLocal8Bit(zlistWOR[cpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if x.startswith('LAYOUT') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('SELECT') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
           break
        else :
           nstr = astring.replace("\"","'")
           nstr = nstr.rstrip("\n")
           zComposer = zComposer + "|" + nstr   
    indexComposer = len(tComposer)
    tComposer['COMPOSER'+str(indexComposer)] = zComposer
    return cpos


#-----------------------------------------------------------------
#FONCTIONS DE RESTITUTION DES TABLEAUX OPENWOR SOUS FORME HTML
# - MakeHTMLView(self , tempLayer, subtempLayer)
#-----------------------------------------------------------------
def MakeHTMLView(self, tempLayer, subtempLayer):
    tempLayer+= "</table><br><hr><br>"
    tempLayer+= "<table width='100%' border=0.5px><tr align='center'><td colspan='3'><font color='#0000ff'><h3>Statistiques du document :</h3></font></td></tr>"
    tempLayer+= "<tr><td>Nombre de carte(s) :</td><td>"+str(len(tMap))+"</td><td>("+str(tMap.keys())+")</td></tr>" 
    tempLayer+= "<tr><td>Nombre de mise(s) en page :</td><td>"+str(len(tComposer))+"</td><td>("+str(tComposer.keys())+")</td></tr>"
    tempLayer+= "<tr><td>Nombre de fenetre(s) donnees :</td><td>"+str(len(tBrowse))+"</td><td>("+str(tBrowse.keys())+")</td></tr>"
    tempLayer+= "<tr><td>Nombre de sélection(s) :</td><td>"+str(len(tSelect))+"</td><td>("+str(tSelect.keys())+")</td></tr>"
    tempLayer+= "<tr><td>Nombre de jointure(s) :</td><td>"+str(len(tJoin))+"</td><td>("+str(tJoin.keys())+")</td></tr>"      
    tempLayer+= "<tr><td>Nombre de couche(s) :</td><td>"+str(len(tLayerMap))+"</td><td>("+str(tLayerMap.keys())+")</td></tr>"
    tempLayer+= "<tr><td>Nombre d'analyse(s) thématique(s) :</td><td>"+str(len(tLayerMapAna))+"</td><td>("+str(tLayerMapAna.keys())+")</td></tr>"
    tempLayer+= "<tr><td>Nombre de groupe(s) :</td><td>"+str(len(tGroupLayer))+"</td><td>("+str(tGroupLayer.keys())+")</td></tr>"
    tempLayer+= "</table>"
    subtempLayer+= "<br><font color='#0000ff'><h3>Cartes (tMap) : " +str(len(tMap))+ " </h3></font>"+MefDic(tMap)
    subtempLayer+= "<br><font color='#0000ff'><h3>Compositions (tComposer) : " +str(len(tComposer))+ " </h3></font>"+MefDic(tComposer)
    subtempLayer+= "<br><font color='#0000ff'><h3>Fenêtres données (tBrowse) : " +str(len(tBrowse))+ " </h3></font>"+MefDic(tBrowse)
    subtempLayer+= "<br><font color='#0000ff'><h3>Couches (tLayer) : " +str(len(tLayer))+ " </h3></font>"+MefDic(tLayer)
    subtempLayer+= "<br><font color='#0000ff'><h3>URL couches (uLayer) : "  +str(len(uLayer))+ " </h3></font>"+MefDic(uLayer)
    subtempLayer+= "<br><font color='#0000ff'><h3>Sélections (tSelect) : "  +str(len(tSelect))+ " </h3></font>"+MefDic(tSelect)
    subtempLayer+= "<br><font color='#0000ff'><h3>Jointures (tJoin) : "  +str(len(tJoin))+ " </h3></font>"+MefDic(tJoin)    
    subtempLayer+= "<br><font color='#0000ff'><h3>Couches de la carte (tLayerMap) : " +str(len(tLayerMap))+ " </h3></font>"+MefDic(tLayerMap)
    subtempLayer+= "<br><font color='#0000ff'><h3>Analyses de la carte (tLayerMapAna) : "  +str(len(tLayerMapAna))+ " </h3></font>"+MefDic(tLayerMapAna)
    subtempLayer+= "<br><font color='#0000ff'><h3>Groupes la carte (tGroupLayer) : "  +str(len(tGroupLayer))+ " </h3></font>"+MefDic(tGroupLayer)    
    intro = "<h2><img src='"+ getThemeIcon("selectplus_a.png")+"'>&nbsp;<u>Variables OPENWOR</u> :</h2>"
    intro+= "<table border='0.5' bordercolor='#000000' width=100% cellspacing=0 cellpadding=0><tr bgcolor='#cccccc'><tr><td>"
    fin = "</td></tr></table>"
    mytextvar = intro+tempLayer+subtempLayer+fin
    self.ViewLOG.setText(mytextvar)

def MefDic(DicGen):
    HTMLMefDic = ""
    for key in DicGen.keys():
        if str(key)!="":  HTMLMefDic = str(HTMLMefDic) + "[<b>" + str(key) + "</b>]" + " : <i>" + str(DicGen[key]) + "</i><br>"
    return HTMLMefDic

def CountValideURL(DicGen):
    zValidURL = 0
    for key in DicGen.keys():
        if str(key)!="":  
           if str(DicGen[key])!="" :  zValidURL+= 1
    return zValidURL

#-----------------------------------------------------------------
#FONCTIONS DE RESTITUTION DES TABLEAUX OPENWOR SOUS FORME TREEVIEW
# - MakeTreeView(self)
# - MakeParentItem(self, zStr)
# - MakeItem(DicGen, parentItem)
#-----------------------------------------------------------------
def MakeTreeView(self):
    self.model = QtGui.QStandardItemModel()

    parentItem = MakeParentItem(self, "Cartes (tMap) : " + str(len(tMap)))
    MakeItem(tMap, parentItem)

    parentItem = MakeParentItem(self, "Compositions (tComposer) : " + str(len(tComposer)))
    MakeItem(tComposer, parentItem)

    parentItem = MakeParentItem(self, "Fenêtres données (tBrowse) : " + str(len(tBrowse)))
    MakeItem(tBrowse, parentItem)

    parentItem = MakeParentItem(self, "Couches (tLayer) : " + str(len(tLayer)))
    MakeItem(tLayer, parentItem)

    parentItem = MakeParentItem(self, "URL couches (uLayer) : " + str(len(uLayer)))
    MakeItem(uLayer, parentItem)

    parentItem = MakeParentItem(self, "Sélections (tSelect) : " + str(len(tSelect)))
    MakeItem(tSelect, parentItem)

    parentItem = MakeParentItem(self, "Jointures (tJoin) : " + str(len(tJoin)))
    MakeItem(tJoin, parentItem)

    parentItem = MakeParentItem(self, "Couches de la carte (tLayerMap) : " + str(len(tLayerMap)))
    MakeItem(tLayerMap, parentItem)

    parentItem = MakeParentItem(self, "Analyses de la carte (tLayerMapAna) : " + str(len(tLayerMapAna)))
    MakeItem(tLayerMapAna, parentItem)

    parentItem = MakeParentItem(self, "Groupes de la carte (tGroupLayer) : " + str(len(tGroupLayer)))
    MakeItem(tGroupLayer, parentItem)

    self.TreeView.setModel(self.model)

def MakeParentItem(self, zStr):
    parentItem = self.model.invisibleRootItem()
    item = QtGui.QStandardItem(QtCore.QString(zStr))
    parentItem.appendRow(item)
    return item


def MakeItem(DicGen, parentItem):
    RacparentItem = parentItem
    for key in DicGen.keys():
        if str(key)!="":
           item = QtGui.QStandardItem(QtCore.QString(str(key)))
           parentItem.appendRow(item)
           parentItem = item

           item = QtGui.QStandardItem(QtCore.QString(str(DicGen[key])))
           parentItem.appendRow(item)
           parentItem = RacparentItem

#------------------------------
#FONCTIONS CREATION DE LA CARTE
#------------------------------           
def MakeMapCanvas(self, iMap):
          global tMap
          global nProj4Infos
          global nProj4

          if not self.CkBx_Surcharge.isChecked(): self.iface.newProject()

          if self.CkBx_UniProj.isChecked():    
             lInfosProj4 = nProj4Infos.split("|")
             nProj4 = int(lInfosProj4[2])
             self.FixenProj4(lInfosProj4[3])
             self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(1)
 
          ic='MAP'+str(iMap)
          cCarte = str(tMap[ic])
          tempo = cCarte.split("|")
          layero = ""

          for i in range(len(tempo)):
              stempo = NetStrInfos(tempo[i], True, False, False, False, ())
              x = stempo.upper()
              if x.startswith("POSITION"): break
              else : layero = layero + str(tempo[i])

          layero = NetStrInfos(layero, True, True, False, False, ("MAP FROM","Map from", "Map From", "|"))
          ssLayer = layero.split(",")

          #initialisation unités de la carte - a minima dans la maquette
          zDD, zUnitsMap = True, ""
          nSizeMap = self.iface.mapCanvas().width()
          nSizeMap = nSizeMap * 20 * (0.00176388888888889) * 1.5
          nSizeMapUnits = "CM"

          zEmprise = ""
          zCenter = ""

          for i in range(len(tempo)):
              stempo = NetStrInfos(tempo[i], True, False, False, False, ()) 
              x = stempo.upper()
              if x.find("DISTANCE UNITS")!= -1:
                 posd = x.find("XY UNITS")+9
                 posf = len(stempo)
                 zUnitsMap = NetStrInfos(stempo[posd:posf], False, False, True, False, ("\"","'"))
              elif x.find("DISPLAY DECIMAL OFF")!=-1: zDD = False
              elif x.find("LAYER ")!=-1: break
              elif x.startswith("ZOOM "): zEmprise =  NetStrInfos(tempo[i].upper(), True, False, False, False, ()) 
              elif x.startswith("CENTER "): zCenter =  NetStrInfos(tempo[i].upper(), True, False, False, False, ("CENTER (",")"))
              elif x.startswith("COORDSYS "): zProj =  NetStrInfos(tempo[i].upper(), True, False, False, False, ())

          self.canvas = self.iface.mapCanvas()

          if zUnitsMap == "IN" and zDD:  zUnitsMap = zUnitsMap + "DD"

          tGroup = QStringList()
          zLayersMap = CountLayersMap(tLayerMap, ic+".LAYER")
          iLayersMap, iGroupsMap, iEltLegend = 1, 1, 1
          tLayerGroup = {}
          tGroupVisibility = {}
          iGroup = 0
          zGroups = ""
          zNameGroupLayer = ""

          
          for j in range(len(ssLayer)):
             if ssLayer[j].upper().find("GROUPLAYER")!=-1:
                 zNameGroupLayer = NetStrInfos(ssLayer[j].split("(")[1], True, True, False, False, (")", "'"))
                 zGroups = str(tGroup[len(tGroup)-1])  + "/" +  zNameGroupLayer if len(tGroup) > 0 else zNameGroupLayer
                 #tableau pour gérer la visibilité des groupes
                 zDisplay = 1
                 if tGroupLayer.has_key("GROUPLAYER"+str(iGroup)):
                    zInfos = tGroupLayer["GROUPLAYER"+str(iGroup)].split("|")
                    if zInfos[1].upper().find("DISPLAY OFF") != -1 : zDisplay = -1
                 tGroupVisibility["GROUP"+str(iGroup)] = zNameGroupLayer + "|" + str(zGroups) + "|" + str(zDisplay)
                 iGroup+= 1
                 
                 if ssLayer[j].find(")")==-1 : tGroup << str(zGroups)
                 else :
                     cEltLegend = ic+".ELT"+str(iEltLegend)
                     cGroupMap = ic+".GROUP"+str(iGroupsMap)
                     tLayerGroup[cEltLegend] = cGroupMap + "||" + str(zGroups)
                     iGroupsMap+= 1
                     iEltLegend+= 1
                     zGroups, tGroup = NettGroup(ssLayer[j], tGroup, zGroups, zNameGroupLayer)
   
             else:
                 if iLayersMap <= zLayersMap :
                    cEltLegend = ic+".ELT"+str(iEltLegend)  
                    cLayerMap = ic+".LAYER"+str(iLayersMap)
                    cLayer = NetStrInfos(ssLayer[j], True, True, False, False, (")", "'"))
                    tLayerGroup[cEltLegend] = cLayerMap + "|" + cLayer + "|" + str(zGroups)
                    iLayersMap+= 1
                    iEltLegend+= 1                    
                    zGroups, tGroup = NettGroup(ssLayer[j], tGroup, zGroups, zNameGroupLayer)


          ProjectHasXLS = False          
          for key in tLayer.keys():
              sKey = str(key)
              if tLayer[sKey] == "XLS" :
                 #Fonction pour récupérer le nom de l'onglet
                 TabFile = str(uLayer[sKey])
                 TabFile = TabFile.upper()
                 TabFile = TabFile.replace(".XLS", ".TAB")                  
                 sCalc = GetRangeTableXLS(TabFile) 
                 vLayer = self.iface.addVectorLayer(uLayer[sKey],sCalc,"ogr")
                 ProjectHasXLS = True
              
          
          total = int(len(tLayerGroup))
          #Passe des groupes
          InitProgressBar(self, "Groupe(s) :")
          for ij in range(total):
              cEltLegend = ic+".ELT"+str(ij+1)           
              zInfos = tLayerGroup[cEltLegend].split("|")
              cLayerMap = str(zInfos[0])           
              cLayer = str(zInfos[1])
              cGroup = str(zInfos[2])
              destGroup = MakeGroupLayer(self, cGroup)
              zPercent = int(100 * float(float(ij+1)/total))
              self.progressBar.setValue(zPercent)

          #Passe des couches
          InitProgressBar(self, "Couche(s) :")    
          for ij in range(total-1, -1, -1):
              cEltLegend = ic+".ELT"+str(ij+1)           
              zInfos = tLayerGroup[cEltLegend].split("|")
              cLayerMap = str(zInfos[0])           
              cLayer = str(zInfos[1])
              cGroup = str(zInfos[2])
              if cLayer != "" :
                 destGroup = MakeGroupLayer(self, cGroup)
                 fLayers = MakeLayer(self, cLayer, cLayerMap, destGroup, iMap, nSizeMap, nSizeMapUnits)
              zPercent = int(100 * float(float(total - ij)/total))
              self.progressBar.setValue(zPercent)

          self.progressBar.setValue(0)
          zCond = True if len(tGroupLayer) > 0 else False
          MakeGroupExpanded(self, zCond)
      
          legendTree = self.iface.mainWindow().findChild(QDockWidget, "Legend").findChild(QTreeWidget)
          for i in range(len(tGroupVisibility)):
              zInfos = tGroupVisibility["GROUP"+str(i)].split("|")
              cGroup = str(zInfos[1])
              destGroup = MakeGroupLayer(self, cGroup)
              nCond = Qt.Unchecked if int(zInfos[2]) == -1 else Qt.Checked
              nCol = legendTree.currentColumn()
              destGroup.setCheckState(nCol, nCond)

          if zCenter != "" and zCenter.find(",")!=-1:
             tCenter = zCenter.split(",")
             xCenter = float(tCenter[1])
             yCenter = float(tCenter[0])

             if zEmprise != "" :
                zZoomProperties = zEmprise.split()
                zUnitsZoom = NetStrInfos(zZoomProperties[3], False, False, True, False, ("\"", "'"))
                zValueZoom = NetStrInfos(zZoomProperties[1], True, True, False, False, ())
                zValueZoom = float(GetValueZoom(float(zValueZoom), zUnitsZoom, nSizeMap, nSizeMapUnits))
                self.iface.mapCanvas().zoomScale(zValueZoom)
                self.iface.mapCanvas().refresh()

             zUnitsProj = NetStrInfos(zProj.split(",")[6], False, False, True, False, ("\"", "'"))
             zUnitsProjList = QStringList()
             zUnitsProjList << "IN" << "DD" << "MM" << "CM" << "KM" << "M"
             
             if (zUnitsProjList.contains(zUnitsProj)):
                 xCenter = float(GetValueZoom(xCenter, zUnitsProj, nSizeMap, nSizeMapUnits))
                 yCenter = float(GetValueZoom(yCenter, zUnitsProj, nSizeMap, nSizeMapUnits))
                 zRenderer = self.iface.mapCanvas().mapRenderer()
                 zPoint = zRenderer.coordinateTransform().toMapPoint( xCenter, yCenter )
                 self.iface.mapCanvas().zoomWithCenter(int(zPoint.x()), int(zPoint.y()), False)

          self.progressBar.setValue(0)


#-----------------------------------
# BLOC Fonctions Groupes ...
#-----------------------------------
def FixeGroupLayer(self, zLayer, destGroup, nCond):
    legendTree = self.iface.mainWindow().findChild(QDockWidget, "Legend").findChild(QTreeWidget)
    itemsel = legendTree.currentItem()   
    if (destGroup != None ):
        if itemsel.parent() : itemsel.parent().takeChild(itemsel.parent().indexOfChild(itemsel))
        else : legendTree.takeTopLevelItem(legendTree.indexOfTopLevelItem(itemsel))
        destGroup.insertChild( destGroup.indexOfChild(destGroup) + 1, itemsel ) 
        itemsel = legendTree.currentItem()
 

def MakeGroupLayer(self, cGroup):
    legend = self.iface.legendInterface()
    legendTree = self.iface.mainWindow().findChild(QDockWidget, "Legend").findChild(QTreeWidget)    
    itemGroup = None
    if cGroup !="" :
       tGroup = cGroup.split("/")
       for i in range(len(tGroup)):
           zGroup = str(tGroup[i])
           itemList = legendTree.findItems(QString(zGroup), Qt.MatchExactly|Qt.MatchCaseSensitive|Qt.MatchRecursive)
           if len(itemList)>0:
              itemGroup = itemList[0]
           else:
              while i < len(tGroup):
                 zGroup = str(tGroup[i])
                 legend.addGroup(zGroup, False, itemGroup)
                 itemList = legendTree.findItems(QString(zGroup), Qt.MatchExactly|Qt.MatchCaseSensitive|Qt.MatchRecursive)
                 if len(itemList): itemGroup = itemList[len(itemList)-1]
                 i+= 1
              break   
    return itemGroup


def getGroupIndex(iface, groupName):
    relationList = iface.legendInterface().groupLayerRelationship()
    i = 0
    for item in relationList:
        if item[0] == groupName:
            i+= 1
            return i
        i+= 1
    return 0


def NettGroup(ssLayer, tGroup, zGroups, zNameGroupLayer):
    zRetrait = CountCaractere(ssLayer, ")")
    zRefRetrait = zRetrait
    while zRetrait > 0 :
          tGroup.removeAt(len(tGroup)-1)
          zRetrait = zRetrait - 1
    if zRefRetrait > 0 : zGroups = str(tGroup[len(tGroup)-1])  + "/" +  zNameGroupLayer if len(tGroup) > 0 else ""
    return zGroups, tGroup
    

def CountLayersMap(zDic, zMap):
    CountLayers = 0
    for key in zDic.keys():
        if key.find(zMap)!=-1: CountLayers+= 1 
    return CountLayers


#-----------------------------------
# BLOC Fonctions MIWI & Autres ...
#-----------------------------------
#-------------------------------------------------------
#FONCTION CORRECTION DES CHEMINS (AJOUT / SI NECESSAIRE)    
#-------------------------------------------------------    
def CorrigePath(nPath):
    nPath = str(nPath)
    a = len(nPath)
    subC = "/"
    b = nPath.rfind(subC, 0, a)
    return (nPath + "/") if a != b else nPath 
     
def GetAdress(nTable, nDir):
    rTable = nTable
    if not os.path.exists(rTable):
       retval = os.path.join(nDir,nTable)
       retval = os.path.abspath(retval)
       rTable = retval if os.path.exists(retval) else ""
    return rTable
    
def GetTypeTable(nTable):
    mytable = open(nTable, 'r')
    nType=""
    for line in mytable:
        astring=str(QString.fromLocal8Bit(line))
        astring = astring.upper()
        if astring.find('TYPE')!=-1:
           lst = astring.split()
           nType = NetStrInfos(lst[1], False, False, False, False, ("\""))
           break
    mytable.closed
    if nType == "": nType = "NATIVE" 
    return nType

def GetRangeTableXLS(nTable):
    mytable = open(nTable, 'r')
    nRange=""
    for line in mytable:
        astring=str(QString.fromLocal8Bit(line))
        astring = astring.upper()
        if astring.find('TYPE')!=-1:
           lst = astring.split()
           zIndex = FixeIndex(0,lst, "RANGE")
           if zIndex != - 1:
              nRangeInfos = NetStrInfos(lst[zIndex], False, False, False, False, ("\""))
              if nRangeInfos.find("!")!=-1 : nRange = nRangeInfos.split("!")[0]
              else : nRange = nRangeInfos
           break
    mytable.closed
    return nRange



def GetRasterFileMIG(nTable):
    mytable = open(nTable, 'r')
    nType=""
    for line in mytable:
        astring=str(QString.fromLocal8Bit(line))
        if astring.find('\Interpolator\Source Data\Table')!=-1:
           lst = astring.split("=")
           nType = NetStrInfos(lst[1], True, True, False, False, ("\""))
           break
    mytable.closed
    return nType

def GetMIGFieldName(nTable):
    mytable = open(nTable, 'r')
    nType=""
    for line in mytable:
        astring=str(QString.fromLocal8Bit(line))
        if astring.find('\Interpolator\Source Data\Expression')>-1:
           lst = astring.split("=")
           nType = NetStrInfos(lst[1], True, True, False, False, ("\""))
           break
    mytable.closed
    return nType

def GetMIGInfos(nTable):
    mytable = open(nTable, 'r')
    myInfos = ""
    myInfos = mytable.readlines()
    mytable.closed
    return myInfos

def GetRessourceFile(nTable):
    mytable = open(nTable, 'r')
    nType=""
    for line in mytable:
        astring=str(QString.fromLocal8Bit(line))
        x = astring.upper()
        if x.find('OPEN TABLE')!=-1: 
           #on récupère le chemin du fichier 
           lst = x.split()
           zIndex = FixeIndex(0,lst, "TABLE")
           lst = astring.split()
           nType = NetStrInfos(lst[zIndex], False, False, False, False, ("\"",".\\"))
           nDir = str(nTable)
           nDir = CorrigePath(os.path.dirname(nDir))
           nType = GetAdress(nType, nDir)
           break
    mytable.closed
    return nType

def GetRasterFile(nTable, IsSHP, IsASCII):
    if IsASCII :
       nType = ""
       UnType = nTable.upper()
       if UnType.rfind(".TAB",len(UnType)-4)!=-1: nType= nTable[0:len(UnType)-4]
       if os.path.exists(nType + ".txt"): nType = nType + ".txt"
       elif os.path.exists(nType + ".csv"): nType = nType + ".csv"
       elif os.path.exists(nType + ".xls"): nType = nType + ".xls"
       else : nType = ""
    else:
        mytable = open(nTable, 'r')
        nType=""
        for line in mytable:
            astring=str(QString.fromLocal8Bit(line))
            x = astring.upper()
            if x.find('FILE')!=-1: #>
               #on récupère le chemin du fichier 
               lst = astring.split()
               nType = NetStrInfos(lst[1], False, False, False, False, ("\""))
               nDir = str(nTable)
               nDir = CorrigePath(os.path.dirname(nDir))
               if IsSHP:
                  if nType == "SHAPEFILE":
                     nType = nTable[0:len(nTable)-3]+"SHP"  
                  else:  
                     nType = nType.rstrip(".DBF") 
                     nType = nType + ".SHP"
               nType = GetAdress(nType, nDir)
               break
        mytable.closed
    return nType

def getThemeIcon(theName):
    myPath = CorrigePath(os.path.dirname(__file__)) 
    myDefPath = myPath.replace("\\","/");
    myIconsPath = myDefPath + "icons/" + theName ;
    myCurThemePath = QgsApplication.activeThemePath() + "/plugins/" + theName;
    myDefThemePath = QgsApplication.defaultThemePath() + "/plugins/" + theName;
    myQrcPath = "python/plugins/openwor/" + theName;

    if QFile.exists(myDefPath + theName): return myDefPath
    elif  QFile.exists(myIconsPath): return myIconsPath
    elif QFile.exists(myCurThemePath): return myCurThemePath
    elif QFile.exists(myDefThemePath): return myDefThemePath
    elif QFile.exists(myQrcPath): return myQrcPath
    else: return theName

#----------------------------------------------
# FONCTION POSITONNEMENT RELATIF ANATHEMA/CARTE  
#----------------------------------------------   
def CountAna(DicGen, Target):
    zCountAna = 0
    for key in DicGen.keys():
        sKey = str(key)
        if sKey.find(Target)!=-1: zCountAna+= 1 
    return zCountAna

def CountAnaiMapSup(iMap, index):
    CountAna = 0
    for key in tLayerMapAna.keys():
        skey = str(key)
        if skey.find("MAP"+str(iMap)+".")!=-1:
           stempo = skey.split(".")
           skey = str(stempo[1])
           skey = skey.replace("LAYER","")
           sindex = skey.split("_")
           svalue = int(sindex[0])
           if svalue > index: CountAna+= 1
    return CountAna

def PosANA(DicGen, Target, iMap):
    zPosAna = 0
    for key in DicGen.keys():
        sKey = str(key)
        if sKey.find("MAP"+str(iMap)+".")!=-1:
           if sKey.find(Target)!=-1: zPosAna+= 1
           else: break
    return zPosAna

def CountAnaMapi(iMap):
    CountAna = 0
    for key in tLayerMapAna.keys():
        sKey = str(key)
        if sKey.find("MAP"+str(iMap)+".")!=-1: CountAna+= 1
    return CountAna

def CountAnaInfMapi(iMap):
    CountAna = 0
    for key in tLayerMapAna.keys():
        stempo = key.split(".")
        schaine = stempo[0]
        schaine = schaine.replace("MAP","")
        avalue = int(schaine)
        if avalue<iMap:  CountAna+= 1
    return CountAna


#-------------------------------------------
# FONCTION CONSTITUTION DE LA LEGENDE CARTE  
#-------------------------------------------
def MakeGroupExpanded(self, nCond):
    Layers = self.iface.legendInterface().layers()
    i = 0
    for layer in Layers:     
        self.iface.legendInterface().setGroupExpanded(i, nCond)
        i+= 1

def FixeExtent(self):
    Layers = self.iface.legendInterface().layers()
    for layer in Layers:   
        isOK = False
        if layer.type()== layer.VectorLayer and layer.isValid() :
           try: zType = str(layer.storageType())
           except: zType = "MEMORY STORAGE"
           if zType.upper().find("MEMORY STORAGE")==-1 and zType.upper().find("XLS")==-1: isOK = True 
        if isOK:
           layer.select([])
           layer.setSelectedFeatures([feat.id() for feat in layer])
           self.iface.mapCanvas().zoomToSelected(layer)
           self.iface.mapCanvas().refresh()
           layer.setSelectedFeatures([])
           zItem = MakeGroupLayer(self, str(layer.name()))
           zItem.setSelected(True) 
           break
    return

def layerIds(layer):
    ids = []
    p = layer.dataProvider()
    allAttrs = p.attributeIndexes()
    p.select(allAttrs)
    f = QgsFeature()
    while p.nextFeature(f): ids.append(f.id())
    return ids
    
#--------------------------------------------
# FONCTION CHARGEMENT DES COUCHES DE LA CARTE  
#--------------------------------------------
def MakeLayer(self, cLayer, cLayerMap, cInGroup, iMap, nSizeMap, nSizeMapUnits):
    global tLayer
    global uLayer
    global tBrowse
    global tLayerMap
    global nProj4
    global nProj4Infos

    fLayers = []
    nCondAna = False
    nNoZoomStep = self.CkBx_NoZoomStep.isChecked()
    nFixeUniProj = self.CkBx_UniProj.isChecked()
    nForceUnitsMap = 0 if self.CkBx_ForceUnitsMap.isChecked() else 1


    if cLayer!="":
        if uLayer.has_key(cLayer):
           vType = str(tLayer[cLayer])


           if tLayer[cLayer] == "NATIVE" or tLayer[cLayer] == "SHAPEFILE" or tLayer[cLayer] == "ASCII" :
              if vType == "NATIVE": driver = ogr.GetDriverByName("MapInfo File")
              elif vType == "SHAPEFILE" : driver = ogr.GetDriverByName("Shapefile")
              
              if tLayer[cLayer] == "NATIVE" or tLayer[cLayer] == "SHAPEFILE" :
                  try:
                      datasource = driver.Open(uLayer[cLayer])
                      layer = datasource.GetLayer() 
                      zFeatureCount = layer.GetFeatureCount()
                  except:  
                      #Fausse couche MapInfo, on va la traiter en couche logique
                      zCible = uLayer[cLayer][0:len(uLayer[cLayer])-4]+".dat"
                      if os.path.exists(zCible):
                         zCible2 = zCible[0:len(zCible)-4]+".dbf"
                         shutil.copy2(zCible, zCible2)
                         uLayer[cLayer] = zCible2
                         sLayerVisibility = tLayerMap[cLayerMap]

                         zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, None) 
                         vLayer = self.iface.addVectorLayer(uLayer[cLayer],cLayer + " (Données Couche Logique)","ogr")
                         zRefGroup = MakeGroupLayer(self, "Groupe : " + cLayer + " (Couche Logique)")
                         
                         zCiblePath = os.path.dirname(zCible)+"\\"
                         p = vLayer.dataProvider()
                         allAttrs = p.attributeIndexes()
                         p.select(allAttrs)
                         fields = p.fields()
                         f = QgsFeature()

                         while p.nextFeature(f): 
                               atMap = f.attributeMap()
                               zTAB = str( atMap[ 0 ].toString())
                               zNAMETAB = str( atMap[ 1 ].toString())
                               zTYPETAB = str(GetTypeTable(zCiblePath+zTAB))
                    
                               if zTYPETAB == "RASTER" :
                                   zTableRaster = GetRasterFile(zCiblePath+zTAB, False, False)
                                   if os.path.exists(zTableRaster): vLayer = self.iface.addRasterLayer(zTableRaster,zNAMETAB)
                               else : vLayer = self.iface.addVectorLayer(zCiblePath+zTAB,zNAMETAB,"ogr")

                               if vLayer != None :
                                  QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                                  indiceVisibility = MakeVisibility(self, vLayer, sLayerVisibility)
                                  FixeGroupLayer(self, vLayer, zRefGroup, indiceVisibility)

                         return []
                         RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)  

                      else: zFeatureCount = 0 #si pas de DAT, on créé une couche vide ...
                  
              else:
                  zFeatureCount = NbRowAsciiFILE(uLayer[cLayer])

              if zFeatureCount > 0:
                  #Il faut regarder si Analyse thématique et combien    
                  NbAna = CountAna(tLayerMapAna, cLayerMap)
                  sLayerVisibility=""
                  LayerSupport = False
                
                  if NbAna > 0:
                     HasLabeller = False
                     ztoto = cLayerMap.split(".")
                     ziii = ztoto[1].replace("LAYER", "")
                     zvalue = int(ziii)
                     zBase = CountAnaiMapSup(iMap, zvalue)
                     self.progressBarL.setValue(0)

                     for i in range(NbAna):
                         
                         if not LayerSupport:
                            if tLayer[cLayer] == "NATIVE" or tLayer[cLayer] == "SHAPEFILE" : vLayer = self.iface.addVectorLayer(uLayer[cLayer],cLayer,"ogr")
                            else: vLayer = AddLayerASCII(self, uLayer[cLayer],cLayer, zFeatureCount)
                                
                            RefLayer = vLayer
                            Symbo2Vector(self, vLayer, tLayerMap[cLayerMap], nSizeMap, nSizeMapUnits, vType, nForceUnitsMap, nFixeUniProj, nProj4Infos, nNoZoomStep)
                            sLayerVisibility = tLayerMap[cLayerMap]
                            indiceVisibility = MakeVisibility(self, vLayer, sLayerVisibility)
                            QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                            nCondAna = False
                            LayerSupport = True

                            if vLayer != None :
                               fLayers.append(vLayer.id())
                               FixeGroupLayer(self, vLayer, cInGroup, indiceVisibility)

                         if tLayerMapAna.has_key(cLayerMap+"_"+str(i+1)):
                             zPosANA = (i+1) + zBase
                             nTypeAna = ""
                             nTypeAna = ValueTypeAna(tMap["MAP"+str(iMap)],zPosANA)

                             if nTypeAna == "VALUES" or nTypeAna == "RANGES" :
                                if tLayer[cLayer] == "NATIVE" or tLayer[cLayer] == "SHAPEFILE" : vLayer = self.iface.addVectorLayer(uLayer[cLayer],cLayer,"ogr")
                                else: vLayer = AddLayerASCII(self, uLayer[cLayer],cLayer, zFeatureCount)
                                QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                                

                             sLayerVisibility = tLayerMapAna[cLayerMap+"_"+str(i+1)]
                             nCondAna = True
                             if nTypeAna == "VALUES" or nTypeAna == "RANGES" : fLayer = SymboVectorAna(self, vLayer, tLayerMap[cLayerMap], nSizeMap, nSizeMapUnits, zPosANA, tMap["MAP"+str(iMap)],vType, tLayerMap[cLayerMap], False, nFixeUniProj, nForceUnitsMap, sLayerVisibility, nProj4Infos, nNoZoomStep)
                             else: fLayer = SymboVectorAna(self, RefLayer, tLayerMap[cLayerMap], nSizeMap, nSizeMapUnits, zPosANA, tMap["MAP"+str(iMap)], vType, tLayerMap[cLayerMap], False, nFixeUniProj, nForceUnitsMap, sLayerVisibility, nProj4Infos, nNoZoomStep)                             
                             indiceVisibility = MakeVisibility(self, fLayer, sLayerVisibility)
                             if fLayer != None :
                                fLayers.append(fLayer.id())
                                FixeGroupLayer(self, fLayer, cInGroup, indiceVisibility)
                            
                         zPercent = int(100 * float(float(i+1)/NbAna))
                         self.progressBarL.setValue(zPercent)
  
                  else:
                     if tLayer[cLayer] == "NATIVE" or tLayer[cLayer] == "SHAPEFILE" : vLayer = self.iface.addVectorLayer(uLayer[cLayer],cLayer,"ogr")
                     else: vLayer = AddLayerASCII(self, uLayer[cLayer],cLayer, zFeatureCount)

                     
                     if tLayerMap.has_key(cLayerMap):
                        sLayerVisibility = tLayerMap[cLayerMap]
                        Symbo2Vector(self, vLayer, sLayerVisibility, nSizeMap, nSizeMapUnits, vType, nForceUnitsMap, nFixeUniProj, nProj4Infos, nNoZoomStep)
                        QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                        indiceVisibility = MakeVisibility(self, vLayer, sLayerVisibility)
                       
                        if vLayer != None :
                           fLayers.append(vLayer.id())
                           FixeGroupLayer(self, vLayer, cInGroup, indiceVisibility)
                        
                  self.progressBarL.setValue(0)
                  if len(tBrowse)> 0 :
                     for key in tBrowse.keys():
                          tempo = tBrowse[key].split("|")
                          stempo = str(tempo[0])
                          if stempo.find(cLayer)!=-1:
                             self.iface.showAttributeTable(vLayer) 
                             break
                  


              else:
                  tempolayer = QgsVectorLayer("Point", QString.fromLocal8Bit(cLayer)+ " (couche vide)", "memory")
                  prCentro = tempolayer.dataProvider()
                  ret = prCentro.addAttributes( [ QgsField("Id", QVariant.Int) ] )
                  tempolayer.updateFieldMap()
                  ztempolayer = QgsMapLayerRegistry.instance().addMapLayer(tempolayer)
                  if tempolayer != None :
                     fLayers.append(tempolayer.id())
                     FixeGroupLayer(self, tempolayer, cInGroup, False)                     

           
           elif tLayer[cLayer] == "RASTER" :
                  hDataset = gdal.Open( uLayer[cLayer], gdal.GA_ReadOnly )
                  if hDataset is None:
                     stempo = os.path.splitext(uLayer[cLayer])
                     zType = NetStrInfos(stempo[1], False, False, True, False, ("."))
                      
                     if zType == "MIG":
                        #Il faut récupérer l'adresse de la table support
                        TabFile = uLayer[cLayer]
                        TabFile = TabFile[0:len(TabFile)-4]+".TAB"
                        
                        zCiblePath = os.path.dirname(TabFile)+"\\"

                        nFile = GetRasterFileMIG(TabFile)
                        nFile = nFile.rstrip()
                        isDEM = False
                            
                        if nFile == "":
                           TabFile = TabFile[0:len(TabFile)-4]+".DEM" 
                           if os.path.exists(TabFile):
                              isDEM = True  
                              nFile = TabFile
                           else:    
                              QMessageBox.information(None,"Avertissement :", "Le format " + str(zType) + " pour la table :\n"+ str(uLayer[cLayer]) +"\nn'est pas supporté.")
                              return [] #format non supporté

                        if not os.path.exists(nFile):
                           if os.path.exists(zCiblePath+nFile): nFile = zCiblePath + nFile
                       
                        if os.path.exists(nFile):
                           if isDEM:
                               vLayer = self.iface.addRasterLayer(nFile, cLayer)
                               QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                               vLayer.setDrawingStyle(QgsRasterLayer.SingleBandPseudoColor)
                               vLayer.setColorShadingAlgorithm(QgsRasterLayer.PseudoColorShader)
                           else: 
                               nField = GetMIGFieldName(TabFile)
                               vLayer = self.iface.addVectorLayer(nFile,cLayer,"ogr")                           
                               nAnaMIG = GetMIGInfos(TabFile)
                               vType = str(GetTypeTable(nFile)) 
                               vType = vType.upper()
                               
                           if tLayerMap.has_key(cLayerMap):
                              sLayerVisibility = tLayerMap[cLayerMap]
                              if not isDEM :
                                  SymboRasterMIG(self, vLayer, nFile, tLayerMap[cLayerMap], nAnaMIG, nField, nSizeMap, nSizeMapUnits, tMap["MAP"+str(iMap)], vType, nForceUnitsMap)                              
                              indiceVisibility = MakeVisibility(self, vLayer, sLayerVisibility)
                              QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                              if vLayer != None :
                                  fLayers.append(vLayer.id())
                                  FixeGroupLayer(self, vLayer, cInGroup, indiceVisibility)                               

                  else:
                     vLayer = self.iface.addRasterLayer(uLayer[cLayer],cLayer)
                     if tLayerMap.has_key(cLayerMap):
                        sLayerVisibility = tLayerMap[cLayerMap]
                        SymboRaster(self, vLayer, tLayerMap[cLayerMap], nSizeMap, nSizeMapUnits, nNoZoomStep)
                        indiceVisibility = MakeVisibility(self, vLayer, sLayerVisibility)
                     QgsMapLayerRegistry.instance().addMapLayers([vLayer])

                     if vLayer != None :
                        fLayers.append(vLayer.id())
                        FixeGroupLayer(self, vLayer, cInGroup, indiceVisibility)                         

             
           elif tLayer[cLayer] == "WMS" :
                lstWMS = GetWMSInfos(uLayer[cLayer])
                SubEltWMS = lstWMS.split("|")
                zURL = str(SubEltWMS[0]) 
                zSRS = str(SubEltWMS[1]) 
                zVersion = str(SubEltWMS[4]) #3

                if zVersion == "" : zURL = zURL + "VERSION=1.3.0"
                else : zURL = zURL + "VERSION=" + zVersion
                   
                zFormatImg = str(SubEltWMS[9]) 
                zLayersWMS = QStringList()
                zStyles = QStringList()

                zLayerWMS = str(SubEltWMS[2])
                zStyle = str(SubEltWMS[3])
                if zLayerWMS.find(",")!=0:
                   stempolayers = zLayerWMS.split(",")
                   stempostyles = zStyle.split(",")

                   if (len(stempolayers)==len(stempostyles)) :
                       for i in range(len(stempolayers)):
                            zLayersWMS << stempolayers[i]
                            zStyles << stempostyles[i]
                   else:
                       for i in range(len(stempolayers)):
                            zLayersWMS << stempolayers[i]
                            zStyles << '' #'default'                       
                else:
                   zLayersWMS << zLayerWMS
                   zStyles << '' #'default'

                """
                #Non utilisés .... pour l'instant               
                zBBOX0, zBBOX1, zBBOX2, zBBOX3  = float(SubEltWMS[5]), float(SubEltWMS[8]), float(SubEltWMS[7]), float(SubEltWMS[6]) #4,7,6,5
                zSizeW = int(self.iface.mapCanvas().width())
                zSizeH = int(self.iface.mapCanvas().height())
                """
                try :
                    vLayer = self.iface.addRasterLayer(zURL, cLayer, 'wms', zLayersWMS, zStyles, zFormatImg, zSRS)
                    if tLayerMap.has_key(cLayerMap):
                        sLayerVisibility = tLayerMap[cLayerMap]
                        indiceVisibility = MakeVisibility(self, vLayer, cInGroup, sLayerVisibility) 
                    QgsMapLayerRegistry.instance().addMapLayers([vLayer])
                    if vLayer != None :
                       fLayers.append(vLayer.id())
                       FixeGroupLayer(self, vLayer, cInGroup, indiceVisibility)                        
                except :
                    QMessageBox.information(None,"Erreur WMS:", "Les informations collectées :\n"+str(lstWMS)+"\nne permettent pas le rappatriement de la couche :\n"+str(cLayer))

    return fLayers

#-----------------------------------------------
#FONCTION TRAITEMENT FICHIER ASCII   
#-----------------------------------------------
def AddLayerASCII(self, AsciiFile, cLayer, NbRows):
    iX, iY = -1, -1
    spamReader = csv.reader(open(AsciiFile, 'rb'))
    i = 0
    LigneData = ""
    CorrectData = True
   
    for row in spamReader:
        if i==0 :Ligne = str(row)
        if i==1 :
           LigneData = str(row)
           break
        i+= 1

    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(Ligne)

    if LigneData!="":
       dialectData = sniffer.sniff(LigneData)
       zQuoteCaracter = str(dialectData.quotechar) 
    else:
       zQuoteCaracter = ""
       
    zDelimiter = str(dialect.delimiter)
    if zDelimiter=="t": zDelimiter = "\\"+zDelimiter    

    hasHEADER = HasHeaderASCII(AsciiFile, Ligne, zDelimiter, zQuoteCaracter)
    
    rb=QgsRubberBand(self.iface.mapCanvas(),True)
    rb.reset()
    feat = QgsFeature()

    zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, None) 
    TempoLayer = QgsVectorLayer("Point", QString.fromLocal8Bit(cLayer)+ " (" + str(fGetTypeFile(AsciiFile)) + ")", "memory")
    TempoPoint = TempoLayer.dataProvider()
    DefineLayerProj(self, None, TempoLayer)
    RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)

    """                
    DestinationCRS = QgsCoordinateReferenceSystem()
    #DestinationCRS.createFromSrid(3452) #SRID WGS84
    #Quel est le SRS ID pour les CSV ???
    DestinationCRS = self.iface.mapCanvas().mapRenderer().destinationCrs()
    TempoLayer.setCrs(DestinationCRS) 
    """               
    ListFields = []
    indexFields = 1
    zFields = Ligne.split(zDelimiter)
    NbFields = len(zFields)

    #A revoir    
    if LigneData!="": zData = LigneData.split(zDelimiter)
    else: zData = zFields #Ligne.split(zDelimiter)

    if len(zData) < len(zFields):
       delta = len(zFields)-len(zData)
       for j in range(len(zData),delta+1):
           LigneData = LigneData + zDelimiter + ""
       zData = LigneData.split(zDelimiter)    
       CorrectData = False
   
    for j in range(len(zFields)):
        zTempo = str(zFields[j])
        zTempo = NetStrInfos(zTempo, False, False, False, False, ("[","]","'"," ", str(zQuoteCaracter)))
     
        if hasHEADER:
            uzTempo = zTempo.upper()
            if (uzTempo == 'LATITUDE') and (iX==-1) : iX = j
            if (uzTempo == 'X') and (iX==-1): iX = j
            if (uzTempo == 'COORDX') and (iX==-1): iX = j
            if (uzTempo == 'LONGITUDE') and (iY==-1): iY = j
            if (uzTempo == 'Y') and (iY==-1): iY = j
            if (uzTempo == 'COORDY') and (iY==-1): iY = j
   
        zTempoData = str(zData[j])
        zTempoData = NetStrInfos(zTempoData, False, False, False, False, ("[","]","'", str(zQuoteCaracter)))

        if not hasHEADER:
           zTempo = "_COL" + str(indexFields)
           indexFields+= 1

        if zTempoData!="":
            if is_number_float(zTempoData): ListFields.append(QgsField(str(zTempo), QVariant.Int))
            elif is_number_int(zTempoData): ListFields.append(QgsField(str(zTempo), QVariant.Double))
            else: ListFields.append(QgsField(str(zTempo), QVariant.String))
        else:
            ListFields.append(QgsField(str(zTempo), QVariant.String))
             
    ret = TempoPoint.addAttributes( ListFields ) 
    TempoLayer.updateFieldMap()

    if not hasHEADER:
       MakeLineASCII(self, rb, feat, TempoPoint, iX, iY, Ligne,zDelimiter, zQuoteCaracter, NbFields)
       TempoLayer.updateExtents()
        
    if LigneData!="" and CorrectData:
       MakeLineASCII(self, rb, feat, TempoPoint, iX, iY, LigneData,zDelimiter, zQuoteCaracter, NbFields)           
       TempoLayer.updateExtents()

    for row in spamReader:
        LigneData = str(row) 
        MakeLineASCII(self, rb, feat, TempoPoint, iX, iY, LigneData,zDelimiter, zQuoteCaracter, NbFields)
        TempoLayer.updateExtents()
        i+= 1

    rb.reset()
    TempoLayer.updateExtents()

    return TempoLayer

#-----------------------------------------------
#FONCTION MAKELIGNE FICHIER ASCII   
#-----------------------------------------------
def MakeLineASCII(self, rb, feat, TempoPoint, iX, iY, LigneData, zDelimiter, zQuoteCaracter, NbFields):
        
        zData = LigneData.split(zDelimiter)
        if len(zData) < NbFields:
           delta = len(zFields)-len(zData)
           for j in range(len(zData),delta+1):
               LigneData = LigneData + zDelimiter + ""
           zData = LigneData.split(zDelimiter)         
        
        if iX!=-1 and iY!=-1:
           zTempoData = NetStrInfos(zData[iX], False, False, False, False, ("[","]","'", str(zQuoteCaracter)))
           Xcoord = float(zTempoData)
           zTempoData = NetStrInfos(zData[iY], False, False, False, False, ("[","]","'", str(zQuoteCaracter)))
           Ycoord = float(zTempoData)
           MyPoint = QgsPoint( Xcoord, Ycoord)
           rb.addPoint(MyPoint)
           g = QgsGeometry().fromPoint(MyPoint)
        else:   
           g = QgsGeometry()

        feat.setGeometry(g)
        if iX!=-1 and iY!=-1: rb.reset()

        for j in range(len(zData)):
            zTempoData = str(zData[j])
            zTempoData = NetStrInfos(zTempoData, False, False, False, False, ("[","]","'", str(zQuoteCaracter)))  
            feat.addAttribute(j, QVariant(zTempoData))
        TempoPoint.addFeatures( [ feat ] )

#-------------------------------------------------
#FONCTION VERIFICATION ENTETE / .TAB FICHIER ASCII   
#-------------------------------------------------
def HasHeaderASCII(AsciiFILE, Ligne, zDelimiter, zQuoteCaracter):
    zHeader = False
    zAsciiFILE = AsciiFILE[0:len(AsciiFILE)-4]+".tab"
    zFieldsNameTAB = ""
    zFirstLINEASCII = ""
    zNb = 0    

    zFields = Ligne.split(zDelimiter)
    for j in range(len(zFields)):
        zTempo = str(zFields[j])
        zTempo = NetStrInfos(zTempo, False, False, False, False, ("[","]","'"," ", str(zQuoteCaracter)))
        zFirstLINEASCII = zFirstLINEASCII  + "|" + str(zTempo)
 
    if os.path.exists(zAsciiFILE):
       zFile = open(zAsciiFILE, 'r')
       zLines = zFile.readlines()
       zFile.close()

       for i in range(len(zLines)):
           zStr = NetStrInfos(str(QString.fromLocal8Bit(zLines[i])), True, True, False, False, ())
           UzStr = zStr.upper()

           if zNb > 0:
              zTempo = zStr.split(" ")                      
              zFieldsNameTAB =  zFieldsNameTAB + "|" + str(zTempo[0])
              zNb = zNb - 1

           if UzStr.startswith('FIELDS') :
              zTempo = UzStr.split(" ")
              zNb = int(zTempo[1])

    if (str(zFieldsNameTAB) == str(zFirstLINEASCII)):
        zHeader = True
    
    return zHeader

#----------------------------------------------
#FONCTION RE-ORDONNANCEMENT COUCHES THEMATIQUES   
#----------------------------------------------
def ReOrgtLayerMapAna():
    global tLayerMapAna
    DicGen = {}
    total = len(tLayerMapAna)
    j = 0
    zListitems = ShortDic(tLayerMapAna)
    if total == 0 : return
    while j < total :    
        zkey = zListitems[j] 
        zpos = zkey.find("_")
        zrac = zkey[0:zpos]
        zCountLayersMapAna = CountLayersMap(tLayerMapAna, zrac)
        if zCountLayersMapAna > 1 :
           for i in range(zCountLayersMapAna, 0, -1):
               zkey = zListitems[j] 
               znewkey = zrac + "_" + str(i)
               DicGen[znewkey] = tLayerMapAna[zkey]
               j+= 1
        else:
           DicGen[zkey] = tLayerMapAna[zkey]
           j+= 1
    tLayerMapAna = DicGen
    return 

def ShortDic(zDic):
    keylist = zDic.keys()
    keylist.sort()
    return keylist

    
#--------------------------------------------------
#FONCTION INSCRIPTION CHEMIN SYMBOLES PERSONNALISES   
#--------------------------------------------------
def VerifSVGPaths():
    ztoto = QSettings().value( "svg/searchPathsForSVG", QVariant( "" ).toString())
    ztotoinfos = ztoto.toString().split("|")
    isPresentPathSVG = False
    zPathSymbols = os.path.dirname(__file__)
    zPathSymbols = zPathSymbols.replace("\\","/") + "/svg/symbols/"
    zpaths = ""
    for i in range(len(ztotoinfos)):
        if ztotoinfos[i] == zPathSymbols : isPresentPathSVG = True
        zpaths = ztotoinfos[i] if i == 0 else zpaths + "|" + ztotoinfos[i]     
    if not isPresentPathSVG :
       QSettings().setValue("svg/searchPathsForSVG",str(zpaths + "|" + zPathSymbols)) if zpaths != "" else  QSettings().setValue("svg/searchPathsForSVG",str(zPathSymbols))

#--------------------------------------------------
#FONCTION REINITIALISATION BARRE PROGRESSION 1   
#--------------------------------------------------
def InitProgressBar(self, zText):
    self.progressBar.setValue(0)
    self.labelprogressBar.setText(zText) 


#-----------------------------------------------
#FONCTION DE RECHERCHE DE DOCUMENTS  
#-----------------------------------------------
#"""    
def listdirectory(self, path):
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            self.labelSearchFILE.setText(">> Analyse du dossier : " + subdirname)
            self.labelSearchFILE.repaint()            
        for filename in filenames:
            scandirectory(self, os.path.join(dirname, filename))
"""
def listdirectory(self, path):
    zPath = os.path.join(path, '*')
    for currentFile in glob.glob(zPath):
        if os.path.isdir(currentFile):
           self.labelSearchFILE.setText(">> Analyse du dossier : " + currentFile)
           self.labelSearchFILE.repaint()
           listdirectory(self, currentFile)
        else : scandirectory(self, currentFile)
    return 
"""

def scandirectory(self, currentFile):
    #Exemple de filtres multiples ....
    #zFilter = "mif|jpg|tab|"
    zFilter = ".wor|"
    if os.path.exists(currentFile):
        if os.path.isfile(currentFile):
            textension = os.path.splitext(currentFile)
            extension = textension[len(textension)-1].lower()
            #extension = extension.replace(".","")
            if zFilter.find(extension+"|")!=-1 and extension!="":
                self.SearchFILE.addItem(currentFile)
                self.SearchFILE.update()
    return 
