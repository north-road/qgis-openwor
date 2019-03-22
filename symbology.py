# -*- coding: iso-8859-1 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from osgeo import ogr
from measured_units import *
import math 
from math import pi,sin,cos,sqrt
from random import *
import os 
import struct
from ow_utils import *

tTypeAnaLib = {'PIE':'Camemberts', 'HALF':'Hémicycles','BAR':'Histogrammes', 'STACKED':'Histo. empilés',
               'GRADUATED':'SymbProp', 'DENSITY':'Densité points',
               'RANGES':'Classes', 'VALUES':'ValIndiv', 'COLORC':'ColorCont'}

tBrush = {'1':'NoBrush', '2':'SolidPattern', '3':'HorPattern', '4':'VerPattern',
          '5':'BDiagPattern', '6':'FDiagPattern','7':'CrossPattern','8':'DiagCrossPattern',
          '12':'Dense1Pattern', '13':'Dense2Pattern','14':'Dense3Pattern','15':'Dense4Pattern',
          '16':'Dense5Pattern', '17':'Dense6Pattern','18':'Dense7Pattern','19':'HorPattern',
          '20':'HorPattern','21':'HorPattern', '24':'VerPattern','25':'VerPattern','26':'VerPattern','29':'BDiagPattern',
          '30':'BDiagPattern','31':'BDiagPattern', '34':'FDiagPattern','35':'FDiagPattern','36':'FDiagPattern','39':'CrossPattern','40':'CrossPattern',
          '41':'CrossPattern'
         }

tBrushV2 = {'1':'no', '2':'solid', '3':'horizontal', '4':'vertical',
          '5':'b_diagonal', '6':'f_diagonal','7':'cross','8':'diagonal_x',
          '12':'dense1', '13':'dense2','14':'dense3','15':'dense4',
          '16':'dense5', '17':'dense6','18':'dense7','19':'horizontal',
          '20':'horizontal','21':'horizontal', '24':'vertical','25':'vertical','26':'vertical','29':'b_diagonal',
          '30':'b_diagonal','31':'b_diagonal', '34':'f_diagonal','35':'f_diagonal','36':'f_diagonal','39':'cross','40':'cross',
          '41':'cross'
         }

tLine = {'1':'NoPen', '2':'SolidLine', '3':'DashLine', '4':'DotLine', '5':'DashDotLine', '6':'DashDotDotLine' }

tLineV2 = {'1':'no', '2':'solid', '3':'dash', '4':'dot', '5':'dash dot', '6':'dash dot dot', '7':'dash' }


#3 Dictionnaires pour réaliser toutes les lignes MAPINFO
#Ce dictionnaire indique le nombre lignes et leur type. Ex '26': '0,1' <=> 2 lignes : 1 de type zéro et 1 de type 1. '0,5' précise le paramètre intervalle
tLineCompositeV2 = {'26':('0,1','0,5'),'39':('0,1','0,10'),'40':('0,1','0,10'),'41':('0,1','0,10'),'42':('0,1','0,15'),'43':('0,1','0,20'),'44':('0,1','0,25'),
                    '45':('0,1','0,5'),
                    '59':('2','0'),'63':('0,0','-0.5,0.5'),'64':('0,0,0','-1,0,1'),'68':('0,0','-0.5,0.5'),'73':('0,0,0','-1,0,1'),
                    '81':('0,1','0,5'),'82':('0,1','0,3'),'83':('0,1','0,3'),'86':('0,1','0,20'),'87':('0,1','0,20'),'88':('0,1','0,20'),'89':('0,1','0,10'), '90':('0,1','0,3'), '91':('0,1','0,3'), '98':('0,1','0,3'),
                    '101':('0,1,0','-0.5,3,0.5'), '106':('0,1','0,10'), '107':('0,1','0,5')
                    }

#Ce dictionnaire indique le style d'une ligne, la taille et la couleur. (fixe : '2.0' ou interprétée taille ligne '%')
# -1 indique toutes les lignes traitées à l'identique
tSubSymbLineCompositeV2 = {'26':('0','solid|%|%'),'39':('0','dash|%|%'), '40':('0','dash|%|%'),'41':('0','dash|%|%'),'42':('0','dash|%|%'), '43':('0','dash|%|%'), '44':('0','dash|%|%'),
                           '45':('0','solid|%|%'),
                           '59':('0','solid|%|%'),'73':('1','dash|2.26|%'), '68':('-1','dash|%|%'),
                           '81':('0','solid|%|0'),'82':('0','no|%|%'),'83':('0','dot|%|0'), '86':('0','solid|0.26|0'), '87':('0','solid|0.26|0'),'88':('0','solid|0.26|0'), '89':('0','solid|0.26|0'),
                           '90':('0','no|%|%'), '91':('0','dot|%|0'), '98':('0','no|%|%'), 
                           '101':('0,2','solid|0.26|0,solid|0.26|0'),'106':('0','no|%|%'), '107':('0','dot|%|0')
                           }

#Ce dictionnaire indique le marker posé sur une ligne, la taille et la couleur (fixe : '2.0' ou proportionnelle taille ligne '%')
tSubSymbSymbolCompositeV2 = {'26':('1','cross','%','%'),'39':('1','cross2','%','%'),'40':('1','cross','%','%'),'41':('1','circle','%','%'),'42':('1','circle','%','%'), '43':('1','circle','%','%'), '44':('1','circle','%','%'),
                             '45':('1','circle','0.52','%'),
                             '81':('1','circle','%','%'),'82':('1','circle','%','0'), '83':('1','circle','%','%'),'86':('1','rectangle','%','%'),'87':('1','rectangle','%','%'), '88':('1','rectangle','%','%'),
                             '89':('1','rectangle','%','%'),'90':('1','rectangle','%','%'), '91':('1','rectangle','%','%'), '98':('1','triangle','%','%'),
                             '101':('1','triangle','%','%'), '106':('1','pentagon','%','%'),'107':('1','pentagon','%','%')
                             }

tSymbol = {'32':'hard:rectangle','33':'hard:pentagon','34':'hard:circle','35':'hard:star',
           '36':'hard:regular_star','37':'hard:triangle','38':'hard:triangle','40':'hard:circle','45':'hard:equilateral_triangle',
           '47':'hard:arrow','48':'hard:arrow','49':'hard:cross','50':'hard:cross2','52':'hard:star'
          }

tSymbolV2 = {'32':'rectangle','33':'pentagon','34':'circle','35':'star',
           '36':'regular_star','37':'triangle','38':'triangle','40':'circle','45':'equilateral_triangle',
           '47':'arrow','48':'arrow','49':'cross','50':'cross2','52':'star'
          }


tStyleLabel = {1:(True, False, False), 2:(False, False, True),3:(True, False, True),
               4:(False, True, False), 5:(True, True, False),6:(False, True, True),
               7:(True, True, True)
              }

RatioMapInfo = 4

#-----------------------------------------------
# BLOC Fonctions Symbolisation VECTEUR / RASTER
#-----------------------------------------------
def Symbo2Vector(self, zLayer, sSymboLayer, nSizeMap, nSizeMapUnits, zType, nForceUnitsMap, nFixeUniProj, zForceCRS, zForceZoom):
    tSymbo = sSymboLayer.split("|")
    nLabelFieldName=""
    zIndex = int(GetIndexLayer(self, zLayer))
    zDisplayGraphic = False
    HasDefautLayerStyle, URIDefautLayerStyle = DefautLayerStyle(self, zLayer.source())
    for i in range(len(tSymbo)):
        sstring = NetStrInfos(tSymbo[i], False, True, False, False, ()) 
        if sstring.upper().find("DISPLAY GRAPHIC")!=-1: zDisplayGraphic = True
        elif sstring.upper().find('GLOBAL')!=-1 and sstring.upper().find('DISPLAY GLOBAL')==-1:
             if not HasDefautLayerStyle :            
                rendererV2 = zLayer.rendererV2()
                symbols = rendererV2.symbols() 
                symbol = symbols[0]
                astyle = sstring.split()
                if zLayer.geometryType() == QGis.Point : zSymbol = MakeMARKERV2(zDisplayGraphic, zLayer, symbol, astyle) 
                elif zLayer.geometryType() == QGis.Line : zSymbol = MakeLINEV2(zDisplayGraphic, zLayer, symbol, astyle)  
                else: zSymbol = MakeBRUSHV2(zDisplayGraphic, zLayer, symbol, astyle, False)
        elif sstring.upper().find("ZOOM (")!=-1 and sstring.upper().find("VISIBILITY ZOOM (")==-1 and  sstring.upper().find("OFF")==-1 and not zForceZoom: FixeZOOM(sstring, zLayer, nSizeMap, nSizeMapUnits, 4, 1, 2, False)
        elif sstring.upper().find('ALPHA')!=-1: FixeALPHA(sstring, zLayer, zSymbol)
        elif sstring.upper().find('LABEL ')!=-1: pass
    MakeLabels(self, zLayer, sSymboLayer, nSizeMap, nSizeMapUnits, zType, nForceUnitsMap, nFixeUniProj, zForceCRS, zForceZoom)
    self.iface.legendInterface().refreshLayerSymbology(zLayer)
    return

def SymboRaster(self, zLayer, sSymboLayer, nSizeMap, nSizeMapUnits, zForceZoom):
    tSymbo = sSymboLayer.split("|")
    for i in range(len(tSymbo)):
        sstring = NetStrInfos(tSymbo[i], False, True, False, False, ())
        if sstring.upper().find('VISIBILITY ZOOM')!=-1 and not zForceZoom:  FixeZOOM(sstring, zLayer, nSizeMap, nSizeMapUnits, 5, 2, 3, True)
        elif sstring.upper().find("ZOOM (")!=-1 and  sstring.upper().find("OFF")==-1 and not zForceZoom: FixeZOOM(sstring, zLayer, nSizeMap, nSizeMapUnits, 4, 1, 2, False)
        elif sstring.upper().find('ALPHA')!=-1: FixeALPHA(sstring, zLayer, None)
    return

#------------------------------------------
# BLOC Fonction détermination type ANATHEMA
#------------------------------------------
# FONCTION MUTUALISEE AVEC FOPENWOR.PY
def ValueTypeAna(sInfosMap, iSymboLayer):
    nTypeAna = ""
    tSymboAna = sInfosMap.split("shade")
    if len(tSymboAna)==0: tSymboAna = sInfosMap.split("SHADE") 
    tInfosAna = tSymboAna[iSymboLayer].split("|")
    tTypeAna = tInfosAna[0].split(" ")
    #la position 3 contient la variable
    #la position 4 ou 6 (si option ignore activée) le type d'analyse
    if tSymboAna[iSymboLayer].upper().find("IGNORE")!=-1: nTypeAna = str(tTypeAna[6])
    else: nTypeAna = str(tTypeAna[4].upper())
    return nTypeAna

