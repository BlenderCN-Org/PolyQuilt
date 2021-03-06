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
import math
import mathutils
import bmesh
import bpy_extras
import collections
from .. import handleutility
from .. import draw_util
from ..QMesh import *
from ..mouse_event_util import ButtonEventUtil, MBEventType
from .subtool import *
from .subtool_makepoly import *
from .subtool_knife import *
from .subtool_edge_slice import *
from .subtool_move import *
from .subtool_fin_slice import *

class SubToolDefault(SubTool) :
    name = "DefaultSubTool"

    def __init__(self,op,currentTarget) :
        super().__init__(op)        
        self.currentTarget = currentTarget
        self.LMBEvent = ButtonEventUtil('LEFTMOUSE' , self , SubToolDefault.LMBEventCallback , op.preferences  )
        self.isExit = False

    @staticmethod
    def LMBEventCallback(self , event ):
        self.debugStr = str(event.type)
        if event.type == MBEventType.Down :
            pass

        elif event.type == MBEventType.Release :
            self.isExit = True

        elif event.type == MBEventType.Click :
            if self.currentTarget.isVert or self.currentTarget.isEmpty or self.currentTarget.isEdge:
                self.SetSubTool( SubToolMakePoly(self.operator,self.currentTarget , self.mouse_pos ) )

        elif event.type == MBEventType.LongClick :
            if self.currentTarget.isVert :
                self.bmo.dissolve_vert( self.currentTarget.element , False , False )
            elif self.currentTarget.isEdge :
                self.bmo.dissolve_edge( self.currentTarget.element , False , False )
            elif self.currentTarget.isFace :
                self.bmo.Remove( self.currentTarget.element )
            self.bmo.UpdateMesh()
            self.currentTarget = ElementItem.Empty()

        elif event.type == MBEventType.Drag :
            if self.currentTarget.isNotEmpty :
                self.SetSubTool( SubToolMove(self.operator,self.currentTarget , self.mouse_pos ) )

        elif event.type == MBEventType.LongPressDrag :
            if self.currentTarget.isEdge :
                self.SetSubTool( SubToolEdgeSlice(self.operator,self.currentTarget.element) )   
            elif self.currentTarget.isVert :
                self.SetSubTool( SubToolFinSlice(self.operator,self.currentTarget ) )   
            elif self.currentTarget.isEmpty :
                self.SetSubTool( SubToolKnife(self.operator,event.mouse_pos) )   

    def OnUpdate( self , context , event ) :
        if self.isExit :
            return 'FINISHED'

        if event.type == 'MOUSEMOVE' and self.LMBEvent.Press == False :
            self.currentTarget = self.bmo.PickElement( self.mouse_pos , self.preferences.distance_to_highlight )

        self.LMBEvent.Update(context,event)

        return 'RUNNING_MODAL'

    def OnDraw( self , context  ) :
        if self.LMBEvent.isPresure :
            if self.currentTarget.isNotEmpty :
                self.LMBEvent.Draw( self.currentTarget.coord , "Melt")
            else:
                self.LMBEvent.Draw( None , "Knife")

    def OnDraw3D( self , context  ) :
        if self.currentTarget.isNotEmpty :
            color = self.color_highlight()
            if self.LMBEvent.presureComplite :
                color = self.color_delete()
            self.currentTarget.Draw( self.bmo.obj , color , self.preferences )

    def OnEnterSubTool( self ,context,subTool ):
        self.currentTarget = ElementItem.Empty()
        self.LMBEvent.Reset(context)

    def OnExitSubTool( self ,context,subTool ):
        self.currentTarget = self.bmo.PickElement( self.mouse_pos , self.preferences.distance_to_highlight )
        return 'FINISHED'

    def OnExit( self ) :
        pass
