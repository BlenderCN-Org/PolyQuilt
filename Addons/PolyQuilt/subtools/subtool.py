# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import blf
import math
import mathutils
import bmesh
from enum import Enum , auto
import bpy_extras
import collections
from ..QMesh.QMesh import *
import time


class SubTool :
    name = "None"
    __timer_handle = None
   
    def __init__(self,op) :
        self.operator = op
        self.bmo : QMesh = op.bmo
        self.debugStr = ""
        self.subTool = None
        self.__enterySubTool = None
        self.step = 0
        self.mouse_pos = mathutils.Vector((0,0))
        self.preferences = op.preferences

    def Active(self) :
        return self if self.subTool == None else self.subTool

    def GetCursor(self) :
        return 'DEFAULT'

    def SetSubTool( self , subTool ) :
        self.__enterySubTool = subTool 

    def OnInit( self , context ) :
        pass

    def OnExit( self ) :
        pass

    def OnUpdate( self , context , event ) :
        return 'FINISHED'

    def OnDraw( self , context  ) :
        pass

    def OnDraw3D( self , context  ) :
        pass

    def Update( self , context , event ) :

        ret = 'FINISHED'
        self.mouse_pos = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))

        if self.__enterySubTool != None :
            self.subTool = self.__enterySubTool
            self.__enterySubTool = None
            self.OnEnterSubTool( context , self.subTool)

        if self.subTool != None :
            ret = self.subTool.Update(context , event)
            if ret == 'FINISHED' :
                self.subTool.OnExit()
                ret = self.OnExitSubTool( context , self.subTool)
                self.subTool = None
        else :
            ret = self.OnUpdate(context,event)

        if ret == 'FINISHED' :
            self.OnExit()

        self.step += 1
        return ret

    def Draw2D( self , context  ) :
        if self.subTool != None :
            self.subTool.Draw2D(context )
        else :
            self.OnDraw(context)
        pass

    def Draw3D( self , context  ) :
        if self.subTool != None :
            self.subTool.Draw3D(context )
        else :
            self.OnDraw3D(context)
        pass

    def OnEnterSubTool( self ,context,subTool ):
        pass

    def OnExitSubTool( self ,context,subTool ):
        return 'RUNNING_MODAL'

    def AddTimerEvent( self , context , time = 1.0 / 60.0 ) :
        if SubTool.__timer_handle is not None :
            SubTool.__timer_handle = context.window_manager.event_timer_add( time , window = context.window)

    def RemoveTimerEvent( self , context ) :
        if SubTool.__timer_handle is not None:
            context.window_manager.event_timer_remove(SubTool.__timer_handle)
            SubTool.__timer_handle = None
        
    def color_highlight( self , alpha = 1.0 ) :
        col = self.preferences.highlight_color
        return (col[0],col[1],col[2],col[3] * alpha)

    def color_create( self , alpha = 1.0 ) :
        col = self.preferences.makepoly_color        
        return (col[0],col[1],col[2],col[3] * alpha)

    def color_split( self , alpha = 1.0 ) :
        col = self.preferences.split_color            
        return (col[0],col[1],col[2],col[3] * alpha)

    def color_delete( self ,alpha = 1.0 ) :
        col = self.preferences.delete_color            
        return (col[0],col[1],col[2],col[3] * alpha)