#--------------------------------------
# BLOC Fonction Symbolisation ANATHEMA
#--------------------------------------
def SymboVectorAna(self, zLayer, sSymboLayer, nSizeMap, nSizeMapUnits, iSymboLayer, sInfosMap, zType, sSymboLayerFather, HasLabeller, zReproject, nForceUnitsMap, zLayerVisibility, zForceCRS, zForceZoom):    
    if zReproject : 
       lInfosProj4 = zForceCRS.split("|")
       zProj4Dest = lInfosProj4[3]
    else :lInfosProj4 = zLayer.crs()

    tSymboAna = sInfosMap.split("shade")
    if len(tSymboAna)==0: tSymboAna = sInfosMap.split("SHADE") 
    tInfosAna = tSymboAna[iSymboLayer].split("|")
    tTypeAna = tInfosAna[0].split(" ")
    nTypeAna = ValueTypeAna(sInfosMap, iSymboLayer)

    zDpi = self.canvas.mapRenderer().outputDpi() * 2.54
    nLabelFieldName = NetStrInfos(tTypeAna[3], True, True, False, False, ())
    vprovider = zLayer.dataProvider()
    zCanvas = self.iface.mapCanvas()

    zIndexField = -1
    zFieldStr = nLabelFieldName
    fLayer = None
    
    if nTypeAna == "PIE" or nTypeAna == "HALF" or nTypeAna == "BAR" or nTypeAna == "STACKED" :
       tFields = nLabelFieldName.split(",")
       zIndexField = 0
       for i in range(len(tFields)):
           if vprovider.fieldNameIndex( tFields[i] )== -1 :
              zIndexField = -1
              zFieldStr = str(tFields[i])
              break
    else: zIndexField = vprovider.fieldNameIndex( nLabelFieldName )

    if zIndexField!=-1:

       if nTypeAna == "VALUES" or nTypeAna == "RANGES":
          if tTypeAnaLib.has_key(nTypeAna): zLayer.setLayerName(zLayer.name() + " (" + tTypeAnaLib[nTypeAna] + " : " + nLabelFieldName + ")")
          zRampe = QgsVectorGradientColorRampV2(QColor(0,255,0), QColor(255,0,0))
          if nTypeAna == "VALUES":
             MakeAna = QgsCategorizedSymbolRendererV2()
          else:
             MakeAna = QgsGraduatedSymbolRendererV2()
             MakeAna.setMode(1) # 0-Intervalles egaux, 1-Quantile, 2-Jenks, 3-Ecart type, 4-Jolies ruptures
          MakeAna.setSourceColorRamp(zRampe)
          MakeAna.setClassAttribute(nLabelFieldName)
          zRendererV2 = zLayer.rendererV2()
             
          iAna, symbs = 0, {}

          for i in range(1, len(tInfosAna)-1,1):   
                 zStr = NetStrInfos(str(tInfosAna[i]), False, False, False, False, ("\"", "'"))

                 if zStr.upper().find("DEFAULT")==-1: 
                    zStyles = zStr.split(" ")
                    j, zValue = 0, ""
               
                    while (zStyles[j].upper()!="BRUSH") and (zStyles[j].upper()!="LINE") and (zStyles[j].upper()!="PEN") and (zStyles[j].upper()!="SYMBOL"):
                        zValue = zValue + " " + str(zStyles[j])
                        j+= 1
                    zValue = NetStrInfos(zValue, True, False, False, False, ("\"", "'"))
                    zValue = QString(zValue)

                    if zValue !="":
                        symbs[iAna] = QgsSymbolV2.defaultSymbol(zLayer.geometryType())
                        
                        #normalement, avant d'attaquer le bloc de représentation ( zIndex = -1 )
                        #il serait préférable de tester la validité de la valeur !!!
                        zValue = str(zValue)
                        zTempoD = zValue.split(":")

                        if zLayer.geometryType()== QGis.Point : MakeMARKERV2(False, MakeAna, symbs[iAna], zStr.split()) 
                        elif zLayer.geometryType() == QGis.Line : MakeLINEV2(False, MakeAna, symbs[iAna], zStr.split()) 
                        else : MakeBRUSHV2(False, MakeAna, symbs[iAna], zStr.split(), True)

                        if nTypeAna == "VALUES":
                           symbs[iAna] = QgsRendererCategoryV2(QVariant(zValue), symbs[iAna], zValue)
                           MakeAna.addCategory(symbs[iAna])
                        else:
                           MakeAna.addClass(symbs[iAna])
                           MakeAna.updateRangeLabel(0, str(float(zTempoD[0]))+ " - "+str(float(zTempoD[1]))) 
                           MakeAna.updateRangeLowerValue(0,float(zTempoD[0])) 
                           MakeAna.updateRangeUpperValue(0,float(zTempoD[1])) 

                        iAna+= 1                       
                 else:
                    break

          zLayer.setRendererV2(MakeAna)

          QgsMapLayerRegistry.instance().addMapLayers([zLayer])
          MakeVisibility(self, zLayer, zLayerVisibility) 
          self.iface.legendInterface().refreshLayerSymbology(zLayer)
          fLayer = zLayer





       elif nTypeAna == "GRADUATED":
            zID = 0
            provider = zLayer.dataProvider()
            allA=provider.attributeIndexes()
            provider.select(allA)
            feat = QgsFeature()


            zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, zLayer) 
            AnaLayer = QgsVectorLayer("Point", QString.fromLocal8Bit(CleanName(zLayer.name())) + " (SymbProp" + " : " + nLabelFieldName + ")", "memory")
            DefineLayerProj(self, zLayer, AnaLayer)
            RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)
 
            prCentro = AnaLayer.dataProvider()
            ret = prCentro.addAttributes( [ QgsField("Id", QVariant.Int), QgsField("Valeur", QVariant.Double)])
            AnaLayer.updateFieldMap()
            fet = QgsFeature()
            zID = 0

            tempo = str(tInfosAna)
            xtempo = tempo.upper()
            tInfos = tempo.split(" ")
            txInfos = xtempo.split(" ")
            zIndex = FixeIndex(0, txInfos, "BY")
            if zIndex!=-1:  zMethode = NetStrInfos(str(txInfos[zIndex]), False, False, False, False, ("'","\""))
            else: zMethode = "CONST"
            
            tempo = str(tInfos[6])
            tInfos = tempo.split(":")
            tempo = str(tInfos[0])
            arefvalue = MakeValue(tempo)
            if arefvalue == 0.0 : arefvalue = 1.0
            arefsize = float(tInfos[1]) 
            avalue = float(arefsize/arefvalue)

            #Valeurs progression barre
            NbFeat = provider.featureCount()
            if NbFeat == 0 : NbFeat = 1
            self.progressBarL.setValue(0)
            Featcounter = 0

            while provider.nextFeature(feat):
                  geom = feat.geometry()
                  attrs = feat.attributeMap()
                  oldVal = float(attrs[zIndexField].toDouble()[0])
                  valueCalc = oldVal
                  valueCalc = valueCalc / arefvalue
                  
                  #Progression de l'analyse  
                  zPercent = int(100 * float(float(Featcounter+1)/NbFeat))
                  self.progressBarL.setValue(zPercent)
                  Featcounter+= 1
  
                  fet.setGeometry(QgsGeometry(geom.centroid()))
                  fet.addAttribute(0, QVariant(zID))
                  fet.addAttribute(1, QVariant(valueCalc))
                  prCentro.addFeatures( [ fet ] )
                  AnaLayer.updateExtents()
                  zID+= 1
            
            zCentroideLayer = QgsMapLayerRegistry.instance().addMapLayers([AnaLayer])[0]
            symbols = AnaLayer.rendererV2().symbols()
            symbol = symbols[0]

            tInfos = tInfosAna[0].split(" ")

            MakeMARKERV2(False, zLayer, symbol, tInfos) 
            zField = QString("Valeur")
            AnaLayer.rendererV2().setSizeScaleField(zField)
              
            self.iface.legendInterface().refreshLayerSymbology(zCentroideLayer)
            fLayer = zCentroideLayer            




    
       elif nTypeAna == "DENSITY":
            xTypeAna = tInfosAna[0].upper()
            xTypeAna = xTypeAna.split(" ")
            tTypeAna = tInfosAna[0].split(" ")

            nSize = 0.0
            zIndex = FixeIndex(0,xTypeAna, "WIDTH")
            if zIndex != -1: nSize = AdapteRatioMapInfo(float(tTypeAna[zIndex]), False, False) 

            nType = "rectangle"
            if tTypeAna[zIndex-2]=="circle":  nType = "circle"

            nRatio = 0.0
            zIndex = FixeIndex(0,xTypeAna, "DENSITY")
            if zIndex != -1: nRatio = float(tTypeAna[zIndex])

            minimum = 0.00
            value = nLabelFieldName
            design = self.tr("field")
            vprovider = zLayer.dataProvider()
            zIndexField = vprovider.fieldNameIndex( nLabelFieldName )
            #TOTO 20 - 20130103 - remplacement GetMinMax
            tmpMax = (zLayer.maximumValue(zIndexField).toDouble()[0])
            #MyList = GetMinMax(zLayer, zIndexField)
            #nMax = float(MyList[1])

            nFillColor = 0
            zIndex = FixeIndex(0,xTypeAna, "COLOR")
            if zIndex != -1: nFillColor = tTypeAna[zIndex]

            zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, zLayer) 
            inLayer = QgsVectorLayer(unicode(zLayer.source()),  unicode(CleanName(zLayer.name())),  unicode(zLayer.dataProvider().name()))             
            DefineLayerProj(self, zLayer, inLayer)
            RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)
            fLayer = randomizePoints(self, inLayer, minimum, design, value, tmpMax, nSize, nRatio, nFillColor, nType)




       elif nTypeAna == "PIE" or nTypeAna =="HALF":
            rb=QgsRubberBand(self.iface.mapCanvas(),True)
            rb.reset()
            
            xTypeAna = tInfosAna[0].upper()
            xTypeAna = xTypeAna.split(" ")
            tInfos = tInfosAna[0].split(" ")

            zIndex = FixeIndex(0,xTypeAna, "WITH")
            zAttributs = tInfos[zIndex]
            zIndex = FixeIndex(0,xTypeAna, "ANGLE")
            zAngle = float(tInfos[zIndex])
            zIndex = FixeIndex(0,xTypeAna, "COUNTER")
            zSens = 1 if zIndex != - 1 else -1
            zFixed = FixeIndex(0,xTypeAna, "FIXED")

            xTypeAna = tInfosAna[1].upper()
            xTypeAna = xTypeAna.split(" ")
            zIndex = FixeIndex(0,xTypeAna, "UNITS")
            zUnits = NetStrInfos( str(xTypeAna[zIndex]), False, False, True, False, ("\"", "'"))
            zIndex = FixeIndex(0,xTypeAna, "SIZE")
            zSize = FixeSize(float(xTypeAna[zIndex]), zDpi, zUnits)
            
            if zFixed == -1:
               zIndex = FixeIndex(0,xTypeAna, "VALUE")
               zValue = float(xTypeAna[zIndex])
               zSize = zValue / zSize
               zIndex = FixeIndex(0,xTypeAna, "BY")
               if zIndex!=-1:  zMethode = NetStrInfos( str(xTypeAna[zIndex]), False, False, True, False, ("\"", "'"))
               else: zMethode = "CONST"
            else : zMethode = "FIXED"      

            xTypeAna = tInfosAna[2].upper().split(" ")
            zIndex = FixeIndex(0,xTypeAna, "POSITION")
            zLeftRightCenterPos = str(xTypeAna[zIndex]) if zIndex != -1 else "CENTER"
            zAboveBelowCenterPos = str(xTypeAna[zIndex+1]) if zIndex != -1 else "CENTER"


            if nTypeAna =="HALF":
                if zSens == 1 : #sens trigonométrique
                    if zLeftRightCenterPos == "LEFT" : zAngle = 180.0 
                    elif zLeftRightCenterPos == "RIGHT" : zAngle = -180.0 
                    else :
                        if zAboveBelowCenterPos == "ABOVE" or zAboveBelowCenterPos == "CENTER" : zAngle = 0.0 
                        else : zAngle = 360.0
                else: #sens horaire
                    if zLeftRightCenterPos == "LEFT" : zAngle = 540.0 
                    elif zLeftRightCenterPos == "RIGHT" : zAngle = 180.0 
                    else :
                        if zAboveBelowCenterPos == "ABOVE" or zAboveBelowCenterPos == "CENTER" : zAngle = 360.0 
                        else : zAngle = 0.0 
                        
            if zAboveBelowCenterPos == "ABOVE" : zPondCoordY = 1.00005
            elif zAboveBelowCenterPos == "BELOW"  : zPondCoordY = 0.99995
            else : zPondCoordY = 1.0

            tAttributs = zAttributs.split(",")
            nLayers, nMaxValues, nMinValues, nBrushStyle = [], [], [], []
            nMax, nMin = 0, 0

            nbFields = len(tAttributs)

            for k in range(len(tInfosAna)):
                xTypeAna = tInfosAna[k].upper()
                if xTypeAna.find("BRUSH (")!=-1 : nBrushStyle.append(xTypeAna)
            
            First = True
            zSommeMaxAttr = 0
            
            for k in range(nbFields):
                zField = NetStrInfos(tAttributs[k], True, True, False, False, ())
                zIndexField = int(vprovider.fieldNameIndex(zField))
                nLayers.append(zIndexField)
                #TOTO 20 - 20130103 - remplacement GetMinMax
                tmpMax = (zLayer.maximumValue(zIndexField).toDouble()[0])
                tmpMin = (zLayer.minimumValue(zIndexField).toDouble()[0])
                """
                MyList = GetMinMax(zLayer, zIndexField)
                tmpMin, tmpMax = float(MyList[0]), float(MyList[1])
                """
                if First:
		   nMin, nMax = tmpMin, tmpMax
     	  	   First = False
		else:
	           if tmpMin < nMin : nMin = tmpMin
	           if tmpMax > nMax : nMax = tmpMax
                  
                if zMethode == "LOG":
                   if tmpMin > 0 : tmpMin = math.log(tmpMin)
                   if tmpMax > 0 : tmpMax = math.log(tmpMax)
                elif zMethode == "SQRT":
                   if tmpMin > 0 : tmpMin = math.sqrt(tmpMin)
                   if tmpMax > 0 : tmpMax = math.sqrt(tmpMax)
                   
                zSommeMaxAttr = zSommeMaxAttr + tmpMax 
                nMinValues.append( tmpMin ) 
                nMaxValues.append( tmpMax ) 

            zID = 0
            provider = zLayer.dataProvider()
            allA=provider.attributeIndexes()
            provider.select(allA)
            feat = QgsFeature()

            zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, zLayer)
            AnaLayer = QgsVectorLayer("Polygon", QString.fromLocal8Bit(CleanName(zLayer.name())) + " (Camemberts" + " : " + str(zAttributs) + ")", "memory")
            DefineLayerProj(self, zLayer, AnaLayer)
            RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)

            prCentro = AnaLayer.dataProvider()
            ret = prCentro.addAttributes( [ QgsField("Id", QVariant.Int)])
            ret = prCentro.addAttributes( [ QgsField("Valeur", QVariant.Double)])
            ret = prCentro.addAttributes( [ QgsField("Categorie", QVariant.String)])
            AnaLayer.updateFieldMap()

            fet = QgsFeature()
            zID = 0
            ConstPoints = 20

            if nTypeAna == "PIE": DimObj = (2.0 * pi )
            else: DimObj = pi
            zStart = (DimObj * float(zAngle / 360))

            QApplication.setOverrideCursor( QCursor( Qt.WaitCursor ) )

            #Valeurs progression barre
            NbFeat = provider.featureCount()
            if NbFeat == 0 : NbFeat = 1
            self.progressBarL.setValue(0)
            Featcounter = 0

            while provider.nextFeature(feat):
                  geom = feat.geometry()
                  attrs = feat.attributeMap()
                  MyCenter = geom.centroid().asPoint() 
                  refX, refY = float(MyCenter.x()), float(MyCenter.y()*zPondCoordY)
                  MyCenter = QgsPoint(refX, refY)
   
                  SommeValueAtt, SommeValueAttM = 0, 0
                  
                  for iAtt in range(len(nLayers)):
                      IdField = int(nLayers[iAtt])
                      zValueAttr = attrs[IdField].toDouble()[0]
                      zValueAttrM = zValueAttr
                      if zMethode == "LOG":
                         if zValueAttr > 0 : zValueAttrM = math.log(zValueAttr)
                      elif zMethode == "SQRT":
                         if zValueAttr > 0 : zValueAttrM = math.sqrt(zValueAttr)
                      SommeValueAtt = SommeValueAtt + zValueAttr
                      SommeValueAttM = SommeValueAttM + zValueAttrM
                      
                      if iAtt==0:  zMaxAttr = zValueAttr
                      else:
                         if zValueAttr > zMaxAttr : zMaxAttr = zValueAttr

                  if zFixed > -1: zSizeCircle = int(zSize) * 2.5
                  else: zSizeCircle = int(zSize * (SommeValueAttM / zSommeMaxAttr)) * 2.5

                       
                  Xcoord = float(refX + zSizeCircle)
                  Ycoord = float(refY + zSizeCircle)
                  SizeCirlePoint = QgsPoint( Xcoord, Ycoord)
                  r = sqrt(MyCenter.sqrDist(SizeCirlePoint))

                  if zReproject: zUnits = int(self.iface.mapCanvas().mapRenderer().destinationCrs().mapUnits())
                  
                  zPosition = zStart
                  First = True
                  #Il faut calculer la répartition entre les attributs (indépendant de la méthode -> taille cercle)
                  for iAtt in range(len(nLayers)): 
                      IdField = int(nLayers[iAtt])
                      zValueAttr = attrs[IdField].toDouble()[0]
                      if zValueAttr != 0 :                       
                          zRatio = float(zValueAttr/SommeValueAtt)
                          zAngle = zPosition + (zSens * (DimObj * zRatio))
                          rb.addPoint(MyCenter)
                          zPoints = int(ConstPoints * zRatio)
                          if zPoints < 1: zPoints = 1
                          zPasAngle = zSens * (float((zAngle - zPosition) / zPoints))

                          if zSens == 1: #sens trigonométrique
                             while zPosition < zAngle :
                                   Xcoord = float(refX+r*cos(zPosition))
                                   Ycoord = float(refY+r*sin(zPosition))
                                   rb.addPoint(QgsPoint(Xcoord, Ycoord))
                                   if First : FirstPoint, First = QgsPoint(Xcoord, Ycoord), False
                                   zPosition = zPosition + (zSens * zPasAngle)
                             zAdjust = abs((zPosition - zAngle)/2)
                             zPosition = zPosition - (zSens * zAdjust)
    
                             if iAtt == 0 : 
                                 Xcoord = float(refX+r*cos(zPosition))
                                 Ycoord = float(refY+r*sin(zPosition))
                                 rb.addPoint(QgsPoint(Xcoord, Ycoord))
                         
                          else: #sens horaire
                             while zPosition > zAngle :
                                   Xcoord = float(refX+r*cos(zPosition))
                                   Ycoord = float(refY+r*sin(zPosition))
                                   rb.addPoint(QgsPoint(Xcoord, Ycoord))
                                   if First : FirstPoint, First = QgsPoint(Xcoord, Ycoord), False
                                   zPosition = zPosition + (zSens * zPasAngle)
                             zAdjust = abs((zPosition - zAngle)/2)
                             zPosition = zPosition - (zSens * zAdjust)

                             if iAtt == 0 : 
                                 Xcoord = float(refX+r*cos(zPosition))
                                 Ycoord = float(refY+r*sin(zPosition))
                                 rb.addPoint(QgsPoint(Xcoord, Ycoord))

                          if iAtt == len(nLayers)-1 and nTypeAna == "PIE": rb.addPoint(FirstPoint)

                          if iAtt == len(nLayers)-1 and nTypeAna == "HALF":
                             zPosition = zStart + (zSens * DimObj)
                             Xcoord = float(refX+r*cos(zPosition))
                             Ycoord = float(refY+r*sin(zPosition))
                             rb.addPoint(QgsPoint(Xcoord, Ycoord))

                          coords = []
                          [coords.append(rb.getPoint(0,ki)) for ki in range(rb.numberOfVertices())]
                          g=QgsGeometry().fromPolygon([coords])
                          rb.reset()

                      else: g = QgsGeometry()

                      #Progression de l'analyse  
                      zPercent = int(100 * float(float(Featcounter+1)/NbFeat))
                      self.progressBarL.setValue(zPercent)
                      Featcounter+= 1
                      
                      fet.setGeometry(g)
                      fet.addAttribute(0, QVariant(zID))
                      fet.addAttribute(1, QVariant(zValueAttr))
                      fet.addAttribute(2, QVariant(tAttributs[iAtt]))    
                      prCentro.addFeatures( [ fet ] )
                      AnaLayer.updateExtents()
                      zID+= 1
       
            rb.reset()
            QgsMapLayerRegistry.instance().addMapLayers([AnaLayer])

            symbs = {}
            zRampe = QgsVectorGradientColorRampV2(QColor(0,255,0), QColor(255,0,0))
            MakeAna = QgsCategorizedSymbolRendererV2()
            MakeAna.setSourceColorRamp(zRampe)
            MakeAna.setClassAttribute("Categorie")
            zRendererV2 = AnaLayer.rendererV2()

            for iAtt in range(len(nLayers)):
                symbs[iAtt] = QgsSymbolV2.defaultSymbol(AnaLayer.geometryType())
                MakeBRUSHV2(False, MakeAna, symbs[iAtt], nBrushStyle[iAtt].split(), True)
                symbs[iAtt] = QgsRendererCategoryV2(QString(tAttributs[iAtt]), symbs[iAtt], QString(tAttributs[iAtt]+" ("+TypeMethode(zMethode)+")"))
                MakeAna.addCategory(symbs[iAtt])
            AnaLayer.setRendererV2(MakeAna)


            self.iface.legendInterface().refreshLayerSymbology(AnaLayer)
            QApplication.restoreOverrideCursor()
            fLayer = AnaLayer




       elif nTypeAna == "BAR" or nTypeAna =="STACKED":

            rb=QgsRubberBand(self.iface.mapCanvas(),True)
            rb.reset()
            
            xTypeAna = tInfosAna[0].upper().split(" ")
            tInfos = tInfosAna[0].split(" ")
            zIndex = FixeIndex(0,xTypeAna, "WITH")
            zAttributs = tInfos[zIndex]
            zFixed = FixeIndex(0,xTypeAna, "FIXED")

            xTypeAna = tInfosAna[1].upper()
            xTypeAna = xTypeAna.split(" ")                
            zIndex = FixeIndex(0,xTypeAna, "UNITS")
            zUnits = NetStrInfos( str(xTypeAna[zIndex]), False, False, True, False, ("\"", "'"))
            zIndex = FixeIndex(0,xTypeAna, "SIZE")
            zSize = FixeSize(float(xTypeAna[zIndex]), zDpi, zUnits)

            xTypeAna = tInfosAna[2].upper()
            xTypeAna = xTypeAna.split(" ")
            zIndex = FixeIndex(0,xTypeAna, "WIDTH")
            zSizeBase = FixeSize(float(xTypeAna[zIndex]), zDpi, zUnits)
    
            if zFixed == -1:
               xTypeAna = tInfosAna[1].upper()
               xTypeAna = xTypeAna.split(" ")
               zIndex = FixeIndex(0,xTypeAna, "VALUE")
               zValue = float(xTypeAna[zIndex])
               if zValue > 1000000 : zSize = zValue / (zSize * RatioMapInfo)
               else :  zSize = zValue / zSize
               zIndex = FixeIndex(0,xTypeAna, "BY")
               if zIndex!=-1: zMethode = NetStrInfos( str(xTypeAna[zIndex]), False, False, True, False, ("\"", "'"))
               else: zMethode = "CONST"
            else:  zMethode = "FIXED"

            xTypeAna = tInfosAna[2].upper().split(" ")
            zIndex = FixeIndex(0,xTypeAna, "POSITION")
            zLeftRightCenterPos = str(xTypeAna[zIndex]) if zIndex != -1 else "CENTER"
            zAboveBelowCenterPos = str(xTypeAna[zIndex+1]) if zIndex != -1 else "CENTER"
            
            zSignCoordX = -1 if zLeftRightCenterPos == "LEFT" or zLeftRightCenterPos == "CENTER" else 1
            zInverse = -1 if (zLeftRightCenterPos == "LEFT" or zLeftRightCenterPos == "RIGHT") else 1
            if zAboveBelowCenterPos == "ABOVE" : zPondCoordY = 1.005
            elif zAboveBelowCenterPos == "BELOW"  : zPondCoordY = 0.995
            else : zPondCoordY = 1.0

            tAttributs = zAttributs.split(",")
            nLayers, nMaxValues, nMinValues, nBrushStyle = [], [], [], []
            nMax, nMin = 0, 0
            nbFields = len(tAttributs)

            for k in range(len(tInfosAna)):
                xTypeAna = tInfosAna[k].upper()
                if xTypeAna.find("BRUSH (")!=-1 : nBrushStyle.append(xTypeAna)

            First, zSommeMaxAttr = True, 0
            
            for k in range(nbFields):
                zField = NetStrInfos(tAttributs[k], True, True, False, False, ())
                zIndexField = int(vprovider.fieldNameIndex(zField))
                nLayers.append(zIndexField)
                #TOTO 20 - 20130103 - remplacement GetMinMax
                tmpMax = (zLayer.maximumValue(zIndexField).toDouble()[0])
                tmpMin = (zLayer.minimumValue(zIndexField).toDouble()[0])
                """
                MyList = GetMinMax(zLayer, zIndexField)
                tmpMin, tmpMax = float(MyList[0]), float(MyList[1])
                """
                if First:
		   nMin, nMax, First = tmpMin, tmpMax, False
		else:
	           if tmpMin < nMin : nMin = tmpMin
	           if tmpMax > nMax : nMax = tmpMax
                if zMethode == "LOG":
                   if tmpMin > 0 : tmpMin = math.log(tmpMin)
                   if tmpMax > 0 : tmpMax = math.log(tmpMax)
                elif zMethode == "SQRT":
                   if tmpMin > 0 : tmpMin = math.sqrt(tmpMin)
                   if tmpMax > 0 : tmpMax = math.sqrt(tmpMax)
                zSommeMaxAttr = zSommeMaxAttr + tmpMax 
                nMinValues.append( tmpMin ) 
                nMaxValues.append( tmpMax ) 

            zID = 0
            provider = zLayer.dataProvider()
            allA=provider.attributeIndexes()
            provider.select(allA)
            feat = QgsFeature()

            zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, zLayer)
            AnaLayer = QgsVectorLayer("Polygon", QString.fromLocal8Bit(CleanName(zLayer.name()))+ " (Histogrammes" + " : " +str(zAttributs) + ")", "memory")
            DefineLayerProj(self, zLayer, AnaLayer)
            RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)

            prCentro = AnaLayer.dataProvider()
            ret = prCentro.addAttributes( [ QgsField("Id", QVariant.Int)])
            ret = prCentro.addAttributes( [ QgsField("Valeur", QVariant.Double)])
            ret = prCentro.addAttributes( [ QgsField("Categorie", QVariant.String)])    
            AnaLayer.updateFieldMap()

            fet = QgsFeature()
            zID = 0
            QApplication.setOverrideCursor(QCursor( Qt.WaitCursor ))

            #Valeurs progression barre
            NbFeat = provider.featureCount()
            if NbFeat == 0 : NbFeat = 1
            self.progressBarL.setValue(0)
            Featcounter = 1            
            zSizeBase = zSizeBase * 100
            zPointDep = zSignCoordX * float(zSizeBase/2)

            while provider.nextFeature(feat):
                  geom = feat.geometry()
                  attrs = feat.attributeMap()
                  
                  SommeValueAtt, SommeValueAttM = 0, 0
                  
                  for iAtt in range(len(nLayers)):
                      IdField = int(nLayers[iAtt])
                      zValueAttr = attrs[IdField].toDouble()[0]
                      zValueAttrM = zValueAttr
                      if zMethode == "LOG":
                         if zValueAttr > 0 : zValueAttrM = math.log(zValueAttr)
                      elif zMethode == "SQRT":
                         if zValueAttr > 0 : zValueAttrM = math.sqrt(zValueAttr)
                      SommeValueAtt = SommeValueAtt + zValueAttr
                      SommeValueAttM = SommeValueAttM + zValueAttrM
                      if iAtt==0: zMaxAttr = zValueAttr
                      else:
                         if zValueAttr > zMaxAttr : zMaxAttr = zValueAttr
                   
                  if zFixed > -1:  zSizeBar = zSize * 100
                  else:
                     zSizeBar = float(zSize * (SommeValueAttM / zSommeMaxAttr))
                     if zSizeBar < 5000 : zSizeBar = zSizeBar * 100 

                  #Il faut calculer la répartition entre les attributs (indépendant de la méthode -> taille histogramme)
                  LastHauteur = 0
                  zSaveSizeBase = zSizeBase
                  
                  for iAtt in range(len(nLayers)): 
                      IdField = int(nLayers[iAtt])
                      zValueAttr = attrs[IdField].toDouble()[0]
                      if zValueAttr != 0 : 
                         zHauteur =  round(((zValueAttr/SommeValueAtt)* zSizeBar),2)
                         
                         if nTypeAna == "BAR" :
                            if zInverse == -1 :
                               Xcoord = float(geom.centroid().asPoint().x())+ zPointDep
                               Ycoord = zPondCoordY * float(geom.centroid().asPoint().y())+LastHauteur
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               Xcoord = float(Xcoord + (zSignCoordX * zHauteur))
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               Ycoord = float(Ycoord+zSizeBase)
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               Xcoord = float(Xcoord-(zSignCoordX * zHauteur)) 
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               LastHauteur = LastHauteur + zSizeBase

                            else :
                               Xcoord = float(geom.centroid().asPoint().x()+zPointDep+(iAtt * zSizeBase))
                               Ycoord = zPondCoordY * float(geom.centroid().asPoint().y())
                               MyPoint = zTransform.transform(QgsPoint( Xcoord, Ycoord)) 
                               rb.addPoint(MyPoint)

                               Ycoord = float(Ycoord+zHauteur)
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               Xcoord = float(Xcoord+(zSignCoordX * zSizeBase))
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               Ycoord =  float(Ycoord-zHauteur)
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)

                               LastHauteur = LastHauteur + zHauteur

                         else :
                            if zInverse == -1 :
                               Xcoord = float(geom.centroid().asPoint().x())+ zPointDep + (zSignCoordX * LastHauteur)
                               Ycoord = zPondCoordY * float(geom.centroid().asPoint().y())
                               MyPoint = zTransform.transform(QgsPoint( Xcoord, Ycoord)) 
                               rb.addPoint(MyPoint)
                                
                               Xcoord = float(Xcoord + (zSignCoordX *zHauteur)) 
                               MyPoint = QgsPoint( Xcoord, Ycoord)  
                               rb.addPoint(MyPoint)

                               Ycoord = float(Ycoord+zSizeBase)
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)

                               Xcoord =  float(Xcoord - (zSignCoordX *zHauteur))                          
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)

                            else:

                               Xcoord = float(geom.centroid().asPoint().x()+ zPointDep)
                               Ycoord = zPondCoordY * float(geom.centroid().asPoint().y()+LastHauteur)
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)

                               Ycoord = float(Ycoord+zHauteur)
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)

                               Xcoord = float(Xcoord+zSizeBase)
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)

                               Ycoord = float(Ycoord-zHauteur)
                               MyPoint = QgsPoint( Xcoord, Ycoord) 
                               rb.addPoint(MyPoint)
                                              
                            LastHauteur = LastHauteur + zHauteur
                      
                         coords = []    
                         [coords.append(rb.getPoint(0,ki)) for ki in range(rb.numberOfVertices())]
                         g=QgsGeometry().fromPolygon([coords])
                         rb.reset()
                         
                      else: g = QgsGeometry()

                      fet.setGeometry(g)
                      fet.addAttribute(0, QVariant(zID))
                      fet.addAttribute(1, QVariant(zValueAttr))
                      fet.addAttribute(2, QVariant(tAttributs[iAtt]))    
                      prCentro.addFeatures( [ fet ] )
                      AnaLayer.updateExtents()
                      zID+= 1
                   
                  #Progression de l'analyse  
                  zPercent = int(100 * float(float(Featcounter+1)/NbFeat))
                  self.progressBarL.setValue(zPercent)
                  Featcounter+= 1


            rb.reset()
            QgsMapLayerRegistry.instance().addMapLayers([AnaLayer])

            symbs = {}
            zRampe = QgsVectorGradientColorRampV2(QColor(0,255,0), QColor(255,0,0))
            MakeAna = QgsCategorizedSymbolRendererV2()
            MakeAna.setSourceColorRamp(zRampe)
            MakeAna.setClassAttribute("Categorie")
            zRendererV2 = AnaLayer.rendererV2()

            for iAtt in range(len(nLayers)):
                symbs[iAtt] = QgsSymbolV2.defaultSymbol(AnaLayer.geometryType())
                MakeBRUSHV2(False, MakeAna, symbs[iAtt], nBrushStyle[iAtt].split(), True)
                symbs[iAtt] = QgsRendererCategoryV2(QString(tAttributs[iAtt]), symbs[iAtt], QString(tAttributs[iAtt]+" ("+TypeMethode(zMethode)+")"))
                MakeAna.addCategory(symbs[iAtt])

            AnaLayer.setRendererV2(MakeAna)
            
            self.iface.legendInterface().refreshLayerSymbology(AnaLayer)
            QApplication.restoreOverrideCursor()
            fLayer = AnaLayer            
          
       else:

            Symbo2Vector(self, zLayer, sSymboLayer, nSizeMap, nSizeMapUnits,zType, nForceUnitsMap, zReproject, zForceCRS, zForceZoom)   
            fLayer = zLayer   
    else:
       msg = "L'attribut : <b>" + zFieldStr + "</b><br>n'a pas été trouvé dans le fichier <b>" + str(zLayer.name()) + "</b> en entrée.<br>Analyse <b>" + str(tTypeAnaLib[nTypeAna]) + "</b> non restituable."
       QMessageBox.information(None,"Erreur de structure ", msg)

    return fLayer

