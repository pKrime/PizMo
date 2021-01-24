import bpy
from bpy.props import PointerProperty
from bpy.props import StringProperty
from bpy.props import EnumProperty
from bpy.props import BoolProperty
from bpy.props import FloatProperty
from bpy.props import FloatVectorProperty

from . import wizmo
from importlib import reload
reload(wizmo)


def register_bone_properties():

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
                                                        update=wizmo.GrouzMo.mark_dirty)

    bpy.types.PoseBone.pizmo_vert_grp = StringProperty(name="Widget Display Group",
                                                       description="Vertices used for Selection Gizmo",
                                                       update=wizmo.GrouzMo.mark_dirty)


def register_armature_properties():
    armature_type = bpy.types.Armature

    armature_type.pizmo_armature_widget = BoolProperty(name="Armature Widget",
                                                       default=False,
                                                       update=wizmo.GrouzMoRoots.mark_dirty)

    armature_type.pizmo_color_base = FloatVectorProperty(name="Widgets Base Color",
                                                         subtype='COLOR',
                                                         default=[0.1, 0.1, 0.1],
                                                         )

    armature_type.pizmo_color_selected = FloatVectorProperty(name="Selected Widgets Color",
                                                             subtype='COLOR',
                                                             default=[0.3, 0.6, 0.7],
                                                             )

    armature_type.pizmo_color_highlight = FloatVectorProperty(name="Widgets Highlight Color",
                                                              subtype='COLOR',
                                                              default=[0.2, 0.5, 0.6],
                                                              )

    armature_type.pizmo_color_alpha = FloatProperty(name="Widgets Alpha",
                                                    min=0.0, max=1.0, default=0.25,
                                                    subtype='PERCENTAGE')


def register_properties():
    register_bone_properties()
    register_armature_properties()


def unregister_properties():
    del bpy.types.PoseBone.pizmo_vis_type
    del bpy.types.PoseBone.pizmo_vis_shape
    del bpy.types.PoseBone.pizmo_shape_frame

    del bpy.types.PoseBone.pizmo_vis_mesh
    del bpy.types.PoseBone.pizmo_vert_grp

    del bpy.types.Armature.pizmo_armature_widget
    del bpy.types.Armature.pizmo_color_base
    del bpy.types.Armature.pizmo_color_highlight
    del bpy.types.Armature.pizmo_color_alpha
    del bpy.types.Armature.pizmo_color_selected
