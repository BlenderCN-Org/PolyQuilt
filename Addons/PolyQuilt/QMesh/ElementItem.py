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
import bmesh
import math
import copy
import mathutils
import collections
from mathutils import *
from .. import handleutility
from .. import draw_util

__all__ = ['ElementItem']

class ElementItem :
    def __init__(self , qmesh , element : bmesh.types.BMVert , coord : Vector, hitPosition : Vector , dist = 0 ) :
        self.__element = element
        self.__hitPosition: Vector = copy.copy(hitPosition)
        self.__coord: Vector = copy.copy(coord)
        self.__dist: float = dist
        self.__mirror = None
        self.__qmesh = qmesh
        self.__mirror = None
        self.setup_mirror()

    def setup_mirror( self ) :
        if self.__qmesh is not None :
            is_mirror = self.__qmesh.is_mirror
            if self.__qmesh.is_mirror :
                self.__mirror = self.__qmesh.find_mirror( self.__element )
        else :
            self.__mirror = None


    @property
    def element(self):
        return self.__element

    @property
    def mirror(self):
        return self.__mirror

    @property
    def hitPosition(self) -> Vector :
        return copy.copy(self.__hitPosition)

    @hitPosition.setter
    def hitPosition(self , value : Vector ) -> Vector :
         self.__hitPosition = copy.copy(value)

    @property
    def coord(self) -> Vector :
        return copy.copy(self.__coord)

    @property
    def normal(self) -> Vector :
        if self.isVert :
            return self.__element.normal
        if self.isEdge :
            return ( self.__element.verts[0].normal + self.__element.verts[1].normal ) * 0.5
        if self.isFace :
            return self.__element.normal

        return Vector(1,0,0)

    @property
    def dist(self) -> float:
        return self.__dist

    @property
    def isEmpty(self) -> bool:
        return self.__element is None

    @property
    def isNotEmpty(self) -> bool :
        return self.__element is not None

    @property
    def is_valid(self) -> bool :
        return self.__element is not None and self.__element.is_valid

    @property
    def isVert(self) -> bool :
        return self.type == bmesh.types.BMVert

    @property
    def isEdge(self) -> bool :
        return self.type == bmesh.types.BMEdge

    @property
    def isFace(self) -> bool :
        return self.type == bmesh.types.BMFace

    @property
    def is_x_zero(self) -> bool :
        dist = bpy.context.scene.tool_settings.double_threshold
        return all( [ abs(v.co.x) < dist for v in self.verts ] )

    @property
    def verts( self ) -> bmesh.types.BMVert:
        if self.isEmpty :
            return []
        elif self.isVert :
            return [self.element]
        else :
            return self.element.verts

    @property
    def mirror_verts( self ) -> bmesh.types.BMVert:
        if self.__mirror is None :
            return []
        elif isinstance( self.__mirror , bmesh.types.BMVert ) :
            return [self.__mirror]
        else :
            return self.__mirror.verts

    @property
    def type(self):
        return type(self.__element)

    @staticmethod
    def Empty():
        return ElementItem( None , None , None , None , 0.0 )

    @staticmethod
    def FormVert( qmesh , v ):
        p = handleutility.location_3d_to_region_2d( v.co )
        return ElementItem( qmesh , v , p , v.co , 0.0 )

    @staticmethod
    def FormElement( qmesh ,e , co ):
        p = handleutility.location_3d_to_region_2d( co )
        return ElementItem( qmesh ,e , p , co , 0.0 )

    def Draw( self , obj , color , preferences ) :
        if self.is_valid :
            size = preferences.highlight_vertex_size
            width = preferences.highlight_line_width
            alpha = preferences.highlight_face_alpha
            draw_util.drawElementHilight3D( obj , self.element , size , width ,alpha, color )
            if self.isEdge :
                draw_util.draw_pivots3D( (self.hitPosition,) , 0.75 , color )

            if self.mirror is not None and self.mirror.is_valid :
                color = ( color[0] , color[1] ,color[2] ,color[3] * 0.5 )
                draw_util.drawElementHilight3D( obj , self.mirror , size , width ,alpha , color )