#----------------------------------------------
# FONCTION CREATION INDEX SPATIAL
# Utilisée pour l'analyse par densité de points
#----------------------------------------------
def createIndex( provider ):
    feat, index = QgsFeature(), QgsSpatialIndex()
    provider.rewind()
    while provider.nextFeature( feat ):
        index.insertFeature( feat )
    return index

#------------------------------
# FONCTIONS RASTER MIG
#------------------------------
def SymboRasterMIG(self, zLayer, zURL, sSymboLayer, nAnaMIG, nLabelFieldName, nSizeMap, nSizeMapUnits, sInfosMap, vType, nForceUnitsMap):    
    vprovider = zLayer.dataProvider()
    zIndexField = vprovider.fieldNameIndex( nLabelFieldName )
    zLayer.setLayerName(zLayer.name() + " (" +tTypeAnaLib["COLORC"]+ " : " + nLabelFieldName + ")")
  
    QgsMapLayerRegistry.instance().addMapLayers([zLayer])
    self.iface.legendInterface().refreshLayerSymbology(zLayer)
    legendTree = self.iface.mainWindow().findChild(QDockWidget, "Legend").findChild(QTreeWidget)
    itemOr = legendTree.currentItem()

    textension = os.path.splitext(zURL)
    extension = textension[len(textension)-1].lower()
    zORURL = zURL
    zURL = zURL[0:len(zURL)-len(extension)]+"_interpolate.TIF"


    zExt = zLayer.extent()
    #Sans objet pour l'instant
    zNbCellX, zNbCellY = 400, 400
    zCellSizeX = float(abs(zExt.xMaximum() - zExt.xMinimum())/zNbCellX)
    zCellSizeY = float(abs(zExt.yMaximum() - zExt.yMinimum())/zNbCellY)

    zCommand = "gdal_grid -zfield " + nLabelFieldName + " -l Us_rain -a invdist:power=4.0:smothing=3.0:radius1=0.0:radius2=0.0:angle=0.0:max_points=10:min_points=5:nodata=0.0 -of GTiff"
    zCommand = zCommand + " " + zORURL + " " + zURL 
    os.system(zCommand)

    #puis symbolisation : Pseudo couleur
    if os.path.exists(zURL):
        zLayerMIG = self.iface.addRasterLayer(zURL, zLayer.name() + "_MIG_TIF")
        QgsMapLayerRegistry.instance().addMapLayers([zLayerMIG])

        QGISVersionID = 0
        try: QGISVersionID = int(unicode( QGis.QGIS_VERSION_INT ))
        except: QGISVersionID = int(unicode( QGis.qgisVersion )[ 0 ])
    
        if QGISVersionID <= 10800:
           zLayerMIG.setDrawingStyle(QgsRasterLayer.SingleBandPseudoColor)
           zLayerMIG.setColorShadingAlgorithm(QgsRasterLayer.PseudoColorShader)
           FixeALPHA("alpha 125", zLayerMIG, None)
        else:
           myRampItemList = []
           myTransparencyList = []
           
           zMin = zLayerMIG.dataProvider().minimumValue(1)
           zMax = zLayerMIG.dataProvider().maximumValue(1)
           zInt = (zMax - zMin)/4
           
           myRampItem = QgsColorRampShader.ColorRampItem(zMin, QColor(0,0,255), str(zMin))
           myRampItemList.append(myRampItem)
           myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
           myPixel.min = 0
           myPixel.max = zMin
           myPixel.percentTransparent = 50
           myTransparencyList.append(myPixel)

           myRampItem = QgsColorRampShader.ColorRampItem(zInt, QColor(0,50,225), str(zInt))
           myRampItemList.append(myRampItem)
           myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
           myPixel.min = zMin
           myPixel.max = zInt
           myPixel.percentTransparent = 50
           myTransparencyList.append(myPixel)

           myRampItem = QgsColorRampShader.ColorRampItem(2*zInt, QColor(0,100,150), str(2*zInt))
           myRampItemList.append(myRampItem)
           myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
           myPixel.min = zInt
           myPixel.max = 2*zInt
           myPixel.percentTransparent = 50
           myTransparencyList.append(myPixel) 

           myRampItem = QgsColorRampShader.ColorRampItem(3*zInt, QColor(0,150,75), str(3*zInt))
           myRampItemList.append(myRampItem)
           myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
           myPixel.min = 2*zInt
           myPixel.max = 3*zInt
           myPixel.percentTransparent = 50
           myTransparencyList.append(myPixel)            
           
           myRampItem = QgsColorRampShader.ColorRampItem(zMax, QColor(0,200,0), str(zMax))
           myRampItemList.append(myRampItem)
           myPixel = QgsRasterTransparency.TransparentSingleValuePixel()
           myPixel.min = 3*zInt
           myPixel.max = zMax
           myPixel.percentTransparent = 50
           myTransparencyList.append(myPixel)

           myRasterShader = QgsRasterShader()
           myColorRampShader = QgsColorRampShader()
           myColorRampShader.setColorRampType(QgsColorRampShader.INTERPOLATED)
           myColorRampShader.setColorRampItemList(myRampItemList)

           myRasterShader.setRasterShaderFunction(myColorRampShader)
           myRenderer = QgsSingleBandPseudoColorRenderer(zLayerMIG.dataProvider(), 1,  myRasterShader)
           zLayerMIG.setRenderer(myRenderer)

           myRenderer = zLayerMIG.renderer()
           myTransparency = QgsRasterTransparency()
           myTransparency.setTransparentSingleValuePixelList(myTransparencyList)
           myRenderer.setRasterTransparency(myTransparency)
           
           
        self.iface.legendInterface().refreshLayerSymbology(zLayerMIG)
        self.iface.mapCanvas().refresh()

        
    return

