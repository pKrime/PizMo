# ====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation, version 3.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ======================= END GPL LICENSE BLOCK ========================


bl_info = {
    "name": "PizMo",
    "version": (0, 0, 1),
    "author": "Paolo Acampora",
    "blender": (2, 90, 0),
    "description": "Display Bone Picker along object",
    "category": "Interface",
}


import bpy

from . import wizmo

from importlib import reload
reload(wizmo)

from .wizmo import AddzMo
from .wizmo import BonezMo, BonezMo3D, ArmzMo
from .wizmo import GrouzMo, GrouzMoRoots
from .ui import BONE_PT_pizmo_buttons

from bpy.props import PointerProperty, StringProperty

# REGISTER #


def register():
    bpy.utils.register_class(ArmzMo)
    bpy.utils.register_class(AddzMo)
    bpy.utils.register_class(BonezMo)
    bpy.utils.register_class(BonezMo3D)
    bpy.utils.register_class(GrouzMo)
    bpy.utils.register_class(GrouzMoRoots)
    bpy.utils.register_class(BONE_PT_pizmo_buttons)

    bpy.types.PoseBone.pizmo_vis_shape = PointerProperty(type=bpy.types.Object,
                                                         name="Pizmo Visual Shape",
                                                         description="Object to use for widget display",
                                                         poll=lambda self, obj: obj.type == 'MESH')

    bpy.types.PoseBone.pizmo_vert_grp = StringProperty(name="Pizmo Display Group",
                                                       description="Vertices used for Selection Gizmo")


def unregister():
    bpy.utils.unregister_class(BONE_PT_pizmo_buttons)
    bpy.utils.unregister_class(GrouzMoRoots)
    bpy.utils.unregister_class(GrouzMo)
    bpy.utils.unregister_class(BonezMo)
    bpy.utils.unregister_class(BonezMo3D)
    bpy.utils.unregister_class(AddzMo)
    bpy.utils.unregister_class(ArmzMo)

    del bpy.types.PoseBone.pizmo_vis_shape
    del bpy.types.PoseBone.pizmo_vert_grp