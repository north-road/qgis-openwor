
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from about import Ui_Dialog

class Dialog(QDialog, Ui_Dialog):
	def __init__(self):
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		
