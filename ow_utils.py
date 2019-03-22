# -*- coding: iso-8859-1 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *


tMapFonction = {"Abs":("null",1,("%")), "Area": ("$area",0,("obj")), "CartesianArea": ("$area",0,("obj")), "CartesianDistance": ("null",1,("obj")), "CartesianObjectLen": ("$length",0,("obj")), "CartesianPerimeter": ("$perimeter",0,("obj")),
                "CentroidX": ("null",1,("obj")), "CentroidY": ("null",1,("obj")), "Chr$": ("GenericFunction",1,("%")), "Cos": ("cos",1,("%")), "CurDate": ("$now",1,("%")), "CurDateTime": ("null",1,("%")), "Day": ("day",1,("%")), "DeformatNumber$": ("format_number",2,("%","%")),
                "Distance": ("null",1,("obj")), "Format$": ("null",2,("%","%")), "FormatDate$": ("format_date",2,("%","%")), "FormatNumber$": ("format_number",2,("%",2)), "FormatTime$": ("null",2,("%","%")), "GetDate": ("$now",0,()), "GetTime": ("$now",0,()),
                "Hour": ("hour",1,("%")), "InStr": ("strpos", 2, ("%","%")), "Int": ("toint",1,("%")), "LCase$": ("lower",1,("%")), "Left$": ("left",2,("%","%")), "Len": ("length",1,("%")), "LTrim$": ("null",1,("%")), "MakeDateTime": ("todatetime",1,("%")), "Maximum": ("null",2,("%","%")), "Mid$": ("substr",3,("%","%","%")),
                "Minimum": ("null",2,("%","%")), "Minute": ("minute",1,("%")), "Month": ("month",1,("%")), "ObjectLen": ("$length",0,("obj")), "Perimeter": ("$perimeter",0,("obj")), "PointToMGRS$": ("null",1,("obj")), "Propers$": ("title",1,("%")), "Right$": ("right",2,("%","%")),
                "Round": ("format_number",2,("%","%")), "RTrim$": ("null",1,("%")), "Second": ("second",1,("%")), "Sin": ("sin",1,("%")), "SphericalArea": ("$area",0,("obj")), "SphericalDistance": ("null",1,("obj")), "SphericalObjectLen": ("$length",0,("obj")), "SphericalPerimeter": ("$perimeter",0,("obj")),                
                "Str$": ("tostring",1,("%")), "UCase$": ("upper",1,("%")), "Val": ("toreal",1,("%")), "Weekday": ("null",1,("%")), "Year": ("year",1,("%"))
              }

zRetLigne =  " '\\n' "

#-----------------------------------------------
#FONCTION RETOURNE EXPRESSION MAPINFO -> QGIS   
#-----------------------------------------------
def CleanExp(zLayer, zExp):
    zprovider = zLayer.dataProvider()
    zfields = zprovider.fields()
    zCarConca = "&" if zExp.find("&")!=-1 else "+"
    tExpression = zExp.split(zCarConca)
    zCleanExp = ""

    for i in range(len(tExpression)):
        if zCleanExp != "" : zCleanExp+= " || "
        if tExpression[i] == "Chr$(13)" : zCleanExp+= zRetLigne
        else :
            NbFonctionsIn, NbFonctionsOut = CountCaractere(tExpression[i],"("), CountCaractere(tExpression[i],")")
            if (tExpression[i].find("'")!=-1 or tExpression[i].find("\"")!=-1) :
                if (NbFonctionsIn!=NbFonctionsOut): NbFonctionsIn, NbFonctionsOut = 0, 0
            if NbFonctionsIn > 0 :
               if (NbFonctionsIn == NbFonctionsOut) : zCleanExp+= NewExpression(tExpression[i])
               else :
                  ztempotExpression = tExpression[i]
                  while NbFonctionsIn > NbFonctionsOut :
                        i+= 1
                        NbFonctionsIn+= CountCaractere(tExpression[i],"(")
                        NbFonctionsOut+= CountCaractere(tExpression[i],")")
                        ztempotExpression+= tExpression[i]
                        
                  zCleanExp+= NewExpression(ztempotExpression)
            else :
              if tExpression[i].find("'")==-1 and tExpression[i].find("\"")==-1:
                 zField =  NetStrInfos(tExpression[i],True, True, False, False, ())
                 zIndexField = zprovider.fieldNameIndex(zField)
                 zCleanExp+= "'" +  zField + "'" if zIndexField == -1 else zField
              else: zCleanExp+= tExpression[i]
    return zCleanExp



