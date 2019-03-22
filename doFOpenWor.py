# -*- coding: iso-8859-1 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from fopenwor import Ui_Dialog_OW
import os


class Dialog(QDialog, Ui_Dialog_OW):
	def __init__(self, iface):
 		QDialog.__init__(self)
 		self.iface = iface
	        self.setupUi(self)

        def reject(self):
            self.SaveInfosIni()            
            self.hide()

        def SaveInfosIni(self):
            self.TxtFile.setReadOnly(False)
            sfileName = QString(self.TxtFile.toPlainText())
            self.TxtFile.setReadOnly(True)
            savefile = os.path.join(os.path.dirname(__file__),"savesession.ini")
            if os.path.exists(savefile)== True :
               try : 
                   os.remove(savefile) 
                   f = file(savefile, "w")
                   
                   ssurcharge = "oui" if self.CkBx_Surcharge.isChecked() else "non"
                   sprojunit = "oui" if self.CkBx_UniProj.isChecked() else "non"
                   szoomstep = "oui" if self.CkBx_NoZoomStep.isChecked() else "non"
                   sforceunitsmap = "0" if self.CkBx_ForceUnitsMap.isChecked() else "1"
                   sinteractivemode = "oui" if self.CkBx_InterActiveMode.isChecked() else "non"
                   
                   sSaveSessionInfos = """[general]\nfilename="""+sfileName+"""\nsurcharge="""+ssurcharge+"""\nzoomstep="""+szoomstep+"""\nprojunit="""+sprojunit+"""\nforceunitsmap="""+sforceunitsmap+"""\ninteractivemode="""+sinteractivemode+""""""     
                   f.write(sSaveSessionInfos)
                   f.close()
               except ValueError:
                   QMessageBox.information(None,"Erreur :", "Les informations de session ne sont pas sauvées.")
            
     
