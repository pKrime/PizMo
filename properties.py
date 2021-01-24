import bpy
from bpy.props import PointerProperty
from bpy.props import StringProperty
from bpy.props import EnumProperty
from bpy.props import BoolProperty

from . import wizmo
from importlib import reload
reload(wizmo)


def register_properties():

    display_types = (
        ("mesh", "Mesh", "Object mesh"),
        ("shape", "Shape", "Geometric shape"),
        ("none", "None", "No Pizmo shape"),
    )

    shape_types = (
        ("circle", "Circle", "Circle Shape"),
        ("quad", "Quad", "Quad Shape"),
        ('none', "None", "No Shape"),
    )

    bpy.types.PoseBone.pizmo_vis_type = EnumProperty(items=display_types,
                                                     name="Display Type",
                                                     default=None)

    bpy.types.PoseBone.pizmo_vis_shape = EnumProperty(items=shape_types,
                                                      name="Shape Type",
                                                      default='none')

    bpy.types.PoseBone.pizmo_shape_frame = BoolProperty(name="Use Frame",
                                                        default=False)

    bpy.types.PoseBone.pizmo_bone_follow = BoolProperty(name="Follow Bone",
                                                        default=True)

    bpy.types.PoseBone.pizmo_vis_mesh = PointerProperty(type=bpy.types.Object,
                                                        name="Widget Mesh",
                                                        description="Object to use for widget display",
                                                        poll=lambda self, obj: obj.type == 'MESH',
                                                        update = wizmo.GrouzMo.mark_dirty)

    bpy.types.PoseBone.pizmo_vert_grp = StringProperty(name="Widget Display Group",
                                                       description="Vertices used for Selection Gizmo",
                                                       update=wizmo.GrouzMo.mark_dirty)


def unregister_properties():
    del bpy.types.PoseBone.pizmo_vis_type
    del bpy.types.PoseBone.pizmo_vis_shape
    del bpy.types.PoseBone.pizmo_shape_frame

    del bpy.types.PoseBone.pizmo_vis_mesh
    del bpy.types.PoseBone.pizmo_vert_grp