def NewExpression(zExpression):
    zindex = zExpression.find("\"")
    if zindex == -1 : zindex = zExpression.find("'")
    if zindex == 0 : return zExpression
    
    ztempo, ztempofunctions = zExpression.split("("), ""

    for j in range(len(ztempo)) :
        zz = NetStrInfos(ztempo[j],True, True, False, False, ())
        if zz.find("+")!=-1 :
           ztempo2 = zz.split("+")
           for k in range(len(ztempo2)):
               zz2 = NetStrInfos(ztempo2[k],True, True, False, False, ())
               if zz2.find(",")!=-1 :
                  ztempo2 = zz2.split(",")
                  zztempo2 = ""
                  for k in range(len(ztempo2)):
                      zz3 = NetStrInfos(ztempo2[k],True, True, False, False, ())
                      if zz3 != "obj" : zztempo2+= zz3 if zztempo2=="" else  "," + zz3
                      else : break 
                  ztempofunctions+= zztempo2 
               else :
                   if tMapFonction.has_key(zz2) :
                      zQGISFunction = tMapFonction[zz2]
                      zQGISNameFunction = zQGISFunction[0]
                      zQGISNbParamFunction = zQGISFunction[1]
                      ztempofunctions+= zQGISNameFunction  if zQGISNbParamFunction==0 else zQGISNameFunction +"("
                   else:
                      ztempofunctions+= zz2 + "+" if k < (len(ztempo2)-1) else zz2  

           
        elif zz.find(",")!=-1 :
           ztempo2 = zz.split(",")
           zztempo2 = ""
           for k in range(len(ztempo2)):
               zz2 = NetStrInfos(ztempo2[k],True, True, False, False, ())
               if zz2 != "obj" : zztempo2+= zz2 if zztempo2=="" else  "," + zz2
               else : break 
           ztempofunctions+= zztempo2 
        else :
            if tMapFonction.has_key(zz) :
               zQGISFunction = tMapFonction[zz]
               zQGISNameFunction = zQGISFunction[0]
               zQGISNbParamFunction = zQGISFunction[1]
               ztempofunctions+= zQGISNameFunction  if zQGISNbParamFunction==0 else zQGISNameFunction +"("
               
            else:    
               ztempofunctions+= zz 

    NbFonctionsIn= CountCaractere(ztempofunctions,"(")
    NbFonctionsOut= CountCaractere(ztempofunctions,")")

    if NbFonctionsOut > NbFonctionsIn : ztempofunctions = "(" + ztempofunctions
    if NbFonctionsOut < NbFonctionsIn : ztempofunctions = ztempofunctions + ")"

    return ztempofunctions




def GenericFunction(zQGISFunction, zQGISParamFunction):
    zRetour = zQGISFunction
    if  zQGISFunction=="Chr$" :
        if int(zQGISParamFunction) > 30 : zRetour = chr(int(zQGISParamFunction[0]) )
    elif zQGISFunction=="Asc" : zRetour = ord(zQGISParamFunction[0])        
    return zRetour

#-----------------------------------------------
#FONCTION RETOURNE LE TYPE MIME D'UN FICHIER   
#----------------------------------------------- 
def fGetTypeFile(stFile):
    mimefile = ""
    if stFile != "":
       if stFile.find(".") != -1:
          tmpStr = stFile.split(".")
          mimefile = str(tmpStr[len(tmpStr)-1])
          mimefile = mimefile.upper()
    return mimefile

