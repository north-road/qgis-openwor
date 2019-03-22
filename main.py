# -*- coding: iso-8859-1 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import sys
import doAbout
import doFOpenWor


class MainPlugin(object):
  def __init__(self, iface):
    self.name = "OpenWor"
    self.iface = iface
    
  def startRender(self, context):
    pass

  def stopRender(self, context):
    pass    

  def initGui(self):
    self.menu=QMenu("OpenWor 1.9")

    self.fopenwor = QAction("Charger des documents ...",self.iface.mainWindow())
    self.fopenwor.setText(QtCore.QCoreApplication.translate("main", "Charger des documents ..."))
    QObject.connect(self.fopenwor,SIGNAL("triggered()"),self.clickFOpenWor)

    self.about = QAction("A propos ...",self.iface.mainWindow())
    self.about.setText(QtCore.QCoreApplication.translate("main", "A propos ..."))
    QObject.connect(self.about,SIGNAL("triggered()"),self.clickAbout)

    self.menu.addAction(self.fopenwor)
    self.menu.addSeparator()
    self.menu.addAction(self.about)

    menuBar = self.iface.mainWindow().menuBar()
    menuBar.addMenu(self.menu)

    reload(sys)
    sys.setdefaultencoding( "iso-8859-1" )

  def clickAbout(self):
    d = doAbout.Dialog()
    d.exec_()

  def clickFOpenWor(self):
    d = doFOpenWor.Dialog(self.iface)
    d.exec_()  
  
  def unload(self):
    pass    

