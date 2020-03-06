# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import os
import re
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,QgsVectorLayer,

                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,QgsProject,
                       QgsProcessingParameterFeatureSink)
from qgis import processing


class ConvertWORAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConvertWORAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'convertwor'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Convert WOR')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def flags(self):
        f = super().flags()

        return f| QgsProcessingAlgorithm.FlagNoThreading


    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('Input WOR'),extension='wor'
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        file = self.parameterAsFile(parameters, self.INPUT, context)
        self.load_wor(file)

        return {}

    def load_wor(self, file):
        with open(file, 'r') as f:
            wor_lines = f.readlines()

        subtempLayer = ""

        mytextfile, iLayer = "", 0
        base_dir = os.path.dirname(file)
        if not base_dir[-1] == '/':
            base_dir += '/'

        layer_index = 0

        for line in wor_lines:
            line= line.strip()

            if line.upper().startswith('OPEN TABLE'):
                layer_index += 1
                table_name = re.match(".*?\"(.*?)\"", line).group(1)
                table_name = table_name.replace("\\", "/")

                try:
                    alias = re.match(r".*?as (.+?)\b", line,flags=re.IGNORECASE).group(1)
                except:
                    alias = ''

                if not table_name.upper().endswith(".TAB"):
                    table_name += ".TAB"

                #if theTest == "INTERACTIVE":
                #    tempoALIAS = " AS " + os.path.splitext(os.path.basename(str(nTable)))[0]
                #    # Il faut rechercher la vraie ressource !!! Table logique
                #    nTable = GetAdress(nTable, nDir)
                #    nRessource = GetRessourceFile(nTable)
                #    if nRessource != "": nTable = nRessource

                if not os.path.exists(table_name):
                    table_name = os.path.join(base_dir, table_name)

                vl = QgsVectorLayer(table_name, alias, 'ogr')
                QgsProject.instance().addMapLayer(vl)

              #if nTable != "":
              #    tempLayer = tempLayer + "<tr><td>Fichier num." + str(
              #        iLayer) + "</td><td align='center'>Ok</td><td><font color='#00ff00'>" + str(
              #        line) + "</font></td></tr>"
              #    nTypeTable = str(GetTypeTable(nTable))
              #    nTypeTable = nTypeTable.upper()

              #    if nTypeTable == "NATIVE":
              #        tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(nTable.replace("\"", ""))
              #    elif nTypeTable == "SHAPEFILE":
              #        nTableRaster = GetRasterFile(nTable, True, False)
              #        if nTableRaster != "": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(
              #            nTableRaster.replace("\"", ""))
              #    elif nTypeTable == "XLS":
              #        nTableRaster = GetRasterFile(nTable, False, True)
              #        if nTableRaster != "": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(
              #            nTableRaster.replace("\"", ""))
              #    elif nTypeTable == "RASTER":
              #        nTableRaster = GetRasterFile(nTable, False, False)
              #        if nTableRaster != "": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(
              #            nTableRaster.replace("\"", ""))
              #    elif nTypeTable == "WMS":
              #        nTableRaster = GetRasterFile(nTable, False, False)
              #        if nTableRaster != "": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(
              #            nTableRaster.replace("\"", ""))
              #    elif nTypeTable == "ASCII":
              #        nTableRaster = GetRasterFile(nTable, False, True)
              #        if nTableRaster != "": tLayer[str(slst[1])], uLayer[str(slst[1])] = str(nTypeTable), str(
              #            nTableRaster.replace("\"", ""))
               # else:
               #     tempLayer = tempLayer + "<tr><td>Fichier num." + str(
               #         iLayer) + "</td><td align='center'>Ko</td><td><b><font color='#ff0000'>" + str(
               #         line) + "</font></b></td></tr>"

          # elif astring.upper().startswith('SELECT'):
          #     nstr = astring.replace("\"", "'")
          #     nstr = nstr.rstrip("\n")
          #     k = MaketSelect(self, mylistWOR, nstr, k)

          # elif astring.upper().startswith('ADD COLUMN'):
          #     nstr = astring.replace("\"", "'")
          #     nstr = nstr.rstrip("\n")
          #     k = MaketJoin(self, mylistWOR, nstr, k)

          # elif astring.upper().startswith('MAP FROM'):
          #     nstr = astring.replace("\"", "'")
          #     nstr = nstr.rstrip("\n")
          #     k = MaketMap(self, mylistWOR, nstr, k)

          # elif astring.upper().startswith('BROWSE *'):
          #     nstr = astring.replace("\"", "'")
          #     nstr = nstr.rstrip("\n")
          #     k = MaketBrowse(self, mylistWOR, nstr, k)

          # elif astring.upper().startswith('LAYOUT'):  # 'SET WINDOW FRONTWINDOW() PRINTER') :
          #     nstr = astring.replace("\"", "'")
          #     nstr = nstr.rstrip("\n")
          #     k = MaketComposer(self, mylistWOR, nstr, k)

          # else:
          #     pass

        #ReOrgtLayerMapAna()