#-----------------------------------------------
#FONCTION TEST SI LE CONTENU EST UN NOMBRE FLOAT   
#-----------------------------------------------    
def is_number_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#-----------------------------------------------
#FONCTION TEST SI LE CONTENU EST UN NOMBRE INT   
#-----------------------------------------------    
def is_number_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False 

#-----------------------------------------------
#FONCTION COMPTEUR NB LIGNES FICHIER ASCII   
#-----------------------------------------------    
def NbRowAsciiFILE(AsciiFILE):
    NbRow = 0
    zFile = open(AsciiFILE, 'r')
    myListRow = zFile.readlines()
    zFile.close()
    NbRow = int(len(myListRow))
    return NbRow

#-----------------------------------
#FONCTION mise en forme des chaînes
#-----------------------------------
def NetStrInfos(nStr, tLstrip, tRstrip, tUpper, tTitle, ListCarac):
    for i in range(len(ListCarac)): nStr = nStr.replace(ListCarac[i], "")
    if tLstrip: nStr = nStr.lstrip()
    if tRstrip: nStr = nStr.rstrip()       
    if tUpper: nStr = nStr.upper()
    if tTitle: nStr = nStr.title()
    return nStr

#--------------------------------------------------
#FONCTION de comptage de caractères dans une chaîne
#--------------------------------------------------
def CountCaractere(zStr, zCar):
    #sample "'", "<br>" ...
    CountCaractere = 0
    CountCaractere = zStr.count(zCar) 
    return CountCaractere

#--------------------------------------------------
#FONCTION de restitution d'un libellé d'unité carte
#--------------------------------------------------
def FixeLibUnits(zUnits, zWidth, zScalezBarWidth):
    if zUnits == 0 :
       if zWidth > 1000.0 : szUnits, zWidth, zScalezBarWidth = " km" , zWidth , zScalezBarWidth / 1000 #km, / 1000
       elif zWidth < 0.01 : szUnits, zWidth, zScalezBarWidth = " mm" , zWidth , zScalezBarWidth * 1000 #mm, * 1000
       elif zWidth < 0.1 : szUnits, zWidth, zScalezBarWidth = " cm" , zWidth , zScalezBarWidth * 100 #cm,  * 100
       else : szUnits, zWidth, zScalezBarWidth  = " m", zWidth, zScalezBarWidth 
    elif zUnits == 1 :
       if zWidth > 5280.0 : szUnits, zWidth, ScalezBarWidth = " miles" , zWidth / 5000, (zScalezBarWidth * 5280) / 5000
       elif zWidth == 5280.0 : szUnits, zWidth, ScalezBarWidth = " mile" , zWidth / 5000, (zScalezBarWidth * 5280) / 5000
       elif zWidth < 1.0 : szUnits, zWidth, ScalezBarWidth = " inches" , zWidth * 10, (zScalezBarWidth * 10) / 12
       elif zWidth == 1.0 : szUnits, zWidth, ScalezBarWidth = " foot" , zWidth / 5000, (zScalezBarWidth * 5280) / 5000
       else : szUnits, zWidth, zScalezBarWidth  = " feet", zWidth, zScalezBarWidth
    elif zUnits == 2 :
       if zWidth == 1.0 : szUnits, zWidth, ScalezBarWidth = " degree" , zWidth, zScalezBarWidth
       else : szUnits, zWidth, ScalezBarWidth = " degrees" , zWidth, zScalezBarWidth
    else: szUnits, zWidth, ScalezBarWidth = " inconnu" , zWidth, zScalezBarWidth

    if zScalezBarWidth == 0 : zScalezBarWidth = 1
    
    return szUnits, zWidth, zScalezBarWidth

  
    

