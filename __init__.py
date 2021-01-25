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
from . import properties
from . import ui

from importlib import reload
reload(wizmo)
reload(properties)
reload(ui)

from .wizmo import BonezMo3D, ArmzMo
from .wizmo import GrouzMo, GrouzMoRoots
from .ui import BONE_PT_pizmo_properties
from .ui import ARMATURE_PT_pizmo_properties


# REGISTER #
def register():
    properties.register_properties()

    bpy.utils.register_class(ArmzMo)
    bpy.utils.register_class(BonezMo3D)
    bpy.utils.register_class(GrouzMo)
    bpy.utils.register_class(GrouzMoRoots)
    bpy.utils.register_class(BONE_PT_pizmo_properties)
    bpy.utils.register_class(ARMATURE_PT_pizmo_properties)


def unregister():
    bpy.utils.unregister_class(ARMATURE_PT_pizmo_properties)
    bpy.utils.unregister_class(BONE_PT_pizmo_properties)
    bpy.utils.unregister_class(GrouzMoRoots)
    bpy.utils.unregister_class(GrouzMo)
    bpy.utils.unregister_class(BonezMo3D)
    bpy.utils.unregister_class(ArmzMo)

    properties.unregister_properties()
