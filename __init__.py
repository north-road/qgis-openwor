"""
/*****************************************************************************
 OPENWOR
==========
                                 A QGIS plugin
                 Plugin to load MapInfo Workspace under QGIS
                              -------------------
        begin                : 2010-05-20
        copyright            : (C) 2012 Christophe MASSE (MEDDE)
        email                : christophe.masse@developpement-durable.gouv.fr
 ****************************************************************************/

/*****************************************************************************
 *                                                                           *
 *   This program is free software; you can redistribute it and/or modify    *
 *   it under the terms of the GNU General Public License as published by    *
 *   the Free Software Foundation; either version 2 of the License, or       *
 *   (at your option) any later version.                                     *
 *                                                                           *
 *   This program is distributed in the hope that it will be useful,         *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of          *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           *   
 *   GNU General Public License for more details.                            *
 *                                                                           *
 *   You should have received a copy of the GNU General Public License along *
 *   with this program; if not, write to the Free Software Foundation, Inc., *
 *   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.             *
 *****************************************************************************/
"""

import ConfigParser
import os.path
p = ConfigParser.ConfigParser()
here = os.path.join(os.path.dirname(__file__),"config.ini")
p.read(here)

def name(): return p.get('general','name')
def authorName():  return p.get('general','authorName')
def icon(): return p.get('general','icon')
def description(): return p.get('general','description')
def version(): return p.get('general','version')
def qgisMinimumVersion(): return p.get("general","qgisMinimumVersion")

def classFactory(iface):
  from main import MainPlugin
  return MainPlugin(iface)

