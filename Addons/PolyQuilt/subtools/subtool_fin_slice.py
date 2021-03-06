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

import sys
import bpy
import math
import mathutils
import bmesh
import copy
import bpy_extras
import collections
from .. import handleutility
from .. import draw_util
from ..QMesh import *
from ..dpi import *
from .subtool import SubTool

class SubToolFinSlice(SubTool) :
    name = "FinSliceTool"

    def __init__(self,op, target ) :
        super().__init__(op)
        self.currentTarget = target
        self.slice_rate = 0.0

    def OnUpdate( self , context , event ) :
        if event.type == 'MOUSEMOVE':
            self.slice_rate = self.CalcRate(context,self.mouse_pos)
        elif event.type == 'RIGHTMOUSE' :
            return 'FINISHED'
        elif event.type == 'LEFTMOUSE' : 
            if event.value == 'RELEASE' :
                if self.slice_rate > 0 and self.slice_rate < 1 :
                    self.DoSlice()
                return 'FINISHED'
        return 'RUNNING_MODAL'


    def OnDraw( self , context  ) :
        pass

    def OnDraw3D( self , context  ) :
        self.currentTarget.Draw( self.bmo.obj , self.color_split() , self.preferences )

        for edge in self.currentTarget.element.link_edges :
            v0 = edge.verts[0].co
            v1 = edge.verts[1].co
            draw_util.draw_lines3D( context , (v0,v1) , self.color_split() , self.preferences.highlight_line_width , 1.0 , primitiveType = 'LINES'  )

        if self.bmo.is_mirror and self.currentTarget.mirror is not None :
            s0 = set(self.currentTarget.element.link_edges)
            s1 = set(self.currentTarget.mirror.link_edges)
            edges = ( s0 | s1 ) - ( s0 & s1 )
            vs = [self.currentTarget.element,self.currentTarget.mirror]
        else :
            edges = self.currentTarget.element.link_edges
            vs = [self.currentTarget.element]

        rate = self.slice_rate

        for vert in vs :
            for face in vert.link_faces :
                links = [ e for e in face.edges if e in edges ]
                if len(links) == 2 :
                    for v in vs :
                        if v in links[0].verts :
                            v0 = v.co *(1-rate) + links[0].other_vert(v).co * rate
                        if v in links[1].verts :
                            v1 = v.co *(1-rate) + links[1].other_vert(v).co * rate
                    draw_util.draw_lines3D( context , (v0,v1) , self.color_split() , self.preferences.highlight_line_width , 1.0 , primitiveType = 'LINES'  )

    def CalcRate( self , context , coord ):
        rate = 0.0
        ray = handleutility.Ray.from_screen( context , coord ).world_to_object( self.bmo.obj )
        dist = self.preferences.distance_to_highlight* dpm()
        for edge in self.currentTarget.element.link_edges :
            d = handleutility.CalcRateEdgeRay( self.bmo.obj , context , edge , self.currentTarget.element , coord , ray , dist )
            if d > rate :
                rate = d
        return rate

    def DoSlice( self ) :
        _slice = {}
        _edges = []

        def append( vert , other_vert ) :
            for edge in vert.link_edges :        
                if other_vert is not None :
                    if edge not in other_vert.link_edges :
                        _edges.append( edge )
                else :
                    _edges.append( edge )
                _slice[ edge ] = self.slice_rate if ( edge.verts[0] == vert ) else (1.0 - self.slice_rate)

        if self.bmo.is_mirror and self.currentTarget.mirror is not None :
            append( self.currentTarget.element , self.currentTarget.mirror )
            append( self.currentTarget.mirror , self.currentTarget.element )
        else :
            append( self.currentTarget.element , None )

        geom_inner , geom_split , geom = bmesh.ops.subdivide_edges(
             self.bmo.bm ,
             edges = _edges ,
             edge_percents  = _slice ,
             smooth = 0 ,
             smooth_falloff = 'SMOOTH' ,
             use_smooth_even = False ,
             fractal = 0.0 ,
             along_normal = 0.0 ,
             cuts = 1 ,
             quad_corner_type = 'STRAIGHT_CUT' ,
             use_single_edge = False ,
             use_grid_fill=False,
             use_only_quads = False ,
             seed = 0 ,
             use_sphere = False 
        )

        self.bmo.UpdateMesh()