#-----------------------------------
#-----------------------------------
# FONCTIONS MUTUALISEES 
#-----------------------------------
#-----------------------------------

#==================================================
# FOCNTIONS CREATION COUCHE AVEC CRS COUCHE ORIGINE
#==================================================
def ChangeSETTINGS(self, zLayer):
    settings = QSettings()
    oldProjectionSetting = settings.value("Projections/defaultBehaviour") 
    oldProjectionCRSValue = settings.value("Projections/layerDefaultCrs") 
    settings.setValue("Projections/defaultBehaviour", "useGlobal")
    if zLayer == None : zProjEPSG = str(self.iface.mapCanvas().mapRenderer().destinationCrs().authid())
    else : zProjEPSG = str(zLayer.crs().authid())
    settings.setValue("Projections/layerDefaultCrs", zProjEPSG)
    settings.sync()
    return oldProjectionSetting, oldProjectionCRSValue

def DefineLayerProj(self, zLayer, CibleLayer):
    if zLayer == None : CibleLayer.setCrs(self.iface.mapCanvas().mapRenderer().destinationCrs()) 
    else : CibleLayer.setCrs(zLayer.crs())
    CibleLayer.updateFieldMap()

def RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue):
    settings = QSettings()
    if zProjectionSetting!= "" : settings.setValue("Projections/defaultBehaviour", zProjectionSetting)
    if zProjectionCRSValue!= "" : settings.setValue("Projections/layerDefaultCrs", zProjectionCRSValue)

    
#----------------------------------
# FONCTION ETIQUETTES / ANNOTATIONS
#----------------------------------
def MakeLabels(self, zLayer, sSymboLayer, nSizeMap, nSizeMapUnits, zType, nForceUnitsMap, zReproject, zForceCRS, zForceZoom):
    tSymbo = sSymboLayer.split("|")
    nLabelFieldName=""
    zIndex = int(GetIndexLayer(self, zLayer))
    HasMakeLabeller = False
    vprovider = zLayer.dataProvider()
    zCanvas = self.iface.mapCanvas()

    for i in range(len(tSymbo)):
        sstring = NetStrInfos(tSymbo[i], True, True, False, False, ()) 
        x = sstring.upper()
        
        if x.startswith('ACTIVATE'):
            break

        elif x.find('WITH')!=-1:
            nLabelFieldName = NetStrInfos(sstring, True, True, False, False, ("WITH", "With"))
            if nLabelFieldName.find("Proper$")!=-1:
               nLabelFieldName = NetStrInfos(nLabelFieldName,True, True, False, False, ("PROPER$", "Proper$","(",")"))
               

        elif x.find('LABEL ')!=-1:
            axstyle = x.split()
            zFontAlignement = str(axstyle[4])
            atempostr = NetStrInfos(axstyle[5], False, False, True, False, ()) 
            if atempostr!="FONT": zFontAlignement = zFontAlignement + str(axstyle[5])
            aFontProperties = MakePropertiesFONT(6, str(axstyle[6]), axstyle)
            aFontProperties = NetStrInfos(aFontProperties, False, False, False, False, ("(", ")"))
            aFont = aFontProperties.split(",")

            zMakeHalo = -1
            if len(aFont)== 5 :
               #il y a un fond ou un halo
               zMakeHalo = ValCarac(int(aFont[1]),2)
               zFontColor = long(aFont[len(aFont)-2]) #InvRGB(long(aFont[len(aFont)-2]))
               zBackColor = long(aFont[len(aFont)-1]) #InvRGB(long(aFont[len(aFont)-1]))
            else:
               zFontColor = long(aFont[len(aFont)-1]) #InvRGB(long(aFont[len(aFont)-1]))  
            zFontSize = int(aFont[2])
            zFontCarac = ValCarac(int(aFont[1]),0)

            zFontBold = False                              
            zFontUnderline = False
            zFontItalic = False
            if tStyleLabel.has_key(zFontCarac):
               TheStyle = tStyleLabel[zFontCarac]
               zFontBold = TheStyle[0]
               zFontUnderline = TheStyle[1]
               zFontItalic = TheStyle[2]
              
            zFont = NetStrInfos(aFont[0], True, True, False, True, ("\"", "'"))

            
        elif x.find('PARALLEL')!=-1:
           axstyle = x.split() 
           aEtiquette = NetStrInfos(axstyle[3], True, True, True, False, ())
           tempoTest = False

           
           if aEtiquette == "ON" and nLabelFieldName!="":
              zIndexField = vprovider.fieldNameIndex(nLabelFieldName)
           
              if zIndexField == -1 :
                 nLabelFieldName = CleanExp(zLayer, nLabelFieldName)
                 zExpression = QgsExpression(nLabelFieldName) 
                 zIndexField = 0
                 tempoTest = True
 
              isFontBold = "true" if zFontBold else "false"
              isFontUnderline = "true" if zFontUnderline else "false"
              isFontItalic = "true" if zFontItalic else "false"

              zLayer.setUsingRendererV2(1)
              zLayer.setCustomProperty("labeling","pal" ) 
              zLayer.setCustomProperty("labeling/fontSize",str(zFontSize))
              zLayer.setCustomProperty("labeling/fontFamily",zFont )
              zLayer.setCustomProperty("labeling/fontWeight","75" )
              zLayer.setCustomProperty("labeling/fontUnderline",isFontUnderline )
              zLayer.setCustomProperty("labeling/fontItalic",isFontItalic )
              zLayer.setCustomProperty("labeling/multiLineLabels","true" )

              if (zFontAlignement.find("CENTER"))!= -1 : zFontAlignement = "1"
              elif (zFontAlignement.find("LEFT"))!=-1 : zFontAlignement = "0"
              else : zFontAlignement = "2"
              
              zLayer.setCustomProperty("labeling/multilineAlign", "1")
              zLayer.setCustomProperty("labeling/enabled","true" ) 

              if tempoTest : zLayer.setCustomProperty("labeling/isExpression","true" )
              else : zLayer.setCustomProperty("labeling/isExpression","false" ) 
              textColorR, textColorG, textColorB = StrRGB(zFontColor)
                 
              zLayer.setCustomProperty("labeling/textColorR",textColorR)
              zLayer.setCustomProperty("labeling/textColorG",textColorG)
              zLayer.setCustomProperty("labeling/textColorB",textColorB)

              if zMakeHalo !=-1:
                 bufferColorR, bufferColorG, bufferColorB = StrRGB(zBackColor)
                 zLayer.setCustomProperty("labeling/bufferColorR",bufferColorR)
                 zLayer.setCustomProperty("labeling/bufferColorG",bufferColorG)
                 zLayer.setCustomProperty("labeling/bufferColorB",bufferColorB)
                 zLayer.setCustomProperty("labeling/bufferSize",str(float(0.1*zFontSize)))
              else:
                 zLayer.setCustomProperty("labeling/bufferColorR","0")
                 zLayer.setCustomProperty("labeling/bufferColorG","0")
                 zLayer.setCustomProperty("labeling/bufferColorB","0")
                 zLayer.setCustomProperty("labeling/bufferSize","0")

              zLayer.setCustomProperty("labeling/plussign", "false")
              zLayer.setCustomProperty("labeling/fieldName", nLabelFieldName)

              self.iface.setActiveLayer(zLayer)
              zContext = self.iface.mapCanvas().mapRenderer().rendererContext()
              zLayer.triggerRepaint()
              self.iface.legendInterface().refreshLayerSymbology( zLayer ) 
              HasMakeLabeller = True
   

     
        elif x.find('VISIBILITY ZOOM')!=-1 and not zForceZoom:  FixeZOOM(x, zLayer, nSizeMap, nSizeMapUnits, 5, 2, 3, True) 


        #ANNOTATIONS <=> etiquettes personnalisees
        elif x.find("OBJECT")!=-1:
            zZoomPropertiesAnnotations = x.split()
            astyle = sstring.split()
            zIndex = FixeIndex(0,zZoomPropertiesAnnotations, "OBJECT")
            zID = int(zZoomPropertiesAnnotations[zIndex])

            IsCallout = False
            zIndexA = FixeIndex(0,zZoomPropertiesAnnotations, "CALLOUT")
            if zIndexA==-1: zIndexA = FixeIndex(0,zZoomPropertiesAnnotations, "ANCHOR")
            else: IsCallout = True
            X,Y = -1,-1

            if zIndexA > -1 and IsCallout :
               zCoordXY = NetStrInfos(zZoomPropertiesAnnotations[zIndexA], True, True, False, False, ("(", ")"))
               MyCoord = zCoordXY.split(",")
               X = float(MyCoord[0])
               Y = float(MyCoord[1])
            else:   
               feat = QgsFeature()
               index2 = vprovider.fieldNameIndex(nLabelFieldName)
               vprovider.featureAtId(zID,feat,True,[index2])
               geom = feat.geometry()
               X = float(geom.centroid().asPoint().x())
               Y = float(geom.centroid().asPoint().y())
            
            zIndex = FixeIndex(0,zZoomPropertiesAnnotations, "TEXT")
            zText = "Une Annotation !"
            nbHauteur = 1
            
            if zIndex > -1:
               zText = str(astyle[zIndex])
               NbCarac = CountCaractere(zText, "'")
               if NbCarac == 1:
                  j = zIndex+1
                  atempostr = str(astyle[j])
                  while atempostr.find("'")==-1:
                        zText = zText + " " + atempostr
                        j+= 1
                        atempostr = str(astyle[j])
                        
                  zText = zText + " " + str(astyle[j])
            else:
               zIndexField = vprovider.fieldNameIndex(nLabelFieldName)
               if zIndexField!=-1:
                  index2 = vprovider.fieldNameIndex(nLabelFieldName)
                  feat = QgsFeature()
                  vprovider.featureAtId(zID,feat,True,[index2])
                  zText = str(feat.attributeMap()[index2].toString())
                  
            zText = NetStrInfos(zText, True, True, False, False, ("'"))
            zText = zText.replace("\\n", "<br>")
            zmaxlen = len(zText)
            zfacteurH = 20
            zfacteurL = 10
            zFontBold = False                              
            zFontUnderline = False
            zFontItalic = False

            zIndex = FixeIndex(0,zZoomPropertiesAnnotations, "FONT")
            zBackColorV = QColor(255,255,255)
            zBackColor = rgb_to_hex(16777215)
            zForeColorV = QColor(0,0,0)
            zForeColor = rgb_to_hex(0)
            zFont = "MS Shell Dlg 2"
            zFontSize = 8.0
            
            if zIndex!=-1:
               nProp = NetStrInfos(zZoomPropertiesAnnotations[zIndex], True, True, False, False, ("(", ")"))
               nProp = nProp.split(",")

               zFont = NetStrInfos(nProp[0], True, True, False, True, ("\"", "'"))
               zFontCarac = ValCarac(int(nProp[1]),0)
               #nProp[1]:concerne le halo, n'est pas joué

               if tStyleLabel.has_key(zFontCarac):
                  TheStyle = tStyleLabel[zFontCarac]
                  zFontBold = TheStyle[0]
                  zFontUnderline = TheStyle[1]
                  zFontItalic = TheStyle[2]
               
               zFontSize = float(nProp[2])
               zForeColorV = InvRGB(long(nProp[3]))
               zForeColor = rgb_to_hex(long(nProp[3])) 

               if len(nProp) == 5:
                  zBackColorV = InvRGB(long(nProp[4]))
                  zBackColor = rgb_to_hex(long(nProp[4])) 


            if X!=-1 and Y!=-1:
               textItem = QgsTextAnnotationItem( self.iface.mapCanvas())
               ztempo = zText.split("<br>")

               if len(ztempo)>1:
                  zmaxlen = 0
                  zfacteurH = 20
                  zfacteurL = 8
                  nbHauteur = len(ztempo)
                  for k in range(len(ztempo)):
                      ztmplen = len(ztempo[k])
                      if ztmplen > zmaxlen : zmaxlen = ztmplen

               if nbHauteur == 1 : zfacteurH = 30
                  
               largeur = int(zfacteurL * zmaxlen)
               hauteur = int(zfacteurH * nbHauteur)
               
               lInfosProj4 = zForceCRS.split("|")
               zProj4Dest = lInfosProj4[3]

               if zProj4Dest!= "" :
                   zTransform = DefzTransform(zLayer, zProj4Dest)
                   point = zTransform.transform(QgsPoint(X, Y))
               else :
                   point = QgsPoint(X, Y)
                   
               textItem.setMapPosition(point)
               textItem.setFrameSize(QSizeF(largeur,hauteur)) 
               textItem.setFrameColor(zForeColorV) 
               textItem.setFrameBackgroundColor(zBackColorV) 
               zDoc = QTextDocument()

               
               if zFontBold: zText = "<b>"+zText+"</b>"
               if zFontItalic: zText = "<i>"+zText+"</i>"
               if zFontUnderline: zText = "<u>"+zText+"</u>"

               zDoc.setHtml(str("<font style=\"color:"+str(zForeColor)+"; font-family:'"+str(zFont)+"'; font-size: " +str(zFontSize)+"px\">"+str(zText)+"</font>"))
               textItem.setDocument(zDoc)

    zStr = str(zLayer.name())
    if HasMakeLabeller  and zStr.find("Etiquettes")==-1:
       zLayer.setLayerName(zLayer.name()+" (Etiquettes : "+nLabelFieldName +")")
    return  



#-----------------------------------
#FONCTION retour couleur RGB -> HEXA
#-----------------------------------
def rgb_to_hex(zColor):
    zColor, zInvColor = long(zColor), 0
    if zColor<0 :
       Red, Green, Blue = 0, 0, 0
    else:
       Red = int(zColor % 256)
       Green = int(zColor // 256 % 256)
       Blue = int(zColor // 256 // 256 % 256 )

    zRGB = (Blue, Green, Red)
    hexColor = '#%02x%02x%02x' % zRGB
    return hexColor
   
#-------------------------------
#FONCTION retour couleur MAPINFO
#-------------------------------
def InvRGB(zColor):
    zColor, zInvColor = long(zColor), 0
    if zColor<0 :
       Red, Green, Blue = 0, 0, 0
    else:
       Red = int(zColor % 256)
       Green = int(zColor // 256 % 256)
       Blue =  int(zColor // 256 // 256 % 256 )
    zInvColor = QColor(Blue, Green, Red)
    return zInvColor

#-------------------------------
#FONCTION retour chaines couleur
#-------------------------------
def StrRGB(zColor):
    zColor = long(zColor)
    if zColor<0 :
       sRed, sGreen, sBlue = "0", "0", "0"
    else:
       sBlue = str(int(zColor % 256))
       sGreen = str(int(zColor // 256 % 256))
       sRed =  str(int(zColor // 256 // 256 % 256 ))
    return sRed, sGreen, sBlue
   
#--------------------------------------------------
#FONCTION création chaîne ID trame (fichier PNG/SVG)
#--------------------------------------------------
def StrBrush(zBrush):
    if len(zBrush)<4:  
       for i in range(3-len(zBrush)):
           zBrush = "0"+zBrush 
    return zBrush


def MakeValue(sValue):
    tempo = sValue.split("e+")
    if len(tempo)>1:
       aMulti = int(tempo[1])
       return float(float(tempo[0])*pow(10,aMulti))
    else:
       return float(sValue) 

#----------------------------------------------------
#FONCTION recherche position mot clef dans un tableau
#----------------------------------------------------   
def FixeIndex(IndexDeb, DicSearch, StrSearch):
    FindSearch = False
    for j in range(IndexDeb, len(DicSearch)):
          ztempo = NetStrInfos(DicSearch[j], True, True, True, False, ())  
          if ztempo == StrSearch :
             FindSearch = True
             break
    if FindSearch: j+= 1
    else: j = -1
    return j
   
#------------------------------------------------------
#FONCTION extrude les options étiquettes non supportées
#------------------------------------------------------   
def ValCarac(nValue, nBorne):
    tValue = (1024, 512, 256, 32)
    for i in range(len(tValue)-nBorne):
        if nValue > tValue[i]: nValue = nValue - tValue[i]
    return nValue
   
#------------------------------------------------------
#FONCTION labellisation méthode analyse proportionnelle
#------------------------------------------------------   
def TypeMethode(zMethode):
    if zMethode == "LOG": zMethode = "Logarithme"
    elif zMethode == "FIXED": zMethode = "Taille fixe"
    elif zMethode == "SQRT": zMethode = "Racine carrée"
    elif zMethode == "CONST": zMethode = "Linéaire"
    return zMethode  

#------------------------------------------------------
#FONCTION calcul valeur zoom échelle
#------------------------------------------------------   
def GetValueZoom(nValue, nUnits,nSizeMap, nSizeMapUnits):
    class Length(object):
        __metaclass__ = MeasureType
        DEFAULT_UNIT = "m"
        _TO_DEFAULT = { "mm":0.001, "cm":0.01, "km":1000,
                        "in":0.0254, "ft":0.3048, "yd":0.9144, "mi":1609.34
                       }

    nSizeMapUnits = str(nSizeMapUnits)
    nSizeMapUnits = nSizeMapUnits.lower()
    nUnits = str(nUnits)
    nUnits = nUnits.lower()
    zValue = Length(nValue, nUnits)
    zSizeMap = Length(nSizeMap, nSizeMapUnits)
    Length.setDefaultUnit(nSizeMapUnits)
    sValue = str(zValue)
    sValue = sValue.replace(nSizeMapUnits,"")
    sSizeMap = str(zSizeMap)
    sSizeMap = sSizeMap.replace(nSizeMapUnits,"")
    zEchelle = long(float(sValue) /float(sSizeMap))
    return zEchelle
      
#---------------------------------------
#FONCTION recherche index / nom attribut
#---------------------------------------   
def GetIndexFieldName(zLayer, nFieldName, zType):
    if zType == "SHAPEFILE": 
       provider = zLayer.dataProvider()
       zIndex = provider.fieldNameIndex(nFieldName)
       
    elif zType == "NATIVE":
       nFileName = str(zLayer.source())
       mytable = open(nFileName, 'r')
       zIndex = -1
       i = 0
       debFields = False
       CountFields = 0
       nFieldName = nFieldName.upper()
       
       for line in mytable:
           astring = NetStrInfos(str(QString.fromLocal8Bit(line)), True, True, True, False, ())
           if debFields and CountFields > 0: 
              CountFields = CountFields - 1
              if astring.startswith(nFieldName):
                 zIndex = i
                 break
              else:
                 tempo = astring.split(" ")
                 FieldNameCible = NetStrInfos(tempo[0], True, True, False, False, ())
                 if nFieldName.find(FieldNameCible)!=-1:
                    zIndex = i
                    break
              i+= 1

           if astring.startswith("FIELDS"):
              debFields = True
              tempo = astring.split()
              CountFields = int(tempo[1])
               
           if CountFields == 0: debFields = False
       mytable.closed
    
    return zIndex

#-------------------------------
#FONCTION recherche index couche
#-------------------------------   
def GetIndexLayer(self, vLayer):
    zIndex = 0
    nLayers = self.iface.mapCanvas().layerCount()
    for i in range(nLayers):
        cLayer = self.iface.mapCanvas().layer(i)
        if cLayer.id()== vLayer.id(): break  
        zIndex+= 1
    return zIndex

#-------------------------------------
#FONCTIONS extraction informations WMS
#-------------------------------------
def GetWMSInfos(nTableRaster):
    mytable = open(nTableRaster, 'r')
    nWMS=str(mytable.readlines())
    mytable.closed
    nParamWMS=("GetMap=\"","<SRS>","<Layer>","wms_version=\"","minx=\"","miny=\"","maxx=\"","maxy=\"","\" format=\"")
    lstWMS = ""
    for i in range(len(nParamWMS)):
        tempo = ExtractValWMS(nWMS,str(nParamWMS[i]))  
        if tempo !="": lstWMS = lstWMS + tempo + "|"
    return lstWMS

def ExtractValWMS(nStr, nRub):
    zTabVal=""
    posd=0
    posf=0
    if nStr!="" and nRub !="":
       if nRub == "<Layer>":
          zTabVal = ExtractLayers(nStr)
       else:  
          posd = nStr.find(nRub)+len(nRub)
          if posd!=-1:
             if nRub.startswith("<"): posf = nStr.find("<",posd)  
             else: posf = nStr.find("\"",posd)
             if posf > posd: zTabVal = nStr[posd:posf]
    return zTabVal
      
def ExtractLayers(nStr):
    zLayersWMS = "" 
    posd=nStr.find("<Name>")+len("<Name>")
    posf=0
    while posd > posf:
          posf = nStr.find("<",posd)
          if posf > posd:
             if zLayersWMS == "": zLayersWMS = nStr[posd:posf] 
             else: zLayersWMS = zLayersWMS + "," + nStr[posd:posf]
          posd = nStr.find("<Name>", posf)+len("<Name>")
    posd=nStr.find("<Style>")+len("<Style>")
    posf=0
    zLayersWMS = zLayersWMS + "|"
    while posd > posf:
          posf = nStr.find("<",posd)
          if posf > posd:
             if zLayersWMS.endswith("|") : zLayersWMS = zLayersWMS + nStr[posd:posf] 
             else: zLayersWMS = zLayersWMS + "," + nStr[posd:posf]
          else :
             if zLayersWMS.endswith("|") : zLayersWMS = zLayersWMS + 'default'
             else: zLayersWMS = zLayersWMS + "," + 'default'
          posd = nStr.find("<Style>", posf)+len("<Style>")
    return zLayersWMS

                
#--------------------------
#FONCTION visibilité couche
#--------------------------
def MakeVisibility(self, vLayer, sLayerVisibility): 
    nCond = True
    stempo = sLayerVisibility.split("|")
    zIndex = FixeIndex(0,stempo, "DISPLAY OFF")
    nCond = True if zIndex == -1 else False
    self.iface.legendInterface().setLayerVisible(vLayer, nCond)
    return nCond


#---------------------------------------
#FONCTIONS Analyse par densité de points
#---------------------------------------
def createSinglePolygon(self, vlayer):
    provider = vlayer.dataProvider()
    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)
    feat = QgsFeature()
    geom = QgsGeometry()
    provider.nextFeature(feat)
    geom = QgsGeometry(feat.geometry())
    count = 10.00
    add = ( 40.00 - 10.00 ) / provider.featureCount()
    while provider.nextFeature(feat):
          geom = geom.combine(QgsGeometry( feat.geometry() ))
          count = count + add
    return geom
    

def vectorRandom(self, n, layer, xmin, xmax, ymin, ymax):
    provider = layer.dataProvider()
    provider.select([])
    index = ftools_utils.createIndex(provider)
    seed()
    points = []
    feat = QgsFeature()
    i = 1
    count = 40.00
    add = ( 70.00 - 40.00 ) / n
    while i <= n:
          point = QgsPoint(xmin + (xmax-xmin) * random(), ymin + (ymax-ymin) * random())
          pGeom = QgsGeometry().fromPoint(point)
          ids = index.intersects(pGeom.buffer(5,5).boundingBox())
          for id in ids:
              provider.featureAtId(int(id),feat,True)
              tGeom = QgsGeometry(feat.geometry())
              if pGeom.intersects(tGeom):
                 points.append(pGeom)
                 i+= 1
                 count = count + add
                 break
    return points


def randomizePoints(self, inLayer, minimum, design, value, nMax, nSize, nRatio, nFillColor, nType):    
    outFeat = QgsFeature()
    if nRatio == 0:
       ratio = 1
       while nMax > 1000:
             ratio = (ratio * 10)
             nMax = (nMax / 1000)
    else: ratio = nRatio   
       
    QApplication.setOverrideCursor( QCursor( Qt.WaitCursor ) )
    
    if design == self.tr("unstratified"):
       ext = inLayer.extent()
       if inLayer.type() == inLayer.RasterLayer:
          points = simpleRandom(self, int(value), ext, ext.xMinimum(), ext.xMaximum(), ext.yMinimum(), ext.yMaximum())
       else:
          points = vectorRandom(self, int(value), inLayer, ext.xMinimum(), ext.xMaximum(), ext.yMinimum(), ext.yMaximum())
    else: points = loopThruPolygons(self, inLayer, value, design, ratio)
    crs = self.iface.mapCanvas().mapRenderer().destinationSrs()
    if not crs.isValid(): crs = None

    idVar, count = 0, 70.00
    add = ( 100.00 - 70.00 ) / len(points)

    zProjectionSetting, zProjectionCRSValue = ChangeSETTINGS(self, inLayer) 
    AnaLayer = QgsVectorLayer("Point", QString.fromLocal8Bit(inLayer.name()) + " (DensitePoints" + " : " + str(value) + " - Taille "+str(nSize)+" pour "+str(ratio) + ")", "memory")
    DefineLayerProj(self, inLayer, AnaLayer)
    RestoreSETTINGS(zProjectionSetting, zProjectionCRSValue)
    
    prCentro = AnaLayer.dataProvider()
    ret = prCentro.addAttributes( [ QgsField("ID", QVariant.Int)])
    AnaLayer.updateFieldMap()

    for i in points:
        outFeat.setGeometry(i)
        outFeat.addAttribute(0, QVariant(idVar))
        prCentro.addFeatures( [ outFeat ] )
        AnaLayer.updateExtents()
        idVar+= 1
        count = count + add

    if nSize == 0 : nSize = 0.26
       
    zCentroideLayer = QgsMapLayerRegistry.instance().addMapLayers([AnaLayer])[0]
    symbols = AnaLayer.rendererV2().symbols()
    symbol = symbols[0]
    symbol = InitLayerSymbol(symbol)
    if nType=="rectangle": nSymbol = "32"
    else : nSymbol = "34"
    #on force une color_border (pos 3) dans ce cas uniquement
    zTempoInfos = str(nSymbol) + "," + str(nFillColor) + "," + str(RatioMapInfo*nSize) + "," + str(nFillColor)

    vInfos = zTempoInfos.split(",")
    sl = MakeSimpleMARKERV2(vInfos)
    symbol.appendSymbolLayer(sl)     
       
    self.iface.legendInterface().refreshLayerSymbology(zCentroideLayer) 
    QApplication.restoreOverrideCursor()
    return zCentroideLayer


def loopThruPolygons(self, inLayer, numRand, design, ratio):
    sProvider = inLayer.dataProvider()
    sAllAttrs = sProvider.attributeIndexes()
    sProvider.select(sAllAttrs)
    sFeat = QgsFeature()
    sGeom = QgsGeometry()
    sPoints = []
    if design == self.tr("field"):
       for (i, attr) in sProvider.fields().iteritems():
           if (unicode(numRand) == attr.name()):
              index = i 
              break
    count = 10.00
    add = 60.00 / sProvider.featureCount()
    while sProvider.nextFeature(sFeat):
          sGeom = sFeat.geometry()
          if design == self.tr("density"):
             sDistArea = QgsDistanceArea()
             value = int(round(numRand * sDistArea.measure(sGeom)))
          elif design == self.tr("field"):
             sAtMap = sFeat.attributeMap()
             value = int(sAtMap[index].toInt()[0] / ratio)
             if value == 0 :
                value = 1
          else:
             value = numRand
          sExt = sGeom.boundingBox()
          sPoints.extend(simpleRandom(self, value, sGeom, sExt.xMinimum(), sExt.xMaximum(), sExt.yMinimum(), sExt.yMaximum()))
          count = count + add
    return sPoints


def simpleRandom(self, n, bound, xmin, xmax, ymin, ymax):
    seed()
    points = []
    i = 1
    count = 40.00
    add = ( 70.00 - 40.00 ) / n
    while i <= n:
          pGeom = QgsGeometry().fromPoint(QgsPoint(xmin + (xmax-xmin) * random(), ymin + (ymax-ymin) * random()))
          if pGeom.intersects(bound):
             points.append(pGeom)
             i+= 1
             count = count + add
    return points   



#-------------------------------------------------
#FONCTIONS SYMBOLOGIE V1, V2 : Fixe SVG FileName
#-------------------------------------------------
def FixeSVGFile(zFileName, zFileLOC):
    isSVGFile = False
    zFileName = zFileName.replace("\\","/")
   
    if os.path.exists(zFileName): isSVGFile = True
    else:
       zPath = os.path.dirname(__file__)
       zPath = zPath.replace("\\","/")
       zPos =  zFileName.rfind(".") 
       zPathSymbol = os.path.join(zPath + zFileLOC, zFileName[0:zPos]+".svg")
       if os.path.exists(zPathSymbol):
          isSVGFile = True
          zFileName = zPathSymbol
       else:
          svgPaths = QgsApplication.svgPaths()
          zFileName = os.path.basename(zFileName)
          for i in range(len(svgPaths)):
              PathSVG =  svgPaths[i] + "/" + zFileName
              if os.path.exists(PathSVG):
                 zFileName = PathSVG 
                 isSVGFile = True
                 break
    if not isSVGFile : zFileName = ""

    return isSVGFile, zFileName
    
#-------------------------------------------------
#FONCTIONS SYMBOLOGIE V2 : Liste des types simples
#-------------------------------------------------
def InitLayerSymbol(zSymbol):
    zsymbolLayerCount = zSymbol.symbolLayerCount()
    for i in range(zsymbolLayerCount,-1, -1):
        zSymbol.deleteSymbolLayer(i)
    return zSymbol
    
def MakeMARKERV2(zDisplayGraphic, zLayer, zSymbol, zInfosSymbos):
    zSymbol = InitLayerSymbol(zSymbol)
    zIndex = FixeIndex(0,zInfosSymbos, "SYMBOL")

    if zIndex == -1 :
       zTempoInfos = "32, 16777215, 1.0" 
       vInfos = zTempoInfos.split(",")
       sl = MakeSimpleMARKERV2(vInfos)
       zSymbol.appendSymbolLayer(sl)       
    else:
       while zIndex!=-1:
             zTypeSymbol = 1 #valeur à défaut, type simple
             zInfos = MakePropertiesFONT(zIndex, zInfosSymbos[zIndex], zInfosSymbos)
             zInfos = NetStrInfos(zInfos, False, False, False, False, ("(", ")"))
             vInfos = zInfos.split(",")
             zTypeSymbol = len(vInfos)

             #Symbole FONT (shape, color, size, fontname, fontstyle, rotation) 
             if zTypeSymbol == 6 : sl = MakeFontMARKERV2(vInfos)
             #Symbole FILE (filename, color, size, customstyle) 
             elif zTypeSymbol == 4 : sl = MakeSvgMARKERV2(vInfos)
             #Symbole simple (shape, color, size)
             else: sl = MakeSimpleMARKERV2(vInfos)

             zIndex = FixeIndex((zIndex+1),zInfosSymbos, "SYMBOL")
             zSymbol.appendSymbolLayer(sl)
    return zSymbol

def MakeLINEV2(zDisplayGraphic, zLayer, zSymbol, zInfosSymbos):
    zSymbol = InitLayerSymbol(zSymbol)
    zIndex = FixeIndex(0,zInfosSymbos, "LINE")
    zColorRGB = 0

    if zIndex!=-1:
       zInfos = NetStrInfos(zInfosSymbos[zIndex], False, False, False, False, ("(", ")"))
       vInfos = zInfos.split(",")
       zSize = float(vInfos[0])
       zTypeLine = str(vInfos[1])
       zColorRGB = long(vInfos[2])
       zLineColor = InvRGB(zColorRGB)
    else:  
       zSize = 0.26
       zTypeLine = '2' 
       zLineColor = QColor(255, 255, 255)
    zTempo = AdapteRatioMapInfo(zSize, True, False) 
    zSizeLine = str(zTempo)
    zColorLine =  QString(QgsSymbolLayerV2Utils.encodeColor(zLineColor))

    if tLineV2.has_key(zTypeLine): zQtLine = QString(tLineV2[zTypeLine])
    else : zQtLine = QString("solid") 
    RefzSizeLine = zSizeLine
    RefzQtLine = zQtLine
    RefzColorLine = zColorLine

    """
    #TATAR !!
    zSymbol = MakeSimpleLINEV2(zSymbol, zColorLine, '0.0', zQtLine, zSizeLine, True)
    QMessageBox.information(None,"DEBUG", "it's not OK ?")
    return
    """
    
    if tLineCompositeV2.has_key(zTypeLine) :
         TheStyles = tLineCompositeV2[zTypeLine]   
         zTypeLines = TheStyles[0]
         zOffsets = TheStyles[1]
         zSubLine = zTypeLines.split(",")
         zOffset = zOffsets.split(",")

         for i in range(len(zSubLine)):
             zSizeLine = RefzSizeLine
             zQtLine = RefzQtLine
             zColorLine = RefzColorLine
             
             if zSubLine[i]=='0':
                #SIMPLELINE : props {'color', 'offset', 'penstyle', 'width', 'use_custom_dash', 'joinstyle', 'custom_dash', 'capstyle'}
                if tSubSymbLineCompositeV2.has_key(zTypeLine) :
                   TheSubStyles = tSubSymbLineCompositeV2[zTypeLine]
                   zSubLines = TheSubStyles[0]
                   zInfoSubLines = TheSubStyles[1]

                   zSubSubLine = zSubLines.split(",")
                   zInfoSubLine = zInfoSubLines.split(",")

                   for k in range(len(zSubSubLine)):
                       if int(zSubSubLine[k])==i or int(zSubSubLine[k])==-1:
                          zQtLine = str(zInfoSubLine[k].split("|")[0])
                          if zInfoSubLine[k].split("|")[1]!= "%": zSizeLine = str(zInfoSubLine[k].split("|")[1])
                          if zInfoSubLine[k].split("|")[2]!= "%":
                             zLineColor = InvRGB(long(zInfoSubLine[k].split("|")[2]))
                             zColorLine =  QString(QgsSymbolLayerV2Utils.encodeColor(zLineColor))
                zSymbol = MakeSimpleLINEV2(zSymbol, zColorLine,  str(float(zOffset[i])), zQtLine, zSizeLine, False)
                
             elif zSubLine[i]=='1':
                #MARKERLINE : props {'color','offset', 'interval', 'rotate', 'placement'} 
                props = {'marker':'','offset':'0.0','interval': str(zOffset[i]), 'rotate':'0','placement': ''}
                sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("MarkerLine").createSymbolLayer(props)
                zSymbol.appendSymbolLayer(sl)
                
                if tSubSymbSymbolCompositeV2.has_key(zTypeLine):
                   TheSubStyles = tSubSymbSymbolCompositeV2[zTypeLine]
                   zQtMarker = str(TheSubStyles[1])
                   if TheSubStyles[2]!= "%": zSizeSymbol = str(TheSubStyles[2])
                   else :  zSizeSymbol = str(zSize) #AdapteRatioMapInfo(zSize, False, True))

                   if TheSubStyles[3]!= "%":
                      zLineColor = InvRGB(long(TheSubStyles[3]))
                      zColorLine =  QString(QgsSymbolLayerV2Utils.encodeColor(zLineColor))                      

                indexSubSymbolLayer = zSymbol.symbolLayerCount()-1
                props = {'color_border' : zColorLine , 'offset' : '0.0', 'size' : zSizeSymbol ,'color' : zColorLine, 'name' :zQtMarker, 'angle': '0.0'}
                slsub = QgsMarkerSymbolV2().createSimple(props)
                zResult = zSymbol.symbolLayer(0).setSubSymbol(slsub) #indexSubSymbolLayer #Avant !
             else:
                #Decoration LINE
                props = {'color' : zColorLine, 'offset': str(zOffset[i]), 'penstyle': zQtLine , 'width': zSizeLine, 'use_custom_dash':'', 'joinstyle':'round', 'custom_dash':'', 'capstyle':'butt'}             
                sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleLine").createSymbolLayer(props)
                zSymbol.appendSymbolLayer(sl)
                 
                props = {'width' : zSizeLine, 'color' : zColorLine}
                sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("LineDecoration").createSymbolLayer(props)
                zSymbol.appendSymbolLayer(sl)

    else:    
 
             zLineSTR = StrBrush(zTypeLine)
             zPathLine = QString("")
             zPath = os.path.dirname(__file__)
             zPath = zPath.replace("\\","/")
             zPathLine = os.path.join(zPath + "/svg/", "mapinfo_line_"+zLineSTR+".svg")

             if os.path.exists(zPathLine): 
                zPathLine = ReColoreSVG(zPath, zPathLine, "line" , zLineSTR, zColorRGB)
                
                if os.path.exists(zPathLine):
                    zSymbol.deleteSymbolLayer(0)
                    props = {'marker':'','offset':'0.0','interval': '3.0', 'rotate':'0','placement': ''}
                    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("MarkerLine").createSymbolLayer(props)
                    zSymbol.appendSymbolLayer(sl)

                    indexSubSymbolLayer = zSymbol.symbolLayerCount()-1
                    
                    props = {'name' :  QString(zPathLine) , 'size' : '3.0' , 'angle': '0.0'}
                    slsub = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SvgMarker").createSymbolLayer(props)
                    zSymbol.symbolLayer(indexSubSymbolLayer).subSymbol().appendSymbolLayer(slsub)
                    zSymbol.symbolLayer(indexSubSymbolLayer).subSymbol().deleteSymbolLayer(0)
                else:
                    zSymbol = MakeSimpleLINEV2(zSymbol, zColorLine, '0.0', zQtLine, zSizeLine, True)
             else:
                 zSymbol = MakeSimpleLINEV2(zSymbol, zColorLine, '0.0', zQtLine, zSizeLine, True)

    return zSymbol


def MakeBRUSHV2(zDisplayGraphic, zLayer, zSymbol, zInfosSymbos, zIsAna):
    #Pour la v2, tous les blocs Brush seront des calques du style
    zSymbol = InitLayerSymbol(zSymbol)
    zIndex = FixeIndex(0,zInfosSymbos, "BRUSH")
    if zIndex == -1: # or zDisplayGraphic
       #props {'color_border', 'style_border', 'offset', 'style', 'color', 'width_border'}
       zLineColor = "0"
       zFillColor = "16777215"
       zIndex = FixeIndex(0,zInfosSymbos, "LINE")
       if zIndex!=-1: 
          zInfos = NetStrInfos(zInfosSymbos[zIndex], False, False, False, False, ("(", ")"))
          vInfos = zInfos.split(",")
          zLineColor = str(vInfos[2])
          zFillColor = zLineColor
       zInfos =  zLineColor + ",2,1.0,2,"+zFillColor+", 0.26"
       vInfos = zInfos.split(",")
       sl = MakeSimpleBRUSHV2(vInfos)
       zSymbol.appendSymbolLayer(sl)

    else:
       
       while zIndex!=-1:
             zInfos = NetStrInfos(zInfosSymbos[zIndex], False, False, False, False, ("(", ")"))
             vInfos = zInfos.split(",")
             zBrush = str(vInfos[0])
             zForeColor = str(vInfos[1])
             zTypeBrush = len(vInfos)

             isMakeSymbol = False
             zBackColor = str(vInfos[2]) if zTypeBrush==3 else str(vInfos[1])

             #Il faut définir quel est le type de représentation à appliquer :
             #SimpleFill ou SVGFill
             if tBrushV2.has_key(zBrush):
                zIndexPEN = FixeIndex(0,zInfosSymbos, "PEN")
                if zIndexPEN!=-1:
                   zInfos = NetStrInfos(zInfosSymbos[zIndexPEN], False, False, False, False, ("(", ")"))
                   vInfos = zInfos.split(",")
                   zSize = str(float(vInfos[0]))
                   zLinePen = str(vInfos[1])
                   zPENColor = str(vInfos[2])
                else:
                   zPENColor = "0" #str(zForeColor)
                   zLinePen = "2" 
                   zSize = "1.0"
                #props {'color_border', 'style_border', 'offset', 'style', 'color', 'width_border'}
                vTempoInfos = zPENColor + "," + zLinePen + ",1.0," + zBrush + "," + zForeColor + "," + zSize

                if int(zBrush) > 2 and zTypeBrush==3 :
                   vTempoInfosSub =  zBackColor + ",2,1.0,2,"+ zBackColor + ", 0.26" 
                   vInfos = vTempoInfosSub.split(",")                    
                   slsub = MakeSimpleBRUSHV2(vInfos)
                   zSymbol.appendSymbolLayer(slsub)  
                
                vInfos = vTempoInfos.split(",")
                sl = MakeSimpleBRUSHV2(vInfos)

             else:
 
                #props {'svgFile', 'width', 'angle'}
                zBrushSTR = StrBrush(zBrush)
                zPathTexture = QString("")
                zPath = os.path.dirname(__file__)
                zPath = zPath.replace("\\","/")
                zPathTexture = os.path.join(zPath + "/svg/", "mapinfo_brush_"+zBrushSTR+".svg")

                if os.path.exists(zPathTexture):
                       zPathTexture = ReColoreSVG(zPath, zPathTexture, "brush" , zBrushSTR, zForeColor)  
                       #props {'color_border', 'style_border', 'offset', 'style', 'color', 'width_border'}
                       zIndexPEN = FixeIndex(0,zInfosSymbos, "PEN")
                       if zIndexPEN!=-1:
                          zInfos = NetStrInfos(zInfosSymbos[zIndexPEN], False, False, False, False, ("(", ")"))
                          vInfos = zInfos.split(",")
                          zSize = str(float(vInfos[0]))
                          zLinePen = str(vInfos[1])
                          zPENColor = str(vInfos[2])
                       else:
                          zPENColor = str(zForeColor)
                          zLinePen = "2" 
                          zSize = str(0.26)

                       if zTypeBrush ==3 :       
                          vTempoInfos = zPENColor + ","+zLinePen+",1.0,2," + zBackColor + "," + zSize
                          vInfos = vTempoInfos.split(",")
                          sl = MakeSimpleBRUSHV2(vInfos)
                          zSymbol.appendSymbolLayer(sl)

                       if os.path.exists(zPathTexture): 
                           zPathTexture = QString(zPathTexture)
                           vTempoInfos = zPathTexture + ",12.0,0.0"
                           vInfos = vTempoInfos.split(",")
                           sl = MakeSvgBRUSHV2(vInfos)
                           zSymbol.appendSymbolLayer(sl)
                           isMakeSymbol = True

                       #il faut une option zIsAna 
                       if zIsAna: return

                       if zSymbol.symbolLayerCount() > 0:
                          indexSubSymbolLayer = zSymbol.symbolLayerCount()-1
                          if tLineV2.has_key(zLinePen): zQtStyleBorder = QString(tLineV2[zLinePen])
                          else : zQtStyleBorder = QString("solid")
                          zQtStyleBrush = QString("no")
                          zBorderColor = InvRGB(long(zPENColor))
                          zColor = QString(QgsSymbolLayerV2Utils.encodeColor(zBorderColor))
                          zSizeLine = str(AdapteRatioMapInfo(float(zSize), True, False))
                          
                          props = {'color' : zColor, 'offset': '0.0', 'penstyle': zQtStyleBorder , 'width': zSizeLine, 'use_custom_dash':'', 'joinstyle':'round', 'custom_dash':'', 'capstyle':'butt'}
                          slsub = QgsLineSymbolV2.createSimple(props)
                          zResult = zSymbol.symbolLayer(0).setSubSymbol(slsub)#indexSubSymbolLayer #Avant !
                          
                else :
                    #props {'color_border', 'style_border', 'offset', 'style', 'color', 'width_border'}
                    vTempoInfos = zForeColor + ",2,1.0,2," + zBackColor + ",0.26"
                    vInfos = vTempoInfos.split(",")
                    sl = MakeSimpleBRUSHV2(vInfos)

             zIndex = FixeIndex((zIndex+1),zInfosSymbos, "BRUSH")
             if not isMakeSymbol: zSymbol.appendSymbolLayer(sl)
                      
    return zSymbol


def MakeSvgBRUSHV2(vInfos):
    #props {'svgFile', 'data', 'width', 'angle'} #svgFile ou data en QByteArray
    zSvgFile = str(vInfos[0])
    zSvgFile = zSvgFile.replace('//', '/')
    zWidth = str(vInfos[1])
    zAngle = str(vInfos[2])

    #TATAR
    #Quelque chose a changé depuis la 1.8  ????
    #Problème idem sur tous les styles avec SVG ...
    props = {'svgFile': zSvgFile, 'width' : zWidth , 'angle' : zAngle}
    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SVGFill").createSymbolLayer(props)
    #solution a minima
    #sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleFill").createSymbolLayer({'color_border' : '0' , 'style_border' : '1', 'offset' : '1.0',
    #            'style' : '2', 'color' : '16777215', 'width_border' : zWidth})
    return sl


def MakeSimpleBRUSHV2(vInfos):
    #props {'color_border', 'style_border', 'offset', 'style', 'color', 'width_border'}
    zBorderColor = InvRGB(long(vInfos[0]))
    zColorBorder =  QString(QgsSymbolLayerV2Utils.encodeColor(zBorderColor))

    zStyleBorder = vInfos[1]
    if tLineV2.has_key(zStyleBorder): zQtStyleBorder = QString(tLineV2[zStyleBorder])
    else : zQtStyleBorder = QString("solid")

    zStyle = vInfos[3]
    zQtStyle = QString(tBrushV2[zStyle])
    zFillColor = InvRGB(long(vInfos[4]))
    zColor = QString(QgsSymbolLayerV2Utils.encodeColor(zFillColor))
    zSize = AdapteRatioMapInfo(float(vInfos[5]), True, False)
    zWidthBorder = str(zSize)
    props = {'color_border' : zColorBorder , 'style_border' : zQtStyleBorder, 'offset' : '1.0',
             'style' : zQtStyle, 'color' : zColor, 'width_border' : zWidthBorder}
    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleFill").createSymbolLayer(props)
    return sl

def MakeCentroidBRUSHV2(vInfos):
    #props {'size', 'offset', 'angle', 'name'}    
    return sl

   
   
def MakeSimpleLINEV2(zSymbol, zColorLine, zOffset, zQtLine, zSizeLine, zNet):
    #SimpleLine
    #joinstyle : bevel, mitre, round
    #capstyle : square, butt, round
    props = {'color' : zColorLine, 'offset': str(zOffset), 'penstyle': str(zQtLine) , 'width': str(zSizeLine), 'use_custom_dash':'', 'joinstyle':'round', 'custom_dash':'', 'capstyle':'butt'}
    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleLine").createSymbolLayer(props)
    zSymbol.appendSymbolLayer(sl)
    if zNet:
       zsymbolLayerCount = zSymbol.symbolLayerCount()
       if zsymbolLayerCount==2: zSymbol.deleteSymbolLayer(0)
    return zSymbol


#----------------------------------------------
# FONCTIONS CREATION DES SYMBOLLAYER PONCTUELS
#----------------------------------------------
def MakeFontMARKERV2(vInfos):
    #props {'color', 'offset', 'angle', 'chr', 'font', 'size'}
    zSymbolCode = str(int(vInfos[0]))
    zSymbolCHR = QString(chr(int(vInfos[0])))
    zSymbolSize = AdapteRatioMapInfo(float(vInfos[2]), False, True)
    zSymbolFontName = str(vInfos[3])
    zSymbolFontStyle = str(vInfos[4])  
    zSymbolRotation = str(360.0-float(vInfos[5]))
    zSymbolColor = InvRGB(long(vInfos[1]))
    zSize = str(zSymbolSize)    
    zFillColor =  QString(QgsSymbolLayerV2Utils.encodeColor(zSymbolColor))
    
    props = {'color' : zFillColor , 'offset' : '1.0', 'angle': zSymbolRotation,
             'chr' : zSymbolCHR, 'font' : zSymbolFontName, 'size' : zSize}
    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("FontMarker").createSymbolLayer(props)

    return sl

def MakeSvgMARKERV2(vInfos):
    #props = {'size', 'offset', 'angle', 'name', 'outlinewidth', 'fillcolor', 'outlinecolor' }
    zSymbolFileName = NetStrInfos(str(vInfos[0]), True, True, False, False, ("\"", "'"))
    isSVGFile, zSymbolFileName = FixeSVGFile(zSymbolFileName, "/svg/symbols/")
   
    zSymbolSize = str(float(vInfos[2]))
    zSymbolCustomStyle = str(float(vInfos[3]))
    zSymbolRotation = '0.0' 
    zSymbolColor = InvRGB(long(vInfos[1]))
    zSize = str(AdapteRatioMapInfo(float(vInfos[2]), False, False))
    zFillColor =  QString(QgsSymbolLayerV2Utils.encodeColor(zSymbolColor))

    props = {'size' : zSize, 'offset': '1.0', 'angle': zSymbolRotation, 'name': str(zSymbolFileName)} 
    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SvgMarker").createSymbolLayer(props)

    return sl

def MakeSimpleMARKERV2(vInfos):
    #props {'color_border', 'offset', 'size', 'color', 'name', 'angle'}
    zSymbolCode = str(vInfos[0])
    zSymbolSize = AdapteRatioMapInfo(float(vInfos[2]), False, False) 
    zSymbolRotation = '0.0'

    if tSymbolV2.has_key(zSymbolCode) : zQtNameMarker = QString(tSymbolV2[zSymbolCode])
    else : zQtNameMarker = 'rectangle'
    
    zSymbolColor = InvRGB(long(vInfos[1]))
    zSize = str(zSymbolSize)    
    zFillColor =  QString(QgsSymbolLayerV2Utils.encodeColor(zSymbolColor))
    if len(vInfos)==4:
       zSymbolColor = InvRGB(long(vInfos[3]))
       zBorderColor =  QString(QgsSymbolLayerV2Utils.encodeColor(zSymbolColor))
    else:    
        #on n'a pas de symbole simple sans fond, on force une couleur blanche intérieure
        if int(zSymbolCode) < 40: zBorderColor = QString(QgsSymbolLayerV2Utils.encodeColor(QColor(0,0,0)))
        else :
            zBorderColor = zFillColor
            zFillColor =  QString(QgsSymbolLayerV2Utils.encodeColor(QColor(255,255,255)))
    
    props = {'color_border' : zBorderColor , 'offset' : '1.0', 'size' : zSize,
             'color' : zFillColor, 'name' : zQtNameMarker, 'angle': zSymbolRotation}
    sl = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleMarker").createSymbolLayer(props)
    return sl

#------------------------------------------------
#FONCTION de recolorisation des SVG ressources
#------------------------------------------------
def ReColoreSVG(zPath, zSVGFileIn, zTypeSVG, zValueSVG, zColor):
    zPathTextureColor = zSVGFileIn
    if zColor != '16777215': 
       MyColorHexa = rgb_to_hex(long(zColor))
       MyColorHexa = MyColorHexa.replace("#","")
       zPathTextureColor = os.path.join(zPath + "/myworks/", "mapinfo_"+zTypeSVG+"_"+zValueSVG+"_"+str(MyColorHexa)+".svg")

    if not os.path.exists(zPathTextureColor):
       mySVG = open(zSVGFileIn, 'r') 
       f = file(zPathTextureColor, "w")
       for line in mySVG:    
           zStr = NetStrInfos(str(QString.fromLocal8Bit(line)), True, True, False, False, ())
           zStr = zStr.replace("fill:#000000","fill:#"+str(MyColorHexa))
           zStr = zStr.replace("stroke:#000000","stroke:#"+str(MyColorHexa))+"\n"
           f.write(zStr.encode("utf-8"))
       f.close()
       mySVG.closed
          
    return zPathTextureColor


#------------------------------------------------
#FONCTION de détermination des seuils de zoom
#------------------------------------------------
def FixeZOOM(zInfos, zLayer, zSizeMap, zSizeMapUnits, indexUnitsZoom, indexValueMinZoom, indexValueMaxZoom, IsZoomLabels):
    zZoomProperties = zInfos.split()
    zUnitsZoom = NetStrInfos(zZoomProperties[indexUnitsZoom], False, False, True, False, ("\"", "'"))
    zValueMinZoom = NetStrInfos(zZoomProperties[indexValueMinZoom], True, True, False, False, ("(", ","))
    zValueMinZoom = float(GetValueZoom(float(zValueMinZoom), zUnitsZoom, zSizeMap, zSizeMapUnits))
    zValueMaxZoom = NetStrInfos(zZoomProperties[indexValueMaxZoom], False, False, False, False, (")"))
    zValueMaxZoom = float(GetValueZoom(float(zValueMaxZoom), zUnitsZoom, zSizeMap, zSizeMapUnits))
    zValueMinZoom = math.floor(zValueMinZoom)    
    zValueMaxZoom = math.ceil(zValueMaxZoom)
    if zValueMaxZoom !=0 and (zValueMinZoom < zValueMaxZoom) :
       if IsZoomLabels :
          zLabel = zLayer.label()
          zLabel.setScaleBasedVisibility(True) 
          zLabel.setMinScale(zValueMinZoom) 
          zLabel.setMaxScale(zValueMaxZoom)  
       else:   
         zLayer.toggleScaleBasedVisibility(True) 
         zLayer.setMinimumScale(zValueMinZoom) 
         zLayer.setMaximumScale(zValueMaxZoom)
    return   

#----------------------------------------------------
#FONCTION pour détermination du seuil de transparence
#----------------------------------------------------
def FixeALPHA(zInfos, zLayer, zSymbol):
    axstyle = zInfos.split()
    aALPHA = int(axstyle[1])
    zALPHA = aALPHA
    aALPHA = round(float(axstyle[1])/255.0,6)
    if aALPHA < 0.0 : aALPHA = 0.0
    if aALPHA > 1.0 : aALPHA = 1.0
    if zLayer.type() == QgsMapLayer.VectorLayer : zSymbol.setAlpha(aALPHA)
    elif zLayer.type() == QgsMapLayer.RasterLayer : zLayer.setTransparency(zALPHA)
    return


def generateTransparencyList(minVal, maxVal, zALPHA ):
    trList = []
    for v in range( int( minVal ), int( maxVal + 1 ) ):
      tr = QgsRasterTransparency.TransparentSingleValuePixel()
      tr.pixelValue = v
      tr.percentTransparent = zALPHA
      trList.append( tr )
    return trList

#------------------------------------------------
#FONCTION de correction des polices noms composés
#------------------------------------------------
def MakePropertiesFONT(zIndex, zRac, zInfos):
   if zRac.find(')')!=-1: return zRac
   zFontProperties = zRac                       
   j = zIndex + 1
   atempostr = str(zInfos[j])
   while atempostr.find(')')==-1:
         zFontProperties = zFontProperties + " " + atempostr
         j+= 1
         atempostr = str(zInfos[j])
   atempostr = str(zInfos[j])
   zFontProperties = zFontProperties + " " + atempostr
   return zFontProperties

#-----------------------------------
#AUTRES FONCTIONS conversion unités
#-----------------------------------
def FixeSize(zSize, zDpi, zUnits):
    if zUnits == "MM" : zSize = float(zSize * zDpi / 25.4)    
    elif zUnits == "CM" : zSize = float(zSize * zDpi / 2.54)
    return zSize  

def CmToPixels(MesureEnCm, zDpi):
    return int(MesureEnCm * zDpi / 2.54)

def MmToPixels(MesureEnMm, zDpi):
    return int(MesureEnCm * zDpi / 25.4) 
       
def CmToTwips(MesureEnCm):
    return int(MesureEnCm * 566.928) 

def DefzTransform(zLayer, zProj4Dest):
    destinationCRS = QgsCoordinateReferenceSystem()
    destinationCRS.createFromProj4(QString(zProj4Dest)) 
    sourceCRS = zLayer.crs()
    zTransform = QgsCoordinateTransform()
    zTransform.setSourceCrs(sourceCRS)
    zTransform.setDestCRS(destinationCRS)
    return zTransform

def AdapteRatioMapInfo(zValue, isLINE, isFONT):
    zCoeff = 1
    if float(zValue)> 10.0 and isLINE and not isFONT: zCoeff = math.ceil(zValue/10.0)* 2
    if float(zValue)< 10.0 and isLINE and not isFONT: zCoeff = 1 
    if float(zValue)> 10.0 and not isLINE and isFONT: zCoeff = 0.5
    zValue = float(zValue)/(RatioMapInfo * zCoeff)   
    return zValue   
   

#-------------------------------------------
# FONCTION REALISATION MISE EN PAGE
#-------------------------------------------
def MakeComposer(self, iComposer, iInfosComposer):
    self.iface.actionPrintComposer().activate(0)
    composerList = self.iface.activeComposers()

    if(len(composerList) < 1): return
    composerView = composerList[0]
    c = composerView.composition()
    if(c is None): return

    c.setPlotStyle(QgsComposition.Preview)
    dpi = c.printResolution()
    dpmm = dpi / 25.4
    dpcm = dpi / 2.54
    w, h = c.paperWidth(), c.paperHeight()

    if int(iComposer) == -1:
        composerMap = QgsComposerMap(c,10.0,10.0,w - 20.0,h-20.0)
        c.addComposerMap(composerMap)
        MakeTEXT(self, c, composerView, c.paperWidth()/3, 10.0, "Ma carte MapInfo", QColor(0,0,255), -1, dpmm, True)
        MakeLEGEND(self, c, composerView, 10.0, 10.0, "-1", QColor(255,240,120), QColor(0,0,0), 0.26)
        MakeNORTHARROW(self, c, composerView, composerMap)        
        MakeSCALEBAR(self, c, composerView, composerMap)

    else:    
        tInfosComposer = iInfosComposer.split("|")
        #Le printer ne sert que si action d'impression derrière
        printer = QPrinter(QPrinter.HighResolution)
        printer.setCreator('OpenWor')
        
        for i in range(len(tInfosComposer)-1,-1, -1):
            stempo = NetStrInfos(tInfosComposer[i], True, False, False, False, ())
            x = stempo.upper()

            if x.find(" ORIENTATION ")!=-1 :
               tX = x.split(" ")
               zIndex = FixeIndex(0,tX, "ORIENTATION")
               if zIndex !=-1:
                  if tX[zIndex]== "PORTRAIT" :
                      c.setPaperSize(float(h), float(w)) 
                      w, h = c.paperHeight(), c.paperWidth()
                      printer.setOrientation(QPrinter.Portrait)
                  else:
                      c.setPaperSize(float(w), float(h)) 
                      w, h = c.paperWidth(), c.paperHeight()
                      printer.setOrientation(QPrinter.Landscape)
                  break

            if x.find("PAPERSIZE")!=-1:
               tX = x.split(" ")
               zIndex = FixeIndex(0,tX, "PAPERSIZE")
               zPaper = int(tX[zIndex])
               w, h = FixePaperSize(zPaper) 
        
        for i in range(len(tInfosComposer)):
            stempo = NetStrInfos(tInfosComposer[i], True, False, False, False, ())
            if stempo.upper().startswith("SET COORDSYS LAYOUT UNITS"):
               stempo = NetStrInfos(stempo.upper(), True, False, False, False, ("SET COORDSYS LAYOUT UNITS " ,"\""))
               zUnit = stempo.lower() 
            elif stempo.upper().startswith("CREATE FRAME"):
               i, composerMap = MakeFRAME(self, c, composerView, tInfosComposer, stempo, i, dpmm)
               MakeSCALEBAR(self, c, composerView, composerMap)
            elif stempo.upper().startswith("CREATE ELLIPSE") or  stempo.upper().startswith("CREATE RECT"): i, composerShape = MakeOBJECT(self, c, composerView, tInfosComposer, stempo, i, dpmm)
            elif stempo.upper().startswith("CREATE LINE"): i = MakeARROW(self, c, composerView, tInfosComposer, stempo, i, dpmm)
            elif stempo.upper().startswith("CREATE TEXT"):
               i = MakeTEXT(self, c, composerView, 0.0, 0.0, tInfosComposer, QColor(255,0,0), i, dpmm, False)
               i+= 1


#-----------------------------
# FONTION NETTOYAGE NOM COUCHE
#-----------------------------
def CleanName(zName):
    zCleanName = str(zName)
    if zCleanName.find("(")!=-1 and zCleanName.find(")")!=-1 :
       ztName = zCleanName.split("(")
       zCleanName = ztName[0].rstrip()
    return zCleanName

#----------------------------------------------------------------------
# FONTIONS GENERIQUES CREATION FONT, APPLICATION OPTIONS GLOBALES OBJET
#----------------------------------------------------------------------
def MakeFONT(zPolice, zSize, zBold, zItalic, zUnderLine, zOverLine, zStrech):
    Font = QFont(zPolice) 
    zFont = QFont(Font)
    zFont.setPointSize(zSize)
    zFont.setBold(zBold)
    zFont.setItalic(zItalic)
    zFont.setUnderline(zUnderLine)
    zFont.setOverline(zOverLine)
    zFont.setStretch(zStrech)
    return zFont

def MakeFRAMEBRUSH(cItem, zBrush, zBackColor):
    brush = QBrush()
    zQtBrush = Qt.NoBrush
    if tBrush.has_key(zBrush): zQtBrush = QgsSymbologyUtils.qString2BrushStyle(tBrush[zBrush])
    brush.setStyle(zQtBrush)
    brush.setColor(zBackColor)
    cItem.setBrush(brush)

def MakeFRAMEPEN(cItem, zPen, zLineColor, zLineSize):
    pen = QPen()
    pen.setColor(zLineColor)
    pen.setWidthF(zLineSize)
    pen.setJoinStyle(Qt.MiterJoin) #Qt.BevelJoin Qt.RoundJoin
    cItem.setPen(pen)


#-------------------------------------------
# SOUS FONCTIONS REALISATION MISE EN PAGE
#-------------------------------------------    
def MakeTEXT(self, c, composerView, posx, posy, zInfos, zColor, zpos, dpmm, isSimpleText):
    zPolice, zFontSize = "Verdana", 24
    zFontBold = False                              
    zFontUnderline = False
    zFontItalic = False
    w, h = 80, 15
    zBackColor = QColor(255,255,255)
    
    if not isSimpleText :
       zText = NetStrInfos(zInfos[zpos+1], True, False, False, False, ("'","\""))
       stempo = NetStrInfos(zInfos[zpos+2], True, False, False, False, ("(", ")"))
       stempo = stempo.replace(" ",",")

       tDim = stempo.split(",")
       posx = float(dpmm * 2 * float(tDim[0]))
       posy = float(dpmm * 2 * float(tDim[1]))
       w = float(dpmm * 2 * (float(tDim[2])-float(tDim[0])))
       h = float(dpmm * 2 * (float(tDim[3])-float(tDim[1])))       

       stempo = NetStrInfos(zInfos[zpos+3], False, False, True, False, ())
       ztempo = stempo.split()
       zIndex = FixeIndex(0,ztempo, "FONT")
       
       
       if zIndex!=-1:
          aFontProperties = MakePropertiesFONT(zIndex, ztempo[zIndex], ztempo)
          aFontProperties = NetStrInfos(aFontProperties, False, False, False, False, ("(", ")"))
          aFont = aFontProperties.split(",")

          if len(aFont)== 5 :
             #il y a un fond ou un halo
             zMakeHalo = ValCarac(int(aFont[1]),2)
             zColor = InvRGB(long(aFont[len(aFont)-2]))
             zBackColor = InvRGB(long(aFont[len(aFont)-1]))
          else:
             zColor = InvRGB(long(aFont[len(aFont)-1]))
          zFontCarac = ValCarac(int(aFont[1]),0)


          if tStyleLabel.has_key(zFontCarac):
             TheStyle = tStyleLabel[zFontCarac]
             zFontBold = TheStyle[0]
             zFontUnderline = TheStyle[1]
             zFontItalic = TheStyle[2]   

          zFontSize = int(aFont[2])
          zPolice = NetStrInfos(aFont[0], True, True, False, True, ("\"", "'"))
       
       labelFont = MakeFONT(zPolice, zFontSize, zFontBold, zFontItalic, zFontUnderline, False, 0)

    else :
       zText = zInfos
       labelFont = MakeFONT(zPolice, zFontSize, zFontBold, zFontItalic, zFontUnderline, False, 2)
       
    composerLabel = QgsComposerLabel(c)
    composerLabel.setText(zText)
    composerLabel.setFont(labelFont)
    composerLabel.setFontColor(zColor)
    composerLabel.setItemPosition(posx, posy, w, h, 0) 
    c.addComposerLabel(composerLabel)
    composerLabel.adjustSizeToText()
    MakeFRAMEBRUSH(composerLabel, "2", zBackColor)  
    
    return (zpos+3)



def MakeARROW(self, c, composerView, zlistCompo, Rac, wpos, dpmm):
    stempo = NetStrInfos(Rac.upper(), False, False, False, False, ("CREATE LINE " ,"(", ")"))
    stempo = stempo.replace(" ",",")
    tDim = stempo.split(",")
                                                                         
    posxs = float(dpmm * 2 * float(tDim[0]))
    posys = float(dpmm * 2 * float(tDim[1]))
    StartPoint = QPointF( posxs, posys)

    posxe = float(dpmm * 2 * float(tDim[2]))
    posye = float(dpmm * 2 * float(tDim[3]))
    EndPoint = QPointF( posxe, posye)

    return
    composerArrow = QgsComposerArrow(StartPoint, EndPoint, c)
    #ou
    #composerArrow = QgsComposerArrow(c)
    #composerArrow.setSceneRect(QRectF(posxs,  posys, posxe, posye))
    if wpos == (len(zlistCompo)-1): return wpos+1    
    zLineColor = Qt.black
    zLineSize = "1.0"

    for mpos in range(wpos+1, len(zlistCompo)):
        line = zlistCompo[mpos]
        astring = str(QString.fromLocal8Bit(zlistCompo[mpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if mpos > tpos :
            if x.startswith('CREATE') or  x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or  x.startswith('SET LEGEND') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
               break
            else :
               if x.startswith("PEN"):
                  zInfos = NetStrInfos(x, False, False, False, False, ("PEN (",")"))
                  vInfos = zInfos.split(",")
                  zLineSize = AdapteRatioMapInfo(float(vInfos[0]), True, False)
                  zPen = str(vInfos[1])
                  zLineColor = InvRGB(long(vInfos[2]))

    composerArrow.setOutlineWidth(zLineSize)
    #MakeFRAMEPEN(composerArrow, "2", zLineColor, zLineSize)
    composerArrow.setArrowColor(zLineColor)
    composerArrow.setArrowHeadWidth(5.0)
    c.addComposerArrow(composerArrow)

    return mpos



def MakeLEGEND(self, c, composerView, posx, posy, zStyleBrush, zFillColor, zLineColor, zLineSize):
    composerLegend = QgsComposerLegend(c)
    layerFont = MakeFONT('Arial',8, True, False, False, False, 0)
    itemFont = MakeFONT('Arial',8, False, False, False, False, 0)
    composerLegend.adjustBoxSize()
    composerLegend.setItemPosition(posx, posy) 
    composerLegend.setItemFont(itemFont)
    composerLegend.setLayerFont(layerFont)
    composerLegend.setTitle("Légende")
    composerLegend.setSymbolWidth(6)
    composerLegend.setSymbolHeight(3)
    composerLegend.setLayerSpace(2)
    composerLegend.setSymbolSpace(1.5)
    composerLegend.setBoxSpace(0)
    if zLineSize > 0 : composerLegend.setFrame(1)
    else : composerLegend.setFrame(0)
    composerLegend.setZValue(30)
    if zStyleBrush == "-1" : zStyleBrush = "2"
    MakeFRAMEBRUSH(composerLegend, zStyleBrush, zFillColor)
    MakeFRAMEPEN(composerLegend, "2", zLineColor, zLineSize)    
    c.addComposerLegend(composerLegend)
    

def MakeTABLE(self, c, composerView, posx, posy, w, h, zLayerName, zFillColor, zLineColor):
    isLayer = False
    Layers = self.iface.legendInterface().layers()
    for layer in Layers:    
        if str(layer.name())== zLayerName:
           isLayer = True 
           break  
    if isLayer :
       headerFont = MakeFONT('Arial',10, True, False, False, False, 0)
       font = MakeFONT('Arial',8, True, True, True, False, 2)
       composerTable = QgsComposerAttributeTable(c)
       composerTable.setItemPosition(posx, posy, w, h, 0)
       composerTable.setVectorLayer(layer)
       composerTable.setMaximumNumberOfFeatures(10)
       composerTable.setDisplayOnlyVisibleFeatures(False)
       composerTable.setHeaderFont(headerFont) 
       composerTable.setContentFont(font)
       composerTable.setGridColor(zLineColor)
       composerTable.setLineTextDistance(0.26)
       MakeFRAMEBRUSH(composerTable, "2", zFillColor)
       c.addComposerTable(composerTable)
       
    
    
def MakeNORTHARROW(self, c, composerView, composerMap):
    composerNorthArrow = QgsComposerPicture(c)
    picNorthArrow = QDir.convertSeparators(QDir.cleanPath(QgsApplication.qgisSettingsDirPath() + "/python/plugins/openwor/svg/arrow/north_arrow.svg"))
    composerNorthArrow.setPictureFile(picNorthArrow)
    composerNorthArrow.setSceneRect(QRectF(0,  0, 32, 32))
    composerNorthArrow.setItemPosition(c.paperWidth()-42, c.paperHeight()-42)
    composerNorthArrow.setRotationMap(0)
    composerNorthArrow.setFrame(0)
    composerNorthArrow.setZValue(10)
    MakeFRAMEBRUSH(composerNorthArrow, "1", Qt.black)
    c.addComposerPicture(composerNorthArrow)


def MakeSCALEBAR(self, c, composerView, composerMap):
    scaleFont = MakeFONT('Arial',10, True, False, False, False, 0)
    composerScaleBar = QgsComposerScaleBar(c)
    composerScaleBar.setComposerMap(composerMap)
    composerScaleBar.setFont(scaleFont)
    #'Single Box', 'Double Box', 'Line Ticks Middle', 'Line Ticks Down', 'Line Ticks Up', 'Numeric' 
    composerScaleBar.setStyle('Double Box')
    zUnits = int(self.iface.mapCanvas().mapRenderer().destinationCrs().mapUnits())
    zValueScale = round(float(composerMap.extent().width()),4)
    szUnits, zValueUnits, zToto = FixeLibUnits(zUnits, zValueScale, zValueScale)
    composerScaleBar.setUnitLabeling(szUnits)
    composerScaleBar.setNumMapUnitsPerScaleBarUnit(float(zToto))
    #Emplacement des étiquettes    
    composerScaleBar.setLabelBarSpace(10.0)
    composerScaleBar.setNumSegments(4)
    composerScaleBar.setFrame(0)
    #taille de la boîte
    composerScaleBar.setBoxContentSpace(0.3) 
    composerScaleBar.update()
    composerScaleBar.setItemPosition(10.0, c.paperHeight()-composerScaleBar.height()-25.0)
    MakeFRAMEBRUSH(composerScaleBar, "2", Qt.black)
    c.addComposerScaleBar(composerScaleBar)
    composerScaleBar.setNumUnitsPerSegment(float(zValueScale/10))
    composerScaleBar.update()    
 

def MakeOBJECT(self, c, composerView, zlistCompo, Rac, wpos, dpmm):
    tpos = -1

    zEnd = Rac.find("(")
    TypeObject = Rac.upper()[7:zEnd-1]
    stempo = NetStrInfos(Rac.upper(), False, False, False, False, ("CREATE " + TypeObject + " " ,"(", ")"))
    stempo = stempo.replace(" ",",")
    tDim = stempo.split(",")
    posx = float(dpmm * 2 * float(tDim[0]))
    posy = float(dpmm * 2 * float(tDim[1]))
    w = float(dpmm * 2 * (float(tDim[2])-float(tDim[0])))
    h = float(dpmm * 2 * (float(tDim[3])-float(tDim[1])))

    composerShape = QgsComposerShape(posx,posy,w,h,c)

    if TypeObject == "ELLIPSE": composerShape.setShapeType(0)
    elif TypeObject == "RECT": composerShape.setShapeType(1)
    elif TypeObject == "CIRCLE": composerShape.setShapeType(2)
    else : composerShape.setShapeType(0)
    
    c.addComposerShape(composerShape)

    if wpos == (len(zlistCompo)-1): return wpos+1    
    zBrush = "2"
    zFillColor = Qt.white
    zPen = "2"
    zLineColor = Qt.black
    zLineSize = "0.26"

    for mpos in range(wpos+1, len(zlistCompo)):
        line = zlistCompo[mpos]
        astring = str(QString.fromLocal8Bit(zlistCompo[mpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if mpos > tpos :
            if x.startswith('CREATE') or  x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or  x.startswith('SET LEGEND') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
               break
            else :
               if x.startswith("PEN"):
                  zInfos = NetStrInfos(x, False, False, False, False, ("PEN (",")"))
                  vInfos = zInfos.split(",")
                  zLineSize = AdapteRatioMapInfo(float(vInfos[0]), True, False)
                  zPen = str(vInfos[1])
                  zLineColor = InvRGB(long(vInfos[2]))
               elif x.startswith("BRUSH"):
                  zInfos = NetStrInfos(x, False, False, False, False, ("BRUSH (",")"))
                  vInfos = zInfos.split(",")
                  zBrush = str(vInfos[0])
                  zFillColor = InvRGB(long(vInfos[1]))

    MakeFRAMEBRUSH(composerShape, zBrush, zFillColor)
    MakeFRAMEPEN(composerShape, zPen, zLineColor, zLineSize)              

    return mpos, composerShape


def MakeFRAME(self, c, composerView, zlistCompo, Rac, wpos, dpmm):
    tpos = -1
    isLegend, isAttributTable = False, False
    composerMap = None
    
    stempo = NetStrInfos(Rac.upper(), False, False, False, False, ("CREATE FRAME " ,"(", ")"))
    stempo = stempo.replace(" ",",")
    tDim = stempo.split(",")
    zBrush = "1"
    zFillColor = Qt.white
    zPen = "2"
    zLineColor = Qt.black
    zLineSize = "0.26"

    posx = float(dpmm * 2 * float(tDim[0]))
    posy = float(dpmm * 2 * float(tDim[1]))
    w = float(dpmm * 2 * (float(tDim[2])-float(tDim[0])))
    h = float(dpmm * 2 * (float(tDim[3])-float(tDim[1])))

    if wpos == (len(zlistCompo)-1): return wpos+1    
    for mpos in range(wpos+1, len(zlistCompo)):
        line = zlistCompo[mpos]
        astring = str(QString.fromLocal8Bit(zlistCompo[mpos]))
        x = NetStrInfos(astring, True, True, True, False, ())
        if mpos > tpos :
            if x.startswith('CREATE') or  x.startswith('SET WINDOW FRONTWINDOW() PRINTER') or x.startswith('LAYOUT') or  x.startswith('SET LEGEND') or x.startswith('SET WINDOW FRONTWINDOW() TITLE') or x.startswith('BROWSE *') or x.startswith('MAP FROM '):
               break
            elif x.startswith('TITLE ') :
               if x.find('LéGENDE')!=-1: isLegend = True
               else :
                  nSTR = NetStrInfos(astring, True, False, False, False, ("Title ","'"))
                  nSTR = nSTR.split(" ")
                  if nSTR[len(nSTR)-1]=="Données" :
                     zLayerName = nSTR[0]
                     isAttributTable = True
            else :
               if x.startswith("BRUSH"):
                  zInfos = NetStrInfos(x, False, False, False, False, ("BRUSH (",")"))
                  vInfos = zInfos.split(",")
                  zBrush = str(vInfos[0])
                  zFillColor = InvRGB(long(vInfos[2])) #1
               if x.startswith("PEN"):
                  zInfos = NetStrInfos(x, False, False, False, False, ("PEN (",")"))
                  vInfos = zInfos.split(",")
                  zLineSize = AdapteRatioMapInfo(float(vInfos[0]), True, False)
                  zPen = str(vInfos[1])
                  zLineColor = InvRGB(long(vInfos[2]))                 

    if not isLegend and not isAttributTable:
       composerMap = QgsComposerMap(c,posx,posy,w,h)
       MakeFRAMEBRUSH(composerMap, zBrush, zFillColor)
       MakeFRAMEPEN(composerMap, zPen, zLineColor, zLineSize)
       c.addComposerMap(composerMap)
    else:
       if isLegend : MakeLEGEND(self, c, composerView, posx, posy, zBrush, zFillColor, zLineColor, zLineSize)
       if isAttributTable : MakeTABLE(self, c, composerView, posx, posy, w, h, zLayerName, zFillColor, zLineColor)
 
    return mpos, composerMap


def FixePaperSize(zPaper):
    #Les x ne sont pas utilisés - orientation paysage ici
    formats = { '304' : ('A0',QPrinter.A0, 1189, 841),
                '305' : ('A1', QPrinter.A1, 841, 594),
                '66'  : ('A2', QPrinter.A2, 594, 420),
                '8'   : ('A3', QPrinter.A3, 420, 297),
                '9'   : ('A4', QPrinter.A4, 297, 210), 
                '11'  : ('A5', QPrinter.A5, 210, 148),
                '70'  : ('A6', QPrinter.A6, 148, 105),
                'x0'  : ('A7', QPrinter.A7, 105, 74),
                'x1'  : ('A8', QPrinter.A8, 74, 52),
                'x3'  : ('B0', QPrinter.B1, 1414, 1000),
                '306' : ('B1', QPrinter.B1, 1000, 707),
                '307' : ('B2', QPrinter.B2, 707, 500),
                '308' : ('B3', QPrinter.B3, 500, 353),
                '12'  : ('B4', QPrinter.B4, 353, 250),
                '13'  : ('B5', QPrinter.B5, 250, 176), 
                '88'  : ('B6', QPrinter.B6, 176,121),
                '28'  : ('C5E', QPrinter.C5E, 228.9, 162),
                'x4'  : ('Comm10E', QPrinter.Comm10E, 241, 105),
                'x5'  : ('DLE', QPrinter.DLE, 210, 99),
                'x6'  : ('Executive', QPrinter.Executive, 184, 267),
                'x7'  : ('Folio', QPrinter.Folio, 470, 370),
                'x8' : ('Ledger', QPrinter.Ledger, 432, 279),
                'x9' : ('Legal', QPrinter.Legal, 215.9, 355.6),
                'x10' : ('Letter', QPrinter.Letter, 216, 279),
                'x11' : ('Tabloid', QPrinter.Tabloid, 279, 432)
               } 
    wpaper, hpaper = 297, 210
    zPaper = str(zPaper)
    if formats.has_key(zPaper):
       zFormat = formats[zPaper]
       TheNameFormat = zFormat[0]
       TheQtFormat = zFormat[1]
       wpaper = float(zFormat[2])
       hpaper = float(zFormat[3])

    return wpaper, hpaper

#-------------------------------------------------
#FONCTION PRISE EN CHARGE DES QML (style à défaut)   
#-------------------------------------------------
def DefautLayerStyle(self, uLayer):
    HasDefautLayerStyle = True
    URIDefautLayerStyle = QDir.convertSeparators(QDir.cleanPath(uLayer[0:len(uLayer)-3]+"qml"))    
    if not os.path.exists(URIDefautLayerStyle): return False, ""
    return HasDefautLayerStyle, URIDefautLayerStyle    
  
           
